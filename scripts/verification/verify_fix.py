import sys
import os
import json
from unittest.mock import MagicMock

# Mock Maya environment
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()

# Append path to allow imports
sys.path.append(r'e:\QYNTARA AI')

try:
    from qyntara_ai.core.validator import QyntaraValidator
    
    # Initialize validator
    rules_path = r'e:\QYNTARA AI\qyntara_ai\rules\qyntara_ruleset.json'
    validator = QyntaraValidator(rules_path=rules_path)
    
    # Find the rule
    rule_id = "geo_missing_bevels"
    rule = next((r for r in validator.rules if r['id'] == rule_id), None)
    
    if rule:
        print(f"Rule '{rule_id}' found.")
        print(f"Enabled Status: {rule.get('enabled')}")
        
        if rule.get('enabled') is True:
            print("SUCCESS: Rule is currently ENABLED.")
        else:
            print("FAILURE: Rule is currently DISABLED.")
    else:
        print(f"FAILURE: Rule '{rule_id}' not found in ruleset.")

except Exception as e:
    print(f"An error occurred during verification: {e}")
