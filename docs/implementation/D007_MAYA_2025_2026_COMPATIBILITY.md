# QYNTARA NEXUS — D-007 MAYA 2025 / MAYA 2026 COMPATIBILITY REPORT

**Feature:** Maya 2025 & Maya 2026 Real Scene Extraction Parity  
**Status:** 🔍 **READ-ONLY AUDIT COMPLETE**

---

## MAYA API COMPATIBILITY TABLE

| Measurement Subsystem | Target Maya 2025 API | Target Maya 2026 API | Parity Status | Notes |
|-----------------------|----------------------|----------------------|---------------|-------|
| **Poly / Mesh Statistics** | `maya.cmds.polyEvaluate()` | `maya.cmds.polyEvaluate()` | 100% Identical | Returns `triangle`, `vertex`, `face`, `edge` counts |
| **Bounding Box** | `maya.cmds.exactWorldBoundingBox()` | `maya.cmds.exactWorldBoundingBox()` | 100% Identical | World space bounding box `[xmin, ymin, zmin, xmax, ymax, zmax]` |
| **Manifold / Topology** | `maya.cmds.polyInfo()` | `maya.cmds.polyInfo()` | 100% Identical | Flags non-manifold edges/vertices |
| **File / Scene Identity** | `maya.cmds.file(q=True, sn=True)` | `maya.cmds.file(q=True, sn=True)` | 100% Identical | Returns active scene file path |
| **Texture Nodes** | `maya.cmds.ls(type="file")` | `maya.cmds.ls(type="file")` | 100% Identical | Enumerates file texture nodes |
| **DAG Hierarchy** | `maya.cmds.ls(dag=True)` | `maya.cmds.ls(dag=True)` | 100% Identical | Traverses scene graph nodes |

---

> **MAYA 2025 & 2026 PARITY:** All scene extraction APIs rely on core `maya.cmds` supported natively in both Maya 2025 (Python 3.11) and Maya 2026 (Python 3.11/3.14). Zero version-specific breaking changes.
