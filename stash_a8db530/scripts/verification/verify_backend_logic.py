import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- MOCK MAYA ---
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
import maya.cmds as cmds

# --- SETUP PATH ---
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(os.path.dirname(current_dir))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# --- IMPORT SCRIPTS ---
# We use importlib to load them even with mocks
import importlib
from scripts.maya import export_industry40_usd
# For validation shader, we need to handle the internal imports
from scripts.maya import validation_shader
# For web gltf
from scripts.maya import export_web_gltf

class TestQyntaraBackend(unittest.TestCase):
    """
    Verifies the LOGIC of the Future Features (OpenUSD, Spatial, HLSL)
    without needing a UI loop.
    """

    def test_openusd_logic(self):
        print("\n[Check] OpenUSD Export Logic (IoT Injection)...")
        # Mock selection
        cmds.ls.return_value = ["pCube1"]
        cmds.listRelatives.return_value = ["pCubeShape1"]
        cmds.attributeQuery.return_value = True # Has QyntaraID
        cmds.getAttr.return_value = "UUID-1234"
        
        # Run Export
        export_industry40_usd.export_smart_asset_usd("test_IoT.usd")
        
        # Check if commands generated right calls
        # We expect a file export with 'options' containing 'Qyntara_Asset_Root'
        self.assertTrue(cmds.file.called)
        args, kwargs = cmds.file.call_args
        self.assertIn("Qyntara_Asset_Root", kwargs.get("options", ""))
        print(" -> OpenUSD Export: OK (IoT Metada Logic Verified)")

    def test_spatial_export_arkit(self):
        print("[Check] Spatial Export: ARKit Logic...")
        # .usdz extension should trigger appleArKit compatibility flag
        export_industry40_usd.export_smart_asset_usd("test_AR.usdz")
        
        args, kwargs = cmds.file.call_args
        # kwargs['options'] should contain 'compatibility=appleArKit'
        self.assertIn("appleArKit", kwargs.get("options", ""))
        print(" -> ARKit (USDZ) Logic: OK (Flags Verified)")

    def test_spatial_export_web(self):
        print("[Check] Spatial Export: WebGL Logic...")
        # Just check it attempts to load plugin or export
        # We mocked pluginInfo to return False (default magicmock bool is False?)
        # MagicMock returns a MagicMock, which evaluates to True usually?
        # Let's see what happens.
        
        export_web_gltf.export_glb("test.glb")
        # Should try to export via FBX fallback if plugin missing
        self.assertTrue(cmds.file.called) 
        # Check argument was an FBX export if fallback
        args, kwargs = cmds.file.call_args
        self.assertIn("FBX export", kwargs.get("typ", ""))
        print(" -> Web GLB Logic: OK (Fallback Verified)")

    def test_director_shader_logic(self):
        print("[Check] Director Shader (HLSL)...")
        cmds.ls.return_value = ["pObj1"]
        cmds.objExists.return_value = False # New shader
        
        validation_shader.apply_validation_shader()
        
        # Should create standardSurface and Ramp
        self.assertTrue(cmds.shadingNode.called)
        # Check if it tried to connect ramp to shader
        self.assertTrue(cmds.connectAttr.called)
        print(" -> Director Shader Logic: OK (Network Creation Verified)")

if __name__ == "__main__":
    unittest.main()
