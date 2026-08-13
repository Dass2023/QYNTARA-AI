"""
Script to run verification/debugging tests INSIDE Maya.
Run this in the Maya Script Editor.
"""
import sys
import os
import traceback

# 1. SETUP ENVIRONMENT
project_root = r"e:\QYNTARA AI"
# Add vendor path explicitly to ensure dependencies
vendor_path = os.path.join(project_root, "qyntara_ai", "vendor")

if project_root not in sys.path:
    print(f"Adding {project_root} to sys.path")
    sys.path.insert(0, project_root)
if vendor_path not in sys.path:
    print(f"Adding {vendor_path} to sys.path")
    sys.path.insert(0, vendor_path)

# 2. IMPORT MODULES (Reload for dev iteration)
try:
    import maya.cmds as cmds
    import qyntara_ai.core.validator
    import qyntara_ai.core.fixer
    from importlib import reload
    
    reload(qyntara_ai.core.validator)
    reload(qyntara_ai.core.fixer)
    
    from qyntara_ai.core.validator import QyntaraValidator
    from qyntara_ai.core.fixer import QyntaraFixer
    print("Modules imported and reloaded.")
except ImportError as e:
    print(f"Error importing Qyntara modules: {e}")
    sys.exit(1)

def run_debug_tests():
    print("\n" + "="*50)
    print("STARTING QYNTARA DEBUG SESSION (IN-MAYA)")
    print("="*50)
    
    # 3. SETUP TEST SCENE
    print(">> Setting up Test Scene...")
    cmds.file(new=True, force=True)
    
    # Create valid cube
    cube = cmds.polyCube(n="ValidCube")[0]
    
    # Create invalid element (History + Scale issues)
    bad_cube = cmds.polyCube(n="BadCube")[0]
    cmds.polyExtrudeFacet(bad_cube + ".f[0]", ltz=1) # Adds history
    cmds.setAttr(bad_cube + ".scaleX", 2.0) # Non-uniform scale
    
    # Create proximity issue
    box1 = cmds.polyCube(n="GapBox1")[0]
    box2 = cmds.polyCube(n="GapBox2")[0]
    cmds.move(1.05, 0, 0, box2) # 0.05 gap
    
    print("   Created: ValidCube, BadCube (History, Scale), GapBox1/2 (Proximity)")
    
    # 4. RUN VALIDATOR
    print("\n>> Running Validator...")
    validator = QyntaraValidator()
    # We select specific objects to avoid validating unrelated default nodes
    selection = ["ValidCube", "BadCube", "GapBox1", "GapBox2"]
    
    try:
        report = validator.run_validation(selection)
        
        # 5. ANALYZE RESULTS
        failed_count = report.get('summary', {}).get('failed', 0)
        print(f"\n>> Validation Complete. Failed Rules: {failed_count}")
        
        for detail in report.get('details', []):
            print(f"   [FAIL] {detail['rule_label']} ({len(detail['violations'])} items)")
            
        # 6. TEST AUTO-FIX
        print("\n>> Testing Auto-Fix (History)...")
        # Find history failure
        hist_fail = next((d for d in report['details'] if d['rule_id'] == 'geo_history'), None)
        
        if hist_fail:
            print("   Fixing history on BadCube...")
            QyntaraFixer.fix_history(hist_fail)
            
            # Verify
            hist = cmds.listHistory("BadCube", pro=True)
            if not hist: 
                print("   Fix executed. Run validator again to verify.")
            else:
                print("   Fix executed.")
        else:
            print("   No history failure found (Unexpected).")

    except Exception as e:
        print(f"CRITICAL ERROR during validation: {e}")
        traceback.print_exc()

    print("\n" + "="*50)
    print("DEBUG SESSION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    run_debug_tests()
