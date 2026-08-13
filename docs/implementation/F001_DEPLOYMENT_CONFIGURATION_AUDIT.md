# QYNTARA NEXUS — F-001 DEPLOYMENT CONFIGURATION READ-ONLY AUDIT REPORT

**Item:** F-001 — Production API Endpoint Configuration  
**Auditor:** Antigravity AI (Gemini 3.6 Flash)  
**Status:** 🟡 **READ-ONLY AUDIT COMPLETE (F-001 = P2 DEPLOYMENT CONFIGURATION REQUIRED)**

---

## 1. API URL RESOLUTION CHAIN ANALYSIS

### Current Client Resolution Flow:
```
System / Shell Environment Variable (QYNTARA_API_URL)
                       ↓ (If defined)
     `maya/qyntara_client.py` Line 59:
     API_URL = os.environ.get("QYNTARA_API_URL", "http://localhost:8000")
                       ↓
     `QyntaraDockable.__init__()` Line 1860:
     self.api_client = NexusAPIClient(base_url=API_URL)
                       ↓
     `NexusAPIClient.__init__()`:
     self.base_url = base_url.rstrip('/')
```

### Key Architectural Behaviors:
1. **Environment-Variable Override:** If `QYNTARA_API_URL` is set in the host environment (e.g. `set QYNTARA_API_URL=https://api.qyntara.ai`), the client automatically connects to the specified HTTPS endpoint.
2. **Development / Offline Fallback:** If `QYNTARA_API_URL` is not set, `API_URL` defaults to `http://localhost:8000` for local development, test automation, and offline evaluation.
3. **Trailing Slash Normalization:** `NexusAPIClient` applies `.rstrip('/')` to prevent invalid double-slash paths (e.g., `https://api.qyntara.ai//login`).
4. **HTTPS Transport Readiness:** `urllib.request` natively supports both `http://` and `https://` schemes without requiring extra third-party transport layers.

---

## 2. PRODUCTION DEPLOYMENT & INSTALLER BEHAVIOR

- **Installer Integration:** `create_installer.py` copies `qyntara_client.py` into the Maya scripts directory (`%USERPROFILE%\Documents\maya\scripts\`).
- **Zero Secrets / Zero Hardcoded Domains:** The installer package contains zero hardcoded API keys, bearer tokens, or speculative production domains.
- **Operator Instruction Requirement:** Production deployment manuals must instruct system administrators to define `QYNTARA_API_URL` in standard Maya launch environments (e.g., `Maya.env` or pipeline environment wrappers).

---

## 3. RECOMMENDED MINIMUM REMEDIATION SPECIFICATION

To ensure 100% defense-in-depth across direct `NexusAPIClient` instantiations in standalone scripts or tests:

In `maya/nexus_api_client.py` Line 44:
```python
def __init__(self, base_url=None):
    if base_url is None:
        base_url = os.environ.get("QYNTARA_API_URL", "http://localhost:8000")
    self.base_url = base_url.rstrip('/')
    self.token = None
```

- **Target Files:** `maya/nexus_api_client.py`
- **Impact on Invariants:** Zero changes to D-001..D-014 contracts, industry mapping, backend validators, or async worker loops.

---

## 4. AUDIT CLASSIFICATION & FINAL STATUS

- **Can F-001 be CLOSED now?** No. Because no authoritative production HTTPS domain (e.g., `https://api.qyntara.ai`) has been supplied by the project owner or cloud deployment team, guessing or inventing a fake domain is strictly forbidden.
- **Final Classification:** **P2 DEPLOYMENT CONFIGURATION REQUIRED** (Non-blocking P2 configuration item for cloud operator setup).

---

> **NO CODE WAS MODIFIED DURING THIS READ-ONLY FORENSIC AUDIT.**
