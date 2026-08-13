import importlib.util
from unittest.mock import MagicMock
import sys

# Mock Environment
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()
sys.modules["universal_framework"] = MagicMock()

# Mock PySide2
class FakeQDialog: pass
class FakeQWidget: pass
class FakeQFrame: pass
pyside2 = MagicMock()
widgets = MagicMock()
widgets.QDialog = FakeQDialog
widgets.QWidget = FakeQWidget
widgets.QFrame = FakeQFrame
pyside2.QtWidgets = widgets # EXPLICIT LINK
sys.modules["PySide2"] = pyside2
sys.modules["PySide2.QtWidgets"] = widgets
sys.modules["PySide2.QtCore"] = MagicMock()
sys.modules["PySide2.QtGui"] = MagicMock()

sys.path.insert(0, r"i:\QYNTARA AI\maya")

print("--- LOADING CLIENT MODULE ---")
try:
    spec = importlib.util.spec_from_file_location("qyntara_client", r"i:\QYNTARA AI\maya\qyntara_client.py")
    client_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(client_module)
    
    print(f"MODULE LOADED: {client_module}")
    
    cls = client_module.QyntaraDockable
    print(f"CLASS: {cls}")
    print(f"TYPE: {type(cls)}")
    print(f"BASES: {cls.__bases__}")
    
    inst = cls()
    print(f"INSTANCE: {inst}")
    print(f"INSTANCE TYPE: {type(inst)}")

except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    import traceback
    traceback.print_exc()
