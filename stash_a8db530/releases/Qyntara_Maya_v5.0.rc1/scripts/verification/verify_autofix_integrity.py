import json
import os
import re

RULES_PATH = r"e:\QYNTARA AI\qyntara_ai\rules\qyntara_ruleset.json"
MAIN_WINDOW_PATH = r"e:\QYNTARA AI\qyntara_ai\ui\main_window.py"
FIXER_PATH = r"e:\QYNTARA AI\qyntara_ai\core\fixer.py"

def verify():
    print("--- Verifying Qyntara Auto-Fix System ---\n")
    
    # 1. Load Rules
    if not os.path.exists(RULES_PATH):
        print(f"ERROR: Ruleset not found at {RULES_PATH}")
        return
        
    with open(RULES_PATH, 'r') as f:
        rules = json.load(f)
        
    print(f"Loaded {len(rules)} rules.")
    
    # 2. Extract Fix Map from UI
    fix_map = {}
    with open(MAIN_WINDOW_PATH, 'r') as f:
        content = f.read()
        # Regex to find "rule_id": fixer.QyntaraFixer.method_name
        # OR "rule_id": fixer.QyntaraFixer.method_name,
        # OR "rule_id": QyntaraFixer.method_name
        
        matches = re.findall(r'"([a-zA-Z0-9_]+)":\s*(?:fixer\.)?QyntaraFixer\.([a-zA-Z0-9_]+)', content)
        for rule_id, method in matches:
            fix_map[rule_id] = method
            
    # 3. Extract Methods from Fixer
    fixer_methods = set()
    with open(FIXER_PATH, 'r') as f:
        content = f.read()
        methods = re.findall(r'def\s+([a-zA-Z0-9_]+)\(', content)
        fixer_methods.update(methods)
        
    # 4. Compare
    print(f"\n{'RULE ID':<30} | {'MAPPED FIXER':<35} | {'STATUS':<15}")
    print("-" * 85)
    
    missing_map_count = 0
    missing_method_count = 0
    
    for rule in rules:
        rid = rule['id']
        label = rule['label']
        enabled = rule.get('enabled', True)
        
        if not enabled:
            continue
            
        mapped_func = fix_map.get(rid)
        
        status = "OK"
        if not mapped_func:
            status = "NO MAPPING"
            missing_map_count += 1
        elif mapped_func not in fixer_methods:
            status = f"MISSING FUNC ({mapped_func})"
            missing_method_count += 1
            
        print(f"{rid:<30} | {str(mapped_func):<35} | {status:<15}")
        
    print("-" * 85)
    print(f"\nVerification Complete.")
    print(f"Rules with NO Mapping: {missing_map_count}")
    print(f"Rules with Broken Mapping: {missing_method_count}")
    
    if missing_map_count == 0 and missing_method_count == 0:
        print("\nAll Systems Nominal. Auto-Fix Integrity Verified.")
    else:
        print("\nACTION REQUIRED: Fix missing mappings or functions.")

if __name__ == "__main__":
    verify()
