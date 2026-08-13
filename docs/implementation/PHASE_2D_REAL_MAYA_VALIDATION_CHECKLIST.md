# PHASE 2D REAL MAYA VALIDATION CHECKLIST

Use this checklist to perform the final manual validation in Maya 2025. You can use the provided script (`tests/maya_validation/phase2d_real_maya_validation.py`) to assist with logging.

## A — Plugin Startup
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- Launch Maya 2025.
- Load Qyntara plugin.
- Open QyntaraDockable without exceptions or crashes.

## B — Job Submission
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- Prepare a test scene.
- Submit a valid optimization/generative job.
- Maya-side export completes.
- JobOrchestrator initiates `NetworkWorker` with the exported file path.
- Async upload and backend execute calls occur on background thread.
- Valid Job ID is returned.

## C — Maya Responsiveness
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- Introduce a 4+ second intentional network delay.
- While the request is active, verify that you can:
    - Pan, orbit, and zoom the viewport fluidly.
    - Select objects in the scene.
    - Interact with Maya UI panels.
- Do NOT simply claim "zero blocking"—record observable behavior.

## D — State Transitions
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- Job reaches `QUEUED`, transitions to `PROCESSING`, and finishes at `COMPLETED`.
- A failed job transitions appropriately to `FAILED`.
- The UI reflects these state changes accurately.

## E — Polling
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- `QTimer` handles polling correctly.
- `poll_in_flight` prevents multiple overlapping workers.
- Polling halts permanently upon terminal state (`COMPLETED`/`FAILED`/`CANCELLED`).
- Timeout works gracefully.

## F — Completion
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- Completion signals correctly bubble up.
- `JobStateMachine` updates.
- `process_backend_result` invokes `import_result`.
- Final scene update executes flawlessly on the main thread.

## G — Network Failure
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- Force a network timeout, unavailable backend, or invalid authentication.
- UI gracefully shows the error.
- Maya does not crash or freeze.
- Worker performs clean termination.
- State transitions to `FAILED`.

## H — Maya Shutdown
**Status:** [ PENDING HUMAN VALIDATION ]
**Evidence:** 
- Start a deliberately delayed network job.
- Close the Qyntara UI and then close Maya while the worker is active.
- Verify Maya shuts down completely without segmentation faults, python exceptions, or orphaned `QThread` processes running in the background.
