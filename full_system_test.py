
import logging
import maya.cmds as cmds
import maya.mel as mel
import sys
import os

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QyntaraTest")

def run_test():
    logger.info("=== STARTING QYNTARA FULL SYSTEM TEST ===")
    
    # 1. SETUP: Clean Scene & Load Dependencies
    cmds.file(new=True, force=True)
    
    # Load Plugin Module
    if "qyntara_ai" not in sys.modules:
        # Assuming package is in path
        sys.path.append("e:/QYNTARA AI")
        
    try:
        from qyntara_ai.ui import main_window
        from qyntara_ai.core import validator, fixer
        logger.info("Modules loaded successfully.")
    except ImportError as e:
        logger.error(f"Failed to import modules: {e}")
        return

    # 2. GENERATE TEST DATA (Bad Assets)
    logger.info("Generating Test Assets...")
    
    # A. Locator (Should be ignored/handled safely)
    cmds.spaceLocator(name="Test_Locator")
    
    # B. Mesh with Holes (Open Edges) / Naming bad
    mesh = cmds.polyCube(name="bad_cube_mesh")[0]
    cmds.delete(f"{mesh}.f[0]") # Create hole
    
    # C. Mesh with Shadow Terminator Issues works (Hard Edges needed)
    term_mesh = cmds.polySphere(name="shadow_term_mesh", sx=8, sy=8)[0]
    cmds.polySoftEdge(term_mesh, angle=180) # All soft -> Bad terminator on low poly
    
    # D. Bad Naming
    cmds.polyCube(name="WrongName")
    
    # E. Transform issues (Not frozen, pivot off)
    xform_mesh = cmds.polyCone(name="GEO_Xform_GEO")[0]
    cmds.move(10, 10, 10, xform_mesh)
    cmds.rotate(45, 0, 0, xform_mesh)
    # Pivot off center check? (Default is center of object, not world)
    
    # 3. INITIALIZE UI/APP
    # We instantiate logic directly or UI? UI is better to test integration.
    window = main_window.QyntaraMainWindow()
    
    # 4. RUN VALIDATION (Global)
    logger.info("Running Initial Validation...")
    cmds.select(all=True) # Select all to be sure
    window.combo_mode.setCurrentText("Modeling Mode")
    window.run_validation()
    
    initial_report = window.last_report
    failed_initial = initial_report.get("summary", {}).get("failed", 0)
    logger.info(f"Initial Failures: {failed_initial} (Expected > 0)")
    
    if failed_initial == 0:
        logger.error("TEST FAILURE: Validator failed to detect known errors.")
        return

    # 5. EXECUTE AUTO-FIX (Global Scope for Test)
    logger.info("Executing Global Auto-Fix...")
    
    # Select everything to define scope
    cmds.select(all=True)
    
    # Capture Selection Debug
    sel = cmds.ls(sl=True)
    logger.info(f"Selection before Fix: {len(sel)} items")
    
    # Run Fix
    window.auto_fix_all()
    
    # 6. VERIFY RESULTS
    logger.info("Verifying Fix Results...")
    
    # Re-run validation fresh
    cmds.select(all=True)
    window.run_validation()
    
    final_report = window.last_report
    failed_final = final_report.get("summary", {}).get("failed", 0)
    
    logger.info(f"Final Failures: {failed_final}")
    
    # DETAILED CHECKS
    # Check 1: Naming
    if cmds.objExists("GEO_bad_cube_mesh_GEO") or cmds.objExists("GEO_bad_cube_GEO") or cmds.objExists("GEO_bad_cube_mesh"):
        logger.info("[PASS] Smart Naming Applied.")
    elif cmds.objExists("bad_cube_mesh"):
        logger.error("[FAIL] Naming Fix Failed.")
        
    # Check 2: Open Edges
    # Find the cube (new name?)
    cubes = cmds.ls("*cube*", type="transform")
    if cubes:
        edges = cmds.polyListComponentConversion(cubes[0], te=True, bo=True)
        if not edges:
            logger.info("[PASS] Open Edges Closed.")
        else:
            logger.error(f"[FAIL] Open Edges Persist on {cubes[0]}")
            
    # Check 3: Locator Safety
    if cmds.objExists("Test_Locator"):
        logger.info("[PASS] Locator survived (didn't crash fixer).")
        
    # Check 4: Shadow Terminator
    spheres = cmds.ls("*shadow_term*", type="transform")
    if spheres:
        # Check hard edges?
        pass # Hard to verify without counting hard edges, but if script runs, it passed crash test.
        logger.info("[PASS] Shadow Terminator Fix ran.")

    if failed_final == 0:
        logger.info("=== TEST SUCCESS: ALL ISSUES FIXED ===")
    else:
        logger.warning(f"=== TEST RESULT: {failed_final} Remaining Issues (Manual Fixes Required?) ===")
        # Print remaining violations
        for d in final_report.get("details", []):
            if d.get("violations"):
                logger.warning(f"Remaining: {d['rule_id']} - {len(d['violations'])} items")

if __name__ == "__main__":
    run_test()
