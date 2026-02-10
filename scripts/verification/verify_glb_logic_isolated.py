import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- PRE-MOCK MAYA ---
mock_maya = MagicMock()
sys.modules["maya"] = mock_maya
sys.modules["maya.cmds"] = mock_maya.cmds

class TestGltfExportIsolated(unittest.TestCase):
    
    def setUp(self):
        if r"i:\QYNTARA AI" not in sys.path:
            sys.path.append(r"i:\QYNTARA AI")
        
        # Now we can safely import the script because maya.cmds is mocked
        import scripts.maya.export_web_gltf as export_script
        import importlib
        importlib.reload(export_script)
        self.export_script = export_script

    @patch("scripts.maya.export_web_gltf.cmds")
    @patch("scripts.maya.export_web_gltf.os")
    def test_native_export_success(self, mock_os, mock_cmds):
        """Verify successful native glTF export."""
        # 1. Setup Mocks
        mock_cmds.ls.return_value = ["pCube1"]
        mock_cmds.pluginInfo.return_value = False # Babylon off, GLTF will be queried
        
        # Translator discovery
        mock_cmds.file.return_value = ["GLTF Export", "FBX export"]
        
        # File existence
        mock_os.path.exists.return_value = True
        mock_os.path.dirname.return_value = "C:/temp"
        
        # 2. Run
        # We need to simulate the loop in translator discovery
        # The script calls cmds.file(q=True, tt=True)
        # So mock_cmds.file return value needs to be consistent
        
        result = self.export_script.export_glb("C:/temp/test.glb")
        
        # 3. Assert
        self.assertTrue(result)
        mock_cmds.file.assert_any_call("C:/temp/test.glb", force=True, options="v=0;", typ="GLTF Export", pr=True, es=True)

    @patch("scripts.maya.export_web_gltf.cmds")
    @patch("scripts.maya.export_web_gltf.os")
    def test_fbx_fallback_when_no_gltf(self, mock_os, mock_cmds):
        """Verify fallback to FBX when no glTF translator is found."""
        # 1. Setup Mocks
        mock_cmds.ls.return_value = ["pCube1"]
        mock_cmds.pluginInfo.return_value = False # No Babylon
        mock_cmds.file.return_value = ["FBX export"] # No GLTF in list
        
        # Simulate file existence for fallback check
        # First call False (glb), second call True (fbx fallback)
        mock_os.path.exists.side_effect = [False, False, True] # dir, glb, fbx
        mock_os.path.dirname.return_value = "C:/temp"
        
        # 2. Run
        result = self.export_script.export_glb("C:/temp/test.glb")
        
        # 3. Assert
        self.assertFalse(result) # Should return False for fallback
        mock_cmds.file.assert_any_call("C:/temp/test_FALLBACK.fbx", force=True, options="v=0;", typ="FBX export", pr=True, es=True)

    @patch("scripts.maya.export_web_gltf.cmds")
    @patch("scripts.maya.export_web_gltf.os")
    def test_missing_selection_error(self, mock_os, mock_cmds):
        """Verify error when nothing is selected."""
        mock_cmds.ls.return_value = []
        result = self.export_script.export_glb("test.glb")
        self.assertIsNone(result) # Script returns None for no selection

if __name__ == "__main__":
    unittest.main()
