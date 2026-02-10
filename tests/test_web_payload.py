import requests
import json

API_URL = "http://localhost:8000"

def test_web_execution():
    print("Testing Web UI Payload...")
    payload = {
        "meshes": ["mesh_01"],
        "materials": ["mat_01"],
        "tasks": ["segment", "validate", "uv", "remesh", "generative"],
        "generative_settings": {"prompt": "cyberpunk helmet"}
    }
    
    try:
        response = requests.post(f"{API_URL}/execute", json=payload)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Failed!")
            print(response.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_web_execution()
