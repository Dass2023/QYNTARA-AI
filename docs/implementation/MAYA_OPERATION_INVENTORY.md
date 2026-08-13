# Maya Operation Inventory

## Purpose
This document inventories all significant `maya.cmds` and `OpenMaya` calls executed within `qyntara_client.py` to establish safe, testable boundaries that prevent raw Maya failures from crashing the plugin, while preserving undo semantics and thread constraints.

## 1. Selection & Context Management
| Function | Maya API Used | Purpose | Thread Req | Undo Implications | Expected Failure Modes |
|---|---|---|---|---|---|
| Selection Retrieval | `cmds.ls(sl=True)` | Fetch active user selection | Main Thread | None | Maya uninitialized; Selection format unexpected. |
| Object Selection | `cmds.select(nodes)` | Set active selection in viewport | Main Thread | Maya handles automatically | Invalid/Deleted nodes; String coercion failure. |
| Constraint Mgmt | `cmds.polySelectConstraint` | Filter viewport selection (e.g., N-Gons, hard edges) | Main Thread | Maya handles automatically | Component selection error. |

**Current Exception Handling:** Barely handled; relies on Maya not throwing exceptions for `cmds.ls()`. 
**Boundary Strategy:** Wrap selection calls in a `MayaContext` boundary that returns predictable types (lists) and validates inputs before calling `cmds.select`.

## 2. Scene Modification & Geometry Processing
| Function | Maya API Used | Purpose | Thread Req | Undo Implications | Expected Failure Modes |
|---|---|---|---|---|---|
| Import/Export | `cmds.file(path, i=True)`, `cmds.file(es=True)` | Import AI results; Export temporary meshes | Main Thread | Highly impactful; Often clears undo stack | Invalid file path; Locked nodes; Corrupted OBJ. |
| Cleanup | `cmds.polyCleanupArgList` | Clean N-Gons/Manifold errors | Main Thread | Must be undoable | Zero-area face crash. |
| Hierarchy | `cmds.makeIdentity`, `cmds.delete(ch=True)`, `cmds.rename` | Prepare meshes for export/import | Main Thread | Must be undoable | Locked transforms; History deletion fails. |
| Triangulation | `cmds.polyTriangulate` | Triangulate for specific engines | Main Thread | Must be undoable | Non-polygonal geometry. |

**Current Exception Handling:** `try/except Exception: pass` frequently used or no handling.
**Boundary Strategy:** Create an `execute_in_undo_chunk()` wrapper boundary. Export/Import operations must catch `RuntimeError` and return structured `Result` objects indicating failure rather than throwing bare exceptions to PySide.

## 3. Scene Query & Evaluation
| Function | Maya API Used | Purpose | Thread Req | Undo Implications | Expected Failure Modes |
|---|---|---|---|---|---|
| Poly Evaluation | `cmds.polyEvaluate`, `cmds.polyInfo` | Count faces/UVs, find non-manifold edges | Main Thread | None | Target is not a mesh; Invalid topology. |
| Connections | `cmds.listHistory`, `cmds.listConnections`, `cmds.listRelatives` | Find parent hierarchies and shading engines | Main Thread | None | None/Null pointer exceptions. |
| Transform Query | `cmds.xform(q=True)` | Get scale/rotation for metadata | Main Thread | None | Target has no transform. |

**Current Exception Handling:** Generally safe but susceptible to `ValueError` if queried on wrong node types.
**Boundary Strategy:** Safe query wrappers that swallow `ValueError`/`RuntimeError` and return `None` or `0` for predictable UI behavior without crashing the event loop.

## 4. UI/Event Hooks (ScriptJobs)
| Function | Maya API Used | Purpose | Thread Req | Undo Implications | Expected Failure Modes |
|---|---|---|---|---|---|
| Event Binding | `cmds.scriptJob(e=["SelectionChanged"])` | Update UI based on Maya selection | Main Thread | None | Duplicate jobs; Memory leaks. |
| Event Unbinding | `cmds.scriptJob(kill=True)` | Cleanup jobs on UI close | Main Thread | None | Invalid job ID. |

**Current Exception Handling:** Basic `try/except`. 
**Boundary Strategy:** A dedicated `MayaEventSubscriber` boundary that tracks Job IDs and ensures robust cleanup.

---

## Proposed Execution Boundaries for Phase 1D
We will introduce `maya.execution_boundary.py` containing:
1. `class MayaCommandRunner`: A centralized static class or singleton boundary for `cmds` calls that wraps standard `RuntimeError` from Maya into structured `MayaExecutionError`.
2. `class UndoChunk`: A context manager ensuring `cmds.undoInfo(openChunk=True)` and `closeChunk=True` are correctly paired, even if inner code crashes.

All Phase 1D execution must remain **Synchronous** and restricted to the **Main Thread**.
