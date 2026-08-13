import sys
import os
import json
from unittest.mock import MagicMock

# Add Qyntara to path
sys.path.insert(0, r"i:\QYNTARA AI")

# Mock Maya environment
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()

# Setup dummy values for cmds calls to avoid iterating None
sys.modules["maya.cmds"].ls.return_value = ["test_obj"]
sys.modules["maya.cmds"].listRelatives.return_value = ["test_shape"]
sys.modules["maya.cmds"].listConnections.return_value = []
sys.modules["maya.cmds"].objExists.return_value = True
sys.modules["maya.cmds"].nodeType.return_value = "transform"

try:
    from qyntara_ai.core.validator import QyntaraValidator
    print("Successfully imported QyntaraValidator")
except ImportError as e:
    print(f"Failed to import QyntaraValidator: {e}")
    sys.exit(1)

def test_execution():
    print("\n" + "="*50)
    print("STARTING VALIDATION EXECUTION TEST")
    print("="*50)

    # Load Validator
    rules_path = r"i:\QYNTARA AI\qyntara_ai\rules\qyntara_ruleset.json"
    validator = QyntaraValidator(rules_path=rules_path)
    
    total_rules = len(validator.rules)
    print(f"Loaded {total_rules} rules from ruleset.")
    
    passed_exec = 0
    failed_exec = 0
    
    test_objects = ["test_cube_1", "test_sphere_1"]
    
    for rule in validator.rules:
        rule_id = rule["id"]
        func_name = rule.get("function")
        
        # Check if function maps
        func = validator.registry.get(func_name)
        if not func:
            print(f"[ERROR] Registry Missing: {rule_id} -> {func_name}")
            failed_exec += 1
            continue
            
        # Try Execution
        try:
            # We call the function directly to test it isolated
            # Most functions expect a list of objects
            # Some functions might crash if mocks aren't perfect, but we catch generic Exceptions
            
            # Simple check: Does it run without unhandled exception?
            # We don't care about the return value (violations list) being correct logic wise
            # We care that calling it doesn't raise NameError, AttributeError (missing imports), etc.
            
            # Handle params if needed? validator.run_validation handles logic, 
            # let's try calling run_validation for a single rule!
            
            # But run_validation runs ALL rules enabled in profile. Use disabled_rules list?
            # Better: Call function directly.
            
            # Param handling logic from validator.py:
            params = rule.get("parameters", {})
            safe_params = {k: v for k, v in params.items() if k != 'objects'}
            
            func(test_objects, **safe_params)
            
            # print(f"[OK] {rule_id}")
            passed_exec += 1
            
        except Exception as e:
            print(f"[CRASH] Rule: {rule_id} ({func_name})")
            print(f"    Error: {e}")
            failed_exec += 1

    print("\n" + "="*50)
    print(f"EXECUTION SUMMARY")
    print(f"Tested: {total_rules}")
    print(f"Passed Execution: {passed_exec}")
    print(f"Failed/Crashed: {failed_exec}")
    print("="*50)
    
    if failed_exec == 0:
        print("SUCCESS: All rules are executable.")
    else:
        print("FAILURE: Some rules crashed.")

if __name__ == "__main__":
    test_execution()
