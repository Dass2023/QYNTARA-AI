
import maya.cmds as cmds
import logging
from qyntara_ai.core import baking, fixer

# Setup Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QyntaraDebug")

def reproduce_bug():
    print("--- STARTING REPRO ---")
    
    # 1. Setup Scene
    cmds.file(new=True, force=True)
    cube = cmds.polyCube(n='DebugCube')[0]
    cmds.select(cube)
    
    # Verify Initial State
    sets_init = cmds.polyUVSet(cube, q=True, allUVSets=True)
    print(f"Initial Sets: {sets_init}")
    assert len(sets_init) == 1, "Should start with 1 set"

    # 2. Run Validation (Directly)
    print("--- Running Check (Expect Fail) ---")
    violations = baking.check_uv2_exists([cube])
    print(f"Violations: {violations}")
    
    if not violations:
        print("ERROR: Validator passed on a single-UV object! (Logic Flaw)")
        return

    # 3. Run Fix (Directly)
    print("--- Running Fix ---")
    # Simulate Report Entry format
    report_entry = {"object": cube} 
    fixer.QyntaraFixer.fix_create_uv2(report_entry)
    
    # 4. Verify Fix
    sets_after = cmds.polyUVSet(cube, q=True, allUVSets=True)
    print(f"Sets After Fix: {sets_after}")
    
    # 5. Run Validation Again
    print("--- Running Check Again (Expect Pass) ---")
    violations_after = baking.check_uv2_exists([cube])
    print(f"Violations After: {violations_after}")
    
    if violations_after:
        print("ERROR: Fixer ran but Validator still fails!")
    elif len(sets_after) < 2:
        print("CRITICAL ERROR: Validator passed ('False Negative') but Object ONLY HAS 1 SET!")
    else:
        print("SUCCESS in Script: Fix worked and verified.")

reproduce_bug()
