import sys
import os
import unittest
from unittest.mock import MagicMock

# 1. Setup Mock for maya.cmds
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
import maya.cmds as cmds

# 2. Add 'maya' folder to path so we can import 'validation_industry_future'
maya_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "maya"))
sys.path.insert(0, maya_folder)

# Now import the module directly
import validation_industry_future as v7

class TestFutureValidation(unittest.TestCase):
    def test_carbon_footprint(self):
        print("\n[Test] Carbon Footprint")
        # Mock selection
        cmds.ls.return_value = ["mesh1"]
        cmds.exactWorldBoundingBox.return_value = [0, 0, 0, 10, 10, 10]
        
        results = v7.calculate_carbon_footprint()
        print(f"Result: {results}")
        
        self.assertTrue(any("4.34 kg CO2e" in r for r in results))
        
    def test_warping_probability(self):
        print("\n[Test] Warping Probability")
        # Mock flat plate
        cmds.exactWorldBoundingBox.return_value = [0, 0, 0, 100, 1, 100]
        
        results = v7.predict_warping_probability()
        print(f"Result: {results}")
        
        self.assertTrue(any("High Aspect Ratio" in r for r in results))

if __name__ == "__main__":
    unittest.main()
