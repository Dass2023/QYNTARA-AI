import logging

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

def check_scene_units(objects, expected_unit="cm"):
    """
    Verifies that the Maya scene linear units match the expected unit.
    Default expected is 'cm'.
    """
    violations = []
    if not cmds:
        return violations
    
    current = cmds.currentUnit(q=True, linear=True)
    if current != expected_unit:
        violations.append({
            "object": "Scene",
            "issue": f"Incorrect Linear Unit: '{current}'",
            "expected": expected_unit,
            "action": f"Change to '{expected_unit}'"
        })
    return violations

def check_up_axis(objects, expected_axis="y"):
    """
    Verifies the scene up-axis (Y-up vs Z-up).
    """
    violations = []
    if not cmds:
        return violations

    current = cmds.upAxis(q=True, axis=True) # returns 'y' or 'z'
    if current != expected_axis:
        violations.append({
            "object": "Scene",
            "issue": f"Incorrect Up-Axis: '{current}'",
            "expected": expected_axis,
            "action": f"Change to '{expected_axis}'-up"
        })
    return violations
    return violations

def check_unused_nodes(objects, type_filter=["camera", "light"]):
    """
    Checks for unused default cameras/lights or clutter.
    Focuses on top-level cameras that are not standard (persp, top, etc).
    """
    violations = []
    if not cmds: return violations
    
    # Check extra cameras
    cameras = cmds.ls(type='camera')
    defaults = ['perspShape', 'topShape', 'sideShape', 'frontShape']
    
    # Find cameras that are not defaults and not referenced?
    # Actually request says "Delete unused cameras/lights".
    # Just listing non-default cameras as potential clutter if "Clean scenes" is required.
    
    extras = [c for c in cameras if c not in defaults and not cmds.referenceQuery(c, isNodeReferenced=True)]
    if extras:
        violations.append({
            "object": "Scene",
            "issue": f"Extra Cameras Found ({len(extras)})",
            "components": extras,
            "action": "Delete Unused",
            "count": len(extras)
        })
        
    # Check Lights?
    # If it's a modeling file, lights might be clutter.
    lights = cmds.ls(type=['light', 'areaLight', 'spotLight', 'pointLight', 'directionalLight'])
    if lights:
         violations.append({
            "object": "Scene",
            "issue": f"Lights in Output Scene ({len(lights)})",
            "components": lights,
            "action": "Delete Lights",
            "count": len(lights)
        })
    
    return violations
    
def check_hierarchy(objects):
    """
    Checks if objects are grouped logically (not just strictly world children).
    Simple check: Are objects strictly under world? (Bad practice usually, need Root group).
    """
    violations = []
    if not cmds: return violations
    
    # Handle Re-validation of Global Rule
    if len(objects) == 1 and objects[0] in ["Scene", "Scene Structure"]:
         assemblies = cmds.ls(assemblies=True)
         defaults = ['persp', 'top', 'front', 'side']
         objects = [a for a in assemblies if a not in defaults]
    
    roots = []
    for obj in objects:
        if not cmds.objExists(obj): continue
        
        parent = cmds.listRelatives(obj, parent=True)
        if not parent:
            roots.append(obj)
            
    if len(roots) > 1:
        violations.append({
             "object": "Scene Structure",
             "issue": "Multiple Root Objects (No Single Group)",
             "components": roots,
             "action": "Group Under One Root",
             "count": len(roots)
        })
        
    return violations

def check_scene_pollution(objects):
    """
    Checks for unwanted plugins or nodes that bloat the file (e.g. Turtle, Bifrost).
    """
    violations = []
    if not cmds: return violations
    
    # List of plugins to flag
    bad_plugins = ['Turtle', 'BifrostGraph', 'MASH', 'Boss', 'haar', 'xgenToolkit']
    
    for plugin in bad_plugins:
        if cmds.pluginInfo(plugin, q=True, loaded=True):
            # Check if actual nodes exist? Or just flag the plugin?
            # Flagging plugin is safer as it saves metadata that carries over.
            violations.append({
                "object": "Scene",
                "issue": f"Unwanted Plugin Loaded: {plugin}",
                "action": f"Unload {plugin} and Delete Nodes"
            })
            
    # Check specifically for Turtle nodes which are notorious
    turtle_nodes = cmds.ls("Turtle*", type="unknown") + cmds.ls(type="ilrBakeLayer")
    if turtle_nodes:
        violations.append({
            "object": "Scene",
            "issue": f"Turtle Nodes Found ({len(turtle_nodes)})",
            "components": turtle_nodes,
            "action": "Delete Turtle Nodes"
        })
        
    return violations

def check_clean_outliner(objects):
    """
    Checks for unused Display Layers and Empty Sets.
    """
    violations = []
    if not cmds: return violations
    
    # Check Display Layers
    layers = cmds.ls(type="displayLayer")
    default_layer = "defaultLayer"
    extras = [l for l in layers if l != default_layer]
    if extras:
        violations.append({
             "object": "Scene",
             "issue": f"Display Layers Found ({len(extras)})",
             "components": extras,
             "action": "Delete Display Layers"
        })
        
    # Check Empty Sets
    sets = cmds.ls(type="objectSet")
    # Exclude default sets
    defaults = ['defaultLightSet', 'defaultObjectSet', 'initialParticleSE', 'initialShadingGroup']
    for s in sets:
        if s not in defaults:
            members = cmds.sets(s, q=True)
            if not members:
                 violations.append({
                     "object": s,
                     "issue": "Empty Set",
                     "action": "Delete Empty Set"
                 })
                 
    return violations

def check_lod_group(objects):
    """
    Checks if LOD groups exist in the scene.
    Useful for game pipelines where LODs are expected.
    """
    violations = []
    if not cmds: return violations
    
    # Check if any lodGroup nodes exist
    lods = cmds.ls(type="lodGroup")
    
    if not lods:
         violations.append({
             "object": "Scene",
             "issue": "No LOD Groups Found",
             "action": "Create LOD Groups for Optimization"
         })
         
    return violations
