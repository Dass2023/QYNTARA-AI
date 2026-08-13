import os
import sys
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
import requests
import json

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from maya import install_client

class TestMayaIntegration(unittest.TestCase):
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.api_url = "http://localhost:8000"

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_installer_logic(self):
        print("\n--- Testing Installer Logic ---")
        # Mock get_maya_scripts_dir to return our test dir
        with patch('maya.install_client.get_maya_scripts_dir', return_value=self.test_dir):
            # Run install
            install_client.install()
            
            # Check if file exists
            expected_file = os.path.join(self.test_dir, "qyntara_client.py")
            if os.path.exists(expected_file):
                print(f"SUCCESS: Client script copied to {expected_file}")
            else:
                self.fail("Client script was not copied.")

    def test_backend_api_simulation(self):
        print("\n--- Testing Backend API Simulation (Client Mock) ---")
        
        # 1. Check Stats
        try:
            resp = requests.get(f"{self.api_url}/stats")
            if resp.status_code == 200:
                print("SUCCESS: Backend is reachable (/stats)")
            else:
                self.fail(f"Backend returned {resp.status_code}")
        except requests.exceptions.ConnectionError:
            self.fail("Backend is NOT running. Please start the backend first.")

        # 2. Upload File
        dummy_obj = os.path.join(self.test_dir, "test_maya.obj")
        with open(dummy_obj, "w") as f:
            f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3")
            
        print(f"Uploading {dummy_obj}...")
        try:
            files = {'file': open(dummy_obj, 'rb')}
            resp = requests.post(f"{self.api_url}/upload", files=files)
            if resp.status_code == 200:
                server_path = resp.json().get("path")
                print(f"SUCCESS: Uploaded to {server_path}")
            else:
                self.fail(f"Upload failed: {resp.text}")
        except Exception as e:
            self.fail(f"Upload exception: {e}")

        # 3. Execute Pipeline
        if server_path:
            print("Executing Pipeline...")
            payload = {
                "meshes": [server_path],
                "materials": [],
                "tasks": ["validate"], # Simple task
                "engineTarget": "unreal",
                "remesh_settings": {},
                "generative_settings": {"prompt": "test", "provider": "internal"}
            }
            
            try:
                resp = requests.post(f"{self.api_url}/execute", json=payload)
                if resp.status_code == 200:
                    result = resp.json()
                    if result.get("status") == "success":
                        print("SUCCESS: Pipeline execution successful")
                        print(f"Validation Report: {result.get('validationReport', {}).get('passed')}")
                    else:
                        self.fail(f"Pipeline returned error: {result}")
                else:
                    self.fail(f"Execute failed: {resp.status_code} - {resp.text}")
            except Exception as e:
                self.fail(f"Execute exception: {e}")

if __name__ == "__main__":
    unittest.main()
