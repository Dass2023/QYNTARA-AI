import unittest
from unittest.mock import MagicMock, patch
import os
import sys
import importlib.util

# Add project root
sys.path.insert(0, r"i:\QYNTARA AI")

# --- MOCK MAYA ENVIRONMENT BEFORE IMPORTING CLIENT ---
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()
sys.modules["universal_framework"] = MagicMock() # Mock the client dependency

# Create a Fake Base Class for Qt Widgets so we don't inherit from MagicMock
class FakeQDialog:
    def __init__(self, parent=None, *args, **kwargs): 
        print(f"DEBUG: FakeQDialog.__init__ called with parent={parent}")
    def setWindowFlags(self, flags): pass
    def resize(self, w, h): pass
    def setStyleSheet(self, style): pass
    def setWindowTitle(self, title): pass
    def closeEvent(self, event): pass

class FakeQWidget:
    def __init__(self, parent=None, *args, **kwargs): pass
    def setStyleSheet(self, style): pass
    def hide(self): pass
    def show(self): pass
    def setProperty(self, name, value): pass
    def property(self, name): return ""
    def style(self): 
        m = MagicMock()
        m.unpolish = MagicMock()
        m.polish = MagicMock()
        return m

class FakeQFrame(FakeQWidget): pass

# Mock PySide2 structure
pyside2 = MagicMock()
widgets = MagicMock()
widgets.QDialog = FakeQDialog # Inject our fake base
widgets.QWidget = FakeQWidget
widgets.QFrame = FakeQFrame
pyside2.QtWidgets = widgets # Link module attribute for import resolution
sys.modules["PySide2"] = pyside2
sys.modules["PySide2.QtWidgets"] = widgets
sys.modules["PySide2.QtCore"] = MagicMock()
sys.modules["PySide2.QtGui"] = MagicMock()

# Add Maya dir to path so client can find its siblings if needed
sys.path.insert(0, r"i:\QYNTARA AI\maya")

# --- LOAD CLIENT MODULE DIRECTLY (Bypassing package namespace issues) ---
# Because "maya" folder conflicts with "maya" mock module
try:
    spec = importlib.util.spec_from_file_location("qyntara_client", r"i:\QYNTARA AI\maya\qyntara_client.py")
    client_module = importlib.util.module_from_spec(spec)
    
    # DO NOT PATCH QDialog HERE - It overwrites our FakeQDialog!
    # Let the module import our pre-set sys.modules["PySide2.QtWidgets"]
    spec.loader.exec_module(client_module)
        
    QyntaraDockable = client_module.QyntaraDockable
    NeuralStatusPanel = client_module.NeuralStatusPanel
    
except Exception as e:
    print(f"FAILED TO LOAD CLIENT MODULE: {e}")
    # Don't raise, let verify in test fail

# Import RLHF normally (it's in qyntara_ai package which has no conflicts)
from qyntara_ai.brain.rlhf import ReinforcementLoop

class TestRLHFIntegration(unittest.TestCase):
    
    def setUp(self):
        # Create a mock client
        # Do NOT patch QDialog again here, it messes up the class we just loaded?
        # Actually patching in setUp affects NEW imports or lookups.
        # But QyntaraDockable class is already defined.
        
        # We need to mock QVBoxLayout and other widgets used inside __init__
        with patch("PySide2.QtWidgets.QVBoxLayout"), \
             patch("PySide2.QtWidgets.QHBoxLayout"), \
             patch("PySide2.QtWidgets.QLabel"), \
             patch("PySide2.QtWidgets.QPushButton"), \
             patch("PySide2.QtWidgets.QComboBox"), \
             patch("PySide2.QtWidgets.QTextEdit"), \
             patch("PySide2.QtWidgets.QLineEdit"), \
             patch("PySide2.QtWidgets.QTabWidget"), \
             patch("PySide2.QtWidgets.QProgressBar"), \
             patch("PySide2.QtWidgets.QSlider"), \
             patch("PySide2.QtWidgets.QScrollArea"), \
             patch("PySide2.QtWidgets.QTreeWidget"), \
             patch("PySide2.QtWidgets.QTreeWidgetItem"):
            
             print("DEBUG: Instantiating QyntaraDockable...")
             self.client = QyntaraDockable()
        
        # Inject real RLHF loop (using a temp log file)
        self.test_log = "tests/temp_rlhf.json"
        if os.path.exists(self.test_log): os.remove(self.test_log)
        
        self.client.rl = ReinforcementLoop(log_path=self.test_log)
        self.client.pnl_neural = MagicMock() # Mock visual panel
        
        # Mock last result
        self.client.last_result_path = "i:/data/hero_prop.obj"
        
        # Mock buttons
        self.client.btn_reject = MagicMock()
        self.client.btn_import = MagicMock()

    def tearDown(self):
        if os.path.exists(self.test_log):
            try: os.remove(self.test_log)
            except: pass

    def test_implicit_accept_on_import(self):
        print("\nTesting RLHF: Implicit ACCEPT on Import...")
        # Simulate import
        # We need to mock os.path.exists to return True for the import check
        with patch("maya.cmds.file"), patch("os.path.exists", return_value=True): 
            self.client.import_result(self.client.last_result_path)
        
        # Verify Log
        # Reload log manually
        with open(self.test_log, 'r') as f:
            log = json.load(f)
            
        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["feedback"], "ACCEPT")
        self.assertEqual(log[0]["asset_id"], "hero_prop.obj")
        print("Integration PASS: 'Import' recorded ACCEPT.")

    def test_explicit_reject_button(self):
        print("\nTesting RLHF: Explicit REJECT Button...")
        # Simulate click
        self.client.on_reject()
        
        # Verify Log
        with open(self.test_log, 'r') as f:
            log = json.load(f)

        self.assertEqual(len(log), 1)
        self.assertEqual(log[0]["feedback"], "REJECT")
        self.assertEqual(log[0]["asset_id"], "hero_prop.obj")
        
        # Verify UI Pulse
        self.client.pnl_neural.pulse_activity.assert_called_with("RLHF LOOP")
        print("Integration PASS: 'Reject' recorded REJECT + UI Pulse.")

if __name__ == '__main__':
    unittest.main()
