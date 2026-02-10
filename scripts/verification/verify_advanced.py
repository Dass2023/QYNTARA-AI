import requests
import json
import os
import time

BASE_URL = "http://localhost:8000"

def test_text_to_3d():
    print("\n--- Testing Text-to-3D Generation ---")
    url = f"{BASE_URL}/execute"
    
    # Minimal payload for generative task
    payload = {
        "meshes": [],
        "materials": [],
        "tasks": ["generative"],
        "engineTarget": "unity",
        "generative_settings": {
            "prompt": "a futuristic chair",
            "provider": "internal" # or "openai" if configured, but internal should trigger local logic
        }
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            print("[PASS] Text-to-3D request successful.")
            print(f"Response Status: {data.get('status')}")
            # Check if generative output is present
            gen_out = data.get("generative3DOutput", {})
            print(f"Generative Output: {gen_out}")
        else:
            print(f"[FAIL] Text-to-3D request failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] {e}")

def test_floorplan_extrusion():
    print("\n--- Testing Floor Plan Extrusion ---")
    url = f"{BASE_URL}/extrude-floorplan"
    
    # Create a dummy image
    dummy_image_path = "test_floorplan.png"
    # Create a simple black square on white background (bytes)
    # BMP header is easier to construct manually than PNG if no PIL, but let's try to just send random bytes as "image/png" 
    # and see if backend accepts it or if we need a real image.
    # The backend uses cv2.imread, so it needs to be a valid image file.
    
    # Let's try to create a valid minimal BMP
    # 2x2 pixel white BMP
    bmp_header = b'BM\x46\x00\x00\x00\x00\x00\x00\x00\x36\x00\x00\x00\x28\x00\x00\x00\x02\x00\x00\x00\x02\x00\x00\x00\x01\x00\x18\x00\x00\x00\x00\x00\x10\x00\x00\x00\x13\x0b\x00\x00\x13\x0b\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    bmp_data = b'\xff\xff\xff\xff\xff\xff\x00\x00\xff\xff\xff\xff\xff\xff\x00\x00'
    
    with open(dummy_image_path, "wb") as f:
        f.write(bmp_header + bmp_data)
        
    files = {
        'file': ('test_floorplan.bmp', open(dummy_image_path, 'rb'), 'image/bmp')
    }
    data = {
        'height': 2.5,
        'threshold': 127,
        'pixels_per_meter': 50.0
    }
    
    try:
        response = requests.post(url, files=files, data=data)
        if response.status_code == 200:
            print("[PASS] Floor Plan Extrusion request successful.")
            print(f"Response: {response.json()}")
        else:
            print(f"[FAIL] Floor Plan Extrusion request failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)

if __name__ == "__main__":
    print("Verifying Advanced Features...")
    test_text_to_3d()
    test_floorplan_extrusion()
