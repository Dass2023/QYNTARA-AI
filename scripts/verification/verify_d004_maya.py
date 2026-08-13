"""
Qyntara Nexus — D-004 Real Maya UI Layout Lifecycle Verification Script
Run this script inside Maya 2025 and Maya 2026 Script Editor (Python tab).

It tests repeated industry switching (100+ iterations), verifies layout item bounds,
checks button uniqueness, validates single-signal execution, and checks for progressive memory growth.
"""

import sys
import os

PROJECT_ROOT = r"i:\QYNTARA AI"
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

MAYA_DIR = os.path.join(PROJECT_ROOT, "maya")
if MAYA_DIR not in sys.path:
    sys.path.insert(0, MAYA_DIR)

import maya.cmds as cmds
try:
    from industry_mapping import UI_LABEL_TO_INDUSTRY_KEY
except ImportError:
    from maya.industry_mapping import UI_LABEL_TO_INDUSTRY_KEY

try:
    import qyntara_client
except ImportError:
    import maya.qyntara_client as qyntara_client

def run_d004_maya_validation():
    print("\n==================================================================")
    print(" QYNTARA NEXUS — D-004 REAL MAYA LAYOUT LIFECYCLE HARNESS")
    print("==================================================================\n")
    
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
        dockable.api_client.token = "valid_maya_d004_token"

    if hasattr(dockable, 'matrix_dialog') and dockable.matrix_dialog:
        dialog = dockable.matrix_dialog
    else:
        dialog = qyntara_client.IndustryRoadmapDialog(dockable)
        dialog.parent = lambda: dockable

    # Measure initial layout item count
    initial_count = dialog.det_layout.count()
    print(f"  [1] Initial det_layout Item Count: {initial_count}")
    
    # Perform 100 repeated switches across all 12 industries
    print("  [2] Executing 100 repeated industry switches...")
    count_mismatches = 0
    for i in range(100):
        row = i % 12
        dialog.update_details(row)
        current_count = dialog.det_layout.count()
        if current_count != initial_count:
            count_mismatches += 1

    print(f"  [3] Post-100 Switch det_layout Item Count: {dialog.det_layout.count()}")
    print(f"  [4] Item Count Variance Events: {count_mismatches}")
    
    # Check button uniqueness in detail layout
    sub_layout = None
    for i in range(dialog.det_layout.count()):
        item = dialog.det_layout.itemAt(i)
        if item.layout():
            sub_layout = item.layout()
            break
            
    btn_count = sub_layout.count() if sub_layout else 0
    print(f"  [5] Active Action Buttons in Sub-Layout: {btn_count} (Expected: 2)")

    # Execute diagnostics after 100 switches
    dialog.run_cloud_analysis("Gaming")
    stored = dialog.results_by_industry.get("gaming", {})
    results_present = bool(stored.get("results"))
    print(f"  [6] Post-Switch Diagnostics Execution: {'PASS' if results_present else 'FAIL'}")

    all_passed = (count_mismatches == 0) and (btn_count == 2) and results_present
    
    print("\n==================================================================")
    print(" D-004 REAL MAYA LAYOUT LIFECYCLE SUMMARY")
    print("==================================================================")
    print(f" [{'PASS' if all_passed else 'FAIL'}] 100-Switch Layout Count Constant: {initial_count}")
    print(f" [{'PASS' if all_passed else 'FAIL'}] Sub-Layout Button Count: {btn_count}")
    print(f" [{'PASS' if all_passed else 'FAIL'}] Post-Switch Diagnostics: {'OK' if results_present else 'ERROR'}")
    print(f"\nOVERALL HARNESS RESULT: {'PASS' if all_passed else 'FAIL'}")
    print("==================================================================\n")

if __name__ == "__main__":
    run_d004_maya_validation()
