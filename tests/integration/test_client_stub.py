import sys
import unittest
from unittest.mock import MagicMock, patch

# --- STUB ENVIRONMENT BEFORE IMPORTS ---
mock_cmds = MagicMock()
mock_om2 = MagicMock()
import types
mock_maya = mock_cmds 

mock_qt = MagicMock()
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

sys.modules['master_prompt'] = MagicMock()
sys.modules['agent_logic'] = MagicMock()
sys.modules['material_framework'] = MagicMock()
sys.modules['universal_framework'] = MagicMock()

import os
sys.path.append(os.path.join(os.getcwd(), 'maya'))

import qyntara_client

class TestClientLogic(unittest.TestCase):
    
    @patch('urllib.request.urlopen')
    def test_submit_job_correctness(self, mock_urlopen):
        print("\n>>> TEST STARTED")
        try:
            client = qyntara_client.QyntaraDockable()
            print(f">>> Client Instantiated: {type(client)}")
        except Exception as e:
            print(f">>> Instantiation Failed: {e}")
            raise

        client.uv_settings = {"mode": "auto"}
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

        client.set_status = MagicMock()
        def side_effect_status(msg, state):
            print(f"STATUS: {msg} [{state}]")
        client.set_status.side_effect = side_effect_status

        client.show_message = MagicMock()
        mock_maya.ls.return_value = ['pCube1'] 
        mock_maya.pluginInfo.return_value = True 
        
        client.api_client.upload_multipart = MagicMock(return_value="server_path.obj")
        
        # 5. RUN
        print(">>> Calling submit_job...")
        client.job_orchestrator.submit = MagicMock()
        client.submit_job(tasks=["remesh"])
        print(">>> submit_job returned.")
        
        # 6. VERIFY
        if not client.job_orchestrator.submit.called:
            print(">>> Orchestrator submit NOT called.")
            self.fail("Orchestrator submit not made.")
            
        # Inspect Payload
        args, kwargs = client.job_orchestrator.submit.call_args
        payload = args[0]
        
        self.assertEqual(payload["tasks"], ["remesh"])
        self.assertEqual(payload["engineTarget"], "unreal")
        self.assertTrue(payload["export_settings"]["neural_compression"])
        self.assertEqual(payload["remesh_settings"]["target_faces"], 12345)
        self.assertEqual(payload["generative_settings"]["prompt"], "A futuristic city")
        self.assertEqual(payload['export_settings']['neural_compression'], True)
        self.assertEqual(payload['generative_settings']['prompt'], "A futuristic city")
        
        print("LOGIC VERIFIED")

if __name__ == "__main__":
    unittest.main()
