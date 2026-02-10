import unittest
import sys
import os
from unittest.mock import MagicMock

# 1. SETUP MOCKS BEFORE IMPORTS
# Create shared mock objects
mock_maya = MagicMock()
mock_cmds = MagicMock()
mock_om = MagicMock()

sys.modules['maya'] = mock_maya
sys.modules['maya.cmds'] = mock_cmds
sys.modules['maya.OpenMaya'] = mock_om
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()

# Link them to be safe
mock_maya.cmds = mock_cmds

# 2. IMPORT MODULES
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from qyntara_ai.core import validator, geometry, transforms

class TestQyntaraCore(unittest.TestCase):
    def setUp(self):
        self.validator = validator.QyntaraValidator()
        # Reset mocks
        mock_cmds.reset_mock()
        
        # Default mock behaviors
        mock_cmds.objectType.return_value = 'transform'
        mock_cmds.listRelatives.return_value = ['meshShape1']
        mock_cmds.ls.return_value = [] # Default empty
        
    def test_rules_load(self):
        self.assertTrue(len(self.validator.rules) > 0)
        
    def test_validator_run(self):
        # Setup mock behavior for check_scale to fail
        # We need to ensure xform returns the bad scale when called
        mock_cmds.xform.return_value = [2.0, 1.0, 1.0] # Bad scale
        
        # Also need to mock other calls to avoid crashes in other rules
        mock_cmds.currentUnit.return_value = 'cm'
        mock_cmds.upAxis.return_value = 'y'
        mock_cmds.polyInfo.return_value = None
        mock_cmds.polyEvaluate.return_value = 10
        mock_cmds.polyUVSet.return_value = ['map1']
        
        objects = ['pCube1']
        report = self.validator.run_validation(objects)
        
        # Check if xform_scale failed
        scale_fail = next((d for d in report['details'] if d['rule_id'] == 'xform_scale'), None)
        self.assertIsNotNone(scale_fail, "Expected xform_scale failure but got None")
        
    def test_open_edges(self):
        # Mock polyListComponentConversion returning edges
        # Note: calling mock_cmds directly because it's the same object as imported cmds
        mock_cmds.polyListComponentConversion.return_value = ['e[1]', 'e[2]']
        
        # Mock ls to return the edges flat
        # We need side_effect to distinguish calls if necessary, but simple return works for this isolated test
        mock_cmds.ls.return_value = ['e[1]', 'e[2]']
        
        violations = geometry.check_open_edges(['pCube1'])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]['count'], 2)

if __name__ == '__main__':
    unittest.main()
