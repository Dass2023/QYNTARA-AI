import unittest
import sys
from unittest.mock import MagicMock, patch

# Mock Maya modules BEFORE importing qyntara_ai
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()

import maya.api.OpenMaya as om
import maya.cmds as cmds

# Now import target module
# We need to assume qyntara_ai is in path
sys.path.append(r"e:/QYNTARA AI")
from qyntara_ai.core import geometry

class TestGeometryOM(unittest.TestCase):
    
    def setUp(self):
        # Reset mocks
        om.MItMeshPolygon.reset_mock()
        om.MItMeshEdge.reset_mock()
        cmds.reset_mock()

    def test_check_zero_area_faces_om(self):
        """Test that zero area faces are detected using OpenMaya iterator."""
        obj = "pCube1"
        cmds.objectType.return_value = 'mesh'
        
        om.MSelectionList.return_value = MagicMock()
        om.MSelectionList.return_value.getDagPath.return_value = MagicMock()
        
        mock_it = MagicMock()
        om.MItMeshPolygon.return_value = mock_it
        
        # Behavior: 2 faces. First Good (1.0), Second Bad (0.0).
        mock_it.isDone.side_effect = [False, False, True]
        mock_it.getArea.side_effect = [1.0, 0.0]
        
        # index() is ONLY called when face is bad.
        # Since only the second face is bad, index() will be called once.
        # We want it to return 1 (index of the second face).
        mock_it.index.return_value = 1 
        
        violations = geometry.check_zero_area_faces([obj])
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]['issue'], "Zero Area Faces")
        self.assertIn(f"{obj}.f[1]", violations[0]['components'])

    def test_check_zero_length_edges_om(self):
        """Test that zero length edges are detected using OpenMaya iterator."""
        obj = "pCube1"
        cmds.objectType.return_value = 'mesh'
        
        om.MSelectionList.return_value = MagicMock()
        om.MSelectionList.return_value.getDagPath.return_value = MagicMock()
        
        mock_it = MagicMock()
        om.MItMeshEdge.return_value = mock_it
        
        mock_it.isDone.side_effect = [False, False, True]
        
        # Fix: MItMeshEdge uses .length() not .getLength() in OM2
        mock_it.length.side_effect = [1.0, 0.0]
        
        # index() called only for bad edge (second one)
        mock_it.index.return_value = 1
        
        violations = geometry.check_zero_length_edges([obj])
        
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]['issue'], "Zero Length Edges")
        self.assertIn(f"{obj}.e[1]", violations[0]['components'])

    def test_check_proximity_gaps(self):
        """Test grid snap logic."""
        obj = "pCube1"
        cmds.objectType.return_value = 'transform' # It checks for meshes but iterates objects
        # We need to ensure _is_mesh returns true. 
        # _is_mesh logic: checks if transform has mesh shape.
        cmds.listRelatives.return_value = ["pCubeShape1"]
        
        # Scenario 1: On grid (10, 20, 0)
        cmds.xform.return_value = [10.0, 20.0, 0.0] 
        violations = geometry.check_proximity_gaps([obj])
        self.assertEqual(len(violations), 0)
        
        # Scenario 2: Off grid (10.05, 20.0, 0.0) -> Gap 0.05
        cmds.xform.return_value = [10.05, 20.0, 0.0]
        violations = geometry.check_proximity_gaps([obj])
        self.assertEqual(len(violations), 1)
        self.assertIn("Off Grid", violations[0]['issue'])

if __name__ == '__main__':
    unittest.main()
