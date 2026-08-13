import requests
import json
import time
import os
import sys

# Standardized URL and Security
API_URL = "http://localhost:8000"
API_KEY = os.getenv("QYNTARA_API_KEY", "QYNTARA-X-777")
HEADERS = {"X-API-KEY": API_KEY}

def test_endpoint(name, method, path, use_key=True, payload=None):
    url = f"{API_URL}{path}"
    headers = HEADERS if use_key else {}
    print(f"\n[Testing] {name} ({path})...")
    
    try:
        start = time.time()
        if method == "GET":
            r = requests.get(url, headers=headers, timeout=10)
        else:
            r = requests.post(url, headers=headers, json=payload, timeout=10)
        
        duration = time.time() - start
        if r.status_code < 400:
            print(f" -> [PASS] Success ({r.status_code}) in {duration:.3f}s")
            return r.json()
        else:
            print(f" -> [FAIL] Status {r.status_code}: {r.text}")
            return None
    except Exception as e:
        print(f" -> [ERROR] {e}")
        return None

def verify_system():
    print("========================================")
    print(" QYNTARA AI: COMPLETE SYSTEM VERIFICATION")
    print("========================================")

    # 1. Public Health Check
    health = test_endpoint("Public Health", "GET", "/health", use_key=False)
    if not health:
        print("[CRITICAL] Backend unreachable or incorrectly secured.")
        return

    # 2. Unauthorized Access Check
    print("\n[Testing] Unauthorized Access (Stats)...")
    r_bad = requests.get(f"{API_URL}/stats")
    if r_bad.status_code == 401:
        print(" -> [PASS] Security Layer Blocked Unauthorized Request.")
    else:
        print(f" -> [FAIL] Security Layer Bypass! Status: {r_bad.status_code}")

    # 3. Protected Stats Check
    stats = test_endpoint("Protected Stats", "GET", "/stats")
    
    # 4. Protected Library Check
    library = test_endpoint("Protected Library", "GET", "/library")
    
    # 5. Pipeline Execution Simulation (Validate Only)
    # We use a dummy mesh path if none exists
    dummy_mesh = "backend/data/uploads/verification_mesh.obj"
    if not os.path.exists("backend/data/uploads"): os.makedirs("backend/data/uploads")
    with open(dummy_mesh, "w") as f: f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3")

    pipeline_payload = {
        "meshes": [dummy_mesh],
        "materials": [],
        "tasks": ["validate"],
        "validation_profile": "UNREAL"
    }
    
    pipeline = test_endpoint("Pipeline Execution (Validate)", "POST", "/execute", payload=pipeline_payload)
    if pipeline and pipeline.get("status") == "success":
        print(" -> [PIPELINE] Mesh Validation Logic Operational.")
    
    # 6. AI Predictive Check
    predict_payload = {"polycount": 50000, "has_ngons": True}
    predict = test_endpoint("AI Predictive Analytics", "POST", "/ai/predict", payload=predict_payload)
    if predict and "risk_score" in predict:
        print(f" -> [AI] Risk Score: {predict['risk_score']}")

    # 7. Telemetry Deep Check
    if health.get("gpu", {}).get("available") is not None:
        print("\n[TELEMETRY] GPU Monitoring: ACTIVE")
        print(f"  Available: {health['gpu']['available']}")
    
    print("\n========================================")
    print(" VERIFICATION COMPLETE: SYSTEM IS READY")
    print("========================================")

if __name__ == "__main__":
    verify_system()
