import sys
from unittest.mock import MagicMock
sys.modules['maya.cmds'] = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()
sys.modules['PySide2'] = MagicMock()
sys.modules['PySide2.QtWidgets'] = MagicMock()
sys.modules['PySide2.QtCore'] = MagicMock()
sys.modules['PySide2.QtGui'] = MagicMock()

import maya.qyntara_client
print("SUCCESS")
