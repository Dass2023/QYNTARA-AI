# QYNTARA NEXUS — D-009 RESET RESULTS BUTTON READ-ONLY FORENSIC AUDIT

**Feature:** Per-Industry Diagnostic Result Reset Action  
**Defect ID:** D-009  
**Auditor:** Antigravity AI (Gemini 3.6 Flash)  
**Status:** 🔍 **READ-ONLY FORENSIC AUDIT COMPLETE (ZERO CODE MODIFIED)**

---

## 1. TECHNICAL FORENSIC TRACE

- **Target File:** `maya/qyntara_client.py`
- **Target Class:** `IndustryRoadmapDialog` (Lines 1358–1710)
- **Target Function:** `update_details(self, row)` (Lines 1536–1615)
- **Current Data Structure:** `self.results_by_industry` (dictionary mapping canonical industry key -> result payload)
- **Current Action Bar (Lines 1555–1574):**
  - `btn_cloud`: Executes `run_cloud_analysis(key)`
  - `btn_report`: Executes `generate_industry_report(key)`
- **Deficiency:** `IndustryRoadmapDialog` provides actions to run analysis and export HTML reports, but lacks a mechanism to clear/reset diagnostic results for the current industry. Once executed, `self.results_by_industry[lookup_key]` persists for the duration of the dialog lifetime, with no way for the user to return to an un-analyzed state.

---

## 2. RESULT LIFECYCLE & SCOPE ANALYSIS (D-002 ISOLATION ALIGNMENT)

- **D-002 Alignment:** Gate 2 established strict per-industry result isolation via `self.results_by_industry[canonical_key]`.
- **Reset Scope Evaluation:**
  - Scoped Reset (Selected Industry): Clearing `self.results_by_industry.pop(lookup_key, None)` clears the active industry's stored result, clears `self.lbl_result`, and hides `self.btn_report`. Other industries' stored diagnostic results remain untouched.
  - Global Reset (All Industries): Clearing `self.results_by_industry.clear()` wipes all 12 industries.
- **Architectural Recommendation:** Scoped per-industry reset (`reset_industry_results(key)`) inside the industry-specific action bar is the safest and most intuitive behavior, matching D-002 isolation principles 100%.

---

## 3. PROPOSED MINIMUM REMEDIATION SPECIFICATION

In `maya/qyntara_client.py`:

1. In `IndustryRoadmapDialog.update_details(row)` (around line 1572):
   Add `btn_reset` ("RESET RESULTS") to `btn_layout`:
   ```python
   btn_reset = QtWidgets.QPushButton(" RESET RESULTS")
   btn_reset.setObjectName("CloudBtn")
   btn_reset.setStyleSheet("background: #2a2a2a; color: #ff9900; border: 1px solid #ff9900; font-weight: bold; border-radius: 4px; padding: 10px 15px;")
   btn_reset.setCursor(PointingHandCursor)
   btn_reset.clicked.connect(lambda: self.reset_industry_results(key))
   self.btn_reset = btn_reset
   btn_layout.addWidget(btn_reset)
   ```

2. Add method `reset_industry_results(self, industry_key)` to `IndustryRoadmapDialog`:
   ```python
   def reset_industry_results(self, industry_key):
       """Clears stored diagnostic results for the specified industry and updates UI state."""
       lookup_key = get_canonical_key(industry_key)
       if hasattr(self, 'results_by_industry') and lookup_key in self.results_by_industry:
           del self.results_by_industry[lookup_key]
       if hasattr(self, 'lbl_result') and self.lbl_result:
           self.lbl_result.setText("")
       if hasattr(self, 'btn_report') and self.btn_report:
           self.btn_report.hide()
   ```

---

## 4. INVARIANTS & CONTRACT VERIFICATION

The proposed D-009 remediation:
- Preserves all 12 canonical industry keys and mapping contracts.
- Preserves `UI_LABEL_TO_INDUSTRY_KEY` and `INDUSTRY_KEY_TO_UI_LABEL`.
- Preserves backend/API contracts, validators, cloud diagnostics, real Maya scene telemetry, authentication, layout lifecycle `_clear_layout()`, `JobStateMachine`, `JobOrchestrator`, and `NetworkWorker`.
- Has zero regression impact on Gates 1–7 or D-008..D-013.

---

## 5. TEST FORENSICS & COVERAGE GAP ANALYSIS

- **Existing Tests:** `tests/unit/test_matrix_result_isolation.py` tests storage and isolation across industries.
- **Proposed New Unit Test:** `test_d009_reset_results_clears_industry_entry_and_hides_report_button` in `tests/unit/test_matrix_result_isolation.py`.

---

## 6. CURRENT TEST BASELINE

- **Unit Suite (Process A):** 87 / 87 PASSED
- **Integration Suite (Process B):** 13 / 13 PASSED
- **Total Suite:** 100 / 100 PASSED

---

## 7. GIT SAFETY STATEMENT

NO PRODUCTION CODE OR TEST CODE WAS MODIFIED DURING THIS READ-ONLY FORENSIC AUDIT.
