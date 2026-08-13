import logging

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

def check_default_material(objects):
    """
    Checks if objects are using the default 'lambert1' material.
    """
    violations = []
    if not cmds:
        return violations

    for obj in objects:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        if not shapes:
            continue
            
        for shape in shapes:
            # Find shading engine
            sgs = cmds.listConnections(shape, type='shadingEngine') or []
            for sg in sgs:
                mats = cmds.ls(cmds.listConnections(sg), materials=True) or []
                for mat in mats:
                    if mat == "lambert1":
                        violations.append({
                            "object": obj,
                            "issue": "Default Material Usage",
                            "components": [shape],
                            "info": f"Using {mat}"
                        })
    return violations

def check_multi_materials(objects):
    """
    Checks if objects have more than 1 material assigned (Multi-Sub).
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        shapes = cmds.listRelatives(obj, shapes=True) or []
        for shape in shapes:
            sgs = cmds.listConnections(shape, type='shadingEngine') or []
            # sgs might be duplicates if per-face assignment
            unique_sgs = list(set(sgs))
            
            if len(unique_sgs) > 1:
                violations.append({
                    "object": obj,
                    "issue": f"Multiple Materials ({len(unique_sgs)})",
                    "components": sgs,
                    "action": "Combine Materials",
                    "count": len(unique_sgs)
                })
    return violations

def check_shader_naming(objects, convention="M_"):
    """Checks if shaders follow a naming convention (e.g. start with M_)."""
    violations = []
    if not cmds: return violations
    
    seen_mats = set()
    for obj in objects:
        shapes = cmds.listRelatives(obj, shapes=True) or []
        for shape in shapes:
            sgs = cmds.listConnections(shape, type='shadingEngine') or []
            for sg in sgs:
                mats = cmds.ls(cmds.listConnections(sg), materials=True) or []
                for mat in mats:
                    if mat in seen_mats: continue
                    seen_mats.add(mat)
                    
                    if not mat.startswith(convention):
                         violations.append({
                            "object": mat,
                            "issue": "Bad Shader Naming",
                            "expected": f"Starts with {convention}",
                            "action": "Rename",
                            "count": 1
                        })
    return violations

def check_missing_shader(objects):
    """Checks for faces with no shader assigned (green/wireframe)."""
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        shapes = cmds.listRelatives(obj, shapes=True, ni=True) or []
        for shape in shapes:
             sgs = cmds.listConnections(shape, type='shadingEngine')
             if not sgs:
                 violations.append({
                    "object": obj,
                    "issue": "Missing Material/Shader",
                    "action": "Assign Material",
                    "count": 1
                })
    return violations
    
def check_complex_nodes(objects):
    """
    Checks for complex node graphs upstream of material (e.g. blendColors, ramps, math nodes).
    Simple Game Exports usually only want File Textures connected to Standard Surface/Lambert.
    """
    violations = []
    if not cmds: return violations
    
    # Heuristic: Check history of material. If node type count > X?
    # Or specifically check for forbidden nodes.
    
    forbidden = ['blendColors', 'remapHsv', 'ramp', 'reverse', 'multiplyDivide', 'plusMinusAverage']
    # These are often baked out or not supported in basic FBX.
    
    seen_mats = set()
    for obj in objects:
         shapes = cmds.listRelatives(obj, shapes=True) or []
         for shape in shapes:
            sgs = cmds.listConnections(shape, type='shadingEngine') or []
            for sg in sgs:
                 mats = cmds.ls(cmds.listConnections(sg), materials=True) or []
                 for mat in mats:
                     if mat in seen_mats: continue
                     seen_mats.add(mat)
                     
                     history = cmds.listHistory(mat)
                     # Filter history for forbidden types
                     bad_nodes = cmds.ls(history, type=forbidden)
                     if bad_nodes:
                         violations.append({
                            "object": mat,
                            "issue": "Complex / Unsupported Nodes",
                            "components": bad_nodes,
                            "info": "Bake textures",
                            "count": len(bad_nodes)
                        })
    return violations

# --- Fixer Functions ---

def fix_assign_default(objects):
    """Auto-fix: Assign 'initialShadingGroup' (lambert1) to objects."""
    if not cmds: return
    for obj in objects:
        try:
            # Assign default shader
            cmds.sets(obj, edit=True, forceElement="initialShadingGroup")
        except: pass

# --- Utilities ---

def assign_checker_material(objects):
    """
    Creates and assigns a utility Checker pattern (Grey/DarkGrey).
    Useful for UV visualization.
    """
    if not cmds or not objects: return
    
    mat_name = "M_Qyntara_Checker"
    if not cmds.objExists(mat_name):
        mat_name = cmds.shadingNode("lambert", asShader=True, name=mat_name)
        sg_name = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=mat_name + "SG")
        cmds.connectAttr(f"{mat_name}.outColor", f"{sg_name}.surfaceShader")
        
        # Create Checker
        checker = cmds.shadingNode("checker", asTexture=True, name="T_Qyntara_Checker")
        place = cmds.shadingNode("place2dTexture", asUtility=True, name="P_Qyntara_Checker")
        
        cmds.connectAttr(f"{place}.outUV", f"{checker}.uvCoord")
        cmds.connectAttr(f"{place}.outUvFilterSize", f"{checker}.uvFilterSize")
        cmds.connectAttr(f"{checker}.outColor", f"{mat_name}.color")
        
        # Set Colors (Professional Grey/Dark)
        cmds.setAttr(f"{checker}.color1", 0.7, 0.7, 0.7, type="double3")
        cmds.setAttr(f"{checker}.color2", 0.3, 0.3, 0.3, type="double3")
        cmds.setAttr(f"{place}.repeatU", 20)
        cmds.setAttr(f"{place}.repeatV", 20)
        
    # Get SG
    sgs = cmds.listConnections(mat_name, type="shadingEngine")
    if sgs:
        sg = sgs[0]
        for obj in objects:
            try:
                cmds.sets(obj, forceElement=sg)
            except: pass
            
def assign_default_material(objects):
    """Wraps fix_assign_default for external use."""
    return fix_assign_default(objects)

def check_material_usage_limit(objects, max_materials=2):
    """
    Warns if a single mesh has too many materials assigned (Draw Call impact).
    Default max is 2. Mobile often prefers 1.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        shapes = cmds.listRelatives(obj, shapes=True, fullPath=True) or []
        if not shapes: continue
        
        for shape in shapes:
            shading_engines = cmds.listConnections(shape, type='shadingEngine') or []
            # Remove duplicates
            shading_engines = list(set(shading_engines))
            
            if len(shading_engines) > max_materials:
                violations.append({
                    "object": obj,
                    "issue": f"Excessive Material Count ({len(shading_engines)})",
                    "info": f"Limit is {max_materials}. High draw calls risk.",
                    "action": "Combine Materials or Split Mesh"
                })
                
    return violations

def check_texture_size(objects, max_res=2048):
    """
    Checks texture resolutions. Flags > 2048 or Non-Power-Of-Two.
    """
    violations = []
    if not cmds: return violations
    
    # Find all file nodes (Global check)
    file_nodes = cmds.ls(type="file")
    
    for file_node in file_nodes:
        # Check if connected to selection? skipping for now, check global for scene
        if not cmds.objExists(file_node): continue

        try:
             # outSize is reliable if file loaded
             res = cmds.getAttr(f"{file_node}.outSize")[0] # returns (w, h)
             w, h = int(res[0]), int(res[1])
             
             if w == 0 or h == 0: continue

             # Check Max Res
             if w > max_res or h > max_res:
                 violations.append({
                     "object": file_node,
                     "issue": f"Large Texture ({w}x{h})",
                     "info": f"Exceeds max {max_res}px.",
                     "action": "Downscale Texture"
                 })
                 
             # Check POT (Power of Two)
             is_pot_w = (w & (w-1) == 0) and w != 0
             is_pot_h = (h & (h-1) == 0) and h != 0
             
             if not (is_pot_w and is_pot_h):
                  violations.append({
                     "object": file_node,
                     "issue": f"NPOT Texture ({w}x{h})",
                     "info": "Dimensions are not Power-of-Two.",
                     "action": "Resize to POT"
                 })
        except:
            pass # Failed to read res
            
    return violations
