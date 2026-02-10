
import urllib.request
import json
import time

BASE_URL = "http://localhost:8000"

def test_endpoint(name, endpoint, payload):
    print(f"Testing {name} ({endpoint})...")
    try:
        req = urllib.request.Request(f"{BASE_URL}{endpoint}")
        req.add_header('Content-Type', 'application/json')
        data = json.dumps(payload).encode('utf-8')
        
        start = time.time()
        with urllib.request.urlopen(req, data=data) as response:
            code = response.getcode()
            body = response.read().decode('utf-8')
            duration = (time.time() - start) * 1000
            
            if code == 200:
                print(f"[SUCCESS] ({duration:.1f}ms): {body[:100]}...")
                return True
            else:
                print(f"[FAILED] Status {code}")
                return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def main():
    print("--- QYNTARA AI BACKEND VERIFICATION (PHASE 3) ---")
    
    # 1. Test Prediction
    test_endpoint("AI Prediction", "/ai/predict", {
        "polycount": 120000, 
        "has_ngons": True
    })
    
    # 2. Test Physics
    test_endpoint("Physics Inference", "/ai/physics", {
        "material_name": "Polished Gold"
    })
    
    # 3. Test SeamGPT (Needs a valid path, we'll send a dummy one, logic is mocked anyway)
    # The mocked logic simulates analyzing formatting, but backend just reads the string
    test_endpoint("SeamGPT", "/ai/seam-gpt", {
        "mesh_path": "backend/data/test_cube.obj"
    })
    
    print("--- Verification Complete ---")

if __name__ == "__main__":
    main()
