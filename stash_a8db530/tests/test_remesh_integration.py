import requests
import os
import json
import time

API_URL = "http://localhost:8000"
TEST_FILE = "test_input_noisy.obj"

def test_remesh_integration():
    print("--- Testing Remesh Integration (Pseudo-Client) ---")
    
    # Check File
    if not os.path.exists(TEST_FILE):
        print(f"[ERROR] Test file {TEST_FILE} not found.")
        return

    # 1. Upload
    print(f"Uploading {TEST_FILE}...")
    with open(TEST_FILE, 'rb') as f:
        files = {'file': (TEST_FILE, f, 'application/octet-stream')}
        try:
            r = requests.post(f"{API_URL}/upload", files=files)
            if r.status_code != 200:
                print(f"[FAIL] Upload failed: {r.status_code} {r.text}")
                return
            server_path = r.json().get("path")
            print(f"[PASS] Uploaded to: {server_path}")
        except Exception as e:
            print(f"[FAIL] Upload exception: {e}")
            return

    # 2. Execute Remesh
    print("Submitting Remesh Job...")
    payload = {
        "meshes": [server_path],
        "materials": [],
        "tasks": ["remesh"],
        "engineTarget": "unreal",
        "uv_settings": {},
        "remesh_settings": {"target_faces": 5000},
        "generative_settings": {
            "prompt": "test", 
            "provider": "internal",
            "quality": "draft"
        }
    }
    
    try:
        start_time = time.time()
        r = requests.post(f"{API_URL}/execute", json=payload, timeout=300)
        duration = time.time() - start_time
        
        if r.status_code == 200:
            result = r.json()
            print(f"[PASS] Job completed in {duration:.2f}s")
            
            remesh_out = result.get("remeshOutput", {})
            mesh_path = remesh_out.get("mesh_path")
            if mesh_path:
                print(f"[PASS] Result Mesh: {mesh_path}")
            else:
                print(f"[WARN] No mesh path in output: {result}")
        else:
            print(f"[FAIL] Execution failed: {r.status_code} {r.text}")
            
    except Exception as e:
        print(f"[FAIL] Execution exception: {e}")

if __name__ == "__main__":
    test_remesh_integration()
