import requests
import time
import json
import sys

url = "http://localhost:8000/execute"
payload = {
    "meshes": [],
    "materials": [],
    "tasks": ["generative"],
    "generative_settings": {
        "mode": "text_to_3d",
        "prompt": "a futuristic chair",
        "provider": "internal"
    }
}

print(f"Sending request to {url}...")
print("This may take a minute or two (loading model + generation)...")
start_time = time.time()
try:
    response = requests.post(url, json=payload, timeout=600) # 10 min timeout
    response.raise_for_status()
    duration = time.time() - start_time
    print(f"Success! Generation took {duration:.2f} seconds.")
    data = response.json()
    print("Response Keys:", data.keys())
    if "generative3DOutput" in data:
        print("Generative Output:", data["generative3DOutput"])
    else:
        print("WARNING: 'generative3DOutput' missing from response.")
except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)
