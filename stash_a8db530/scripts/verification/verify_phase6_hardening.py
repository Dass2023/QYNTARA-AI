import requests
import json
import time

BASE_URL = "http://localhost:8000"
API_KEY = "QYNTARA-X-777"

def test_health():
    print("Testing /health (Public)...")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        if resp.status_code == 200:
            print("[PASS] Health endpoint reachable.")
            print(f"       System Data: {resp.json()}")
        else:
            print(f"[FAIL] Health returned {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Health check failed: {e}")

def test_security():
    print("\nTesting API Security (Protected Registry)...")
    
    # Test without key
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/registry")
        if resp.status_code == 401:
            print("[PASS] Unauthorized access blocked (Expected 401).")
        else:
            print(f"[FAIL] Unauthorized access allowed or returned {resp.status_code}")
    except Exception as e:
        print(f"[ERROR] Security test failed: {e}")

    # Test with correct key
    try:
        headers = {"X-API-KEY": API_KEY}
        resp = requests.get(f"{BASE_URL}/api/v1/registry", headers=headers)
        if resp.status_code == 200:
            print("[PASS] Authorized access granted with API Key.")
        else:
            print(f"[FAIL] Authorized access failed with {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[ERROR] Security test failed: {e}")

def test_registry_write():
    print("\nTesting Registry Write (Internal Logic Check)...")
    # This simulates an internal registration - normally done via execute()
    # But we can check if it exists or create a dummy entry via a test endpoint if we added one
    # For now, let's just check the list
    try:
        headers = {"X-API-KEY": API_KEY}
        resp = requests.get(f"{BASE_URL}/api/v1/registry", headers=headers)
        if resp.status_code == 200:
            print(f"[INFO] Registry contains {len(resp.json())} assets.")
        else:
             print(f"[FAIL] Registry read failed.")
    except Exception as e:
        print(f"[ERROR] Registry test failed: {e}")

if __name__ == "__main__":
    print("=== QYNTARA PHASE 6 VERIFICATION ===\n")
    test_health()
    test_security()
    test_registry_write()
