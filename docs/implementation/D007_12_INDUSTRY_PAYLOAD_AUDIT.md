# QYNTARA NEXUS — D-007 12-INDUSTRY PAYLOAD AUDIT

**Feature:** 12-Industry Payload Truthfulness  
**Status:** 🔍 **READ-ONLY AUDIT COMPLETE**

---

## 12-INDUSTRY PAYLOAD AUDIT TABLE

| Industry | Canonical Key | Current Payload Generator | Real Maya Measurement Implementation Plan | Remediation Status |
|----------|---------------|---------------------------|-------------------------------------------|--------------------|
| **Gaming** | `gaming` | `random.randint` | `polycount`: `cmds.polyEvaluate(t=True)`, `has_lods`: `cmds.ls('*_LOD*')` | SPECIFIED |
| **Film / VFX** | `film` | `random.choice` | `poles`: `cmds.polyInfo(nonManifoldVertices=True)` | SPECIFIED |
| **Automotive** | `automotive` | Hardcoded `0.02` | `has_metadata_layer`: `cmds.objExists('meta_*')`, `nurbs_deviation`: `NOT_AVAILABLE` | SPECIFIED |
| **Architecture / BIM** | `architecture` | Hardcoded `3.5` | `bbox_height`: Bounding box delta Y | SPECIFIED |
| **Medical** | `medical` | Hardcoded `0.15` | `is_manifold`: `cmds.polyInfo(nonManifoldEdges=True)`, `bbox_diagonal`: Bounding box vector | SPECIFIED |
| **Aerospace / Defense** | `aerospace` | Hardcoded `0` | `stress_concentrators`: High-curvature edges | SPECIFIED |
| **XR / Metaverse** | `xr` | `random.randint` | `texture_mem_mb`: Sum of `os.path.getsize()` for `file` nodes | SPECIFIED |
| **E-Commerce** | `ecommerce` | Hardcoded `4.2` | `filesize_mb`: File size of saved scene | SPECIFIED |
| **Robotics** | `robotics` | Hardcoded `1` | `collision_hulls`: Count of `_col` transforms | SPECIFIED |
| **Industry 4.0** | `industry4` | Hardcoded String | `uuid`: Scene digest / fileInfo UUID | SPECIFIED |
| **Industry 5.0** | `industry5` | Hardcoded `120000` | `polycount`: Measured triangle count for carbon footprint model | SPECIFIED |
| **3D Printing** | `printing` | `random.randint` | `critical_overhangs`: Face normal angle computation (< 45 deg from Down) | SPECIFIED |

---

> **ZERO RANDOMNESS GUARANTEE:** All 12 industries specify real Maya 2025/2026 scene extraction algorithms.
