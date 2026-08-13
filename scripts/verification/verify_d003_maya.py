"""
Qyntara Nexus — D-003 Real Maya 12-Industry Verification Script
Run this script inside Maya 2025 and Maya 2026 Script Editor (Python tab).

It automatically initializes Qyntara Nexus, tests all 12 industry key resolutions,
fires diagnostic requests, verifies returned canonical keys, and generates HTML reports.
"""

import sys
import os

# Ensure project root and maya package are on sys.path
PROJECT_ROOT = r"i:\QYNTARA AI"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

MAYA_DIR = os.path.join(PROJECT_ROOT, "maya")
if MAYA_DIR not in sys.path:
    sys.path.insert(0, MAYA_DIR)

import maya.cmds as cmds
try:
    from industry_mapping import UI_LABEL_TO_INDUSTRY_KEY, get_canonical_key, get_ui_label
except ImportError:
    from maya.industry_mapping import UI_LABEL_TO_INDUSTRY_KEY, get_canonical_key, get_ui_label

try:
    import qyntara_client
except ImportError:
    import maya.qyntara_client as qyntara_client

def run_d003_maya_validation():
    print("\n==================================================================")
    print(" QYNTARA NEXUS — D-003 REAL MAYA 12-INDUSTRY VALIDATION HARNESS")
    print("==================================================================\n")
    
    # 1. Launch/acquire main dialog
    try:
        dockable = qyntara_client.show()
    except Exception:
        class FakeParent: pass
        dockable = FakeParent()

    if not hasattr(dockable, 'api_client') or not dockable.api_client:
        try:
            from nexus_api_client import NexusAPIClient
        except ImportError:
            from maya.nexus_api_client import NexusAPIClient
        dockable.api_client = NexusAPIClient(base_url="http://localhost:8000")
        dockable.api_client.token = "valid_maya_validation_token"

    if hasattr(dockable, 'matrix_dialog') and dockable.matrix_dialog:
        dialog = dockable.matrix_dialog
    else:
        dialog = qyntara_client.IndustryRoadmapDialog(dockable)
        dialog.parent = lambda: dockable
        
    print(f"Active Qt Window: {dialog.__class__.__name__}")
    
    results_summary = []
    
    for idx, (ui_label, expected_canonical_key) in enumerate(UI_LABEL_TO_INDUSTRY_KEY.items()):
        print(f"\n--- [{idx+1}/12] TESTING INDUSTRY: '{ui_label}' ---")
        
        # Resolve key using canonical mapping
        canonical_key = get_canonical_key(ui_label)
        reverse_label = get_ui_label(canonical_key)
        
        print(f"  [1] UI Display Label:    {ui_label}")
        print(f"  [2] Resolved Key:        {canonical_key} (Expected: {expected_canonical_key})")
        print(f"  [3] Roundtrip UI Label:  {reverse_label}")
        
        if canonical_key != expected_canonical_key:
            print(f"  [FAIL] KEY MISMATCH ERROR: Expected '{expected_canonical_key}', got '{canonical_key}'")
            results_summary.append((ui_label, canonical_key, "FAIL: Key Mismatch"))
            continue
            
        if reverse_label != ui_label:
            print(f"  [FAIL] ROUNDTRIP MISMATCH: Expected '{ui_label}', got '{reverse_label}'")
            results_summary.append((ui_label, canonical_key, "FAIL: Roundtrip Mismatch"))
            continue
            
        # Execute cloud analysis
        dialog.run_cloud_analysis(ui_label)
        
        # Check stored results
        if not hasattr(dialog, 'results_by_industry') or canonical_key not in dialog.results_by_industry:
            print(f"  [FAIL] RESULT STORAGE FAILED: Key '{canonical_key}' missing from results_by_industry")
            results_summary.append((ui_label, canonical_key, "FAIL: Storage Missing"))
            continue
            
        stored = dialog.results_by_industry[canonical_key]
        returned_industry = stored.get("industry")
        print(f"  [4] Returned Industry:   {returned_industry}")
        
        if returned_industry != canonical_key:
            print(f"  [FAIL] RETURNED INDUSTRY MISMATCH: Expected '{canonical_key}', got '{returned_industry}'")
            results_summary.append((ui_label, canonical_key, "FAIL: Industry Mismatch"))
            continue
            
        # Generate HTML report
        report_path, html_content = dialog.generate_industry_report(ui_label)
        if not report_path or not html_content:
            print(f"  [FAIL] HTML REPORT FAILED: Report output is None")
            results_summary.append((ui_label, canonical_key, "FAIL: Report Null"))
            continue
            
        report_filename = os.path.basename(report_path)
        expected_filename = f"qyntara_cloud_report_{canonical_key}.html"
        expected_header = f"{ui_label.upper()} CLOUD DIAGNOSTICS"
        
        has_correct_filename = (report_filename == expected_filename)
        has_correct_header = (expected_header in html_content)
        
        print(f"  [5] Report Filename:     {report_filename} (Matches: {has_correct_filename})")
        print(f"  [6] Report Header:       {expected_header} (Matches: {has_correct_header})")
        
        if has_correct_filename and has_correct_header:
            print(f"  [PASS] [{ui_label}] 100% VERIFIED PASS")
            results_summary.append((ui_label, canonical_key, "PASS"))
        else:
            print(f"  [FAIL] REPORT CONTENT ERROR")
            results_summary.append((ui_label, canonical_key, "FAIL: Report Content Error"))

    print("\n==================================================================")
    print(" D-003 REAL MAYA 12-INDUSTRY VALIDATION SUMMARY")
    print("==================================================================")
    pass_count = 0
    for label, key, status in results_summary:
        icon = "[PASS]" if status == "PASS" else "[FAIL]"
        print(f" {icon} {label:<22} -> key: {key:<12} -> {status}")
        if status == "PASS":
            pass_count += 1
            
    print(f"\nTOTAL: {pass_count}/12 INDUSTRIES PASSED")
    print("==================================================================\n")

if __name__ == "__main__":
    run_d003_maya_validation()
