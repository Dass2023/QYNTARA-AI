import sys
from unittest.mock import MagicMock

# Mock Maya
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
import maya.cmds as cmds

# Custom mock for exactWorldBoundingBox side effect
bbox_data = []
def mock_bbox(obj):
    if not bbox_data: return [0]*6
    return bbox_data.pop(0)

cmds.exactWorldBoundingBox.side_effect = mock_bbox
cmds.ls.return_value = ["Source", "Target"]

# Import
sys.path.append(r'e:\QYNTARA AI')
from qyntara_ai.core.fixer import QyntaraFixer

print("--- START VERIFICATION ---")

# TEST 1: X Adjacency
# Source: 0..10, Target: 20..30. Gap is 10. Source needs to move +10.
bbox_data = [
    [0.0, 0.0, 0.0, 10.0, 10.0, 10.0],
    [20.0, 0.0, 0.0, 30.0, 10.0, 10.0]
]

cmds.move.reset_mock()
result = QyntaraFixer.fix_vertex_snap()

if result:
    args, _ = cmds.move.call_args
    print(f"Test 1 Move Args: {args}")
    # Expected: 10.0, 0.0, 0.0
    if abs(args[0] - 10.0) < 0.001:
        print("Test 1: PASSED (X Offset Correct)")
    else:
        print(f"Test 1: FAILED. Expected 10.0, got {args[0]}")
else:
    print("Test 1: FAILED (Function returned False)")

print("--- END VERIFICATION ---")
