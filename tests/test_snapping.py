import sys
import os
import unittest
from unittest.mock import MagicMock

# Mock Maya environment
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()
import maya.cmds as cmds

# Append path to allow imports
sys.path.append(r'e:\QYNTARA AI')

from qyntara_ai.core.fixer import QyntaraFixer

class TestSmartSnap(unittest.TestCase):
    def setUp(self):
        # Mock Object Selection
        cmds.ls.return_value = ["Source", "Target"]
        # Default mock impl for move
        cmds.move = MagicMock()

    def test_snap_x_adjacency(self):
        """Test Source snaps to Target on X axis (Adjacency)"""
         # Source: 0 to 10 on X
        # Target: 20 to 30 on X (Target is RIGHT of Source)
        # Expected: Source moves +10 in X to touch target at 20.
        
        # exactWorldBoundingBox returns [xmin, ymin, zmin, xmax, ymax, zmax]
        cmds.exactWorldBoundingBox.side_effect = [
            [0.0, 0.0, 0.0, 10.0, 10.0, 10.0], # Source
            [20.0, 0.0, 0.0, 30.0, 10.0, 10.0] # Target
        ]
        
        QyntaraFixer.fix_vertex_snap()
        
        # Check cmds.move call
        # args: (x, y, z, obj)
        # We expect x offset = 20 (tgt_min) - 10 (src_max) = 10.0
        
        args, kwargs = cmds.move.call_args
        self.assertAlmostEqual(args[0], 10.0, places=2)
        self.assertAlmostEqual(args[1], 0.0, places=2) # Y aligned
        self.assertAlmostEqual(args[2], 0.0, places=2) # Z aligned
        
    def test_snap_y_adjacency(self):
        """Test Source snaps to Target on Y axis"""
        # Source: at 0,0,0
        # Target: below at -20 in Y
        
        cmds.exactWorldBoundingBox.side_effect = [
             [0.0, 0.0, 0.0, 10.0, 10.0, 10.0], # Source
             [0.0, -20.0, 0.0, 10.0, -10.0, 10.0] # Target
        ]
        
        QyntaraFixer.fix_vertex_snap()
        
        # Target y_max = -10. Source y_min = 0.
        # Target is BELOW (-Y). Source should move DOWN.
        # c_src_y = 5. c_tgt_y = -15. dy = -20.
        # Y is dominant.
        # move_y = -10 (tgt_max) - 0 (src_min) = -10.
        
        args, kwargs = cmds.move.call_args
        self.assertAlmostEqual(args[1], -10.0, places=2)

if __name__ == '__main__':
    unittest.main()
