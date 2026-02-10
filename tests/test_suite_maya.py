import maya.cmds as cmds
import sys
import os
import importlib

# --- SETUP ---
PROJECT_ROOT = r"e:/QYNTARA AI" 
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import qyntara_ai.core.validator as validator_module
import qyntara_ai.core.geometry as geometry
import qyntara_ai.ui.main_window as main_window
importlib.reload(validator_module)
importlib.reload(geometry)
importlib.reload(main_window)

def setup_test_scene():
    print("--- 1. Setting Up Test Scene ---")
    cmds.file(new=True, force=True)
    
    # Object 1: Bad Geometry (N-Gon)
    # Create a plane and remove an edge to ensure an N-Gon
    cube = cmds.polyCube(name="Test_NGon_Mesh")[0]
    cmds.polySplit(cube, ip=[(2, 0.5), (3, 0.5)]) # Split face to create potential cleanup target
    cmds.delete(cube + ".e[4]") # Simple delete to maybe create n-gon or just bad topo
    # Better N-Gon: Create plane, merge faces?
    cmds.delete("Test_NGon_Mesh")
    
    # Create a plane 2x2
    p = cmds.polyPlane(name="Test_NGon", w=10, h=10, sx=2, sy=1)[0]
    # Delete the edge in the middle -> 1 face with 6 vertices? No, just 1 quad.
    # To make N-gon: 
    # Create pentagon
    cmds.polyCylinder(name="Test_NGon_Cyl", sx=5, sy=1, sz=1)
    cmds.delete("Test_NGon_Cyl.f[0:4]") # caps
    cmds.delete("Test_NGon_Cyl.f[1]")   # Create a hole?
    # Actually, simplest N-Gon:
    # 1. Create Plane
    p = cmds.polyPlane(name="Bad_NGon", sx=1, sy=1)[0]
    # 2. Cut a vertex on one edge
    cmds.polySplit(p, ip=[(0, 0.5), (2, 0.5)]) 
    # This creates triangles. 
    # Let's just create a poly with 5 verts manually
    cmds.delete(p)
    
    # Reliable N-gon
    cmds.polyPlane(name="Bad_NGon", sx=2, sy=2)
    cmds.delete("Bad_NGon.e[4]") # Delete internal edge, merging two quads into one 6-vert face
    
    # Object 2: Unfrozen Transforms
    t = cmds.polyCube(name="Bad_Transform")[0]
    cmds.setAttr(f"{t}.tx", 10)
    cmds.setAttr(f"{t}.ry", 45)
    
    # Object 3: History
    h = cmds.polySphere(name="Bad_History")[0]
    cmds.polyExtrudeFacet(f"{h}.f[0]", ltz=1) 
    
    cmds.select(clear=True)
    print("Scene Setup Complete.")
    return ["Bad_NGon", "Bad_Transform", "Bad_History"]

def run_tests():
    print("\n========================================")
    print("   QYNTARA AI VALIDATOR - E2E TEST")
    print("========================================")
    
    objects = setup_test_scene()
    
    # --- STEP 1: INITIAL VALIDATION ---
    print("\n[TEST 1] Running Validation on Faulty Objects...")
    val = validator_module.QyntaraValidator()
    # Force Game Profile (Strict)
    val.set_pipeline_profile("game") 
    
    report = val.run_validation(objects)
    
    # Analyze Report
    errors_found = {}
    for item in report:
        if item['severity'] == 'error':
            errors_found[item['rule_id']] = True
            print(f"  -> Found Expected Error: {item['rule_name']}")

    # Assertions
    if "geo_ngons" in errors_found:
        print("  [PASS] N-Gons Detected")
    else:
        print("  [FAIL] N-Gons NOT Detected")
        
    if "xform_frozen" in errors_found:
        print("  [PASS] Unfrozen Transforms Detected")
    else:
        print("  [FAIL] Unfrozen Transforms NOT Detected")
        
    if "geo_history" in errors_found:
        print("  [PASS] Construction History Detected")
    else:
        print("  [FAIL] Construction History NOT Detected")

    # --- STEP 2: AUTO-FIX ---
    print("\n[TEST 2] Running Auto-Fix...")
    
    # We need to simulate the Main Window's auto-fix logic
    # Or instantiate the Main Window headless?
    # Let's instantiate the window properly
    try:
        win = main_window.QyntaraMainWindow()
        # Mock the report in the window so it knows what to fix
        win.last_report = report
        win.validator = val
        
        # Run Auto Fix
        win.auto_fix()
        print("  Auto-Fix executed.")
        
    except Exception as e:
        print(f"  [FAIL] Auto-Fix Crashing: {e}")
        import traceback
        traceback.print_exc()

    # --- STEP 3: VERIFY FIXES ---
    print("\n[TEST 3] Verifying Fixes...")
    
    # Re-run validation
    new_report = val.run_validation(objects)
    remaining_errors = [r['rule_id'] for r in new_report if r['severity'] == 'error']
    
    if "geo_history" not in remaining_errors and not cmds.listHistory("Bad_History", pdo=True):
        print("  [PASS] History Deleted")
    else:
        print(f"  [FAIL] History still present or detected: {remaining_errors}")

    if "xform_frozen" not in remaining_errors:
        tx = cmds.getAttr("Bad_Transform.tx")
        if abs(tx) < 0.001:
             print("  [PASS] Transforms Frozen")
        else:
             print(f"  [FAIL] Transforms checked out but values not zero? Tx={tx}")
    else:
        print("  [FAIL] Unfrozen Transforms still detected")

    print("\n[TEST 4] UI Launch Check...")
    win.show()
    print("  [PASS] UI Launched without crash.")

    print("\n========================================")
    print("   TEST SUITE COMPLETE")
    print("========================================")

if __name__ == "__main__":
    run_tests()
