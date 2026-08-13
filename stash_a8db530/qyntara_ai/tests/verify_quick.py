
import sys
import os
# Add root to path
sys.path.insert(0, "e:/QYNTARA AI")

from unittest.mock import MagicMock
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()

import qyntara_ai.core.geometry as geo
import maya.cmds as cmds

# Mock setup
def mock_ls(*args, **kwargs):
    if kwargs.get('sl'): return [] # Simulate CLEAN cube (no borders selected)
    return ["pCube1"]
    
cmds.ls.side_effect = mock_ls
cmds.listRelatives.return_value = ["shape1"]

# Test
print("Testing check_open_edges...")
violations = geo.check_open_edges(["pCube1"])
print(f"Violations Found: {len(violations)}")

if len(violations) == 0:
    print("TEST PASSED: Clean cube reported 0 violations.")
else:
    print("TEST FAILED: Logic error.")
