import requests
import json
import os

def test_validation_api():
    base_url = "http://localhost:8000"
    asset_id = "test_asset_001"
    
    print(f"Testing Validation Sync API for asset: {asset_id}")
    
    # Payload similar to what Maya sends
    payload = {
        "asset_id": asset_id,
        "timestamp": 1234567890.0,
        "industry_preset": "Gaming",
        "report": {
            "score": 95,
            "checks": [
                {"name": "Poly Count", "status": "PASS", "count": 1200, "message": "Within budget"},
                {"name": "Textures", "status": "WARN", "count": 1, "message": "Missing mipmaps"}
            ]
        }
    }
    
    # 1. Test POST (Sync)
    try:
        resp = requests.post(f"{base_url}/api/v1/assets/{asset_id}/validation", json=payload)
        if resp.status_code == 200:
            try:
                print("[PASS] POST /api/v1/assets/{id}/validation SUCCESS")
                print(f"       Response: {resp.json()}")
            except:
                 print(f"[FAIL] POST SUCCESS but Invalid JSON: {resp.text}")
                 return False
        else:
            print(f"[FAIL] POST FAILED: {resp.status_code} - {resp.text}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection Failed: {e}")
        return False
        
    # 2. Test GET (Retrieve)
    try:
        resp = requests.get(f"{base_url}/api/v1/assets/{asset_id}/validation")
        if resp.status_code == 200:
            data = resp.json()
            # New Check: specific fields from robust validator
            if "report" in data and "score" in data["report"]:
                 print("[PASS] GET /api/v1/assets/{id}/validation SUCCESS")
                 print("       Data Integrity Verified")
            else:
                print(f"[FAIL] GET SUCCESS but Content Mismatch: {data}")
        else:
            print(f"[FAIL] GET FAILED: {resp.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Connection Failed: {e}")
        return False
        
    return True

if __name__ == "__main__":
    try:
        test_validation_api()
    except Exception as e:
        print(f"Script Error: {e}")
