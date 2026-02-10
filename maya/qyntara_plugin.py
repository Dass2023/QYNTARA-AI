
# qyntara_plugin.py
# QYNTARA AI - Maya Plugin Entry Point & Command Registration
# Connects Maya Commands to Qyntara Backend

import sys
import json
import os
import urllib.request
import urllib.parse
import maya.api.OpenMaya as om
import maya.cmds as cmds
import tempfile

PLUGIN_VENDOR = "Qyntara"
PLUGIN_VERSION = "1.0.0"
API_URL = "http://localhost:8000"

# ---------- Utility ----------

def _log(msg):
    om.MGlobal.displayInfo(f"[Qyntara Plugin] {msg}")

def _err(msg):
    om.MGlobal.displayError(f"[Qyntara Plugin] {msg}")

def _backend_request(endpoint, payload):
    try:
        url = f"{API_URL}{endpoint}"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        _err(f"Backend connection failed: {e}")
        return None

def _export_selection(temp_name="q_export.obj"):
    """Exports selected objects to a temp OBJ file."""
    sel = cmds.ls(sl=True)
    if not sel:
        _err("Nothing selected.")
        return None
        
    path = os.path.join(tempfile.gettempdir(), temp_name)
    # Using 'file' command to export selection
    # Ensure OBJ plugin is loaded
    if not cmds.pluginInfo("objExport", q=True, l=True):
        try:
            cmds.loadPlugin("objExport")
        except:
            pass
            
    cmds.file(path, force=True, options="groups=1;ptgroups=1;materials=0;smoothing=1;normals=1", 
              typ="OBJexport", pr=True, es=True)
    return path.replace("\\", "/")

def _import_result(path):
    """Imports the result OBJ back into Maya."""
    if not os.path.exists(path):
        _err(f"Result file not found: {path}")
        return
        
    cmds.file(path, i=True, type="OBJ", ignoreVersion=True, ra=True, mergeNamespacesOnClash=False, namespace="QyntaraResult")
    _log(f"Imported: {path}")

# ---------- COMMANDS ----------

class QyntaraQuadRemeshCmd(om.MPxCommand):
    COMMAND_NAME = "qyntaraQuadRemesh"

    def __init__(self):
        super(QyntaraQuadRemeshCmd, self).__init__()

    @staticmethod
    def cmdCreator():
        return QyntaraQuadRemeshCmd()

    def doIt(self, args):
        # 1. Parse Args (Simplification: accept JSON string or assumes global args via flags if strict)
        # For simplicity in this v1, we export selection and ask backend with default or provided JSON config
        
        # We can implement MArgDatabase parsing here for full flags support.
        # Stub: just send selection to backend default remesh.
        
        _log("Quad Remesh Started...")
        
        path = _export_selection()
        if not path: return

        # Payload
        payload = {
            "pipeline": ["remesh"],
            "mesh_paths": [path],
            "remesh_settings": {
                "target_faces": 5000,
                "density_mode": "ADAPTIVE",
                "detect_hard_edges": True
            }
        }
        
        # In a real cmd, we would parse -targetFaces 1000 etc. or accept a -config "json_string"
        
        res = _backend_request("/execute", payload)
        if res and res.get("status") == "success":
            output = res.get("results", {}).get("optimization_export", {}).get("files", []) # wait, pipeline structure varies
            # Remesh pipeline step usually returns a RemeshOutput in the 'remeshing' key or similar
            # Based on backend implementation...
            # Pipeline returns dict keyed by step? 
            # Actually pipeline.py logic usually runs steps sequentially.
            # Let's assume the backend handles the response structure.
            # For now, print result.
            _log(f"Success: {res}")
            # If we want to import, we need the file path.
            # Assuming backend returns path in 'remeshOutput' logic (legacy) or 'results' list.
        else:
            _err("Remesh failed.")


class QyntaraMaterialAICmd(om.MPxCommand):
    COMMAND_NAME = "qyntaraMaterialAI"

    def __init__(self):
        super(QyntaraMaterialAICmd, self).__init__()

    @staticmethod
    def cmdCreator():
        return QyntaraMaterialAICmd()

    def doIt(self, args):
        _log("Material AI Executing...")
        # Stub: Analyze Selection
        
        path = _export_selection()
        if not path: return
        
        payload = {
            "pipeline": ["material_ai"],
            "mesh_paths": [path],
            "material_settings": {
                "target_profile": "UNREAL", 
                "scope": "SCENE"
            }
        }
        
        res = _backend_request("/execute", payload)
        if res: _log("Material AI Completed.")


class QyntaraValidateSceneCmd(om.MPxCommand):
    COMMAND_NAME = "qyntaraValidateScene"

    def __init__(self):
        super(QyntaraValidateSceneCmd, self).__init__()

    @staticmethod
    def cmdCreator():
        return QyntaraValidateSceneCmd()

    def doIt(self, args):
        _log("Validating Scene...")
        path = _export_selection()
        if not path: return
        
        payload = {
            "pipeline": ["validate"],
            "mesh_paths": [path],
            "validation_profile": "UNREAL"
        }
        
        res = _backend_request("/execute", payload)
        if res:
             issues = res.get("results", {}).get("validation", {}).get("issues", [])
             _log(f"Validation: Found {len(issues)} issues.")
             for i in issues:
                 _log(f"[{i['severity']}] {i['object']}: {i['description']}")


class QyntaraUniversalUVCmd(om.MPxCommand):
    COMMAND_NAME = "qyntaraUniversalUV"

    def __init__(self):
        super(QyntaraUniversalUVCmd, self).__init__()

    @staticmethod
    def cmdCreator():
        return QyntaraUniversalUVCmd()

    def doIt(self, args):
        _log("Generating Universal UVs...")
        path = _export_selection()
        if not path: return
        
        payload = {
            "pipeline": ["uv"],
            "mesh_paths": [path],
            "uv_settings": {
                "mode": "UDIM",
                "resolution": 4096
            }
        }
        
        res = _backend_request("/execute", payload)
        if res: _log("UV Generation Completed.")


class QyntaraOptimizationExportCmd(om.MPxCommand):
    COMMAND_NAME = "qyntaraOptimizationExport"

    def __init__(self):
        super(QyntaraOptimizationExportCmd, self).__init__()

    @staticmethod
    def cmdCreator():
        return QyntaraOptimizationExportCmd()

    def doIt(self, args):
        _log("Running Optimization & Export...")
        path = _export_selection()
        if not path: return
        
        payload = {
            "pipeline": ["export"],
            "mesh_paths": [path],
            "export_settings": {
                "platform": "UNREAL_HIGH",
                "gen_lods": True,
                "formats": ["USD", "GLTF"]
            }
        }
        
        res = _backend_request("/execute", payload)
        if res: _log("Export Completed.")


# ---------- Plugin registration ----------

def initializePlugin(mobject):
    plugin = om.MFnPlugin(mobject, PLUGIN_VENDOR, PLUGIN_VERSION)
    try:
        plugin.registerCommand(QyntaraQuadRemeshCmd.COMMAND_NAME, QyntaraQuadRemeshCmd.cmdCreator)
        plugin.registerCommand(QyntaraMaterialAICmd.COMMAND_NAME, QyntaraMaterialAICmd.cmdCreator)
        plugin.registerCommand(QyntaraValidateSceneCmd.COMMAND_NAME, QyntaraValidateSceneCmd.cmdCreator)
        plugin.registerCommand(QyntaraUniversalUVCmd.COMMAND_NAME, QyntaraUniversalUVCmd.cmdCreator)
        plugin.registerCommand(QyntaraOptimizationExportCmd.COMMAND_NAME, QyntaraOptimizationExportCmd.cmdCreator)
        _log("Qyntara Plugin Loaded Successfully.")
    except Exception as e:
        om.MGlobal.displayError(f"Failed to register Qyntara commands: {e}")


def uninitializePlugin(mobject):
    plugin = om.MFnPlugin(mobject)
    try:
        plugin.deregisterCommand(QyntaraQuadRemeshCmd.COMMAND_NAME)
        plugin.deregisterCommand(QyntaraMaterialAICmd.COMMAND_NAME)
        plugin.deregisterCommand(QyntaraValidateSceneCmd.COMMAND_NAME)
        plugin.deregisterCommand(QyntaraUniversalUVCmd.COMMAND_NAME)
        plugin.deregisterCommand(QyntaraOptimizationExportCmd.COMMAND_NAME)
        _log("Qyntara Plugin Unloaded.")
    except Exception as e:
        om.MGlobal.displayError(f"Failed to deregister Qyntara commands: {e}")
