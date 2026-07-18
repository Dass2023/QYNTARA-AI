import requests
import sys

def check_service(name, url):
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            print(f"[OK] {name} is ONLINE ({url})")
            return True
        else:
            print(f"[FAIL] {name} returned {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] {name} is UNREACHABLE: {e}")
        return False

def verify_maya_logic():
    print("\n--- Simulating Maya Client Request ---")
    url = "http://localhost:8008/validate/core"
    
    # Mock Payload based on qyntara_client.py logic
    payload = {
        "industry": "gaming",
        "metadata": {
            "polycount": 12000,
            "has_uvs": True,
            "history_clean": False,
            "scene_scale": "meters"
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "success":
                print(f"[OK] Maya Client Logic: Validation Successful.")
                print(f"     Response: {data['results'][0]['message']}")
            else:
                print(f"[FAIL] Maya Client Logic: Validation Failed (Logic Error).")
        else:
            print(f"[FAIL] Maya Client Logic: Server returned {response.status_code}")
            print(f"     Response: {response.text}")

    except Exception as e:
        print(f"[FAIL] Maya Client Logic: Connection Error: {e}")

if __name__ == "__main__":
    print("=== QYNTARA SPATIAL INTELLIGENCE VERIFICATION ===\n")
    
    backend_ok = check_service("Backend API", "http://localhost:8008/docs")
    frontend_ok = check_service("Web Frontend", "http://localhost:3000")
    
    verify_maya_logic()
    print("\n=== VERIFICATION COMPLETE ===")
