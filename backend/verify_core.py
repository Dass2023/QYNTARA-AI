import requests
import json

URL = "http://localhost:8006/validate/core"

def test_gaming_validator():
    print("Testing Gaming Validator (Unified Core)...")
    
    # 1. Test Passing Case
    payload_pass = {
        "industry": "gaming",
        "metadata": {
            "polycount": 50000,
            "has_lods": True,
            "drawcalls": 2
        }
    }
    
    try:
        res = requests.post(URL, json=payload_pass)
        print(f"PASS Payload Response: {res.status_code}")
        print(json.dumps(res.json(), indent=2))
        assert res.status_code == 200
        assert res.json()["status"] == "success"
    except Exception as e:
        print(f"FAILED (Connection): {e}")

    # 2. Test Warning Case (High Poly)
    payload_warn = {
        "industry": "gaming",
        "metadata": {
            "polycount": 150000,  # > 100k trigger
            "has_lods": True
        }
    }
    
    try:
        res = requests.post(URL, json=payload_warn)
        print(f"\nWARNING Payload Response: {res.status_code}")
        data = res.json()
        print(json.dumps(data, indent=2))
        
        # Check for specific warning
        results = data["results"]
        frame_time_check = next(r for r in results if r["check_name"] == "GPU Frame-Time")
        assert frame_time_check["status"] == "WARNING"
        print(">> GPU Frame-Time Prediction correctly triggered WARNING.")

    except Exception as e:
        print(f"FAILED (Logic): {e}")

def test_medical_validator():
    print("\nTesting Medical Validator (Unified Core)...")
    
    # 1. Test Warning Case (Non-Watertight)
    payload_warn = {
        "industry": "medical",
        "metadata": {
            "is_manifold": False,
            "bbox_diagonal": 0.15 # 15cm
        }
    }
    
    try:
        res = requests.post(URL, json=payload_warn)
        print(f"WARNING Payload Response: {res.status_code}")
        data = res.json()
        
        results = data["results"]
        watertight_check = next(r for r in results if r["check_name"] == "Watertight Integrity")
        assert watertight_check["status"] == "FAIL"
        print(">> Watertight Check correctly triggered FAIL.")
        
    except Exception as e:
        print(f"FAILED (Medical Logic): {e}")

def test_aerospace_validator():
    print("\nTesting Aerospace Validator (Unified Core)...")
    
    # 1. Test Fail Case (Fatigue Risk)
    payload_risk = {
        "industry": "aerospace",
        "metadata": {
            "stress_concentrators": 3
        }
    }
    
    try:
        res = requests.post(URL, json=payload_risk)
        print(f"RISK Payload Response: {res.status_code}")
        data = res.json()
        
        results = data["results"]
        fatigue_check = next(r for r in results if r["check_name"] == "Fatigue Risk Analysis")
        assert fatigue_check["status"] == "FAIL"
        print(">> Fatigue Risk Check correctly triggered FAIL.")
        
    except Exception as e:
        print(f"FAILED (Aerospace Logic): {e}")

def test_gaming_future_check():
    print("\nTesting Gaming Future Check (Shader Complexity)...")
    payload = {
        "industry": "gaming",
        "metadata": {
            "shader_instructions": 450, # High complexity
            "polycount": 10000
        }
    }
    try:
        res = requests.post(URL, json=payload)
        data = res.json()
        print("DEBUG RESPONSE:", json.dumps(data, indent=2))
        results = data["results"]
        shader_check = next(r for r in results if r["check_name"] == "Shader Complexity Heatmap")
        assert shader_check["status"] == "WARNING"
        print(">> Shader Complexity correctly triggered WARNING.")
    except Exception as e:
        print(f"FAILED (Gaming Future): {e}")

def test_omniverse_validator():
    print("\nTesting Omniverse Validator (Unified Core)...")
    payload = {
        "industry": "omniverse",
        "metadata": {
            "meters_per_unit": 0.01,
            "up_axis": "Y", # Should Trigger Warning
            "usd_kind": "component",
            "nucleus_connected": True
        }
    }
    try:
        res = requests.post(URL, json=payload)
        data = res.json()
        results = data["results"]
        axis_check = next(r for r in results if r["check_name"] == "Up-Axis Alignment")
        assert axis_check["status"] == "WARNING"
        print(">> Up-Axis Check correctly triggered WARNING (Y-Up vs Z-Up).")
    except Exception as e:
        print(f"FAILED (Omniverse Logic): {e}")

if __name__ == "__main__":
    test_gaming_validator()
    test_medical_validator()
    test_aerospace_validator()
    test_gaming_future_check()
    test_omniverse_validator()
