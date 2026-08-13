# Phase 2 Architecture Recommendations

Based on the Phase 1 completion audit, the following recommendations are made for Phase 2.

## P0: Extract Asynchronous Job Orchestrator
- **Evidence**: `QyntaraDockable.submit_job` blocks the Maya UI thread using `while True`, `time.sleep()`, and `processEvents()`. It completely ignores the newly approved `JobStateMachine` contract.
- **Business Value**: Prevents Maya from appearing "frozen" to users during 10+ minute AI generation tasks. Enables graceful UI cancellation.
- **Technical Value**: Decouples network polling from the view layer. Allows testability of job orchestration logic without mocking UI dialogs.
- **Risk**: High. Requires transitioning the blocking logic to asynchronous workers or `QTimer`-based state machine ticks without breaking PySide2 lifecycle rules.
- **Effort**: Medium.
- **Dependencies**: Phase 1E (Complete).
- **Reason for Priority**: UI blocking is the single largest stability and UX risk remaining in the frontend application.

## P1: Controller Extraction (MVC Implementation)
- **Evidence**: `QyntaraDockable` is over 2500 lines long, housing raw widget creation, payload assembly, and event routing.
- **Business Value**: Faster iteration on new UI features.
- **Technical Value**: Enforces separation of concerns, enabling unit testing of business logic entirely independent of Maya or PySide2 imports.
- **Risk**: Medium. 
- **Effort**: High. Requires carefully untangling widget references from business logic.
- **Dependencies**: P0 (Orchestrator extraction will naturally remove the hardest coupling).
- **Reason for Priority**: Required to achieve a fully testable frontend ecosystem.

## P2: Maya Runtime Validation Strategy
- **Evidence**: 100% of the current automated test suite runs via Pytest with `StrictMayaCmdsMock`.
- **Business Value**: Prevents regression in actual production environments.
- **Technical Value**: Validates the `MayaCommandRunner` and `UndoChunk` abstractions against real C++ exceptions.
- **Risk**: Low.
- **Effort**: Medium. Requires setting up `mayapy` test runners.
- **Dependencies**: None.
- **Reason for Priority**: Mock validation provides false confidence if real Maya APIs change or behave unexpectedly.

## DEFER: PostgreSQL / Persistence
- **Evidence**: Current jobs are ephemeral. State is lost if Maya crashes.
- **Reason for Deferral**: While job recovery is important, a full PostgreSQL deployment is architectural overkill for a desktop plugin client. A lightweight local SQLite cache or JSON file bound to `SessionState` satisfies the requirement at a fraction of the cost.
- **Action**: Deferred until a lightweight local persistence layer is designed.

## DEFER: Kubernetes & Microservices
- **Evidence**: The backend is currently a monolithic FastAPI application.
- **Reason for Deferral**: Until production load proves that AI generative tasks require multi-node worker scaling, introducing Docker Compose and Kubernetes adds unnecessary operational overhead.
- **Action**: Deferred indefinitely pending load-testing evidence.

## REJECT: PySide6 Migration
- **Evidence**: Maya versions pre-2024 (e.g., 2022, 2023) use PySide2 natively.
- **Reason for Rejection**: A forced migration to PySide6 will instantly break compatibility with industry-standard Maya versions. 
- **Action**: Rejected. The UI must remain PySide2 compatible, or implement a dual-compatibility abstraction layer (e.g., `Qt.py`).
