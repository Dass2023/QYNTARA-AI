# Current Job Lifecycle

This document traces the existing job lifecycle as discovered in `qyntara_client.py` during Phase 1E.

## The Flow
1. **UI Action**: A button click connects to `self.submit_job(tasks=["xyz"])`.
2. **Job Submission**: 
   - Synchronous mesh export via `export_temp_obj` (blocks main thread).
   - Synchronous HTTP POST to `/upload` (blocks main thread).
   - Synchronous HTTP POST to `/execute` (blocks main thread).
3. **Job Identifier**: The backend responds with `task_id`.
4. **Queue & Processing**: Assumed backend behavior (not visible to client).
5. **Polling**:
   - The UI spawns a `QProgressDialog`.
   - Enters a synchronous `while True:` loop.
   - Calls `QtWidgets.QApplication.processEvents()` to keep the UI from freezing completely.
   - Performs a synchronous HTTP GET to `/tasks/{task_id}`.
   - Calls `time.sleep(1)`.
6. **Result**: 
   - If state is `"done"`, loop breaks, and `process_backend_result(result)` is called.
7. **Failure**: 
   - If state is `"failed"`, loop breaks, status updated to `PIPELINE ERROR`.
   - If loop exceeds 600s, status updated to `TIMEOUT`, and an attempt to POST `/tasks/{task_id}/cancel` is made.
   - If user clicks Cancel on `QProgressDialog`, posts to `/cancel`.

## Architectural Findings

### Where job IDs are created
Server-side. Client receives them via `/execute`.

### Where job state is stored
Server-side. The client has no authoritative state memory; it merely holds the active `task_id` locally within the lexical scope of the `submit_job` function's `while` loop.

### How polling works
It does **not** use `QTimer`. It uses a blocking `while True:` loop with `time.sleep(1)` and `QApplication.processEvents()`.

### How failures are represented
String representations from the server (`"failed"` state). Handled by breaking the loop. 

### Cancellation & Retries
- **Cancellation**: Supported via user UI interrupt (progress dialog) or hardcoded 600s timeout. Calls `/tasks/{task_id}/cancel`.
- **Retries**: None.

### Network & Reliability Edges
- **If Maya client disconnects/crashes**: The job ID is lost forever. The server likely finishes the job, but the client can never retrieve it because state is bound to the local function scope.
- **If backend restarts**: The client poll will throw an HTTP exception, `try/except` catches it, prints to console, and continues looping/sleeping until the 600s timeout.
- **Client or Server Authority**: The Server is authoritative. However, the client discards the authority if the UI closes.

## Summary
The current architecture is highly fragile, susceptible to UI-blocking lockups, and incapable of resuming lost sessions. However, the contract (the states it relies on) is relatively simple (`running`, `done`, `failed`, `cancelled`).
