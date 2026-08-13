# QYNTARA NEXUS — D-007 / D-013 REAL SCENE PAYLOAD FORENSIC AUDIT

**Feature:** Real Scene Telemetry & Metric Truth (Zero Randomness)  
**Defect ID:** D-007 / D-013  
**Auditor:** Antigravity AI (Gemini 3.6 Flash)  
**Status:** 🔍 **READ-ONLY AUDIT COMPLETE (READY FOR IMPLEMENTATION)**

---

## 1. RANDOMNESS FORENSIC INVENTORY

| File Path | Line | Metric / Logic | Current Value Generation | Classification | Required Remediation |
|-----------|------|----------------|--------------------------|----------------|----------------------|
| `maya/qyntara_client.py` | 1397 | Gaming (`polycount`) | `random.randint(50000, 150000)` | **ILLEGITIMATE DIAGNOSTIC RANDOMNESS** | Replace with `cmds.polyEvaluate(t=True)` |
| `maya/qyntara_client.py` | 1397 | Gaming (`shader_instructions`) | `random.randint(200, 500)` | **ILLEGITIMATE DIAGNOSTIC RANDOMNESS** | Classify as `BACKEND_COMPUTED` or `NOT_AVAILABLE` |
| `maya/qyntara_client.py` | 1399 | Medical (`bbox_diagonal`) | Hardcoded `0.15` | **ILLEGITIMATE MOCK METRIC** | Calculate via `cmds.exactWorldBoundingBox` |
| `maya/qyntara_client.py` | 1401 | Film (`poles`) | `random.choice([3, 5, 8])` | **ILLEGITIMATE DIAGNOSTIC RANDOMNESS** | Calculate via `cmds.polyInfo(nonManifoldVertices=True)` |
| `maya/qyntara_client.py` | 1403 | Automotive (`nurbs_deviation`) | Hardcoded `0.02` | **ILLEGITIMATE MOCK METRIC** | Measure via NURBS surface curvature or `NOT_AVAILABLE` |
| `maya/qyntara_client.py` | 1409 | XR / Metaverse (`texture_mem_mb`) | `random.randint(30, 80)` | **ILLEGITIMATE DIAGNOSTIC RANDOMNESS** | Calculate total file sizes of connected `file` texture nodes |
| `maya/qyntara_client.py` | 1419 | 3D Printing (`critical_overhangs`) | `random.randint(0, 3)` | **ILLEGITIMATE DIAGNOSTIC RANDOMNESS** | Measure face normals pointing below print threshold angle |
| `maya/tabs/industry_40_tab.py` | 318 | Demo Temp/RPM | `60 + random.random() * 10` | **DEMO ONLY** | Mark UI component as Simulated Demo Data |

---

## 2. PROVENANCE CLASSIFICATION RULES

- `REAL_MAYA_MEASUREMENT`: Directly measured from Maya 2025/2026 scene via `maya.cmds` or `OpenMaya`.
- `BACKEND_COMPUTED`: Derived deterministically by backend engine from geometry/file buffers.
- `PREDICTED`: Machine-learning risk or performance model estimate.
- `ESTIMATED`: Dynamic heuristic estimate (e.g., VRAM usage).
- `STATIC_RULE_RESULT`: Boolean pass/fail rule result based on fixed parameters.
- `NOT_AVAILABLE`: Metric cannot be measured honestly from current Maya scene state.

---

## 3. ANTI-FABRICATION RULE ENFORCEMENT

1. **NEVER** replace a random number with another hardcoded number.
2. If a real measurement is unavailable (e.g., unsaved scene file size), explicitly return `NOT_AVAILABLE` with human-readable reason.
3. Every payload metric passed to backend API must include explicit `provenance` metadata tag.

---

> **MANDATORY STOP:** Read-only forensic audit complete. Zero production code changes made. Awaiting human authorization to proceed.
