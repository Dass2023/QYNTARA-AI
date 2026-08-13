# QYNTARA NEXUS VALIDATION RULE TRACEABILITY

**Status Date:** 2026-08-09
**Audit Status:** READ-ONLY EVALUATION (Pass 1 - 2)

| Rule ID | Rule Name | Category | Ruleset (JSON) | Registry (Validator) | UI (Client) | Expected Result | Actual Result | Status | Severity |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `check_ngons` | N-Gons (>4 sides) | Topology & Geo | YES | YES | YES | FAIL > 4 edges | PASS | 🟢 VERIFIED | ERROR |
| `check_triangles` | Triangles | Topology & Geo | YES | YES | YES | FAIL = 3 edges | PASS | 🟢 VERIFIED | WARNING |
| `check_poles` | Poles (>5 edges) | Topology & Geo | YES | YES | YES | FAIL > 5 edges on vtx| PASS | 🟢 VERIFIED | WARNING |
| `check_non_manifold`| Non-Manifold Geo | Topology & Geo | YES | YES | YES | FAIL on bad edges | PASS | 🟢 VERIFIED | ERROR |
| `check_lamina_faces`| Lamina Faces | Topology & Geo | YES | YES | YES | FAIL on shared faces | PASS | 🟢 VERIFIED | WARNING |
| `check_open_edges` | Open Edges (Leaks) | Topology & Geo | YES | YES | YES | FAIL on mesh borders | PASS | 🟢 VERIFIED | ERROR |
| `check_missing_bevels`| Missing Bevels | Topology & Geo | YES | YES | YES | FAIL on sharp angles | PASS | 🟢 VERIFIED | WARNING |
| `check_proximity_gaps`| Proximity Gaps | Topology & Geo | YES | YES | YES | FAIL on micro-gaps | PASS | 🟢 VERIFIED | WARNING |
| `check_scan_outliers`| LiDAR Scan Outliers | Topology & Geo | YES | YES | YES | FAIL on stray verts | PASS | 🟢 VERIFIED | ERROR |
| `check_shadow_terminator`| Shadow Terminators | Topology & Geo | YES | YES | YES | FAIL on low-poly curve | PASS | 🟢 VERIFIED | WARNING |
| `check_watertight` | Watertight Mesh | Topology & Geo | YES | YES | YES | FAIL if not closed vol | PASS | 🟢 VERIFIED | ERROR |
| `check_missing_uvs` | Missing UVs | UVs & Textures | YES | YES | YES | FAIL on 0 UVs | PASS | 🟢 VERIFIED | ERROR |
| `check_overlapping_uvs`| Overlapping UVs | UVs & Textures | YES | YES | YES | FAIL on overlap | PASS | 🟢 VERIFIED | ERROR |
| `check_history` | Construction History| Scene & XForms | YES | YES | YES | FAIL if history exists | PASS | 🟢 VERIFIED | ERROR |
| `check_transforms` | Unfrozen Transforms | Scene & XForms | YES | YES | YES | FAIL if not 0/0/0 | PASS | 🟢 VERIFIED | ERROR |
| `check_names` | Duplicate Names | Naming | YES | YES | YES | FAIL on dupes | PASS | 🟢 VERIFIED | WARNING |
| `check_skin_weights` | Skin Weights | Animation | YES | YES | YES | FAIL on unweighted | PASS | 🟢 VERIFIED | ERROR |
| `check_uv2_exists` | UV2 Exists (Baking) | Baking | YES | YES | YES | FAIL if missing UV2 | PASS | 🟢 VERIFIED | WARNING |
| `check_coinciding_geometry`| Coinciding Geometry | ORPHANED | YES | YES | NO | FAIL on intersect | N/A | 🔴 ORPHANED | ERROR |
| `check_lod_group` | LOD Groups | ORPHANED | YES | YES | NO | FAIL on missing LOD | N/A | 🔴 ORPHANED | WARNING |
| `check_light_leakage` | Light Leakage | Baking | YES | YES (Dupe)| YES | FAIL on light bounds| PASS | 🟠 DUPLICATED IN ENGINE| WARNING |

> **Note:** Several industry/game checks (`check_lod_group`, `check_strict_quads`, `check_scene_pollution`) exist in `legacy_core.validator` but are currently MISSING from the injected `qyntara_client.py` categories list.

---
## Traceability Summary
- **Rules in JSON:** 42+
- **Rules in Registry:** 35
- **Rules mapped in UI:** 26
- **Duplicate Rules:** 1 (`check_light_leakage` registered twice in validator.py)
- **Dead Code:** `check_degenerate_geometry` is registered but commented out as deprecated.
