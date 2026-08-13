import requests
import json
import os
import re

URL = "http://localhost:8008/validate/core"
CS_SDK_PATH = r"i:\QYNTARA AI\unity_plugin\Assets\Scripts\QyntaraSDK.cs"
CS_EDITOR_PATH = r"i:\QYNTARA AI\unity_plugin\Assets\Scripts\Editor\QyntaraEditorWindow.cs"

def verify_csharp_files():
    print("--- Verifying C# Scripts ---")
    
    # 1. Check SDK
    if os.path.exists(CS_SDK_PATH):
        with open(CS_SDK_PATH, 'r') as f:
            content = f.read()
            if "UnityWebRequest" in content and "MonoBehaviour" in content:
                print(f"[OK] QyntaraSDK.cs: Valid Unity Script.")
            else:
                print(f"[FAIL] QyntaraSDK.cs: Missing Unity dependencies.")
    else:
        print(f"[FAIL] QyntaraSDK.cs: File not found.")

    # 2. Check Editor Window
    if os.path.exists(CS_EDITOR_PATH):
        with open(CS_EDITOR_PATH, 'r') as f:
            content = f.read()
            if "EditorWindow" in content and "OnGUI" in content:
                print(f"[OK] QyntaraEditorWindow.cs: Valid Editor Script.")
            else:
                print(f"[FAIL] QyntaraEditorWindow.cs: Missing Editor logic.")
    else:
        print(f"[FAIL] QyntaraEditorWindow.cs: File not found.")

def simulate_unity_request():
    print("\n--- Simulating Unity Runtime Request ---")
    print(f"Target: {URL}")
    
    # Mock Metadata from typical Unity MeshFilter
    metadata = {
        "polycount": 4500,
        "name": "Unity_Hero_Prop",
        "has_uvs": True,
        "is_manifold": True
    }
    
    payload = {
        "industry": "gaming",
        "metadata": metadata
    }
    
    try:
        res = requests.post(URL, json=payload, timeout=2)
        if res.status_code == 200:
            data = res.json()
            print("[OK] API Connection Successful.")
            print(f"Response: {json.dumps(data['results'][0], indent=2)}...")
        else:
            print(f"[FAIL] API Error: {res.status_code}")
            
    except Exception as e:
        print(f"[FAIL] Connection Failed: {e}")

if __name__ == "__main__":
    verify_csharp_files()
    simulate_unity_request()
