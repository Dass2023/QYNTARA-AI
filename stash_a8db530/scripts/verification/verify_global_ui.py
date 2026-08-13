import sys
import os
import unittest
import types
from unittest.mock import MagicMock

# --- Robust Mocking System ---
def mock_package(name):
    mock = types.ModuleType(name)
    sys.modules[name] = mock
    return mock

# Mock Maya
mock_package('maya')
mock_package('maya.cmds')
mock_package('maya.mel')
mock_package('maya.OpenMaya')
mock_package('maya.api')
mock_package('maya.api.OpenMaya')
mock_package('maya.OpenMayaUI')

# Mock PySide2 / PySide6 Structure
for pkg_name in ['PySide2', 'PySide6']:
    pkg = mock_package(pkg_name)
    for sub in ['QtWidgets', 'QtCore', 'QtGui']:
        sub_mod = mock_package(f"{pkg_name}.{sub}")
        setattr(pkg, sub, sub_mod)
        # Add basic classes that UI code expects
        setattr(sub_mod, 'QWidget', MagicMock)
        setattr(sub_mod, 'QMainWindow', MagicMock)
        setattr(sub_mod, 'QFrame', MagicMock)
        setattr(sub_mod, 'QVBoxLayout', MagicMock)
        setattr(sub_mod, 'QHBoxLayout', MagicMock)
        setattr(sub_mod, 'QPushButton', MagicMock)
        setattr(sub_mod, 'QLabel', MagicMock)
        setattr(sub_mod, 'QScrollArea', MagicMock)
        setattr(sub_mod, 'QCheckBox', MagicMock)
        setattr(sub_mod, 'QTabWidget', MagicMock)
        setattr(sub_mod, 'QComboBox', MagicMock)
        setattr(sub_mod, 'QLineEdit', MagicMock)
        setattr(sub_mod, 'QGroupBox', MagicMock)
        setattr(sub_mod, 'QProgressBar', MagicMock)
        setattr(sub_mod, 'QListWidget', MagicMock)
        setattr(sub_mod, 'QTextEdit', MagicMock)
        setattr(sub_mod, 'QSlider', MagicMock)
        setattr(sub_mod, 'QSpinBox', MagicMock)
        setattr(sub_mod, 'QGraphicsView', MagicMock)
        setattr(sub_mod, 'QGraphicsScene', MagicMock)
        setattr(sub_mod, 'Signal', MagicMock)
        setattr(sub_mod, 'Qt', MagicMock)

# Mock shiboken / shiboken6
for s in ['shiboken', 'shiboken6']:
    sh = mock_package(s)
    setattr(sh, 'wrapInstance', MagicMock())

# Add Root to Path
root_dir = r"i:\QYNTARA AI"
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

class TestGlobalUIFunctions(unittest.TestCase):
    def test_all_tabs_existence(self):
        """Verify that all UI tab classes and their critical methods are defined."""
        import qyntara_ai.ui.main_window as main_window
        import qyntara_ai.ui.industry_40_tab as i40
        import qyntara_ai.ui.industry_50_tab as i50
        import qyntara_ai.ui.export_tab as export
        import qyntara_ai.ui.scanner_tab as scanner
        import qyntara_ai.ui.blueprint_tab as blueprint
        import qyntara_ai.ui.alignment_tab as alignment
        import qyntara_ai.ui.uv_tab as uv
        import qyntara_ai.ui.baking_tab as baking
        import qyntara_ai.ui.style as style

        # Check MainWindow
        from qyntara_ai.ui.main_window import QyntaraMainWindow
        methods = ['load_scene', 'run_validation', 'auto_fix', 'undo_last_fix', 'generate_visual_report']
        for m in methods:
            self.assertTrue(hasattr(QyntaraMainWindow, m), f"MainWindow lacks {m}")

        # Check Industry 4.0
        from qyntara_ai.ui.industry_40_tab import Industry40Tab
        self.assertTrue(hasattr(Industry40Tab, 'toggle_sync'))
        self.assertTrue(hasattr(Industry40Tab, 'update_telemetry'))

        # Check Industry 5.0
        from qyntara_ai.ui.industry_50_tab import Industry50Tab
        self.assertTrue(hasattr(Industry50Tab, 'evolve_design'))
        self.assertTrue(hasattr(Industry50Tab, 'apply_director_shader'))

        # Check Export
        from qyntara_ai.ui.export_tab import ExportWidget
        self.assertTrue(hasattr(ExportWidget, 'run_safe_export'))
        self.assertTrue(hasattr(ExportWidget, 'run_usd_export'))
        self.assertTrue(hasattr(ExportWidget, 'detect_vcs'))

        # Check Scanner
        from qyntara_ai.ui.scanner_tab import ScannerWidget
        self.assertTrue(hasattr(ScannerWidget, 'run_retopo'))
        self.assertTrue(hasattr(ScannerWidget, 'run_material_generation'))

        # Check Blueprint
        from qyntara_ai.ui.blueprint_tab import BlueprintWidget
        self.assertTrue(hasattr(BlueprintWidget, 'run_floorplan_build'))
        self.assertTrue(hasattr(BlueprintWidget, 'run_ai_analysis'))

        print("[OK] All UI Tab methods and imports verified (Static Analysis).")

if __name__ == "__main__":
    unittest.main()
