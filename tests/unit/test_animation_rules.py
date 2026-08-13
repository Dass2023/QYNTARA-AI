
import logging
import maya.cmds as cmds
import os
import sys

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AnimTest")

def run_anim_test():
    logger.info("=== TEST: ANIMATION & MATERIAL RULES ===")
    
    # Clean Scene
    cmds.file(new=True, force=True)
    
    # 1. SETUP VIOLATIONS
    
    # A. Material Violation: No Shader (Green)
    cube = cmds.polyCube(name="NoShaderCube")[0]
    # Default is lambert1 usually, but let's ensure it's "lambert1" (Default Material Violation)
    # And create a face with NO shader? Hard to do in Maya without crash, usually assigns default.
    # We will test "Default Material" rule.
    
    # B. Material Violation: Complex Nodes
    sphere = cmds.polySphere(name="ComplexMatSphere")[0]
    mat = cmds.shadingNode("blinn", asShader=True, name="ComplexBlinn")
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="ComplexBlinnSG")
    cmds.connectAttr(mat + ".outColor", sg + ".surfaceShader")
    cmds.sets(sphere, forceElement=sg)
    
    # Add Forbidden Node (e.g. blendColors)
    blend = cmds.shadingNode("blendColors", asUtility=True)
    cmds.connectAttr(blend + ".output", mat + ".color")
    
    # C. Animation: Root Motion (Missing)
    # Create "Root" joint
    root = cmds.joint(name="Root_Jnt")
    # No keys on root = Violation
    
    # D. Animation: Constraints (Live)
    # Create constraint
    loc = cmds.spaceLocator(name="TargetLoc")[0]
    cmds.parentConstraint(loc, root, name="LiveConstraint")
    
    # E. Animation: Skin Weights (Max Inf > 4)
    # Bind skin
    cyl = cmds.polyCylinder(name="SkinCyl")[0]
    j1 = cmds.joint(p=(0,0,0))
    j2 = cmds.joint(p=(0,5,0))
    j3 = cmds.joint(p=(0,10,0))
    j4 = cmds.joint(p=(0,15,0))
    j5 = cmds.joint(p=(0,20,0))
    
    sc = cmds.skinCluster([j1,j2,j3,j4,j5], cyl, toSelectedBones=True)[0]
    # Set Max Influences to 5
    cmds.setAttr(sc + ".maxInfluences", 5)
    
    # F. Animation: Baked (Missing keys on joint)
    # j1 has no keys. Violation.
    
    # 2. RUN VALIDATOR
    if "qyntara_ai" not in sys.modules:
        sys.path.append("e:/QYNTARA AI")
        
    from qyntara_ai.ui import main_window
    window = main_window.QyntaraMainWindow()
    
    # Force Game Profile (Strict)
    window.combo_mode.setCurrentText("Game Engines") # Assuming this maps to "game" profile
    
    logger.info("Running Validation (Game Profile)...")
    window.run_validation()
    
    report = window.last_report
    valid_map = {d["rule_id"]: d for d in report.get("details", [])}
    
    # 3. VERIFY
    
    def check_rule(rule_id, expected_obj):
        if rule_id in valid_map:
            violators = [v["object"] for v in valid_map[rule_id].get("violations", [])]
            # Check partial match (long names vs short)
            found = any(expected_obj in v for v in violators)
            if found:
                logger.info(f"[PASS] Detected {rule_id} on {expected_obj}")
            else:
                 logger.error(f"[FAIL] {rule_id} NOT detected on {expected_obj}. Violators: {violators}")
        else:
             logger.error(f"[FAIL] Rule {rule_id} not found in report.")

    check_rule("mat_default", "NoShaderCube") # Default material
    check_rule("mat_complex", "ComplexBlinn") # Material name or object? Rule reports Material usually.
    check_rule("anim_root_motion", "Root_Jnt")
    check_rule("anim_constraints", "LiveConstraint") # Or object with constraint? 
    # check_constraints reports constraint node.
    check_rule("anim_skin_weights", "SkinCyl")
    check_rule("anim_baked", "Root_Jnt") # or j1

    logger.info("Test Complete.")

if __name__ == "__main__":
    run_anim_test()
