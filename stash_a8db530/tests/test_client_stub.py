
import sys
import unittest
from unittest.mock import MagicMock, patch

# --- STUB ENVIRONMENT BEFORE IMPORTS ---

# 1. Stub Maya
# We must mock maya RECURSIVELY but NOT the top 'maya' if we want to treat it as a namespace 
# OR we just mock the submodules qyntara_client needs.
# However, if we are inside 'maya' directory, 'qyntara_client' is a top level module relative to sys.path.

# Option A: Mock only what's needed
mock_cmds = MagicMock()
sys.modules['maya.cmds'] = mock_cmds

mock_om2 = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = mock_om2

# IMPORTANT: We need 'maya' to be a module so 'import maya.cmds' works?
# Actually if we put 'maya.cmds' in sys.modules, python is usually happy.
# But 'import maya' might be called?
import types
sys.modules['maya'] = types.ModuleType('maya')
sys.modules['maya'].cmds = mock_cmds
sys.modules['maya'].api = sys.modules['maya.api']

# For global usage in test
mock_maya = mock_cmds 

# 2. Stub Qt (Crucial: Define QMainWindow so inheritance works)
mock_qt = MagicMock()
sys.modules['PySide2'] = mock_qt
sys.modules['PySide2.QtCore'] = mock_qt
sys.modules['PySide2.QtGui'] = mock_qt
sys.modules['PySide2.QtWidgets'] = mock_qt

# We need QMainWindow to be a class we can inherit from
class MockWindow:
    def __init__(self, *args, **kwargs): pass
    def setCentralWidget(self, *args): pass
    def addDockWidget(self, *args): pass
    def tabifyDockWidget(self, *args): pass
    def resize(self, *args): pass
    def show(self): pass
    def setWindowFlags(self, *args): pass
    def setStyleSheet(self, *args): pass
    def setWindowTitle(self, *args): pass
    def objectName(self): return ""
    def setObjectName(self, *args): pass
    def close(self): pass

mock_qt.QMainWindow = MockWindow
mock_qt.QWidget = MockWindow
mock_qt.QDialog = MockWindow
mock_qt.QFrame = MockWindow
mock_qt.QTabWidget = MockWindow
mock_qt.QSplitter = MockWindow
mock_qt.QTreeWidget = MockWindow
mock_qt.QTreeWidgetItem = MagicMock # This is a class
mock_qt.QLabel = MockWindow
mock_qt.QPushButton = MockWindow
mock_qt.QLineEdit = MockWindow
mock_qt.QTextEdit = MockWindow
mock_qt.QComboBox = MockWindow
mock_qt.QCheckBox = MockWindow
mock_qt.QSlider = MockWindow
mock_qt.QVBoxLayout = MockWindow
mock_qt.QHBoxLayout = MockWindow
mock_qt.QGridLayout = MockWindow
mock_qt.QFormLayout = MockWindow
mock_qt.QGroupBox = MockWindow

# 3. Stub other modules
sys.modules['master_prompt'] = MagicMock()
sys.modules['agent_logic'] = MagicMock()
sys.modules['material_framework'] = MagicMock()
sys.modules['universal_framework'] = MagicMock()

# --- IMPORT TARGET ---
import os
# Add the directory containing qyntara_client.py
sys.path.append(os.path.join(os.getcwd(), 'maya'))

# Import directly
import qyntara_client

class TestClientLogic(unittest.TestCase):
    
    @patch('urllib.request.urlopen')
    def test_submit_job_correctness(self, mock_urlopen):
        print("\n>>> TEST STARTED")
        # 1. Instantiate (No patch on init_ui to see what happens)
        try:
            client = qyntara_client.QyntaraDockable()
            print(f">>> Client Instantiated: {type(client)}")
        except Exception as e:
            print(f">>> Instantiation Failed: {e}")
            raise

        # 2. Setup Data State
        client.uv_settings = {"mode": "auto"}
        
        # 3. Setup Mock Widgets
        # We need to ensure we are mocking the widgets on the instance
        client.face_slider = MagicMock()
        client.face_slider.value.return_value = 12345
        
        client.prompt_input = MagicMock()
        client.prompt_input.toPlainText.return_value = "A futuristic city"
        
        client.chk_reproj = MagicMock()
        client.chk_reproj.isChecked.return_value = True 
        
        client.chk_curve = MagicMock()
        client.chk_curve.isChecked.return_value = False 
        
        client.chk_neural = MagicMock()
        client.chk_neural.isChecked.return_value = True 

        # IMPORTANT: Mock set_status so we can see errors
        client.set_status = MagicMock()
        def side_effect_status(msg, state):
            print(f"STATUS: {msg} [{state}]")
        client.set_status.side_effect = side_effect_status

        client.show_message = MagicMock()
        
        # 4. Setup Global Mocks
        mock_maya.ls.return_value = ['pCube1'] 
        mock_maya.pluginInfo.return_value = True 
        
        # Bypass upload 
        client.upload_file = MagicMock(return_value="server_path.obj")
        
        # 5. Mock Network
        mock_resp = MagicMock()
        mock_resp.status = 200
        mock_resp.read.return_value = b'{}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp
        
        # 6. RUN
        print(">>> Calling submit_job...")
        client.submit_job(tasks=["remesh"])
        print(">>> submit_job returned.")
        
        # 7. VERIFY
        if not mock_urlopen.called:
            print(">>> Mock URLOpen NOT called.")
            self.fail("Network call not made.")
            
        # Inspect Payload
        args, _ = mock_urlopen.call_args
        import json
        payload = json.loads(args[1])
        
        print("\n--- GENERATED PAYLOAD ---")
        print(json.dumps(payload, indent=2))
        
        self.assertEqual(payload['remesh_settings']['target_faces'], 12345)
        self.assertEqual(payload['remesh_settings']['auto_reproject'], True)
        self.assertEqual(payload['remesh_settings']['use_curvature'], False)
        self.assertEqual(payload['export_settings']['neural_compression'], True)
        self.assertEqual(payload['generative_settings']['prompt'], "A futuristic city")
        
        print("✅ LOGIC VERIFIED")

if __name__ == "__main__":
    unittest.main()
