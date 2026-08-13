import requests
import json

def reproduce():
    print("--- Reproducing 3D Generation Error ---")
    url = "http://localhost:8000/segment-to-3d"
    
    # Mock payload based on user logs
    payload = {
        "image_path": "backend/data/uploads/image-10.jpg", # We might need to create this file first
        "click_point": [75.49, 152.37],
        "click_type": "left"
    }
    
    # Ensure dummy file exists
    import os
    os.makedirs("backend/data/uploads", exist_ok=True)
    with open("backend/data/uploads/image-10.jpg", "wb") as f:
        f.write(b"dummy image content")

    try:
        res = requests.post(url, json=payload)
        print(f"Status Code: {res.status_code}")
        print(f"Response: {res.text}")
    except Exception as e:
        print(f"Request Failed: {e}")

if __name__ == "__main__":
    reproduce()
