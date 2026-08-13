import sys
import unittest
import os
import shutil
import json
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.autonomy.knowledge_graph import KnowledgeGraph
from backend.autonomy.remediator import AutoFixer
from backend.models import ValidationReport, GeometryValidation, UVValidation, MaterialValidation, TopologyValidation

class TestAutonomyLayer(unittest.TestCase):

    def setUp(self):
        self.kg_path = "tests/data/kg_test.json"
        self.kg = KnowledgeGraph(persist_path=self.kg_path)
        self.fixer = AutoFixer()

    def tearDown(self):
        if os.path.exists("tests/data"):
            shutil.rmtree("tests/data")

    def test_knowledge_graph_reasoning(self):
        """Verify KG can infer rules from classification."""
        # 1. Register Asset as 'Prop'
        self.kg.register_asset("barrel_01", "Prop", {"material": "wood"})
        
        # 2. Query Rules
        rules = self.kg.get_rules_for_asset("barrel_01")
        
        # 3. Assert Inherited Rules
        rule_names = [r["name"] for r in rules]
        self.assertIn("requires_collision", rule_names)
        self.assertIn("requires_lods", rule_names)
        print("\n[KG] Reasoning Pass: inferred Prop rules for barrel_01.")

    @patch("trimesh.load")
    @patch("trimesh.repair.fill_holes")
    @patch("trimesh.repair.fix_inversion")
    @patch("trimesh.repair.fix_normals")
    def test_auto_fix_geometry(self, mock_normals, mock_inversion, mock_fill, mock_load):
        """Verify AutoFixer triggers repair on broken report."""
        # Mock Mesh
        mock_mesh = MagicMock()
        mock_load.return_value = mock_mesh
        
        # Mock Report (Broken Geometry)
        report = ValidationReport(
            geometry=GeometryValidation(watertight=False, issues=["holes detected"]),
            uv=UVValidation(),
            material=MaterialValidation(),
            topology=TopologyValidation()
        )
        
        # Run Fix
        fixed_path, fixes = self.fixer.remedate_asset("test_mesh.obj", report)
        
        # Verify
        mock_fill.assert_called_once()
        self.assertIn("Filled mesh holes", fixes)
        self.assertTrue(fixed_path.endswith("_fixed.obj"))
        print("\n[AutoFix] Remediation Pass: Holes filled.")

if __name__ == "__main__":
    unittest.main()
