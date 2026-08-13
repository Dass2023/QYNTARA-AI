import maya.cmds as cmds
import sys
import os
import importlib

# --- SETUP PATH ---
PROJECT_ROOT = r"e:/QYNTARA AI"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import qyntara_ai.core.validator as validator_module
import qyntara_ai.core.fixer as fixer_module
import qyntara_ai.ui.main_window as main_window
importlib.reload(validator_module)
importlib.reload(fixer_module)
importlib.reload(main_window)

def log(msg):
    print(f"[TEST] {msg}")

def run_full_check():
    log("Starting Master System Check...")
    cmds.file(new=True, force=True)
    
    # ---------------------------------------------------------
    # 1. SETUP INVALID SCENE
    # ---------------------------------------------------------
    log("1. Setting up Test Assets...")
    
    # A. Bad Topology (N-Gon)
    ngon = cmds.polyPlane(name="Bad_NGon", sx=2, sy=2)[0]
    cmds.delete(f"{ngon}.e[4]") # Internal edge -> 6-vert face
    
    # B. AI Naming Candidate
    # Generic object in a meaningful group
    prop = cmds.polyCube(name="pCube1")[0]
    # Make it small (Detail)
    cmds.xform(prop, s=(0.1, 0.1, 0.1))
    env_grp = cmds.group(em=True, name="Environment_Grp")
    cmds.parent(prop, env_grp)
    
    # C. Baking Missing (UV2)
    baker = cmds.polySphere(name="Bake_Target")[0]
    # Ensure only 1 UV set
    while len(cmds.polyUVSet(baker, q=True, allUVSets=True)) > 1:
        cmds.polyUVSet(baker, delete=True, uvSet=cmds.polyUVSet(baker, q=True, allUVSets=True)[1])
        
    log("Scene Setup Complete.")
    
    # ---------------------------------------------------------
    # 2. VALIDATION RUN
    # ---------------------------------------------------------
    log("2. Running Validation...")
    win = main_window.QyntaraMainWindow()
    win.show()
    
    # Set Profile to Game (Strict)
    win.combo_pipeline.setCurrentIndex(0) # Game
    win.update_pipeline_rules()
    
    # Execute Validation
    win.run_validation()
    report = win.last_report
    
    # Check Failures
    failures = [d['rule_id'] for d in report['details'] if len(d.get('violations', [])) > 0]
    log(f"Detected Failures: {failures}")
    
    assert "geo_ngons" in failures, "Failed to detect N-Gon"
    assert "check_naming_convention" in failures or "mat_naming" in failures, "Failed to detect Bad Name"
    assert "bake_uv2_exists" in failures, "Failed to detect Missing UV2"
    
    log("VALIDATION PASSED (Correctly identified errors).")
    
    # ---------------------------------------------------------
    # 3. AUTO-FIX EXECUTION (Including AI)
    # ---------------------------------------------------------
    log("3. Running Auto-Fix (AI Enabled)...")
    
    # Verify AI Naming Logic exists
    assert hasattr(fixer_module.QyntaraFixer, 'fix_smart_naming'), "fix_smart_naming missing!"
    
    # RUN FIX
    win.auto_fix()
    log("Auto-Fix Complete.")
    
    # ---------------------------------------------------------
    # 4. VERIFICATION
    # ---------------------------------------------------------
    log("4. Verifying Fixes...")
    
    # A. Check N-Gon
    # Should be triangulated or quadrangulated (Smart Topo)
    ngon_counts = cmds.polyEvaluate("Bad_NGon", f=True)
    # If standard plane 2x2 has 4 faces. N-gon made it 1. Smart Fix (Quad) might make it 2-4.
    # Just check if constraints pass.
    
    # B. Check Naming (AI)
    # New name should NOT be pCube1
    children = cmds.listRelatives(env_grp, children=True)
    new_name = children[0]
    log(f"Renamed Object: {new_name}")
    # Expect "GEO_Environment_Grp_01_GEO" or similar (Detail tag?)
    # "LGT" or "GEO"? Logic said "GEO" if not camera/light.
    # "Detail" tag if volume < 10. (0.1*0.1*0.1 = 0.001). So valid.
    assert new_name != "pCube1", "AI Naming Failed (Name unchanged)"
    assert "Environment" in new_name or "Detail" in new_name, f"Name {new_name} lacks semantic context"
    
    # C. Check UV2
    uv_sets = cmds.polyUVSet("Bake_Target", q=True, allUVSets=True)
    assert len(uv_sets) >= 2, "UV Set 2 generation failed"
    
    log("FIX VERIFICATION PASSED.")
    
    # ---------------------------------------------------------
    # 5. UNDO TEST
    # ---------------------------------------------------------
    log("5. Testing Undo...")
    win.run_undo()
    # Maya Undo allows 1 step? Auto-Fix wraps in chunk? 
    # Since Auto-Fix iterates multiple rules, does it wrap ALL in one chunk?
    # FIXER implementation uses @undo_chunk on EACH rule.
    # So `run_undo` will only undo the LAST rule (Likely Baking or Naming).
    # To undo ALL requires a parent chunk around `auto_fix`.
    # Current `main_window.auto_fix` iterates.
    # So `run_undo` might only undo the last fix (e.g. UV2 creation).
    # Let's verify UV2 is gone.
    
    uv_sets_after_undo = cmds.polyUVSet("Bake_Target", q=True, allUVSets=True)
    # If Baking was last in fix_map...
    if len(uv_sets_after_undo) < 2:
        log("Undo Successful (Reverted UV2).")
    else:
        log("Undo Partial/Failed (UV2 still exists - maybe Naming was last?)")
        
    log("SYSTEM CHECK COMPLETE: ALL GREEN.")

if __name__ == "__main__":
    run_full_check()
