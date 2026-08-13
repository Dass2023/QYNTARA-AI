# Phase 2A: Job Orchestrator Design

## 1. Current Job Lifecycle
The current `submit_job()` relies on a synchronous, UI-blocking `while True` loop with `time.sleep(1)` and `QtWidgets.QApplication.processEvents()`. This blocks the Maya thread continuously, heavily degrades user experience, and loses job state entirely if the UI is interrupted or closed.

## 2. Target Orchestration Boundary
The goal is to cleanly decouple the job execution from the UI while enforcing strict semantic bounds.
**Target Flow:**
`QyntaraDockable` (receives user intent) 
  -> `JobOrchestrator` (coordinates submission/lifecycle)
  -> `JobMonitor` (encapsulates when and how to poll)
  -> `JobStateMachine` (enforces valid lifecycle states)
  -> `NexusAPIClient` (performs raw HTTP)
  -> `Backend`

## 3. JobMonitor Responsibility
- Decides *when* monitoring occurs (e.g., ticking on an interval).
- Controls the polling interval and termination conditions (e.g., 600s hard timeout).
- Observes job status and monitors reconnect capability.
- **Does NOT:** Implement HTTP transport, Maya operations, UI widgets, authentication, or business logic.

## 4. JobStateMachine Responsibility
- Holds the canonical `JobState` contract.
- Enforces valid states and valid/invalid transitions (`QUEUED` -> `PROCESSING` -> `COMPLETED`).
- Provides authoritative lifecycle semantics.

## 5. NexusAPIClient Responsibility
- Handles HTTP transport exclusively.
- Manages authentication, network timeouts, and JSON parsing.
- Remains unchanged and unaware of the Orchestrator, Maya, or PySide.

## 6. QTimer Role
`QTimer` serves purely as a **scheduling mechanism**. It determines the frequency at which the `JobMonitor` checks state. It ensures that callbacks are fired on the Qt/Maya main event-loop thread. `QTimer` replaces the `time.sleep()` polling loop, but it does *not* make the network transport itself non-blocking.

## 7. Network Blocking Analysis
It is critical to distinguish between polling-loop blocking and network I/O blocking:
1. **Polling-loop blocking:** The current `while True` loop locks the main thread permanently until the job completes. `QTimer` eliminates this.
2. **Network I/O blocking:** If a `QTimer` callback executes a synchronous HTTP request via `NexusAPIClient`, the Maya main thread will still be frozen for the duration of that specific network round-trip.
3. **Maya main-thread execution:** Maya requires API commands and Qt updates to run on the main thread, but network operations do not.

## 8. Maya Thread Requirements
Maya API operations (`cmds`, `OpenMaya`) and Qt UI updates **must** execute in the appropriate Maya main thread context. However, network I/O operations do not inherently require Maya's main thread. If a worker/network mechanism executes off-thread, its results or callbacks that interact with Maya/Qt must be safely marshalled back to the main thread.

## 9. Network Execution Strategy Options

### OPTION A: QTimer + synchronous NexusAPIClient
- **Description**: `JobMonitor` ticks via `QTimer`, calling `NexusAPIClient.request_json` synchronously.
- **Pros**: Simplest to implement. Maya-safe from a direct API perspective (no cross-thread scene access).
- **Cons**: Network requests still temporarily block the Maya UI during the exact moment of the HTTP round-trip (e.g. 50-200ms stutter per second).

### OPTION B: Qt-Compatible Asynchronous Network (e.g., QNetworkAccessManager)
- **Description**: Replace `urllib` in `NexusAPIClient` with PySide2's `QNetworkAccessManager`.
- **Pros**: Natively non-blocking network I/O handled entirely by the Qt event loop. Eliminates UI stutter completely without manual thread management.
- **Cons**: Requires rewriting `NexusAPIClient`'s core transport. Can be highly complex to manage authentication/multipart file uploads natively through Qt's older API compared to modern Python libraries.

### OPTION C: Worker/Network Execution Context (QThread + Signals)
- **Description**: Execute `NexusAPIClient` requests on a background `QThread` or `QRunnable`. Results are marshalled back to the main thread via Qt Signals.
- **Pros**: Uses existing `NexusAPIClient` (no HTTP rewrite). Completely eliminates UI blocking. Safe for Maya if implemented strictly (background thread only touches network, Signal slot handles UI/Maya cmds).
- **Cons**: Medium complexity. Requires disciplined boundary management to prevent background threads from accidentally touching Maya state. Requires careful management of Maya shutdown behavior and orphan threads.

## 10. Risks and Trade-offs
- Option A is the safest regarding thread crashes but retains UX stutter.
- Option B requires rewriting a proven networking component (`NexusAPIClient`).
- Option C is the most standard architectural approach in PySide but requires robust signal marshaling to prevent fatal Maya exceptions during off-thread execution.

## 11. Recommended Implementation Sequence
1. Implement `JobOrchestrator`, `JobMonitor`, and `JobStateMachine` utilizing **Option A** (QTimer + synchronous HTTP) as a baseline. This immediately solves the permanent UI lockup and allows us to validate the state machine contract using existing, proven `NexusAPIClient` logic.
2. Once the orchestration boundary is proven stable and testable, strategically migrate the transport execution to **Option C** (Worker thread marshaled via Signals) in a later phase to eliminate the remaining intermittent network I/O stutter.
