import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# --- MOCK MAYA ---
mock_cmds = MagicMock()
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = mock_cmds

def setup_mock_maya(translator_list=None, file_exists=True):
    mock_cmds.reset_mock()
    
    # Precise mock for ls(sl=True)
    def mock_ls(*args, **kwargs):
        if kwargs.get("sl") or kwargs.get("selection"): return ["testObject"]
        return []
    mock_cmds.ls.side_effect = mock_ls
    
    # Precise mock for file(q=True, tt=True) vs file(export)
    def mock_file(*args, **kwargs):
        if kwargs.get("q"):
            if kwargs.get("tt"): return translator_list or ["FBX export"]
            return []
        return None # Export returns None
    mock_cmds.file.side_effect = mock_file
    
    # Precise mock for pluginInfo(plugin, q=True, loaded=True)
    def mock_plugin_info(*args, **kwargs):
        if kwargs.get("q") and kwargs.get("loaded"):
            # Disable BabylonJS to avoid bypassing the main logic in tests
            if args and args[0] == "Maya2Babylon": return False
            if args and args[0] == "mayaGLTF": return "GLTF Export" in (translator_list or [])
            if args and args[0] == "fbxmaya": return True
        return False
    mock_cmds.pluginInfo.side_effect = mock_plugin_info
    
    # Mock os.path.exists
    patcher = patch("os.path.exists", side_effect=lambda p: file_exists if p else False)
    patcher.start()
    return patcher

class TestGltfExport(unittest.TestCase):
    
    def setUp(self):
        if r"i:\QYNTARA AI" not in sys.path:
            sys.path.append(r"i:\QYNTARA AI")
        
        import scripts.maya.export_web_gltf as export_script
        import importlib
        importlib.reload(export_script)
        self.export_script = export_script

    def test_successful_native_export(self):
        """Tests that the script uses 'GLTF Export' when available."""
        patcher = setup_mock_maya(translator_list=["GLTF Export"], file_exists=True)
        
        test_path = "C:/temp/test_export.glb"
        with patch("os.makedirs"):
            result = self.export_script.export_glb(test_path)
        
        self.assertTrue(result)
        mock_cmds.file.assert_any_call(test_path, force=True, options="v=0;", typ="GLTF Export", pr=True, es=True)
        patcher.stop()

    def test_missing_plugin_fallback(self):
        """Tests that the script loads plugin then exports."""
        # Setup: initially NO gltf, but after loadPlugin it appears
        discovery_results = [
            ["FBX export"], # First scan
            ["GLTF Export", "FBX export"], # Second scan (post load)
            ["GLTF Export", "FBX export"]  # Third scan
        ]
        mock_cmds.file.side_effect = lambda *args, **kwargs: discovery_results.pop(0) if kwargs.get("q") else None
        
        # pluginInfo mock: mayaGLTF returns True only if it's in the current "discovery"
        # However, for simplicity here, we'll just mock the flow.
        mock_cmds.pluginInfo.side_effect = lambda *args, **kwargs: False if args[0] == "mayaGLTF" and len(discovery_results) > 1 else True

        test_path = "C:/output/test.glb"
        with patch("os.path.exists", return_value=True):
            with patch("os.makedirs"):
                result = self.export_script.export_glb(test_path)
            
        self.assertTrue(result)
        mock_cmds.loadPlugin.assert_any_call("mayaGLTF")

    def test_fbx_fallback(self):
        """Tests that the script falls back to FBX if no translator is found."""
        setup_mock_maya(translator_list=["FBX export"], file_exists=True)
        
        test_path = "C:/temp/test.glb"
        fallback_path = "C:/temp/test_FALLBACK.fbx"
        
        with patch("os.path.exists") as mock_exists:
            with patch("os.makedirs"):
                mock_exists.side_effect = lambda p: p == fallback_path
                result = self.export_script.export_glb(test_path)
            
        self.assertFalse(result)
        mock_cmds.file.assert_any_call(fallback_path, force=True, options="v=0;", typ="FBX export", pr=True, es=True)

if __name__ == "__main__":
    unittest.main()
