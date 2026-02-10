import sys
import os
import unittest
from unittest.mock import MagicMock

# 1. MOCK MAYA ENVIRONMENT
# We need to mock maya.cmds and maya.api.OpenMaya before importing core modules
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()
sys.modules["maya.standalone"] = MagicMock()

# Setup Mock behavior
import maya.cmds as cmds
import maya.api.OpenMaya as om

# Mock ls to return some objects
def mock_ls(*args, **kwargs):
    if kwargs.get('sl'): return ["pCube1"]
    if kwargs.get('long'): return ["|pCube1", "|pSphere1"]
    return ["pCube1", "pSphere1"]

cmds.ls.side_effect = mock_ls
cmds.listHistory.return_value = ["polyExtrude1", "pCubeShape1"] # Simulate history
cmds.nodeType.side_effect = lambda n: "polyExtrude" if "poly" in n else "mesh"
cmds.currentUnit.return_value = "m" # Simulate wrong units
cmds.upAxis.return_value = "z" # Simulate wrong axis
cmds.polyInfo.return_value = None # No issues by default

# 2. IMPORT QYNTARA MODULES
# Add root to path
# Add root to path
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, root_dir)

from qyntara_ai.core.validator import QyntaraValidator
from qyntara_ai.core.fixer import QyntaraFixer
from qyntara_ai.ai_assist.ai_interface import AIAssist

class TestQyntaraRelease(unittest.TestCase):
    
    def setUp(self):
        print("\n------------------------------------------------")
        print(f"Testing: {self._testMethodName}")
        self.validator = QyntaraValidator()
        
    def test_01_core_validation(self):
        print(">> Running Core Validation Logic...")
        # We simulate objects
        report = self.validator.run_validation(["pCube1"])
        
        # Check structure
        self.assertIn("summary", report)
        self.assertIn("details", report)
        
        # We expect some failures due to our mocks (Units=m, Axis=z, History=True)
        failures = [d['rule_id'] for d in report['details']]
        print(f"Detected simulated failures: {failures}")
        
        self.assertIn("scene_units", failures)
        self.assertIn("scene_axis", failures)
        self.assertIn("geo_history", failures)
        print("Pass: Validation engine detected issues correctly.")

    def test_02_auto_fixer(self):
        print(">> Testing Auto-Fix Logic...")
        
        # Simulate a report detail for History
        detail = {
            "rule_id": "geo_history",
            "violations": [{"object": "pCube1"}]
        }
        
        # Run Fix
        result = QyntaraFixer.fix_history(detail)
        self.assertTrue(result)
        
        # Verify cmds.delete was called with ch=True
        cmds.delete.assert_called_with("pCube1", ch=True)
        print("Pass: Auto-Fixer executed 'delete history' command.")
        
        # Simulate Units fix
        QyntaraFixer.fix_scene_units({})
        cmds.currentUnit.assert_called_with(linear="cm")
        print("Pass: Auto-Fixer set scene units.")

    def test_03_ai_model_integration(self):
        print(">> Testing AI Model Loading...")
        ai = AIAssist()
        ai.load_models()
        
        self.assertTrue(ai.models_loaded)
        if hasattr(ai, "model"):
            print(f"Pass: Advanced Model Loaded: {type(ai.model)}")
            # Verify it is the PyTorch model
            import torch.nn as nn
            self.assertTrue(isinstance(ai.model, nn.Module))
        else:
            print("Warning: PyTorch model not loaded (Torch missing?), running in Heuristic mode.")

    def test_04_remote_client_import(self):
        print(">> Testing Client Import...")
        try:
            from qyntara_ai.core.client import QyntaraClient
            c = QyntaraClient()
            print("Pass: QyntaraClient initialized successfully.")
        except ImportError as e:
            print(f"Warning: Client Module not found: {e}")
    def test_05_advanced_checks(self):
        print(">> Testing Advanced Geometry Checks...")
        from qyntara_ai.core import geometry
        
        # Mock cmds.xform behavior for Proximity/Leaks
        # Return dummy BBoxes: xmin, ymin, zmin, xmax, ymax, zmax
        original_xform = cmds.xform
        
        # Scenario: 2 objects close to each other (Proximity)
        # Obj1: [0,0,0, 1,1,1], Obj2: [1.05, 0, 0, 2.05, 1, 1] -> Gap 0.05
        def mock_xform_bbox(obj, **kwargs):
            if obj == "pCube1": return [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
            if obj == "pCube2": return [1.05, 0.0, 0.0, 2.05, 1.0, 1.0] # 0.05 gap
            return [0,0,0,0,0,0]
            
        cmds.xform.side_effect = mock_xform_bbox
        
        # Test Proximity
        violations = geometry.check_proximity_gaps(["pCube1", "pCube2"], tolerance=0.1)
        self.assertTrue(len(violations) > 0, "Should detect proximity gap")
        print("Pass: Proximity Check detected gap.")
        
        # Test Light Leaks (Unsealed Edges)
        # Mock polySelectConstraint to return 'edges' (simulating open borders)
        cmds.ls.side_effect = lambda sl=False, flatten=False: ["pCube1.e[0]"] if sl else ["pCube1"]
        
        # If we use the same BBox logic, pCube1 e[0] vs pCube2 BBox.
        # We need to mock 'edge' xform too.
        # Let's verify component selection logic calls.
        
        # Reset side effect for ls to avoid breaking other tests if any
        # (Mocking complex logic is hard, we verify the function runs without error)
        try:
            geometry.check_light_leaks(["pCube1"])
            print("Pass: Light Leaks check ran successfully.")
        except Exception as e:
            self.fail(f"Light Leaks check crashed: {e}")

    def test_06_exporter(self):
        print(">> Testing Exporter Presets...")
        from qyntara_ai.core.exporter import QyntaraExporter
        
        # Mock pluginInfo
        cmds.pluginInfo.return_value = True
        
        # Test Unity
        success, msg = QyntaraExporter.export_asset("test_unity.fbx", "unity")
        self.assertTrue(success)
        # Verify Units=m, Axis=y
        # Note: calls are cumulative on the mock, we check if called at least once with these args
        cmds.currentUnit.assert_any_call(linear="m")
        cmds.upAxis.assert_any_call(axis="y")
        print("Pass: Export to Unity set 'Meters' and 'Y-Up'.")
        
        # Test Unreal (should be last call)
        success, msg = QyntaraExporter.export_asset("test_unreal.fbx", "unreal")
        self.assertTrue(success)
        cmds.currentUnit.assert_called_with(linear="cm") # Should restore or set to cm
        cmds.upAxis.assert_called_with(axis="z")
        print("Pass: Export to Unreal set 'Centimeters' and 'Z-Up'.")


if __name__ == "__main__":
    unittest.main()
