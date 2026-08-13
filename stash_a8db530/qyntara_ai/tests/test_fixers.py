import sys
import unittest
from unittest.mock import MagicMock

# Mock Maya
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()

import maya.cmds as cmds

# Import modules (assuming paths are set or we append)
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from qyntara_ai.core import geometry, transforms, materials, uv

class TestQyntaraFixers(unittest.TestCase):
    
    def setUp(self):
        # Reset mocks
        cmds.reset_mock()
        
    def test_fix_geometry(self):
        obj = "pCube1"
        
        # Test Open Edges
        # Mock finding borders
        cmds.polyListComponentConversion.return_value = ["e[0]", "e[1]"]
        geometry.fix_open_edges([obj])
        cmds.polyCloseBorder.assert_called_with(obj, ch=True)
        
        # Test Ngons
        cmds.ls.side_effect = lambda sl=False: ["f[1]"] if sl else []
        geometry.fix_ngons([obj])
        cmds.polyTriangulate.assert_called()
        
        # Test Lamina
        geometry.fix_lamina_faces([obj])
        cmds.polyCleanup.assert_called_with(obj, laminaFaces=True)
        
    def test_fix_transforms(self):
        obj = "pCube1"
        
        # Test Freeze
        transforms.fix_transform_zero([obj])
        cmds.makeIdentity.assert_called_with(obj, apply=True, t=1, r=1, s=1, n=0, pn=1)
        
    def test_fix_materials(self):
        obj = "pCube1"
        
        # Test Assign Default
        materials.fix_assign_default([obj])
        cmds.sets.assert_called_with(obj, edit=True, forceElement="initialShadingGroup")
        
    def test_fix_uv(self):
        obj = "pCube1"
        
        # Test Flip
        uv.fix_flip_uvs([obj])
        cmds.polyEditUV.assert_called_with(obj, pivotU=0.5, pivotV=0.5, scaleU=-1, scaleV=1)


if __name__ == "__main__":
    unittest.main()
