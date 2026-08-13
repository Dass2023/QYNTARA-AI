# QYNTARA NEXUS — D-008 THROUGH D-014 TEST STRATEGY & SPECIFICATION

**Feature:** Test Strategy for Gate 8 P2/P3 Polish Remediation  
**Status:** 🔍 **READ-ONLY SPECIFICATION COMPLETE**

---

## FUTURE TEST SPECIFICATIONS FOR GATE 8 REMEDIATION

| Defect ID | Test Target | Proposed Test Name | Test Type | Expected Assertion |
|-----------|-------------|--------------------|-----------|--------------------|
| **D-008** | Comment/Docstring accuracy | `test_docstrings_no_legacy_mock_references` | Static Inspection | Docstrings contain no references to Phase 0 mocks |
| **D-009** | Reset Results Button | `test_matrix_dialog_reset_results_clears_state` | Unit Test | `results_by_industry` cleared, `btn_report` hidden |
| **D-010** | Checkbox Tooltips | `test_roadmap_checkbox_tooltips_assigned` | Unit Test | `chk.toolTip() == text` for all checkboxes |
| **D-011** | Professional Terminology | `test_ui_label_terminology_standardized` | Unit Test | Check dictionary keys match enterprise terminology |
| **D-012** | HTML Header Formatting | `test_html_report_header_uses_canonical_display_label` | Unit Test | Subtitle uses `get_ui_label(key).upper()` |
| **D-013** | Standalone Demo Labeling | `test_demo_tab_contains_simulated_feed_label` | Unit Test | IoT tab header contains "SIMULATED SENSOR FEED" |
| **D-014** | Window Re-entrancy | `test_open_matrix_dialog_prevents_duplicate_windows` | Unit Test | Calling `open_matrix_dialog()` twice focuses single dialog instance |

---

> **MANDATORY STOP:** Test strategy specified. Zero tests implemented or modified yet. Implementation is NOT authorized.
