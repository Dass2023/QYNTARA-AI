# Test Warning Audit

This document classifies the 54 warnings reported during the Phase 1C test execution, as required before proceeding with Phase 1D implementation.

## Warning 1: FastAPI Lifespan Events
- **Warning:** `DeprecationWarning: on_event is deprecated, use lifespan event handlers instead.`
- **Source:** `backend\main.py:81` / `fastapi\applications.py:4580`
- **Severity:** Low. (Deprecation warning for future Python versions, no immediate threat).
- **Action:** Deferred. (Backend code modification is out of scope for Phase 1D).

## Warning 2: Scikit-Image / NumPy Shape Assignment
- **Warning:** `DeprecationWarning: Setting the shape on a NumPy array has been deprecated in NumPy 2.5.`
- **Source:** `tests/unit/test_remesher.py` (48 warnings) mapping to `skimage.measure._marching_cubes_lewiner.py`.
- **Severity:** Low. (Dependency-internal warning regarding future NumPy compatibility).
- **Action:** Deferred. (Third-party library code; upgrading dependencies is restricted during Phase 1 stabilization).

## Warning 3: UTC Datetime Deprecation
- **Warning:** `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version. Use timezone-aware objects to represent datetimes in UTC: datetime.datetime.now(datetime.UTC).`
- **Source:** `backend\security.py:31` (Triggered by 3 backend tests).
- **Severity:** Low. (Python 3.12+ standard library deprecation warning).
- **Action:** Deferred. (Backend code modification is out of scope for Phase 1D).

## Summary
All 54 warnings are `DeprecationWarning` exceptions raised by third-party libraries (FastAPI, Scikit-Image) or the backend code interacting with standard libraries in Python 3.14. None of these warnings originate from the Maya UI or API Client code currently under stabilization. None pose an immediate execution risk to Phase 1D. They are formally logged and deferred to a future backend tech-debt phase.
