
import requests
import json
import time

API_URL = "http://localhost:8000"

def test_uv_ecosystem():
    print("Testing Advanced AI UV Ecosystem...")
    
    # Create dummy mesh
    test_obj = "backend/data/uploads/uv_test_cube.obj"
    
    scenarios = [
        {"mode": "hard_surface", "quality": "superb", "desc": "Superb Packing (Tetris Block Align)"}
    ]
    
    for scenario in scenarios:
        print(f"\n--- Running Scenario: {scenario['desc']} ---")
        payload = {
            "meshes": [test_obj],
            "materials": [],
            "tasks": ["uv"], 
            "engineTarget": "unreal",
            "uv_settings": {
                "mode": scenario.get("mode", "auto"),
                "quality": scenario.get("quality", "standard"),
                "resolution": 1024,
                "padding": "medium"
            },
            "generative_settings": {},
            "remesh_settings": {}
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/execute", json=payload)
            response.raise_for_status()
            data = response.json()
            
            uv_out = data.get("uvOutput", {})
            eff = uv_out.get("packing_efficiency", 0.0)
            status = uv_out.get("unwrap_status", "unknown")
            
            print(f"Status: {status}")
            print(f"Efficiency: {eff}")
            print(f"Time: {time.time() - start_time:.2f}s")
            
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_uv_ecosystem()
