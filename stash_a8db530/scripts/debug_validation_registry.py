import json
import os
import sys

# Add project root to path
sys.path.insert(0, r"i:\QYNTARA AI")

# Mock Maya environment
from unittest.mock import MagicMock
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()

try:
    from qyntara_ai.core.validator import QyntaraValidator
    print("Successfully imported QyntaraValidator")
except ImportError as e:
    print(f"Failed to import QyntaraValidator: {e}")
    sys.exit(1)

def check_registry():
    # Load Ruleset
    rules_path = r"i:\QYNTARA AI\qyntara_ai\rules\qyntara_ruleset.json"
    if not os.path.exists(rules_path):
        print(f"Ruleset not found at {rules_path}")
        return

    with open(rules_path, 'r') as f:
        rules = json.load(f)

    required_functions = set()
    for rule in rules:
        if "function" in rule:
            required_functions.add(rule["function"])

    print(f"\nTotal Unique Functions Required by Ruleset: {len(required_functions)}")

    # Instantiate Validator to check registry
    validator = QyntaraValidator(rules_path=rules_path)
    registered_functions = set(validator.registry.keys())

    print(f"Total Functions Registered in Validator: {len(registered_functions)}")

    # Find Missing
    missing = required_functions - registered_functions
    
    print("\n" + "="*50)
    print("MISSING FUNCTIONS (Ruleset requires them, Validator lacks them)")
    print("="*50)
    
    if missing:
        for func in sorted(missing):
            print(f"[MISSING] {func}")
            # Find which rules use this
            using_rules = [r["id"] for r in rules if r.get("function") == func]
            print(f"    Used by: {', '.join(using_rules)}")
    else:
        print("NONE - All required functions are registered!")

    print("\n" + "="*50)

if __name__ == "__main__":
    check_registry()
