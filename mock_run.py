import sys
from PySide6 import QtWidgets, QtCore

class MockCmds:
    def __getattr__(self, item):
        def dummy(*args, **kwargs):
            return None
        return dummy

sys.modules['maya.cmds'] = MockCmds()
sys.modules['maya'] = type('maya', (), {'cmds': MockCmds()})()
sys.modules['maya.api.OpenMaya'] = MockCmds()
sys.modules['maya.api'] = type('api', (), {'OpenMaya': MockCmds()})()
sys.modules['maya.mel'] = MockCmds()

sys.path.insert(0, r"I:\QYNTARA AI")
from maya.qyntara_client import QyntaraDockable

app = QtWidgets.QApplication(sys.argv)
ui = QyntaraDockable()
print("UI instantiated successfully!")
print(f"Tabs count: {ui.tabs.count()}")
for i in range(ui.tabs.count()):
    print(f"Tab {i}: {ui.tabs.tabText(i)}")
