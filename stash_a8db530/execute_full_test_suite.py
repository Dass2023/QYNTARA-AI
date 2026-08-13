
import maya.cmds as cmds
import logging
from qyntara_ai.core import baking, fixer, validator, geometry

# Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("QyntaraFinalTest")

def run_full_system_test():
    print("==========================================")
    print("   QYNTARA AI - FINAL SYSTEM TEST SUITE   ")
    print("==========================================")
    
    # 1. SETUP: Clean Scene
    cmds.file(new=True, force=True)
    
    # 2. INJECT ERRORS
    print("[TEST] Creating Defective Assets...")
    
    # A. N-gon + History + Missing UV2
    cube = cmds.polyCube(n='Test_NGon_Cube')[0]
    cmds.polyExtrudeFacet(f"{cube}.f[0]", ltz=1) # Adds History
    cmds.delete(f"{cube}.f[0]") # Makes it open? No, deletes face.
    # Create N-gon by deleting edge
    cmds.delete(f"{cube}.e[0]") 
    
    # B. Missing UV2 (Default is only map1)
    # Ensure only 1 set
    while len(cmds.polyUVSet(cube, q=True, allUVSets=True) or []) > 1:
         cmds.polyUVSet(cube, delete=True)

    # 3. VERIFY DETECTION
    print("[TEST] Running Validator (Expect FAIL)...")
    
    # Check 1: History
    hist_vio = geometry.check_construction_history([cube])
    if not hist_vio: print("  [FAIL] Did not detect History!")
    else: print(f"  [PASS] Detected History ({len(hist_vio)} items)")

    # Check 2: UV2
    uv2_vio = baking.check_uv2_exists([cube])
    if not uv2_vio: print("  [FAIL] Did not detect Missing UV2!")
    else: print(f"  [PASS] Detected Missing UV2 ({len(uv2_vio)} items)")
    
    # Check 3: N-gons
    ngon_vio = geometry.check_ngons([cube])
    if not ngon_vio: print("  [FAIL] Did not detect N-gons!")
    else: print(f"  [PASS] Detected N-gons ({len(ngon_vio)} items)")

    # 4. RUN AUTO-FIX
    print("[TEST] Running Auto-Fix (100% Repair)...")
    
    # Simulate UI calling Fixers directly for these known issues
    # Note: Using the FixMap from UI is complex in script, calling Fixers directly
    
    # Fix History
    fixer.QyntaraFixer.fix_history({"object": cube})
    print("  > Fixed History")
    
    # Fix N-Gons
    fixer.QyntaraFixer.fix_ngons({"object": cube})
    print("  > Fixed N-Gons")
    
    # Fix UV2 (The complex one we debugged)
    fixer.QyntaraFixer.fix_create_uv2({"object": cube})
    print("  > Fixed UV2")

    # 5. VERIFY CLEAN STATE
    print("[TEST] Re-Validating (Expect PASS)...")
    
    pass_cnt = 0
    if not geometry.check_construction_history([cube]): pass_cnt += 1
    else: print("  [FAIL] History still exists!")
    
    if not baking.check_uv2_exists([cube]): pass_cnt += 1
    else: print("  [FAIL] UV2 Missing/Empty!")
    
    if not geometry.check_ngons([cube]): pass_cnt += 1
    else: print("  [FAIL] N-gons still exist!")
    
    if pass_cnt == 3:
        print("==========================================")
        print("   RESULT: TEST PASSED (3/3 Checks)       ")
        print("   SYSTEM IS PRODUCTION READY             ")
        print("==========================================")
    else:
        print("==========================================")
        print("   RESULT: TEST FAILED                    ")
        print("==========================================")

run_full_system_test()
