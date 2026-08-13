import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- MOCK ENVIRONMENT ---
mock_maya = MagicMock()
sys.modules["maya"] = mock_maya
sys.modules["maya.cmds"] = mock_maya.cmds
sys.modules["maya.OpenMaya"] = MagicMock()

mock_qt = MagicMock()
sys.modules["PySide2"] = mock_qt
sys.modules["PySide2.QtWidgets"] = mock_qt.QtWidgets
sys.modules["PySide2.QtCore"] = mock_qt.QtCore
sys.modules["PySide2.QtGui"] = mock_qt.QtGui
sys.modules["PySide6"] = mock_qt
sys.modules["shiboken6"] = MagicMock()

# Setup simpler Mock classes to avoid MagicMock inheritance issues
class MockWidget(object):
    def __init__(self, *args, **kwargs):
        self._text = args[0] if args and isinstance(args[0], str) else ""
        self.clicked = MagicMock()
        self.toggled = MagicMock()
    def setContentsMargins(self, *args): pass
    def setSpacing(self, *args): pass
    def addWidget(self, *args, **kwargs): pass
    def addLayout(self, *args): pass
    def addStretch(self): pass
    def setObjectName(self, *args): pass
    def setStyleSheet(self, *args): pass
    def setToolTip(self, *args): pass
    def setFrameShape(self, *args): pass
    def setWidgetResizable(self, *args): pass
    def setHorizontalScrollBarPolicy(self, *args): pass
    def setWidget(self, *args): pass
    def setAlignment(self, *args): pass
    def setPlaceholderText(self, *args): pass
    def setReadOnly(self, *args): pass
    def resize(self, *args): pass
    def clear(self): pass
    def setCheckable(self, *args): pass
    def setChecked(self, *args): pass
    def text(self): return self._text
    def isChecked(self): return True
    def addButton(self, *args): pass
    def setText(self, text): self._text = text
    def setIcon(self, *args): pass
    def setIconSize(self, *args): pass

mock_qt.QtWidgets.QWidget = MockWidget
mock_qt.QtWidgets.QPushButton = MockWidget
mock_qt.QtWidgets.QGroupBox = MockWidget
mock_qt.QtWidgets.QVBoxLayout = MockWidget
mock_qt.QtWidgets.QHBoxLayout = MockWidget
mock_qt.QtWidgets.QGridLayout = MockWidget
mock_qt.QtWidgets.QScrollArea = MockWidget
mock_qt.QtWidgets.QLabel = MockWidget
mock_qt.QtWidgets.QFileDialog = MagicMock()
mock_qt.QtWidgets.QCheckBox = MockWidget
mock_qt.QtWidgets.QRadioButton = MockWidget
mock_qt.QtWidgets.QButtonGroup = MockWidget
mock_qt.QtCore.Qt.ScrollBarAlwaysOff = 0
mock_qt.QtWidgets.QFrame.NoFrame = 0

class TestGltfIOIsolated(unittest.TestCase):
    
    def setUp(self):
        if r"i:\QYNTARA AI" not in sys.path:
            sys.path.append(r"i:\QYNTARA AI")
        
        # Load scripts
        import scripts.maya.export_web_gltf as export_script
        import scripts.maya.import_web_gltf as import_script
        import importlib
        importlib.reload(export_script)
        importlib.reload(import_script)
        self.export_script = export_script
        self.import_script = import_script

    @patch("scripts.maya.export_web_gltf.cmds")
    @patch("scripts.maya.export_web_gltf.os")
    def test_export_logic(self, mock_os, mock_cmds):
        """Verify GLB export logic."""
        mock_cmds.ls.return_value = ["pCube1"]
        mock_cmds.pluginInfo.return_value = False
        mock_cmds.file.return_value = ["GLTF Export"]
        mock_os.path.exists.return_value = True
        mock_os.path.dirname.return_value = "C:/temp"
        
        result = self.export_script.export_glb("C:/temp/test.glb")
        self.assertTrue(result)
        mock_cmds.file.assert_any_call("C:/temp/test.glb", force=True, options="v=0;", typ="GLTF Export", pr=True, es=True)

    @patch("scripts.maya.import_web_gltf.cmds")
    @patch("scripts.maya.import_web_gltf.os")
    def test_import_logic(self, mock_os, mock_cmds):
        """Verify GLB import logic."""
        # File exists for import
        mock_os.path.exists.return_value = True
        
        # Translator discovery
        mock_cmds.file.return_value = ["GLTF Export"]
        mock_cmds.pluginInfo.return_value = True
        
        result = self.import_script.import_glb("C:/temp/test.glb")
        
        # Assertions
        self.assertTrue(result)
        # Verify right translator used via cmds.file with i=True
        mock_cmds.file.assert_any_call("C:/temp/test.glb", i=True, typ="GLTF Export", pr=True, options="v=0;")

    def test_ui_integration(self):
        """Verify UI tab has both export and import buttons with correct labels."""
        from qyntara_ai.ui.export_tab import ExportWidget
        widget = ExportWidget()
        
        self.assertTrue(hasattr(widget, "btn_glb"), "Export GLB button missing")
        self.assertTrue(hasattr(widget, "btn_import_glb"), "Import GLB button missing")
        self.assertEqual(widget.btn_import_glb.text(), "IMPORT GLB/GLTF")

if __name__ == "__main__":
    unittest.main()
