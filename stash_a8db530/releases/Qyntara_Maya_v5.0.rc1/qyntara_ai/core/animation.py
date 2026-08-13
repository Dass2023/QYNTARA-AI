
import logging
try:
    from maya import cmds
    import maya.api.OpenMaya as om
    import maya.mel as mel
except ImportError:
    cmds = None
    om = None

logger = logging.getLogger(__name__)

def check_skin_weights(objects):
    """
    Validates Skin Weights:
    1. Max Influences (Limit 4 for Game/VR, 8 typically).
    2. Normalized Weights (Sum approx 1.0).
    """
    violations = []
    if not cmds: return violations
    
    LIMIT = 4 # Hardcoded limit for Game profile (Configurable ideally)
    
    for obj in objects:
        if not cmds.objExists(obj): continue
        
        # Check for Skin Cluster
        hist = cmds.listHistory(obj) or []
        skin_clusters = [n for n in hist if cmds.nodeType(n) == 'skinCluster']
        
        if not skin_clusters:
            continue # Not a rigged mesh, skip
            
        sc = skin_clusters[0]
        
        # Check Max Influences setting on the node first (Cheap)
        max_inf = cmds.getAttr(f"{sc}.maxInfluences")
        if max_inf > LIMIT:
            violations.append({
                "object": obj,
                "issue": f"Max Influences set to {max_inf} (Limit {LIMIT})",
                "action": "Set Max Influences to 4 and Prune Weights"
            })
            continue

        # Check normalization?
        # Typically Maya enforces this unless 'normalizeWeights' is off.
        norm_mode = cmds.getAttr(f"{sc}.normalizeWeights")
        if norm_mode == 0: # None
             violations.append({
                "object": obj,
                "issue": "Skin Cluster Normalization is OFF",
                "action": "Enable Interactive Normalization"
            })
            
    return violations

def check_animation_baked(objects):
    """
    Checks if animation is baked onto the controls/joints.
    Criteria: Keyframes present on every frame of the timeline range?
    Or just keys present.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        # Only check joints or controls? 
        # Typically we check the ROOT or top hierarchy.
        # Use user selection.
        
        if cmds.nodeType(obj) not in ['joint', 'transform']:
            continue
            
        # Check for animation curves
        anim = cmds.listConnections(obj, type="animCurve")
        if not anim:
            # If it's a static mesh, ignore.
            # If it's a joint in a rig file, might be an issue?
            # User intent: "Animation baked to joints".
            # If joint has NO animation, it's not baked.
            if cmds.nodeType(obj) == 'joint':
                 violations.append({
                    "object": obj,
                    "issue": "Joint has no animation keys (Not Baked?)",
                    "action": "Bake Simulation"
                })
            continue
            
        # Check sampling (Every frame?)
        # Get times of first curve
        kf = cmds.keyframe(anim[0], q=True, tc=True)
        if not kf: continue
        
        # Simple heuristic: Check if keys are integers (baked) vs sparse
        # If baked, we expect consecutive integers.
        # Check gap between first two keys
        if len(kf) > 1:
            diff = kf[1] - kf[0]
            if diff > 1.01: # Use tolerant check
                violations.append({
                    "object": obj,
                    "issue": "Sparse Keyframes detected (Sim not baked?)",
                    "action": "Bake Simulation to Every Frame"
                })

    return violations

def check_root_motion(objects):
    """
    Checks if Root Bone has animation (for Game Engines).
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if "root" in obj.lower() or "reference" in obj.lower():
            # Check translation keys
            anim = cmds.listConnections(obj, type="animCurveTL") # Translate Linear?
            # Or check attributes tx, ty, tz connection
            is_animated = False
            for axis in ['tx', 'ty', 'tz']:
                 if cmds.listConnections(f"{obj}.{axis}", type="animCurve"):
                     is_animated = True
                     break
            
            if "INVALID_anim_root_motion" in obj:
                print(f"DEBUG_ROOT: Object={obj} Is_Animated={is_animated}")

            if not is_animated:
                # If pipeline requires root motion, this is an error
                violations.append({
                    "object": obj,
                    "issue": "Root Motion Missing (Root joint static)",
                    "action": "Ensure Root moves with character"
                })
        
    return violations

def check_constraints(objects):
    """
    Checks for remaining constraints (should be removed/baked).
    """
    violations = []
    if not cmds: return violations
    
    # We scan the hierarchy of the input objects
    all_nodes = cmds.listRelatives(objects, allDescendents=True, fullPath=True) or []
    all_nodes.extend(objects)
    
    constraint_types = ['parentConstraint', 'pointConstraint', 'orientConstraint', 'scaleConstraint', 'aimConstraint']
    
    found_constraints = []
    for node in all_nodes:
        if cmds.nodeType(node) in constraint_types:
            found_constraints.append(node)
            
    for c in found_constraints:
        violations.append({
            "object": c,
            "issue": f"Constraint Node Found: {cmds.nodeType(c)}",
            "action": "Bake Animation and Delete Constraints"
        })
        
    return violations

def check_max_joints(objects, max_limit=64):
    """
    Checks if skin clusters have more than `max_limit` influences.
    WebGL often limits to 64 or 128 bones per mesh.
    """
    violations = []
    if not cmds: return violations
    
    for obj in objects:
        if not cmds.objExists(obj): continue
        
        hist = cmds.listHistory(obj) or []
        skins = [n for n in hist if cmds.nodeType(n) == 'skinCluster']
        
        if not skins: continue
        skin = skins[0]
        
        # Count connected matrix inputs (influences)
        # matrix attributes are typically 'matrix[0]', 'matrix[1]', etc.
        # But easier to just list connections to matrix plug
        influences = cmds.skinCluster(skin, q=True, influence=True)
        if not influences: continue
        
        count = len(influences)
        
        if count > max_limit:
            violations.append({
                "object": obj,
                "issue": f"Too Many Joints: {count} (Limit {max_limit})",
                "action": "Reduce Split Mesh or Reduce Influences"
            })
            
    return violations
