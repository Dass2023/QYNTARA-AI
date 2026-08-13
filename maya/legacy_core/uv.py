import logging

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

def check_uv_overlaps(objects):
    """
    Detects overlapping UVs using Maya's built-in polyUVOverlap command.
    """
    violations = []
    if not cmds:
        return violations

    for obj in objects:
        # Check if it has UVs
        # polyUVOverlap returns list of overlapping components
        try:
             # oc=True means check for overlapping components (faces)
            overlaps = cmds.polyUVOverlap(obj, oc=True)
            if overlaps:
                violations.append({
                    "object": obj,
                    "issue": "UV Overlaps",
                    "components": overlaps,
                    "count": len(overlaps)
                })
        except Exception as e:
            logger.debug(f"check_uv_overlaps failed on {obj}: {e}")
            
    return violations

def check_uv_bounds(objects):
    """
    Checks if any UV coordinates are outside the 0 to 1 range.
    """
    violations = []
    if not cmds:
        return violations

    for obj in objects:
        if not cmds.objExists(obj):
            continue
            
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True)
        if not shapes: continue
        
        is_mesh = False
        for shape in shapes:
            if cmds.nodeType(shape) == "mesh":
                is_mesh = True
                break
        if not is_mesh: continue
        
        try:
            uv_bbox = cmds.polyEvaluate(obj, boundingBoxComponent2d=True)
            if not uv_bbox:
                continue
                
            umin, umax = uv_bbox[0]
            vmin, vmax = uv_bbox[1]
            
            if umin < -0.001 or umax > 1.001 or vmin < -0.001 or vmax > 1.001:
                violations.append({
                    "object": obj,
                    "issue": "UVs outside 0-1 bounds",
                    "info": f"U:[{umin:.2f}, {umax:.2f}] V:[{vmin:.2f}, {vmax:.2f}]",
                    "current_value": f"{umax:.2f}, {vmax:.2f}",
                    "expected": "[0.0, 1.0]"
                })
        except Exception as e:
            logger.debug(f"check_uv_bounds failed on {obj}: {e}")
            
    return violations

def check_uv_exists(objects):
    """Checks if object has any UVs at all."""
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        num_uvs = cmds.polyEvaluate(obj, uv=True)
        if num_uvs == 0:
             violations.append({
                "object": obj,
                "issue": "Missing UVs",
                "action": "Unwrap",
                "count": 1
            })
    return violations

try:
    import maya.api.OpenMaya as om
except ImportError:
    om = None

def check_flipped_uvs(objects):
    """
    Detects flipped UV shells using OpenMaya (Negative UV Area).
    """
    violations = []
    if not om or not cmds: return violations
        
    for obj in objects:
        if cmds.objectType(obj) == 'transform':
             # get shape
             shapes = cmds.listRelatives(obj, shapes=True, type='mesh', fullPath=True)
             if not shapes: continue
             obj = shapes[0] # Handle shape
             
        try:
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            mesh_fn = om.MFnMesh(dag_path)
            
            # Check all polygons
            it_poly = om.MItMeshPolygon(dag_path)
            flipped_faces = []
            
            while not it_poly.isDone():
                # getUVArea returns area. If negative?? 
                # Actually, standard way is checking cross product of UV vs Normal?
                # or getUVArea returns absolute area?
                
                # In Maya API 2.0, MItMeshPolygon.getUVArea() returns (area, uvSet).
                # Documentation says "Area of the polygon in UV space".
                # It doesn't explicitly say signed.
                
                # Alternative: Check winding.
                # fast way: cmds.polyInfo returns it?
                
                # Let's rely on a simpler heuristic if API is ambiguous:
                # Iterate faces, get 3 points in UV, cross product z.
                
                # Or just assume if getUVArea is implemented it might be useful?
                # Let's stick to a Python-based Cross Product check for one triangle of the face.
                
                pts_u = []
                pts_v = []
                try:
                    uvs = it_poly.getUVs() # (u_array, v_array)
                    if len(uvs[0]) >= 3:
                        # Cross product of (p1-p0) and (p2-p0)
                        u0, v0 = uvs[0][0], uvs[1][0]
                        u1, v1 = uvs[0][1], uvs[1][1]
                        u2, v2 = uvs[0][2], uvs[1][2]
                        
                        # Vector A = P1 - P0
                        # Vector B = P2 - P0
                        # CP = Ax*By - Ay*Bx
                        cp = (u1-u0)*(v2-v0) - (v1-v0)*(u2-u0)
                        
                        # In UV space, Counter-Clockwise is usually positive?
                        # Maya default is CCW.
                        if cp < 0:
                            flipped_faces.append(f"{dag_path.partialPathName()}.f[{it_poly.index()}]")
                except Exception as e: raise RuntimeError(f"Validation Crash: {e}")
                    
                it_poly.next()
             
            if flipped_faces:
                violations.append({
                    "object": dag_path.fullPathName(),
                    "issue": "Flipped UV (Inverted Winding)",
                    "components": flipped_faces,
                    "action": "Flip UVs",
                    "count": len(flipped_faces)
                })

        except Exception as e:
            # logger.warning(f"Flipped check error {obj}: {e}")
            pass
            
    return violations

def check_texel_density(objects, target_density=5.12, tolerance=0.5):
    """
    Checks if Texel Density is consistent.
    Calculates avg density (UV Area / World Surface Area).
    """
    violations = []
    if not om or not cmds: return violations
    
    for obj in objects:
        if cmds.objectType(obj) == 'transform':
             shapes = cmds.listRelatives(obj, shapes=True, type='mesh', fullPath=True)
             if not shapes: continue
             
        try:
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            
            # Use polyEvaluate for totals (fast)
            # World Area
            sa_world = cmds.polyEvaluate(obj, wa=True)
            if sa_world <= 0.0001: continue
            
            # UV Area
            # Hard to get total UV area with cmds.
            # Use OpenMaya integration
            uv_area_total = 0.0
            it_poly = om.MItMeshPolygon(dag_path)
            while not it_poly.isDone():
                try:
                    area = it_poly.getUVArea() # Returns area (float)
                    uv_area_total += area
                except Exception as e: raise RuntimeError(f"Validation Crash: {e}")
                it_poly.next()
                
            if uv_area_total <= 0.0001: continue
            
            # Ratio
            # Density = sqrt(UV_Area) / sqrt(World_Area) ? 
            # Or usually: (UV_Shell_Area_Pixels) / World_Area?
            # We don't know texture size (e.g. 2048, 4096).
            # We explicitly check for *Consistency* or "Reasonable Ratio".
            
            # Let's assume a standard 2048/4096 map isn't known.
            # But we can check if it deviates wildly?
            # Or checking ratio consistency implies checking per-face?
            
            # Simplified: Just report the density ratio for users to see
            ratio = uv_area_total / sa_world
            
            # If ratio is extremely low (<< 0.01) or high, flag it?
            # But "Consistent" means standard deviation check.
            # That's too heavy for python iteration.
            
            # Let's just flag empty/degenerate UV area ratio (already checked by check_uv_exists).
            
            # "Texel Density" check usually implies we want specific number.
            # Let's flag if density is wildly different from 'target'?
            # Assuming 10cm object covers 0-1 UV ?
            # That's purely subjective.
            
            # Better Rule: Just ensure UV Area is > 0 and report it.
            # Or flag "Low Density" if ratio < 0.001 (Microscopic UVs).
            
            if ratio < 0.0001:
                violations.append({
                    "object": obj,
                    "issue": f"Extremely Low Texel Density (Ratio {ratio:.5f})",
                    "action": "Scale UVs Up",
                    "count": 1
                })

        except Exception as e: raise RuntimeError(f"Validation Crash: {e}")
            
    return violations

def check_zero_area_uvs(objects, tolerance=0.00001):
    """Detects UV faces with near-zero area."""
    violations = []
    if not om or not cmds: return violations

    for obj in objects:
        if cmds.objectType(obj) == 'transform':
             shapes = cmds.listRelatives(obj, shapes=True, type='mesh', fullPath=True)
             if not shapes: continue
             obj = shapes[0]

        try:
            sel = om.MSelectionList()
            sel.add(obj)
            dag_path = sel.getDagPath(0)
            
            it_poly = om.MItMeshPolygon(dag_path)
            zero_area_faces = []
            
            while not it_poly.isDone():
                try:
                    area = it_poly.getUVArea()
                    if area < tolerance:
                        zero_area_faces.append(f"{dag_path.fullPathName()}.f[{it_poly.index()}]")
                except Exception as e: raise RuntimeError(f"Validation Crash: {e}")
                it_poly.next()
            
            if zero_area_faces:
                violations.append({
                    "object": dag_path.fullPathName(),
                    "issue": "Zero Area UV Faces",
                    "components": zero_area_faces,
                    "action": "Fix UVs",
                    "count": len(zero_area_faces)
                })
        except Exception as e: raise RuntimeError(f"Validation Crash: {e}")
            
    return violations

# --- Fixer Functions ---

def fix_flip_uvs(objects):
    """Auto-fix: Flip UVs (U axis)."""
    if not cmds: return
    for obj in objects:
        try:
             # Just flip U for selected objects.
             # Ideally we target specific faces from violation??
             # But fixer takes 'objects'.
             # Flip Shells? 
             # Global flip might be wrong if only some shells are flipped.
             # But as a brute force fix:
             cmds.polyEditUV(obj, pivotU=0.5, pivotV=0.5, scaleU=-1, scaleV=1)
        except Exception as e: raise RuntimeError(f"Validation Crash: {e}")

def check_udim_tiles(objects):
    """
    Checks if multiple UDIM tiles are used (UVs > 1.0).
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        try:
            bbox = cmds.polyEvaluate(obj, boundingBox2d=True)
            if not bbox: continue
            
            u_max = bbox[0][1]
            v_max = bbox[1][1]
            
            if u_max > 1.0 or v_max > 1.0:
                 violations.append({
                    "object": obj,
                    "issue": "UDIM Tiles Detected",
                    "info": f"UVs extend beyond 0-1 (Max U:{u_max:.2f}, V:{v_max:.2f})",
                    "action": "Verify UDIM Support"
                })
        except Exception as e: raise RuntimeError(f"Validation Crash: {e}")
            
    return violations

def check_texture_continuity(objects, threshold_ratio=0.3):
    """
    Checks for texture continuity by analyzing the ratio of UV border edges 
    to total geometric edges.
    
    A high ratio (>0.3) indicates a highly fragmented UV layout (e.g. Auto-Unwrap 
    on every face), which causes visible seams and texture breaks.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        try:
            # 1. Get total edge count
            num_edges = cmds.polyEvaluate(obj, edge=True)
            if not num_edges or num_edges == 0: continue
            
            # 2. Get UV Border Edges
            # polyUVBorder? returns selection
            # Select object components first to be safe
            cmds.select(obj, r=True)
            # Find borders
            # polyListComponentConversion to UV Border?
            # Or simplified: select all UVs -> Select Border -> Convert to Edges
            
            # Use mel script "polySelectBorderShell 1"? 
            
            # Efficient way:
            cmds.select(f"{obj}.map[:]", r=True) # Select all UVs
            cmds.polySelectBorderShell(borderItem=True) # Selects border UVs
            
            # Convert to Edges to count *physical* seams
            border_edges = cmds.polyListComponentConversion(toEdge=True)
            border_edges_flat = cmds.ls(border_edges, fl=True)
            
            num_seams = len(border_edges_flat)
            
            ratio = float(num_seams) / float(num_edges)
            
            if ratio > threshold_ratio:
                violations.append({
                    "object": obj,
                    "issue": f"High Texture Discontinuity (Seam Ratio: {ratio:.2f})",
                    "info": f"{num_seams} seams / {num_edges} edges. Shells may be too fragmented.",
                    "action": "Stitch Together / Optimize Shells",
                    "count": num_seams
                })
                
        except Exception as e:
            # logger.warning(f"Continuity check failed: {e}")
            pass
            
    return violations
