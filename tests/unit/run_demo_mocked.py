import sys
import os
import logging
from unittest.mock import MagicMock

# --- MOCK MAYA ENVIRONMENT ---
mock_maya = MagicMock()
mock_cmds = MagicMock()
mock_om = MagicMock()

# sys.modules["maya"] = mock_maya
# sys.modules["maya.cmds"] = mock_cmds
# sys.modules["maya.api"] = mock_maya
# sys.modules["maya.api.OpenMaya"] = mock_om
mock_maya.cmds = mock_cmds

# Mocking return values specifically for the demo script
mock_cmds.polySphere = MagicMock(return_value=["Hero_Asset", "polySphere1"])
mock_cmds.polyCube = MagicMock(return_value=["Factory_Wall_Scan", "polyCube1"])
mock_cmds.polyCylinder = MagicMock(return_value=["Screw_Master", "polyCylinder1"])
mock_cmds.duplicate = MagicMock(side_effect=lambda *args, **kwargs: [kwargs.get("name", "Mock_Clone")])
mock_cmds.polyEvaluate = MagicMock(return_value=12000)
mock_cmds.exactWorldBoundingBox = MagicMock(return_value=[-1, -1, -1, 1, 1, 1])
mock_cmds.instance = MagicMock(return_value=["Mock_Instanced_Obj"])

# Allow import of the demo script
project_dir = r"i:\QYNTARA AI"
if project_dir not in sys.path:
    sys.path.append(project_dir)

try:
    # Now import the actual demo
    import scripts.maya.demo_nexus_topology as demo
    print("\n[Executing Demo Script within Mocked Maya Context...]\n")
    demo.run_demo()
except Exception as e:
    print(f"Failed to run demo in mock: {e}")
    import traceback
    traceback.print_exc()
