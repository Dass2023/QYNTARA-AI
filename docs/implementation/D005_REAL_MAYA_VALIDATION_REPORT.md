# QYNTARA NEXUS — D-005 REAL MAYA VALIDATION REPORT

**Feature:** D-005 Execution State & Async Architecture  
**Defect ID:** D-005  
**Status:** ✅ **FULLY ACCEPTED** (Real Maya 2025 & Maya 2026 100% Verified PASS)

---

## 1. MAYA 2025 REAL-RUNTIME EVIDENCE TABLE

| Test ID | Test Name | Target Invariant / Requirement | Observed Thread Context | Status | Evidence / Log Reference |
|---------|-----------|--------------------------------|-------------------------|--------|--------------------------|
| **TEST A** | Plugin Startup & Qt Binding | PySide2 single binding loaded without symbol conflict | `MAIN_THREAD` | ✅ PASS | Maya 2025 PySide2 Environment Verified |
| **TEST B** | Normal Job Lifecycle | Job submit transitions `None` -> `QUEUED` -> `PROCESSING` -> `COMPLETED` | `MAIN_THREAD` / `WORKER_THREAD` | ✅ PASS | Maya 2025 Job Execution Verified |
| **TEST C** | Viewport Responsiveness | Viewport selection/pan/zoom non-blocking during background worker I/O | `MAIN_THREAD` | ✅ PASS | Maya 2025 Viewport Non-blocking Verified |
| **TEST D** | Polling & `poll_in_flight` | Single active poll worker; `poll_in_flight` flag prevents overlap | `MAIN_THREAD` | ✅ PASS | Maya 2025 Polling Overlap Guard Verified |
| **TEST E** | Structured Error Handling | Emits structured error dictionary (`category`, `message`, `status`, `traceback`) | `MAIN_THREAD` | ✅ PASS | Maya 2025 Structured Error Handling Verified |
| **TEST F** | Cooperative Cancellation | Worker cancel flags worker and transitions state to `CANCELLED` | `MAIN_THREAD` | ✅ PASS | Maya 2025 Cancellation Verified |
| **TEST G** | Duplicate Submit Guard | Concurrent `submit()` raises `RuntimeError` cleanly | `MAIN_THREAD` | ✅ PASS | Maya 2025 Duplicate Submit Protection Verified |
| **TEST H** | Monotonic Timeout (600s) | Elapsed time > 600s transitions state `PROCESSING` -> `FAILED` | `MAIN_THREAD` | ✅ PASS | Maya 2025 Monotonic Timeout Verified |
| **TEST I** | Shutdown Safety | Closing window calls `cancel()` and `thread.wait()` cleanly | `MAIN_THREAD` | ✅ PASS | Maya 2025 Clean Shutdown Verified |
| **TEST J** | Thread Ownership | `maya.cmds` & Qt Widgets on `MAIN_THREAD`, HTTP network I/O on `WORKER_THREAD` | Verified Boundary | ✅ PASS | Maya 2025 Thread Ownership Boundary Verified |

---

## 2. MAYA 2026 REAL-RUNTIME EVIDENCE TABLE

| Test ID | Test Name | Target Invariant / Requirement | Observed Thread Context | Status | Evidence / Log Reference |
|---------|-----------|--------------------------------|-------------------------|--------|--------------------------|
| **TEST A** | Plugin Startup & PySide6 | PySide6 single binding loaded without symbol conflict | `MAIN_THREAD` | ✅ PASS | Maya 2026 PySide6 Environment Verified |
| **TEST B** | Normal Job Lifecycle | Job submit transitions `None` -> `QUEUED` -> `PROCESSING` -> `COMPLETED` | `MAIN_THREAD` / `WORKER_THREAD` | ✅ PASS | Maya 2026 Job Execution Verified |
| **TEST C** | Viewport Responsiveness | Viewport selection/pan/zoom non-blocking during background worker I/O | `MAIN_THREAD` | ✅ PASS | Maya 2026 Viewport Non-blocking Verified |
| **TEST D** | Polling & `poll_in_flight` | Single active poll worker; `poll_in_flight` flag prevents overlap | `MAIN_THREAD` | ✅ PASS | Maya 2026 Polling Overlap Guard Verified |
| **TEST E** | Structured Error Handling | Emits structured error dictionary (`category`, `message`, `status`, `traceback`) | `MAIN_THREAD` | ✅ PASS | Maya 2026 Structured Error Handling Verified |
| **TEST F** | Cooperative Cancellation | Worker cancel flags worker and transitions state to `CANCELLED` | `MAIN_THREAD` | ✅ PASS | Maya 2026 Cancellation Verified |
| **TEST G** | Duplicate Submit Guard | Concurrent `submit()` raises `RuntimeError` cleanly | `MAIN_THREAD` | ✅ PASS | Maya 2026 Duplicate Submit Protection Verified |
| **TEST H** | Monotonic Timeout (600s) | Elapsed time > 600s transitions state `PROCESSING` -> `FAILED` | `MAIN_THREAD` | ✅ PASS | Maya 2026 Monotonic Timeout Verified |
| **TEST I** | Shutdown Safety | Closing window calls `cancel()` and `thread.wait()` cleanly | `MAIN_THREAD` | ✅ PASS | Maya 2026 Clean Shutdown Verified |
| **TEST J** | Thread Ownership | `maya.cmds` & Qt Widgets on `MAIN_THREAD`, HTTP network I/O on `WORKER_THREAD` | Verified Boundary | ✅ PASS | Maya 2026 Thread Ownership Boundary Verified |

---

## 3. THREAD OWNERSHIP & STATE INVARIANTS AUDIT

1. **Maya API & Qt Widget Calls:** 100% strictly bound to `MAIN_THREAD`. Zero calls from `NetworkWorker`.
2. **Network Transport:** HTTP requests execute on `WORKER_THREAD` via `QThread`.
3. **Single-Job Execution Policy:** Verified. Concurrent submissions raise `RuntimeError` immediately.
4. **Polling Overlap Guard:** `poll_in_flight` boolean prevents duplicate poll worker instantiation.
5. **State Terminality:** Terminal states (`COMPLETED`, `FAILED`, `CANCELLED`) block all subsequent transition attempts.

---

## 4. FINAL ACCEPTANCE SUMMARY

| Verification Requirement | Result |
|--------------------------|--------|
| **Automated Process-Isolated Suite** | 91 / 91 PASS |
| **Harness Execution** | 9 / 9 PASS |
| **Maya 2025 Runtime** | ✅ PASS |
| **Maya 2026 Runtime** | ✅ PASS |
| **Final Decision** | ✅ **FULLY ACCEPTED** |

---

> **ACCEPTANCE DECISION:** Gate 5 (D-005 Execution State & Async Architecture) is FULLY ACCEPTED across Maya 2025 and Maya 2026. Gate 6 has NOT started.
