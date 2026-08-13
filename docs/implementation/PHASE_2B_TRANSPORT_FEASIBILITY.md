# Phase 2B Transport Feasibility

## CURRENT ENVIRONMENT
-------------------
**Maya version(s):** 2022+ (Supported range based on repository metadata)
**Python version:** 3.7+ (Maya 2022+ ships with Python 3)
**PySide version:** PySide2 (Strict requirement for Maya 2022-2024 compatibility)
**Qt version:** 5.15.x
**Existing event-loop assumptions:** Maya's main thread owns the Qt `QApplication` event loop. All `cmds` operations and UI updates must execute on this main thread.

## OPTION A: QTimer + Synchronous NexusAPIClient
--------
**Advantages:**
- Absolute highest implementation safety and lowest architectural risk.
- Zero cross-thread complexity. No chance of causing Maya fatal crashes from background threads touching scene state.
- 100% compatible with the existing, battle-tested `NexusAPIClient` (which uses `urllib`).
- Eliminates the infinite `while True` lockup.

**Disadvantages:**
- Retains minor UI stutter. The Maya main thread will block for the exact duration of the HTTP round-trip (e.g., 50-200ms) every time the `QTimer` ticks.

**Risks:**
- Lowest technical risk.
- High UX risk (users may complain about the interface momentarily sticking during polling).

**Compatibility:**
- Universal across all Maya and PySide versions.

**UI impact:**
- The UI recovers from the permanent freeze, but intermittent stutter remains during active polling.

## OPTION B: QNetworkAccessManager
--------
**Advantages:**
- Natively non-blocking network I/O fully integrated into the Qt event loop.
- Complete elimination of UI stutter.

**Disadvantages:**
- Requires completely replacing and rewriting the `NexusAPIClient` transport layer.
- `QNetworkAccessManager` is verbose and complex for tasks like multipart file uploads (which `urllib`/`requests` handle elegantly).
- Ties the HTTP transport strictly to the GUI framework, violating the current decoupled architecture.

**Risks:**
- High implementation risk. Breaking the core API client could destabilize all phases (0, 1A, 1B).

**Compatibility:**
- Compatible with PySide2, but Qt HTTP APIs often differ subtly across PySide versions (e.g., PySide6 migration later would be painful).

**UI impact:**
- Perfect UI responsiveness.

## OPTION C: Worker/Network Execution Context + Qt Signals
--------
**Advantages:**
- Retains `NexusAPIClient` completely unmodified.
- Eliminates UI stutter by executing the HTTP request on a background thread (`QThread` or `QRunnable`).
- Standard PySide asynchronous pattern: worker thread emits a Signal, which safely marshals the response back to a Slot executing on the Maya main thread.

**Disadvantages:**
- Medium architectural complexity.
- Requires explicit cleanup logic (e.g., waiting on threads during plugin unload or Maya shutdown) to prevent orphaned threads or segmentation faults.

**Risks:**
- **FATAL MAYA CRASH RISK:** If the background thread accidentally invokes any Maya `cmds` or Qt UI updates directly, Maya will instantly crash. Strict Signal/Slot marshalling boundaries are mandatory.

**Compatibility:**
- Standard feature of PySide2 (`QtCore.QThread`, `QtCore.Signal`).

**UI impact:**
- Perfect UI responsiveness.

## DECISION
--------
**Recommended option:** **OPTION C (Worker/Network Execution Context + Qt Signals)**
**Reason:** Option A fails the primary objective ("eliminate UI-blocking architecture") by merely swapping a permanent freeze for an intermittent stutter. Option B violates the "compatibility with NexusAPIClient" requirement by forcing a rewrite of the transport layer. Option C achieves a perfectly responsive UI, retains the `NexusAPIClient` unmodified, and strictly respects Maya's main-thread requirements by marshalling results back via native PySide Signals.

**Rejected alternatives:** 
- Option A is rejected as the final target due to remaining UI stutter.
- Option B is rejected due to violating the boundary of `NexusAPIClient` and requiring a high-risk HTTP rewrite.

**Migration risks:**
- Maya is extremely unforgiving regarding multi-threading. The `JobMonitor` must ensure that the `QThread` *only* executes the `NexusAPIClient` HTTP call, and strictly returns primitive data (JSON/dict) via a Signal.
- Shutdown behavior must be carefully managed. If the user closes the UI while a background thread is waiting for an HTTP timeout, the thread must be gracefully interrupted or orphaned safely.

**Testing strategy:**
- **MOCK VALIDATION:** We can use Pytest and `pytest-qt` (or manual `QCoreApplication` loops) to validate that the `JobMonitor` properly spawns a thread, executes the mock HTTP call, and emits the completion Signal back to the main thread.
- **REAL MAYA VALIDATION:** **VALIDATION REQUIRED**. Mocking PySide threading does not guarantee Maya stability. The Signal marshalling boundary *must* be manually tested inside a live `mayapy` or Maya.exe session to confirm that cross-thread crashes do not occur when updating the `JobStateMachine`.
