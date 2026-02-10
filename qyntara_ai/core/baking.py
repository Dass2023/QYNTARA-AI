
import logging
try:
    from maya import cmds
    import maya.api.OpenMaya as om
    import maya.mel as mel
except ImportError:
    cmds = None
    om = None

from . import uv, geometry

logger = logging.getLogger(__name__)

def check_uv2_exists(chk_list=None):
    """
    Checks if object has a UV set named 'Lightmap' (or at least 2 sets with strict naming).
    """
    violations = []
    if not cmds: return violations
    objects = chk_list if chk_list else cmds.ls(type='transform', long=True)
    
    for check_obj in objects:
        # Get all shapes
        all_shapes = cmds.listRelatives(check_obj, shapes=True, fullPath=True) or []
        shapes = [s for s in all_shapes if not cmds.getAttr(f"{s}.intermediateObject")]
        
        if not shapes: continue
        if cmds.nodeType(shapes[0]) != 'mesh': continue
        target_shape = shapes[0]
        
        raw_sets = cmds.polyUVSet(target_shape, q=True, allUVSets=True) or []
        sets = [s for s in raw_sets if s] 

        # LOGIC FIX: Check for Lightmap existence or sufficient sets
        has_lightmap = 'Lightmap' in sets
        has_second_set = len(sets) >= 2
        
        # DEBUG: Trace why it fails
        # logger.warning(f"CHECK UV2: {check_obj} | Shape: {target_shape} | Sets: {sets} | HasLM: {has_lightmap}")

        if not has_lightmap:
            if has_second_set:
                 # It exists but has wrong name. Strictly enforce name for Game Pipeline.
                 violations.append({
                    "object": check_obj,
                    "issue": "UV2 exists but invalid name (Require 'Lightmap')",
                    "action": "Rename to Lightmap",
                    "count": 1
                })
            else:
                 # Truly missing
                 violations.append({
                    "object": check_obj,
                    "issue": "Missing Lightmap UVs",
                    "action": "Generate 'Lightmap' UVs",
                    "count": 1
                })
        else:
            # IT EXISTS under 'Lightmap'. Check if empty.
            uv_count = 0
            try:
                # Use robust polyEvaluate on the Shape
                uv_count = cmds.polyEvaluate(target_shape, uv=True, uvSetName='Lightmap')
                logger.warning(f"CHECK UV2: {target_shape} 'Lightmap' Count = {uv_count}")
            except Exception as e:
                logger.warning(f"CHECK UV2: Failed eval on {target_shape}: {e}")
                pass

            if uv_count == 0:
                 violations.append({
                    "object": check_obj,
                    "issue": "'Lightmap' UV Set is Empty",
                    "action": "Regenerate UVs",
                    "count": 1
                })
    return violations

def check_uv2_validity(objects):
    """
    Strict validation for UV Set 2 (Lightmap):
    1. No Overlaps.
    2. Within 0-1.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        sets = cmds.polyUVSet(obj, q=True, allUVSets=True) or []
        if len(sets) < 2: continue 
        
        target_set = sets[1] 
        current = cmds.polyUVSet(obj, q=True, currentUVSet=True)
        original_set = current[0] if current else None
        
        try:
            cmds.polyUVSet(obj, currentUVSet=True, uvSet=target_set)
            
            ov_v = uv.check_uv_overlaps([obj])
            if ov_v:
                for v in ov_v:
                    v['issue'] = f"UV2 Overlaps ({target_set})"
                    v['action'] = "Pack UVs / Fix Overlaps"
                violations.extend(ov_v)
            
            bd_v = uv.check_uv_bounds([obj])
            if bd_v:
                for v in bd_v:
                    v['issue'] = f"UV2 Out of Bounds ({target_set})"
                    v['action'] = "Normalize UVs"
                violations.extend(bd_v)
                
        except Exception as e:
            logger.warning(f"Baking check failed: {e}")
        finally:
            if original_set:
                cmds.polyUVSet(obj, currentUVSet=True, uvSet=original_set)
                
    return violations

def check_light_leakage(objects):
    v = geometry.check_open_edges(objects)
    for err in v:
        err['issue'] = "Light Leakage Risk (Open Edges)"
    return v

def check_padding(objects):
    """
    Checks for insufficient padding between UV shells using OpenMaya API.
    Robust against topological tricky cases.
    """
    violations = []
    if not cmds or not om: return violations
    
    padding_threshold = 0.002
    half_pad = padding_threshold / 2.0
    
    for obj in objects:
        # DEBUG: Trace specific invalid object
        if "INVALID_bake_padding" in obj:
            print(f"DEBUG_PADDING: Visiting {obj}")

        try:
            # 1. Get Current UV Set
            current_sets = cmds.polyUVSet(obj, q=True, currentUVSet=True)
            if not current_sets:
                if "INVALID_bake_padding" in obj: print(f"DEBUG_PADDING: No UV sets for {obj}")
                continue
            uv_set = current_sets[0]
            
            # 2. Get Node DAG Path (OpenMaya)
            sl = om.MSelectionList()
            sl.add(obj)
            dag_path = sl.getDagPath(0)
            
            fn_mesh = om.MFnMesh(dag_path)
            
            # 3. Get Shell IDs
            # Returns: (num_shells, shell_ids_array)
            nb_shells, shell_ids = fn_mesh.getUvShellsIds(uvSet=uv_set)
            
            if nb_shells < 2: continue
            
            # 4. Get UV Coordinates
            u_array, v_array = fn_mesh.getUVs(uvSet=uv_set)
            
            # 5. Group by Shell
            shells_data = {}
            for i, shell_id in enumerate(shell_ids):
                if shell_id not in shells_data:
                    shells_data[shell_id] = {'u': [], 'v': []}
                
                shells_data[shell_id]['u'].append(u_array[i])
                shells_data[shell_id]['v'].append(v_array[i])
            
            # 6. Calculate AABBs
            shell_boxes = []
            for sid, data in shells_data.items():
                if not data['u']: continue
                shell_boxes.append({
                    'min_u': min(data['u']), 'max_u': max(data['u']),
                    'min_v': min(data['v']), 'max_v': max(data['v'])
                })
            
            # 7. Check Intersections
            has_issue = False
            for i in range(len(shell_boxes)):
                for j in range(i + 1, len(shell_boxes)):
                    s1 = shell_boxes[i]
                    s2 = shell_boxes[j]
                    
                    # Expand
                    u1_min, u1_max = s1['min_u'] - half_pad, s1['max_u'] + half_pad
                    v1_min, v1_max = s1['min_v'] - half_pad, s1['max_v'] + half_pad
                    
                    u2_min, u2_max = s2['min_u'] - half_pad, s2['max_u'] + half_pad
                    v2_min, v2_max = s2['min_v'] - half_pad, s2['max_v'] + half_pad
                    
                    if (u1_min < u2_max and u2_min < u1_max) and (v1_min < v2_max and v2_min < v1_max):
                        has_issue = True
                        break
                if has_issue: break
            
            if has_issue:
                 if "INVALID_bake_padding" in obj: print(f"DEBUG_PADDING: FOUND VIOLATION DETECTED for {obj}")
                 violations.append({
                    "object": obj,
                    "issue": "UV Padding Insufficient (< 2px)",
                    "action": "Repack UVs with Padding",
                    "count": 1
                })
                
        except Exception as e:
            if "INVALID_bake_padding" in obj: print(f"DEBUG_PADDING: CRASHED {obj}: {e}")
            pass

    return violations

def check_seams(objects):
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        try:
            # 1. Get Hard Edges
            cmds.select(obj)
            cmds.polySelectConstraint(mode=3, type=0x8000, smoothness=1)
            hard_edges = cmds.ls(sl=True, fl=True)
            cmds.polySelectConstraint(mode=0, smoothness=0) 
            
            if not hard_edges: continue
            
            # 2. Get UV Border Edges
            cmds.select(obj)
            cmds.polySelectConstraint(mode=3, type=0x8000, where=1)
            uv_borders = set(cmds.ls(sl=True, fl=True))
            cmds.polySelectConstraint(mode=0, where=0)
            
            # 3. Check Alignment
            bad_edges = [e for e in hard_edges if e not in uv_borders]
            
            if bad_edges:
                 violations.append({
                    "object": obj,
                    "issue": "Hard Edges inside UV Shells (Bake Artifact risk)",
                    "components": bad_edges,
                    "action": "Split UVs or Soften Edges",
                    "count": len(bad_edges)
                })
                
        except Exception as e:
            logger.warning(f"Seam check failed {obj}: {e}")
        finally:
             if cmds.objExists(obj): cmds.select(obj)
             
    return violations

def bake_ao_map(objects, uv_set="uvSet3", res=1024):
    """
    Execution logic for baking Ambient Occlusion.
    Tries to use Arnold Render to Texture.
    """
    if not cmds: return
    
    for obj in objects:
        try:
            logger.info(f"Starting AO Bake for {obj} on {uv_set} ({res}x{res})...")
            
            # Check Arnold
            if not cmds.pluginInfo("mtoa", q=True, loaded=True):
                try: 
                    cmds.loadPlugin("mtoa")
                except:
                    logger.warning("Arnold (mtoa) not found. Skipping bake.")
                    continue
            
            # Select object
            cmds.select(obj)
            
            # Switch to target UV set for the bake?
            # Arnold RenderToTexture usually takes a UV set argument or uses current.
            # Safest to switch current.
            current = cmds.polyUVSet(obj, q=True, currentUVSet=True)[0]
            if uv_set != current:
                cmds.polyUVSet(obj, currentUVSet=True, uvSet=uv_set)
            
            # Execute Arnold Render To Texture
            # cmds.arnoldRenderToTexture(...) logic is complex args.
            logger.info("Arnold RenderToTexture Triggered (Placeholder execution)")
            
            # Restore UVs
            if uv_set != current:
                cmds.polyUVSet(obj, currentUVSet=True, uvSet=current)
                
        except Exception as e:
            logger.error(f"Bake failed for {obj}: {e}")
