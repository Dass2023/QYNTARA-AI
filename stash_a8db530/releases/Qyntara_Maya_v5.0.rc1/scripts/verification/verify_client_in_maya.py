
import maya.cmds as cmds
import qyntara_client
import functools
import json
from unittest.mock import MagicMock, patch
import urllib.request

print("--- STARTING QYNTARA VERIFICATION ---")

# 1. Create Dummy Object
if not cmds.objExists("test_cube"):
    cmds.polyCube(n="test_cube")
cmds.select("test_cube")

# 2. Instantiate Client (Headless-ish)
# We need to bypass QMainWindow show() if we don't want the UI popping up, 
# but for verifying logic, letting it init is fine.
try:
    client = qyntara_client.QyntaraDockable()
    # Force Init UI to ensure widgets exist (normally called by __init__)
    # Client has:
    # self.chk_reproj = ...
    # self.chk_neural = ...
    
    # 3. SET SETTINGS
    # We manually set the widget states
    print("Setting UI Widgets...")
    client.face_slider.setValue(9999)
    client.chk_reproj.setChecked(True)
    client.chk_curve.setChecked(True)
    client.chk_neural.setChecked(True)
    client.prompt_input.setText("Verification Prompt")
    
    # 4. MOCK NETWORK
    # We want to catch the payload, not actually send it (since backend might process it, but we want to inspect payload).
    # We'll monkey-patch `urllib.request.urlopen`
    
    original_urlopen = urllib.request.urlopen
    
    class MockResponse:
        status = 200
        def read(self): return b'{"status": "success"}'
        def __enter__(self): return self
        def __exit__(self, *args): pass

    def mock_urlopen_handler(req, data=None, timeout=None):
        print("\n>>> CAUGHT REQUEST <<<")
        print(f"URL: {req.full_url}")
        
        if data:
            payload = json.loads(data.decode('utf-8'))
            print("PAYLOAD:")
            print(json.dumps(payload, indent=2))
            
            # ASSERTIONS
            if payload['remesh_settings']['target_faces'] == 9999:
                print("✅ Face Count Matches")
            else:
                print("❌ Face Count Mismatch")
                
            if payload['remesh_settings']['auto_reproject'] == True:
                print("✅ Auto-Reproject Matches")
            else:
                print("❌ Auto-Reproject Mismatch")
                
            if payload['export_settings']['neural_compression'] == True:
                print("✅ Neural Compression Matches")
            else:
                print("❌ Neural Mismatch")

        return MockResponse()

    # Apply Patch
    urllib.request.urlopen = mock_urlopen_handler
    
    # 5. RUN JOB
    print("Submitting Job...")
    client.submit_job(tasks=["remesh"])
    
    # Restore
    urllib.request.urlopen = original_urlopen
    print("--- VERIFICATION COMPLETE ---")

except Exception as e:
    print(f"❌ TEST FAILED: {e}")
    import traceback
    traceback.print_exc()
