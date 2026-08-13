# Phase 2 Architecture Reassessment

## 1. QyntaraDockable Remaining Responsibilities
**ALREADY EXTRACTED:**
- Direct HTTP networking (`NexusAPIClient`).
- Isolated session variables (`SessionState`).
- Destructive/unsafe Maya operations (`MayaCommandRunner`, `UndoChunk`).
- Job State Logic definitions (`JobStateMachine`).

**STILL COUPLED:**
- UI Widget initialization and event binding.
- Business logic routing (deciding which AI task to execute).
- Job orchestration (the `submit_job` method).
- Telemetry/Stats polling (`QTimer` polling `fetch_stats`).

**SHOULD EXTRACT:** Job orchestration and business logic routing.
**SHOULD REMAIN:** Pure PySide2 view layer (UI rendering, layout, styling).

## 2. UI/Business/Network Coupling
High coupling remains in the job submission flow. `submit_job` currently instantiates a `QProgressDialog`, performs blocking network uploads, and handles state logic synchronously in a single method.

## 3. Remaining Maya Coupling
Significantly reduced. Destructive scene modifications are routed through execution boundaries. The remaining `cmds` calls are primarily fast queries or UI event hooks (`scriptJob`).

## 4. Remaining State Coupling
UI widgets still directly dictate payload structures, but global variables have been eliminated.

## 5. Remaining Direct HTTP Usage
None. `urllib` and `requests` calls have been fully eradicated from the frontend and routed through `NexusAPIClient`.

## 6. Job Lifecycle Integration Gap
Phase 1E established the `JobStateMachine` contract, but `submit_job` currently ignores it, relying on hardcoded string-matching (`"done"`, `"failed"`) directly coupled to the API response. 

## 7. QTimer / Polling Architecture
- `QTimer` is currently used *only* for the background `fetch_stats` telemetry.
- Job polling uses a synchronous `while True:` loop paired with `QApplication.processEvents()` and `time.sleep(1)`. 

## 8. Synchronous Network/UI Blocking
The UI thread fundamentally blocks during large file exports, network uploads, and polling iteration intervals. This is a primary risk for user experience (Maya freezing).

## 9. Error Handling Consistency
Greatly improved via `MayaExecutionError` and `NexusAPIClient` exception normalization, but the UI layer still contains some `except Exception: pass` blocks around non-critical logic.

## 10. Testability Gaps
`submit_job` cannot be effectively unit tested because it launches blocking GUI components (`QProgressDialog`) and loops indefinitely. 

## 11. Maya Runtime Validation Gaps
All automated testing is currently driven by Pytest using `StrictMayaCmdsMock`. Validating the execution boundaries inside a live `mayapy` session or Maya GUI is completely pending.

## 12. Security Debt
- Hardcoded test credentials or environment variable fallbacks (like `ACCESS_CODE`) exist.
- Upload paths are sanitized, but backend authentication lacks robust role-based access control (RBAC).

## 13. Backend Reliability
FastAPI `on_event` deprecation warnings indicate aging dependencies.

## 14. AI/ML Architecture Maturity
The backend executes AI/ML payloads, but lacks a sophisticated queue (e.g., Celery/Redis). Job execution is assumed synchronous or handled via simple thread pools on the server.

## 15. Deployment Architecture
Monolithic FastAPI backend running locally or on a single remote server. No container orchestration (Kubernetes) is present.

## 16. Documentation Gaps
The `docs/` directory is highly mature regarding Phase 1 stabilization, but lacks developer onboarding guides for the newly separated layers (`NexusAPIClient`, `SessionState`, `MayaCommandRunner`).
