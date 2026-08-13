import sys
import os
import unittest
import types
from unittest.mock import MagicMock

# --- 1. Define Fake Base Classes ---
class FakeQDialog:
    def __init__(self, parent=None):
        pass
    def setWindowTitle(self, title): pass
    def setWindowFlags(self, flags): pass
    def resize(self, w, h): pass
    def setStyleSheet(self, sheet): pass
    def setObjectName(self, name): pass
    def show(self): pass
    def setLayout(self, layout): pass

# --- 2. Manually Mock Modules (No MagicMock for modules) ---
# This avoids MagicMock auto-creating attributes that override our classes
pyside2 = types.ModuleType('PySide2')
qtwidgets = types.ModuleType('PySide2.QtWidgets')
qtcore = types.ModuleType('PySide2.QtCore')
qtgui = types.ModuleType('PySide2.QtGui')

# Define a generic Fake Widget that accepts any method call
class FakeWidget:
    # Constants used by widgets
    Password = 1
    
    def __init__(self, *args, **kwargs): 
        self.text_value = ""
        
    def __getattr__(self, name):
        # Return a FakeWidget for any attribute access
        # This allows chaining like .clicked.connect()
        return FakeWidget()
        
    def __call__(self, *args, **kwargs):
        return FakeWidget()
        
    @staticmethod
    def processEvents():
        pass

    def text(self):
        return self.text_value
        
    def setText(self, *args):
        if args:
            self.text_value = str(args[-1])

# --- 2b. Specific Fake Classes ---
class FakeLayout(FakeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._count = 0
        
    def count(self):
        return self._count
        
    def addWidget(self, widget, *args):
        self._count += 1
        
    def insertWidget(self, index, widget):
        self._count += 1
        
    def addLayout(self, layout):
        pass

# Inject Fakes
qtwidgets.QDialog = FakeQDialog
qtwidgets.QWidget = FakeWidget
qtwidgets.QVBoxLayout = FakeLayout
qtwidgets.QHBoxLayout = FakeLayout
qtwidgets.QFormLayout = FakeLayout
qtwidgets.QGridLayout = FakeLayout

qtwidgets.QLabel = FakeWidget
qtwidgets.QFrame = FakeWidget
qtwidgets.QLineEdit = FakeWidget
qtwidgets.QPushButton = FakeWidget
qtwidgets.QCheckBox = FakeWidget
qtwidgets.QApplication = FakeWidget # Added mock
qtwidgets.QGroupBox = FakeWidget
qtwidgets.QMessageBox = FakeWidget
qtwidgets.QSizePolicy = FakeWidget
qtwidgets.QSplitter = FakeWidget
qtwidgets.QTreeWidget = FakeWidget
qtwidgets.QTreeWidgetItem = FakeWidget
qtwidgets.QComboBox = FakeWidget
qtwidgets.QTextEdit = FakeWidget
qtwidgets.QSlider = FakeWidget
qtwidgets.QScrollArea = FakeWidget
qtwidgets.QHeaderView = FakeWidget
qtwidgets.QAction = FakeWidget
qtwidgets.QMenu = FakeWidget
qtwidgets.QButtonGroup = FakeWidget
qtwidgets.QSpinBox = FakeWidget
qtwidgets.QDoubleSpinBox = FakeWidget
qtwidgets.QRadioButton = FakeWidget
qtwidgets.QListWidget = FakeWidget
qtwidgets.QListWidgetItem = FakeWidget
qtwidgets.QFileDialog = FakeWidget # For browse_image

# QtCore additions (for Stats)
class FakeQTimer(FakeWidget):
    @staticmethod
    def singleShot(msec, callback):
        # Execute immediately for test
        callback()

qtcore.QTimer = FakeQTimer

# Additional Fake for TabWidget
class FakeQTabWidget(FakeWidget):
    def __init__(self):
        self._tabs = []
    def addTab(self, widget, label):
        self._tabs.append(label)
    def insertTab(self, index, widget, label):
        self._tabs.insert(index, label)
    def count(self):
        return len(self._tabs)
    def tabText(self, index):
        return self._tabs[index]
    def currentIndex(self):
        return 0

qtwidgets.QTabWidget = FakeQTabWidget

# Constants
qtcore.Qt = MagicMock()
qtcore.Qt.AlignCenter = 1
qtcore.Qt.WindowStaysOnTopHint = 2
qtcore.Qt.PointingHandCursor = 3

class FakeQObject:
    def __init__(self, parent=None): pass

def FakeSignal(*args):
    return MagicMock()

qtcore.QObject = FakeQObject
qtcore.Signal = FakeSignal

# Link modules
pyside2.QtWidgets = qtwidgets
pyside2.QtCore = qtcore
pyside2.QtGui = qtgui

# Add QtGui mocks
qtgui.QBrush = FakeWidget
qtgui.QColor = FakeWidget
qtgui.QPixmap = FakeWidget
qtgui.QIcon = FakeWidget

# Register in sys.modules
sys.modules['PySide2'] = pyside2
sys.modules['PySide2.QtWidgets'] = qtwidgets
sys.modules['PySide2.QtCore'] = qtcore
sys.modules['PySide2.QtGui'] = qtgui

# Mock Maya modules
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
sys.modules['maya.OpenMayaUI'] = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()

# Mock Maya commands
sys.modules['maya.cmds'].confirmDialog.return_value = 'OK'
sys.modules['maya.cmds'].pluginInfo.return_value = True
sys.modules['maya.cmds'].ls.return_value = ['pCube1']
sys.modules['maya.cmds'].file.return_value = None

# --- 3. Import Client ---
sys.path.append(os.path.join(os.getcwd(), 'maya'))

try:
    import qyntara_client
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("qyntara_client", os.path.join(os.getcwd(), "maya", "qyntara_client.py"))
    qyntara_client = importlib.util.module_from_spec(spec)
    sys.modules["qyntara_client"] = qyntara_client
    spec.loader.exec_module(qyntara_client)

# --- 4. Test Class ---
class TestMayaIntegration(unittest.TestCase):
    def setUp(self):
        # Instantiate the real class
        self.ui = qyntara_client.QyntaraDockable()
        self.ui.auth_input.text_value = "QYNTARA-X-777"
        
    def test_connection(self):
        print("\nTesting Connection to Backend...")
        try:
            self.ui.login()
            if self.ui.token == "VALID":
                print("[PASS] Token is VALID.")
            else:
                self.fail(f"Token is {self.ui.token}")
        except Exception as e:
            self.fail(f"Login failed: {e}")

    def test_ui_navigation(self):
        print("\nTesting UI Navigation Logic...")
        # Now self.ui.tabs is a FakeQTabWidget
        count = self.ui.tabs.count()
        print(f"Tab Count: {count}")
        
        indices = {self.ui.tabs.tabText(i): i for i in range(count)}
        print(f"Tabs Found: {indices}")
        
        expected_tabs = [
            "GENERATE AI ASSIST",
            "QUAD REMESH", 
            "VALIDATE SCENE", 
            "UNIVERSAL UV", 
            "OPTIMIZATION & EXPORT"
        ]
        
        for tab in expected_tabs:
            if tab not in indices:
                self.fail(f"Missing expected tab: {tab}")
                
        print("[PASS] All feature tabs verified.")
        
if __name__ == '__main__':
    unittest.main()
