import re
import logging

try:
    from maya import cmds
except ImportError:
    cmds = None

logger = logging.getLogger(__name__)

def check_naming_convention(objects, pattern=r"^([A-Z]+)_([\w]+)_([A-Z]{3})$"):
    """
    Checks if object names match a regex pattern.
    Default pattern expects: CATEGORY_Name_XYZ (e.g. PROP_Chair_GEO)
    """
    violations = []
    
    # Compile regex
    try:
        regex = re.compile(pattern)
    except re.error:
        logger.error(f"Invalid regex pattern: {pattern}")
        return violations

    for obj in objects:
        # Get short name
        short_name = obj.split("|")[-1]
        
        if not regex.match(short_name):
            violations.append({
                "object": obj,
                "issue": "Naming Convention Violation",
                "info": f"Name {short_name} does not match {pattern}"
            })
    return violations
    return violations

def check_collision_naming(objects):
    """
    Validates that collision meshes (UCX_, UBX_, USP_) have a matching render mesh.
    Example: UCX_ChairParent_01 must correspond to ChairParent.
    """
    violations = []
    if not cmds: return violations
    
    # Prefixes for collision
    prefixes = ["UCX_", "UBX_", "USP_"]
    
    for obj in objects:
        short = obj.split("|")[-1]
        
        is_collision = False
        prefix_used = ""
        for p in prefixes:
            if short.startswith(p):
                is_collision = True
                prefix_used = p
                break
                
        if is_collision:
            # Expected render mesh name: Remove prefix, remove suffix numbers (_01, _02)
            # Strategy: UCX_BaseName_01 -> BaseName
            # Or strict: UCX_BaseName -> BaseName. UE4/5 usually allows UCX_BaseName_suffix
            
            # Simple check: Does *some* object exists that matches the core name?
            core_name = short[len(prefix_used):] # Strip prefix
            
            # If suffix like _01, _02 exists, try stripping it?
            # Let's check exact match first
            if not cmds.objExists(core_name):
                 # Try stripping suffix _01..._99
                 found = False
                 # Regex to strip trailing _\d+
                 base_name = re.sub(r'_\d+$', '', core_name)
                 
                 if cmds.objExists(base_name):
                     found = True
                 else:
                     # Maybe parent?
                     pass
                     
                 if not found:
                     violations.append({
                         "object": obj,
                         "issue": "Orphaned Collision Mesh",
                         "info": f"Could not find render mesh '{core_name}' or '{base_name}'",
                         "action": "Rename to match render mesh"
                     })
                     
    return violations
