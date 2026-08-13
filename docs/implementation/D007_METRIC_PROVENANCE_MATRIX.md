# QYNTARA NEXUS — D-007 METRIC PROVENANCE MATRIX

**Feature:** Real Scene Telemetry & Metric Truth  
**Status:** 🔍 **READ-ONLY AUDIT COMPLETE**

---

## METRIC PROVENANCE TRACEABILITY MATRIX

| Metric Name | Current Source | Current Truth | Target Maya API (Maya 2025/2026) | Provenance Class | Replacement Required |
|-------------|----------------|---------------|-----------------------------------|------------------|----------------------|
| `polycount` | `random.randint` | INVALID | `cmds.polyEvaluate(t=True)` | `REAL_MAYA_MEASUREMENT` | YES |
| `has_lods` | Hardcoded `True` | MOCK | `bool(cmds.ls("*_LOD*", "*_lod*"))` | `REAL_MAYA_MEASUREMENT` | YES |
| `is_manifold` | Hardcoded `True` | MOCK | `len(cmds.polyInfo(nonManifoldEdges=True) or []) == 0` | `REAL_MAYA_MEASUREMENT` | YES |
| `bbox_diagonal` | Hardcoded `0.15` | MOCK | Vector length of `cmds.exactWorldBoundingBox()` | `REAL_MAYA_MEASUREMENT` | YES |
| `topology_type` | Hardcoded `"triangulated"` | MOCK | Inspect face vertex count (`3` = tri, `4` = quad) | `REAL_MAYA_MEASUREMENT` | YES |
| `poles` | `random.choice` | INVALID | `len(cmds.polyInfo(nonManifoldVertices=True) or [])` | `REAL_MAYA_MEASUREMENT` | YES |
| `has_circular_ref` | Hardcoded `False` | MOCK | Inspect Maya DAG reference hierarchy loops | `REAL_MAYA_MEASUREMENT` | YES |
| `nurbs_deviation` | Hardcoded `0.02` | MOCK | `NOT_AVAILABLE` (if no NURBS nodes in scene) | `NOT_AVAILABLE` / `REAL_MAYA` | YES |
| `occludes_sensor` | Hardcoded `False` | MOCK | `NOT_AVAILABLE` (unless sensor node exists) | `NOT_AVAILABLE` | YES |
| `bbox_height` | Hardcoded `3.5` | MOCK | Bounding box Y-height (`ymax - ymin`) | `REAL_MAYA_MEASUREMENT` | YES |
| `fire_rating` | Hardcoded `"A1"` | MOCK | Custom Maya attribute or `NOT_AVAILABLE` | `NOT_AVAILABLE` | YES |
| `stress_concentrators` | Hardcoded `0` | MOCK | High-curvature / non-manifold edge count | `REAL_MAYA_MEASUREMENT` | YES |
| `texture_mem_mb` | `random.randint` | INVALID | Total size of texture files connected to `file` nodes | `REAL_MAYA_MEASUREMENT` | YES |
| `filesize_mb` | Hardcoded `4.2` | MOCK | `os.path.getsize(cmds.file(q=True, sn=True))` | `REAL_MAYA_MEASUREMENT` | YES |
| `collision_hulls` | Hardcoded `1` | MOCK | `len(cmds.ls("*_col*", type="transform"))` | `REAL_MAYA_MEASUREMENT` | YES |
| `uuid` | Hardcoded `"Asset-77"` | MOCK | Maya scene file hash / workspace ID | `REAL_MAYA_MEASUREMENT` | YES |
| `critical_overhangs` | `random.randint` | INVALID | Normal angle computation relative to Down vector | `REAL_MAYA_MEASUREMENT` | YES |

---

> **ANTI-FABRICATION GUARANTEE:** Zero random numbers. Zero hardcoded fake telemetry. Missing measurements are returned strictly as `NOT_AVAILABLE`.
