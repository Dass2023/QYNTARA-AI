# Job State Contract

This document formalizes the job state machine that governs the Qyntara Nexus pipeline.

## 1. Canonical States
- **QUEUED**: Job is accepted by the server but execution has not started.
- **PROCESSING**: Job is actively being computed. (Maps to backend "running").
- **COMPLETED**: Job finished successfully and result is available. (Maps to backend "done").
- **FAILED**: Job encountered an unrecoverable error.
- **CANCELLED**: Job was intentionally terminated by the user or timed out.
- **RETRYING**: Job encountered a transient error and is attempting recovery.

## 2. State Definitions

### QUEUED
- **Meaning**: Server has acknowledged the job submission.
- **Entry Conditions**: Valid `/execute` HTTP POST succeeds.
- **Exit Conditions**: Backend begins processing, or user cancels.
- **Allowed Transitions**: `PROCESSING`, `CANCELLED`
- **Owner**: Server

### PROCESSING
- **Meaning**: AI/Mesh generation is active.
- **Entry Conditions**: Backend worker picks up the task.
- **Exit Conditions**: Task finishes, errors out, or is cancelled.
- **Allowed Transitions**: `COMPLETED`, `FAILED`, `CANCELLED`, `RETRYING`
- **Owner**: Server

### COMPLETED
- **Meaning**: Terminal state. Payload ready for Maya import.
- **Entry Conditions**: Successful task output.
- **Exit Conditions**: None (Terminal).
- **Allowed Transitions**: None
- **Owner**: Server

### FAILED
- **Meaning**: Terminal error state.
- **Entry Conditions**: Unrecoverable computation error or hard Maya export/upload failure.
- **Exit Conditions**: Manual resubmission (creates a *new* job, not a transition).
- **Allowed Transitions**: None (Client-side resubmit creates new ID).
- **Owner**: Server

### CANCELLED
- **Meaning**: Terminal aborted state.
- **Entry Conditions**: Client issues `/cancel` request or 600s hard timeout triggers.
- **Exit Conditions**: None (Terminal).
- **Allowed Transitions**: None
- **Owner**: Client/Server Hybrid

### RETRYING
- **Meaning**: (Proposed for future) Transient network or backend load issue detected.
- **Entry Conditions**: Client gets 503 or 429 during polling.
- **Exit Conditions**: Network recovers (resume PROCESSING) or retry limit reached (FAILED).
- **Allowed Transitions**: `PROCESSING`, `FAILED`
- **Owner**: Client (as server does not natively communicate this state yet)

## 3. Transition Matrix & Invalid Transitions
| Current State | Valid Next States |
|---------------|-------------------|
| `QUEUED`      | `PROCESSING`, `CANCELLED` |
| `PROCESSING`  | `COMPLETED`, `FAILED`, `CANCELLED`, `RETRYING` |
| `RETRYING`    | `PROCESSING`, `FAILED` |
| `COMPLETED`   | *None (Terminal)* |
| `FAILED`      | *None (Terminal)* |
| `CANCELLED`   | *None (Terminal)* |

**Explicitly Invalid Transitions:**
- `COMPLETED` -> `PROCESSING` (Cannot restart a finished job)
- `FAILED` -> `COMPLETED` (Must be a new job)
- `CANCELLED` -> `QUEUED` (Cannot un-cancel)

## 4. Client vs Server Authority
**SERVER STATE IS AUTHORITATIVE.**
The client acts strictly as a *view* of the server's state. 
- **Reconnect Behavior (Proposed)**: If Maya restarts, the client *should* be able to query the server for pending jobs. However, because local `submit_job` loses the `task_id` upon function exit/crash, the client currently lacks the persistence required to perform recovery.

## 5. Failure Model
| Scenario | Behavior / State |
|---|---|
| Network Timeout (600s) | Transitions to `CANCELLED`, attempts to notify server. |
| HTTP 401 / 403 | Transitions to `FAILED` (Auth error). |
| HTTP 429 / 503 | Transitions to `RETRYING` (Proposed) or `FAILED` (Current). |
| Backend Unavailable (ConnectionRefused) | Transitions to `FAILED`. |
| Malformed Job Response | Transitions to `FAILED`. |
| Maya Shutdown | Job continues on server. Client loses reference (Orphaned). |
| Missing Result Payload | Transitions to `FAILED` (Corrupt completion). |

## 6. QTimer Decision
**QTimer usage for job polling is deferred.**
The current system relies on a strictly synchronous `while True` loop with `QApplication.processEvents()`. Because no backend event mechanism (e.g., WebSockets) exists, polling *must* continue. Replacing the synchronous loop with a `QTimer` now would require a massive architectural rewrite of `submit_job` into an asynchronous, callback-driven method, violating the Phase 1 rule to "not rewrite QyntaraDockable" and "not introduce async architecture".

## 7. Persistence Decision
**POSTGRESQL DEFERRED.**
- **Current**: No persistence. Job IDs live in local memory stack frames.
- **Required**: Ability to recover job state if Maya crashes.
- **Proposed**: A lightweight local SQLite cache or JSON file managed by `SessionState` to store active `task_id`s, rather than a full PostgreSQL deployment. PostgreSQL is explicitly deferred as unnecessary complexity for a desktop client.
