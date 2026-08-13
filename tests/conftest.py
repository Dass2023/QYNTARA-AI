import sys
import os
import pytest
from unittest.mock import MagicMock

# Ensure the project root is on sys.path so 'maya' is found as a package
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Also ensure maya directory is in sys.path for direct imports like 'import universal_framework'
maya_dir = os.path.join(project_dir, 'maya')
if maya_dir not in sys.path:
    sys.path.insert(0, maya_dir)

class StrictMayaCmdsMock:
    """Minimal Maya mock that fails loudly on unmocked APIs."""
    def __init__(self):
        self._mocks = {}
    
    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            return MagicMock()
        if name == "optionVar":
            def mock_optionVar(*args, **kwargs):
                return 0
            return mock_optionVar
        if name in ("pluginInfo", "loadPlugin", "window", "showWindow", "workspaceControl", "ls", "file", "polyEvaluate", "workspace", "exactWorldBoundingBox", "xform", "move", "progressWindow", "progressControl"):
            if name not in self._mocks:
                self._mocks[name] = MagicMock()
            return self._mocks[name]
        raise NotImplementedError(f"MOCK ERROR: maya.cmds.{name} is not mocked or unsupported in this test.")

class StrictOpenMayaMock:
    def __getattr__(self, name):
        if name.startswith("__") and name.endswith("__"):
            return MagicMock()
        raise NotImplementedError(f"MOCK ERROR: OpenMaya.{name} is not mocked or unsupported in this test.")

def apply_mocks():
    try:
        import maya.cmds as cmds
    except ImportError:
        import maya
        
        # 1. Mock Maya commands and api ONLY
        cmds_mock = StrictMayaCmdsMock()
        api_mock = MagicMock()
        om_mock = StrictOpenMayaMock()
        api_mock.OpenMaya = om_mock
        mel_mock = MagicMock()
        
        # Attach to the real maya package
        maya.cmds = cmds_mock
        maya.api = api_mock
        maya.mel = mel_mock
        
        sys.modules['maya.cmds'] = cmds_mock
        sys.modules['maya.api'] = api_mock
        sys.modules['maya.api.OpenMaya'] = om_mock
        sys.modules['maya.mel'] = mel_mock
        
        # 2. Mock PySide2
        class FakeMeta(type):
            def __getattr__(cls, name):
                if name.startswith('__'):
                    raise AttributeError(name)
                return MagicMock()
                
        class FakeQObject(metaclass=FakeMeta):
            def __init__(self, *args, **kwargs):
                self._mocks = {}
            def __getattr__(self, name):
                if name.startswith('__'):
                    raise AttributeError(name)
                if name not in self._mocks:
                    self._mocks[name] = MagicMock()
                return self._mocks[name]
        class FakeQWidget(FakeQObject): pass
        class FakeQDialog(FakeQWidget): pass
        class FakeQMainWindow(FakeQWidget): pass
        class FakeQApplication(metaclass=FakeMeta):
            @classmethod
            def instance(cls): return cls()
            def __init__(self, *args): pass
            
        class FakeQtWidgets:
            def __getattr__(self, name):
                if name == "QApplication":
                    return FakeQApplication
                return FakeQWidget
        
        qt_widgets_mock = FakeQtWidgets()
        
        qt_mock = MagicMock()
        qt_mock.QtWidgets = qt_widgets_mock
        
        sys.modules['PySide2'] = qt_mock
        sys.modules['PySide2.QtWidgets'] = qt_widgets_mock
        sys.modules['PySide2.QtCore'] = MagicMock()
        sys.modules['PySide2.QtGui'] = MagicMock()

# Apply immediately so collection phase imports succeed
apply_mocks()

@pytest.fixture(autouse=True, scope="session")
def patch_maya():
    # Keep fixture in case tests need it, but actual patching is done above.
    pass
