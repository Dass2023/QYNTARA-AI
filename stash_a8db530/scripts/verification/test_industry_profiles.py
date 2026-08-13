import os
import sys
import json

# Add project root to sys.path
# Script is in root/scripts/verification/test_industry_profiles.py
# 1 level: scripts/verification
# 2 level: scripts
# 3 level: root
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(project_root)

# Mock Maya for standalone verification
import unittest.mock
mock_maya = unittest.mock.MagicMock()
sys.modules["maya"] = mock_maya
sys.modules["maya.cmds"] = mock_maya.cmds
sys.modules["maya.api"] = mock_maya.api
sys.modules["maya.api.OpenMaya"] = mock_maya.api.OpenMaya

def test_profiles():
    from qyntara_ai.core.validator import QyntaraValidator
    
    print("="*60)
    print("QYNTARA AI - INDUSTRY PROFILE VERIFICATION SCAN")
    print("="*60)
    
    validator = QyntaraValidator()
    
    # Expected counts from Research Table (Applications of rules)
    expected_counts = {
        "game": 10,
        "vfx": 8,
        "auto": 8,
        "arch": 7,
        "med": 7,
        "aero": 8,
        "xr": 9,
        "ecomm": 6,
        "robotics": 7,
        "i40": 6,
        "i50": 6,
        "print3d": 8
    }
    
    all_passed = True
    
    print(f"{'INDUSTRY':<20} | {'EXPECTED':<10} | {'ACTUAL':<10} | {'STATUS':<10}")
    print("-" * 60)
    
    for profile_name, expected in expected_counts.items():
        validator.set_pipeline_profile(profile_name)
        
        # Count enabled rules in this profile
        profile_overrides = validator.profiles.get(profile_name, {})
        
        # In our implementation, a rule is enabled if:
        # 1. It exists in the profile overrides and enabled is not False
        # 2. It's a standard rule that isn't explicitly disabled by the profile
        # BUT the research table refers to the specific "Specialized/Key" checks + Core checks
        # For simplicity, we count how many rules this profile configures/enables specifically.
        
        enabled_count = 0
        for rule in validator.rules:
            rule_id = rule["id"]
            enabled = rule.get("enabled", True)
            
            if rule_id in profile_overrides:
                override = profile_overrides[rule_id]
                if override.get("enabled", True):
                    enabled_count += 1
            else:
                # If it's a core rule (geometry/naming etc) we might count it, 
                # but the research table focused on the specific industrial coverage.
                # In validator.py, we explicitly enabled/configured the specific rules.
                pass
        
        status = "PASS" if enabled_count >= expected else "FAIL"
        if status == "FAIL": all_passed = False
        
        print(f"{profile_name:<20} | {expected:<10} | {enabled_count:<10} | {status:<10}")

    print("-" * 60)
    
    # Check total rules in master file
    total_rules = len(validator.rules)
    print(f"Total Master Rules in Ruleset: {total_rules} (Requirement: 90)")
    
    if total_rules >= 90 and all_passed:
        print("\n[SUCCESS] All 12 industries verified with 90+ total validation coverage.")
        sys.exit(0)
    else:
        print("\n[ERROR] Verification failed. Check rule counts or master ruleset.")
        sys.exit(1)

if __name__ == "__main__":
    test_profiles()
