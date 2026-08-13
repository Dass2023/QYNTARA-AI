# QYNTARA NEXUS — D-007 TEST STRATEGY & SPECIFICATION

**Feature:** Test Strategy for Real Scene Telemetry (No Randomness)  
**Status:** 🔍 **READ-ONLY SPECIFICATION COMPLETE**

---

## TEST SUITE SPECIFICATION (12 TEST SCENARIOS)

| Test ID | Test Scenario | Input Scene State | Expected Maya Extraction | Expected Payload | Expected Result |
|---------|---------------|-------------------|--------------------------|------------------|-----------------|
| **TEST 1** | Empty Scene | New empty scene (`cmds.file(new=True, force=True)`) | `polycount`: 0 | `{"polycount": 0, "provenance": "REAL_MAYA_MEASUREMENT"}` | PASS / Handled Safely |
| **TEST 2** | Single Cube | `polyCube()` in scene | `polycount`: 12 tris (6 faces) | `{"polycount": 12, "provenance": "REAL_MAYA_MEASUREMENT"}` | PASS |
| **TEST 3** | Multi-Object Scene | 10 primitives | Exact sum of all mesh tris | `{"polycount": exact_sum, "provenance": "REAL_MAYA_MEASUREMENT"}` | PASS |
| **TEST 4** | Dense Mesh | High-poly sphere (100k tris) | `polycount`: 100,000 | `{"polycount": 100000, "provenance": "REAL_MAYA_MEASUREMENT"}` | PASS |
| **TEST 5** | Non-Manifold Geometry | Mesh with non-manifold edge | `is_manifold`: False | `{"is_manifold": False, "provenance": "REAL_MAYA_MEASUREMENT"}` | FAIL / WARNING |
| **TEST 6** | Texture Memory | Scene with 2 connected file textures (10MB total) | `texture_mem_mb`: 10.0 | `{"texture_mem_mb": 10.0, "provenance": "REAL_MAYA_MEASUREMENT"}` | PASS |
| **TEST 7** | Unsaved Scene File | Unsaved new scene | `filesize_mb`: `NOT_AVAILABLE` | `{"filesize_mb": "NOT_AVAILABLE", "provenance": "NOT_AVAILABLE"}` | Handled Safely |
| **TEST 8** | Overhang Computation | Cube tilted 45 degrees | `critical_overhangs`: Exact faces pointing down | `{"critical_overhangs": count, "provenance": "REAL_MAYA_MEASUREMENT"}` | PASS |
| **TEST 9** | Collision Hulls | 2 `_col` transforms | `collision_hulls`: 2 | `{"collision_hulls": 2, "provenance": "REAL_MAYA_MEASUREMENT"}` | PASS |
| **TEST 10** | Maya 2025 Execution | Executed inside Maya 2025 Script Editor | Real telemetry extracted | Clean API response | PASS |
| **TEST 11** | Maya 2026 Execution | Executed inside Maya 2026 Script Editor | Real telemetry extracted | Clean API response | PASS |
| **TEST 12** | All 12 Industries E2E | Switch across 12 industries sequentially | Zero random numbers emitted | 100% deterministic results | PASS |

---

> **MANDATORY STOP:** Specification complete. Zero tests implemented or modified yet. Awaiting human authorization.
