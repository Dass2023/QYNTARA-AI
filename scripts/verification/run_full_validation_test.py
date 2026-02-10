import maya.cmds as cmds
import sys
import os
import importlib

# --- SETUP ---
project_root = r"e:/QYNTARA AI" 
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import qyntara_ai.core.validator as validator_module
import qyntara_ai.core.geometry as geometry
import qyntara_ai.ui.main_window as main_window
import qyntara_ai.core.fixer as fixer

# Explicit Reload sequence
importlib.reload(geometry)
importlib.reload(fixer)
importlib.reload(validator_module)
importlib.reload(main_window)

def setup_scene_comprehensive():
    """Creates a scene with EVERY supported error type."""
    print("--- Setting Up Comprehensive Test Scene ---")
    cmds.file(new=True, force=True)
    
    # 1. Open Edges (Border)
    # Cylinder with deleted cap
    p1 = cmds.polyCylinder(name="ERR_OpenEdges", sx=8, sy=1, sz=1)[0]
    cmds.delete(f"{p1}.f[8:15]") # Delete top cap
    cmds.move(0, 0, 0, p1)

    # 2. Non-Manifold
    # Extrude edge of a CUBE to create internal face/non-manifold edge
    p2 = cmds.polyCube(name="ERR_NonManifold", w=1, h=1, d=1)[0]
    cmds.polyExtrudeEdge(f"{p2}.e[1]", ltz=1) 
    
    # 3. Lamina Faces
    # Duplicate face on top of itself
    p3 = cmds.polyCube(name="ERR_Lamina", sx=1, sy=1, sz=1)[0]
    # To create lamina on cube: duplicate face and keep?
    # Actually just create a separate face and combine/merge?
    # Simple setup:
    extra = cmds.polyPlane(sx=1, sy=1)[0]
    cmds.move(0,0,0.5, extra) # Front face of cube
    p3 = cmds.polyUnite(p3, extra, ch=False, name="ERR_Lamina")[0]
    cmds.polyMergeVertex(p3, d=0.1) # Merge them to create shared edges but overlapping faces
    cmds.move(5, 0, 0, p3)
    
    # 4. Zero Area Face
    # Create triangle, move 3rd vert to be on line of 1-2
    p4 = cmds.polyPlane(name="ERR_ZeroArea", sx=1, sy=1)[0]
    cmds.move(0,0,0, f"{p4}.vtx[1]", ws=True)
    cmds.move(0,0,0, f"{p4}.vtx[3]", ws=True) # collapse a face?
    # safer: merge verts 1 and 3
    cmds.polyMergeVertex([f"{p4}.vtx[1]", f"{p4}.vtx[3]"], d=1.0)
    cmds.move(10, 0, 0, p4)

    # 5. Lock Normals
    p5 = cmds.polyCube(name="ERR_LockedNormals")[0]
    cmds.polyNormalPerVertex(p5, freezeNormal=True)
    cmds.move(15, 0, 0, p5)

    # 6. Unfrozen Transform & Scale
    p6 = cmds.polyCube(name="ERR_Transform")[0]
    cmds.setAttr(f"{p6}.tx", 10.512) # Not on grid
    cmds.setAttr(f"{p6}.ry", 45)
    cmds.setAttr(f"{p6}.sz", 2.0)
    cmds.move(20, 0, 0, p6)

    # 7. No Materials / Default Material
    p7 = cmds.polyCube(name="ERR_Material")[0]
    # Defaults to lambert1, so it should flag "mat_default"
    cmds.move(25, 0, 0, p7)

    cmds.select(clear=True)
    return [p1, p2, p3, p4, p5, p6, p7]

def run_tests():
    print("\n========================================")
    print("   QYNTARA AI - COMPREHENSIVE E2E TEST")
    print("========================================")
    
    objects = setup_scene_comprehensive()
    
    # --- 1. VALIDATION ---
    print("\n[STEP 1] Validating...")
    win = main_window.QyntaraMainWindow()
    win.show() # Must show to init UI logic
    
    # Mock Selection
    cmds.select(objects)
    
    # Run Validation
    win.run_validation()
    
    report = win.last_report
    if not report: 
        print("[FAIL] No Report Generated!")
        return
        
    print(f"Initial Issues: {report['summary']['failed']} Categories Failed.")
    # Detailed check
    issues = [d['rule_id'] for d in report['details']]
    print(f"Issues Detected: {issues}")
    
    expected = ["geo_open_edges", "geo_zero_area", "xform_frozen", "mat_default"]
    missing = [e for e in expected if e not in issues]
    if missing:
        print(f"[WARN] Some expected errors were NOT detected: {missing}")
    
    # --- 2. AUTO-FIX ---
    print("\n[STEP 2] Running Auto-Fix...")
    if win.btn_fix.isEnabled():
        win.auto_fix_all()
    else:
        print("[FAIL] Auto-Fix button disabled?")
        
    # --- 3. RE-VALIDATION ---
    print("\n[STEP 3] Re-Validating...")
    win.run_validation()
    new_report = win.last_report
    
    fail_count = new_report['summary']['failed']
    print(f"Remaining Issues: {fail_count}")
    
    if fail_count == 0:
        print("\n[SUCCESS] All issues resolved automatically!")
    else:
        print("\n[PARTIAL] Some issues remain:")
        for d in new_report['details']:
            print(f"  - {d['rule_label']}: {len(d['violations'])} items")

if __name__ == "__main__":
    run_tests()
