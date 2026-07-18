import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- 1. SETUP PATHS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Mock Maya BEFORE any import that might trigger it
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()

from qyntara_ai.core import topology_engine

class TestTopologySafetySwap(unittest.TestCase):
    def setUp(self):
        self.engine = topology_engine.TopologyEngine()
        # Surgically patch the module level cmds and om
        self.mock_cmds = MagicMock()
        self.mock_om = MagicMock()
        topology_engine.cmds = self.mock_cmds
        topology_engine.om = self.mock_om
        
        self.mock_cmds.ls.return_value = ["|pCube1"]
        self.mock_cmds.duplicate.return_value = ["pCube1_Retopo_Candidate"]
        self.mock_cmds.objExists.return_value = True
        self.mock_cmds.pluginInfo.return_value = True
        
    def test_retopo_success_path(self):
        print("\n[Test] Testing Safety Swap: SUCCESS PATH")
        
        # Setup OM2 success mocks
        mock_mesh_instance = MagicMock()
        mock_mesh_instance.numPolygons = 5000
        self.mock_om.MFnMesh.return_value = mock_mesh_instance
        
        res = self.engine.tool_retopology(target_faces=5000)
        
        # Verification:
        # 1. Did we duplicate?
        self.mock_cmds.duplicate.assert_called()
        # 2. Did we rename candidate back?
        self.mock_cmds.rename.assert_called_with("pCube1_Retopo_Candidate", "pCube1")
        # 3. Did we delete original?
        self.mock_cmds.delete.assert_any_call("|pCube1")
        
        print(f" -> Result: {res}")
        self.assertIn("Processed", res)
        self.assertNotIn("FAILED", res)

    def test_retopo_failure_recovery(self):
        print("\n[Test] Testing Safety Swap: FAILURE RECOVERY")
        
        # Setup OM2 failure mocks (0 polygons)
        mock_mesh_instance = MagicMock()
        mock_mesh_instance.numPolygons = 0
        self.mock_om.MFnMesh.return_value = mock_mesh_instance
        
        # Fallback polyEvaluate also returns 0
        self.mock_cmds.polyEvaluate.return_value = 0
        
        res = self.engine.tool_retopology(target_faces=5000)
        
        # Verification:
        # 1. Did we restore original visibility?
        self.mock_cmds.setAttr.assert_any_call("|pCube1.visibility", 1)
        # 2. Did we delete the bad candidate?
        self.mock_cmds.delete.assert_any_call("pCube1_Retopo_Candidate")
        
        print(f" -> Result: {res}")
        self.assertIn("Processed", res)
        self.assertIn("FAILED", res)

if __name__ == "__main__":
    print("========================================")
    print(" TOPOLOGY ENGINE: SAFETY SWAP PROOF")
    print("========================================")
    unittest.main()
