import requests
import json

url = "http://localhost:8000/execute"
headers = {
    "Content-Type": "application/json",
    "Origin": "http://localhost:3000"
}
payload = {
    "meshes": ["backend/data/sample_cube.obj"],
    "tasks": ["validation"],
    "materials": [],
    "generative_settings": {
        "prompt": "test",
        "provider": "internal"
    },
    "remesh_settings": {},
    "engineTarget": "unreal"
}

try:
    print(f"Sending POST to {url}...")
    response = requests.post(url, json=payload, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print("Headers:")
    for k, v in response.headers.items():
        print(f"  {k}: {v}")
        
    print("\nResponse Body:")
    print(response.text[:500]) # Print first 500 chars
    
except Exception as e:
    print(f"Request failed: {e}")
