import sys
import os
from unittest.mock import MagicMock

# --- MOCK ENVIRONMENT ---
mock_maya = MagicMock()
mock_cmds = MagicMock()
mock_om = MagicMock()
mock_omui = MagicMock()
mock_shiboken = MagicMock()

sys.modules["maya"] = mock_maya
sys.modules["maya.cmds"] = mock_cmds
sys.modules["maya.OpenMaya"] = mock_om
sys.modules["maya.OpenMayaUI"] = mock_omui
sys.modules["shiboken6"] = mock_shiboken
sys.modules["shiboken"] = mock_shiboken

mock_pyside2 = MagicMock()
mock_qtwidgets = MagicMock()
mock_qtcore = MagicMock()
mock_qtgui = MagicMock()

sys.modules["PySide2"] = mock_pyside2
sys.modules["PySide2.QtWidgets"] = mock_qtwidgets
sys.modules["PySide2.QtCore"] = mock_qtcore
sys.modules["PySide2.QtGui"] = mock_qtgui

mock_pyside2.QtWidgets = mock_qtwidgets
mock_pyside2.QtCore = mock_qtcore
mock_pyside2.QtGui = mock_qtgui

mock_cmds.scriptJob = MagicMock(return_value=123)
mock_cmds.ls = MagicMock(return_value=[])

# --- CUSTOM MOCKS ---
class MockWidget(object):
    def __init__(self, parent=None):
        # SIGNALS must be objects with .connect(), not methods
        self.clicked = MagicMock()
        self.toggled = MagicMock()
        self.returnPressed = MagicMock()
        self.currentIndexChanged = MagicMock()
        self.valueChanged = MagicMock()
        self.currentChanged = MagicMock()
        self.customContextMenuRequested = MagicMock()
        self.fixRequested = MagicMock() 

    def setObjectName(self, name): pass
    def setContextMenuPolicy(self, policy): pass
    def setStyleSheet(self, sheet): pass
    def setVisible(self, vis): pass
    def setEnabled(self, enabled): pass
    def setLayout(self, layout): pass
    def layout(self): return MagicMock()
    def setToolTip(self, tip): pass
    def setCheckable(self, check): pass
    def setChecked(self, checked): pass
    def setMinimumSize(self, w, h): pass
    def setMaximumHeight(self, h): pass
    def setMinimumHeight(self, h): pass
    def setMaximumWidth(self, w): pass
    def setMinimumWidth(self, w): pass
    def setFixedSize(self, w, h): pass
    def setFixedHeight(self, h): pass
    def setFixedWidth(self, w): pass
    def setSizePolicy(self, h, v): pass
    def setIcon(self, icon): pass
    def setIconSize(self, size): pass
    def setPlaceholderText(self, text): pass
    def setReadOnly(self, ro): pass
    def resize(self, w, h): pass
    # Common widget methods
    def blockSignals(self, b): pass
    def setAlignment(self, align): pass
    def clear(self): pass
    def setForeground(self, col, brush): pass
    def setBackground(self, col, brush): pass
    def setFont(self, col, font): pass
    def setExpanded(self, val): pass
    def addChild(self, item): pass
    def text(self, col): return ""
    def show(self): pass
    def hide(self): pass
    def update(self): pass
    def repaint(self): pass
    def setWordWrap(self, wrap): pass
    def setScaledContents(self, val): pass
    def setValue(self, val): pass
    def setRange(self, min, max): pass
    def setTickPosition(self, pos): pass
    def setTickInterval(self, interval): pass
    def setOrientation(self, orient): pass
    def addItems(self, items): pass
    def currentText(self): return "MOCK"
    def currentIndex(self): return 0
    def isChecked(self): return True
    def checkState(self): return 2 # Checked
    def setFrameShape(self, shape): pass
    def setFrameShadow(self, shadow): pass
    def setLineWidth(self, w): pass
    def setMidLineWidth(self, w): pass
    def setWidget(self, widget): pass
    def setWidgetResizable(self, val): pass
    def setHorizontalScrollBarPolicy(self, policy): pass
    def verticalScrollBar(self): return MagicMock()
    def horizontalScrollBar(self): return MagicMock()
    def setCurrentIndex(self, idx): pass
    def count(self): return 0
    def itemText(self, idx): return ""
    def setCurrentText(self, text): pass
    def setCurrentIndex(self, idx): pass
    def setPlaceholderText(self, text): pass
    def setReadOnly(self, ro): pass
    def resize(self, w, h): pass
    def clear(self): pass

class MockQMainWindow(MockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
    def setWindowFlags(self, flags): pass
    def setWindowTitle(self, title): pass
    def setCentralWidget(self, widget): pass

class MockTabWidget(MockWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tabs = []
    def addTab(self, widget, label):
        self._tabs.append(label)
    def count(self):
        return len(self._tabs)
    def tabText(self, index):
        if 0 <= index < len(self._tabs):
            return self._tabs[index]
        return ""
    def setDocumentMode(self, mode): pass

class MockLayout(object):
    def __init__(self, parent=None): 
        self._items = []
    def setContentsMargins(self, l, t, r, b): pass
    def setSpacing(self, s): pass
    def addWidget(self, w, stretch=0): 
        self._items.append(w)
    def addLayout(self, l): 
        self._items.append(l)
    def addStretch(self): pass
    def setAlignment(self, align): pass
    def count(self): 
        return len(self._items)
    def takeAt(self, idx):
        if 0 <= idx < len(self._items):
            return self._items.pop(idx)
        return None

mock_qtwidgets.QWidget = MockWidget
mock_qtwidgets.QMainWindow = MockQMainWindow
mock_qtwidgets.QFrame = MockWidget
mock_qtwidgets.QTabWidget = MockTabWidget

# Factories
mock_qtwidgets.QScrollArea = type("QScrollArea", (MockWidget,), {"setWidgetResizable": MagicMock(), "setFrameShape": MagicMock(), "setWidget": MagicMock(), "setHorizontalScrollBarPolicy": MagicMock(), "verticalScrollBar": MagicMock()})

# Add QFrame Enums to the underlying class or specific mock if needed
# Since QtWidgets.QFrame = MockWidget, we add them to MockWidget class
MockWidget.NoFrame = 0
MockWidget.Box = 1
MockWidget.Panel = 2
MockWidget.StyledPanel = 6
MockWidget.HLine = 4
MockWidget.VLine = 5
MockWidget.Sunken = 48
MockWidget.Plain = 16
MockWidget.Raised = 32

mock_qtwidgets.QLabel = type("QLabel", (MockWidget,), {"setText": MagicMock(), "setAlignment": MagicMock(), "setPixmap": MagicMock(), "setMinimumWidth": MagicMock()})
mock_qtwidgets.QPushButton = type("QPushButton", (MockWidget,), {})
mock_qtwidgets.QCheckBox = type("QCheckBox", (MockWidget,), {"isChecked": MagicMock(return_value=True)})
mock_qtwidgets.QComboBox = type("QComboBox", (MockWidget,), {"addItem": MagicMock(), "addItems": MagicMock(), "currentText": MagicMock(return_value="Game Engine"), "currentIndex": MagicMock(return_value=0)})
mock_qtwidgets.QTextEdit = type("QTextEdit", (MockWidget,), {"append": MagicMock(), "verticalScrollBar": MagicMock()})
mock_qtwidgets.QLineEdit = type("QLineEdit", (MockWidget,), {"text": MagicMock(return_value="")})
mock_qtwidgets.QGroupBox = type("QGroupBox", (MockWidget,), {})
mock_qtwidgets.QTreeWidget = type("QTreeWidget", (MockWidget,), {"setHeaderLabels": MagicMock(), "setAlternatingRowColors": MagicMock(), "setMinimumHeight": MagicMock(), "clear": MagicMock(), "addTopLevelItem": MagicMock()})
mock_qtwidgets.QTreeWidgetItem = MockWidget # Use our class with explicit methods
mock_qtwidgets.QVBoxLayout = MockLayout
mock_qtwidgets.QHBoxLayout = MockLayout
mock_qtwidgets.QGridLayout = type("QGridLayout", (MockLayout,), {"addWidget": MagicMock()})
mock_qtwidgets.QApplication = MagicMock()
mock_qtwidgets.QApplication.instance = MagicMock(return_value=True)
mock_qtwidgets.QFileDialog = MagicMock()

mock_qtcore.Qt = MagicMock()
mock_qtcore.Qt.Window = 1
mock_qtcore.Qt.AlignCenter = 1
mock_qtwidgets.QFrame.NoFrame = 0
mock_qtcore.Qt.ScrollBarAlwaysOff = 0
mock_qtcore.Qt.ScrollBarAsNeeded = 1
mock_qtcore.Qt.Horizontal = 1
mock_qtcore.Qt.Vertical = 2

# --- RUN CHECK ---
def check_all_tabs():
    print("      QYNTARA AI: TOP LEVEL SYSTEM CHECK")
    if r"i:\QYNTARA AI" not in sys.path:
        sys.path.append(r"i:\QYNTARA AI")
    try:
        from qyntara_ai.ui.main_window import QyntaraMainWindow
        print("[System] Instantiating QyntaraMainWindow...")
        window = QyntaraMainWindow()
        
        tabs = window.tabs
        count = tabs.count()
        print(f"[UI] Total Tabs Loaded: {count}")
        
        expected_tabs = [
            "INDUSTRY 4.0", "INDUSTRY 5.0", "Validation", "Alignment", 
            "UVs", "Baking", "Export", "Scanner", "Blueprint Studio"
        ]
        all_passed = True
        for i in range(count):
            label = tabs.tabText(i)
            status = "OK"
            expected = expected_tabs[i] if i < len(expected_tabs) else "UNKNOWN"
            if label != expected:
                status = f"MISMATCH (Expected {expected})"
                all_passed = False
            print(f"  [Tab {i}] {label:<20} ... {status}")
            
        if count != len(expected_tabs):
             print(f"[WARNING] Count Mismatch! Expected {len(expected_tabs)}, got {count}")
             all_passed = False

        if all_passed:
            print("\n[SUCCESS] All Tabs & Modules Verified.")

        # Check for Voice Command
        print("\n[FEATURES] Checking Extensions...")
        if hasattr(window, "btn_mic"):
             print("  [x] Voice Command Interface ... OK")
        else:
             print("  [ ] Voice Command Interface ... MISSING")

    except Exception as e:
        print(f"\n[ERROR] Verification Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_all_tabs()
