import sys
from unittest.mock import MagicMock

print("Starting checks...")

# 1. Mock Maya Dependencies
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()

import maya.cmds as cmds
print("Maya Mocked.")

sys.path.insert(0, r"e:/QYNTARA AI")

try:
    from qyntara_ai.ui.main_window import QyntaraMainWindow
    print("MainWindow Imported.")
    from qyntara_ai.core.fixer import QyntaraFixer
    print("Fixer Imported.")
except ImportError as e:
    print(f"Import Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"General Error: {e}")
    sys.exit(1)

print("All imports successful.")
context_menu_check = getattr(QyntaraMainWindow, 'auto_fix_all', None)
if context_menu_check:
    print("auto_fix_all found.")
else:
    print("auto_fix_all MISSING!")
