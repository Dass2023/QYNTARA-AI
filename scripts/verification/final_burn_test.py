import sys
import unittest
from unittest.mock import MagicMock, patch

# 1. MOCK MAYA
mock_maya = MagicMock()
mock_cmds = MagicMock()
mock_om = MagicMock()
mock_mel = MagicMock()

sys.modules["maya"] = mock_maya
sys.modules["maya.cmds"] = mock_cmds
sys.modules["maya.api"] = mock_om
sys.modules["maya.api.OpenMaya"] = mock_om
sys.modules["maya.mel"] = mock_mel

# Link attributes
mock_maya.cmds = mock_cmds
mock_maya.mel = mock_mel
mock_maya.api = mock_om
mock_om.OpenMaya = mock_om

# 2. SETUP PATHS
import os
project_root = r"i:\QYNTARA AI"
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 3. IMPORT TARGETS
from qyntara_ai.core.topology_engine import TopologyEngine
from qyntara_ai.core import geometry

class FinalBurnTest(unittest.TestCase):
    
    def setUp(self):
        mock_cmds.reset_mock()
        mock_mel.reset_mock()
        
        # Standard ls mock for long paths
        def mock_ls(obj=None, **kwargs):
            if kwargs.get('sl'):
                # Simulate selection return long paths
                return ["|Group1|pCube1", "|Group2|pCube1"]
            if obj:
                if isinstance(obj, list): return [f"|{o}" for o in obj]
                return [f"|{obj}"]
            return []
        mock_cmds.ls.side_effect = mock_ls
        mock_cmds.objExists.return_value = True
        mock_cmds.nodeType.return_value = 'mesh'
        
        # Mock polyBoolean as available (Maya 2023+)
        # We'll test both success and fallback
        mock_cmds.polyBoolean = MagicMock(return_value=["Qyntara_Boolean_Result"])
        
    def test_manifold_shell_burn(self):
        """Tests the absolute limit of the aggregator: Duplicates + polyBoolean + Retopo."""
        engine = TopologyEngine()
        
        # Execute Aggregation
        # Selection is mocked to return |Group1|pCube1 and |Group2|pCube1
        result = engine.tool_aggregate_meshes(resolution="high", mode="standard")
        
        # VERIFY: Long Paths used for Boolean
        # First call is to polyBoolean
        mock_cmds.polyBoolean.assert_called()
        args, kwargs = mock_cmds.polyBoolean.call_args
        self.assertIn("|Group1|pCube1", args[0])
        self.assertIn("|Group2|pCube1", args[0])
        
        # VERIFY: Retopo called with High Density (30000 quads for resolution="high")
        mock_cmds.polyRetopo.assert_called()
        _, r_kwargs = mock_cmds.polyRetopo.call_args
        self.assertEqual(r_kwargs['targetFaceCount'], 30000)
        
        # VERIFY: Undo Chunk
        # undo_chunk uses cmds.undoInfo(openChunk=True)
        mock_cmds.undoInfo.assert_any_call(openChunk=True, chunkName="VolumetricAggregate")
        mock_cmds.undoInfo.assert_any_call(closeChunk=True)

    def test_plugin_redundancy(self):
        """Tests that the engine tries both Retopologize and remeshTerminator."""
        # Force Retopologize to fail load, but terminator to succeed
        def mock_load(p):
            if p == "Retopologize": raise Exception("Not Found")
            return True
        mock_cmds.loadPlugin.side_effect = mock_load
        mock_cmds.pluginInfo.return_value = False
        
        # Run shelling
        geometry.generate_manifold_shell(["A", "B"])
        
        # Should have called loadPlugin for both
        mock_cmds.loadPlugin.assert_any_call("Retopologize")
        mock_cmds.loadPlugin.assert_any_call("remeshTerminator")

    def test_naming_stability_fix(self):
        """Verifies that the engine never uses short names even if polyBoolean fails."""
        # Fail polyBoolean to trigger legacy fallback
        mock_cmds.polyBoolean.side_effect = Exception("Not available")
        mock_cmds.polyBoolOp.return_value = ["Legacy_Boolean"]
        
        engine = TopologyEngine()
        engine.tool_aggregate_meshes()
        
        # Legacy fallback should still use long paths
        mock_cmds.polyBoolOp.assert_called()
        args, _ = mock_cmds.polyBoolOp.call_args
        self.assertIn("|Group1|pCube1", args[0])

if __name__ == "__main__":
    unittest.main()
