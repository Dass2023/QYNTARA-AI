import maya.cmds as cmds
import os

def export_glb(file_path):
    """
    Exports selection to GLTF Binary (.glb) for WebGPU/Three.js.
    Uses 'gameExporter' or fallback.
    """
    selection = cmds.ls(sl=True)
    if not selection:
        print("[GLB] Error: No selection.")
        return

    print(f"[GLB] Exporting {selection} to {file_path}")
    
    # Method 1: BabylonJS Plugin (Industry Standard for Web)
    if cmds.pluginInfo("Maya2Babylon", q=True, loaded=True):
        print("[GLB] Using BabylonJS Exporter...")
        # (Hypothetical command, varies by version)
        # cmds.BabylonExport(file_path, format="glb") 
        pass 
        
    # Method 2: GameExporter (Built-in)
    # The 'gameFbxExporter' usually does FBX. 
    # Maya 2025 might have native GLTF.
    
    # Method 3: FBX-to-GLTF (If instant conversion tool exists) or just export FBX and warn.
    # But user asked for GLB.
    
    # Let's try the modern standard 'mayaUsd' often has 'AL_USDMaya' but GLTF is separate.
    # If no plugin, we export FBX and rename it? No, that's lying.
    
    # Robust Implementation
    try:
        # 0. Directory Validation
        export_dir = os.path.dirname(file_path)
        if not os.path.exists(export_dir):
            try:
                os.makedirs(export_dir)
            except Exception as e:
                print(f"[GLB] Error: Could not create directory {export_dir}: {e}")
                return False

        # 1. Translator Discovery
        # We look for 'GLTF Export' (Native) or 'gltf' (Legacy/Alternative)
        translators = cmds.file(q=True, tt=True)
        gltf_translator = None
        for t in ["GLTF Export", "mayaGLTF", "gltf"]:
            if t in translators:
                gltf_translator = t
                break
        
        # If not found, try loading plugin and checking again
        if not gltf_translator:
            for plugin in ["mayaGLTF", "mayaUsdPlugin"]:
                if not cmds.pluginInfo(plugin, q=True, loaded=True):
                    try: cmds.loadPlugin(plugin)
                    except: pass
            
            translators = cmds.file(q=True, tt=True)
            for t in ["GLTF Export", "mayaGLTF", "gltf"]:
                if t in translators:
                    gltf_translator = t
                    break

        # 2. Execute Export
        if gltf_translator:
            print(f"[GLB] Found glTF translator: {gltf_translator}. Proceeding...")
            # es=True exports only selected items
            cmds.file(file_path, force=True, options="v=0;", typ=gltf_translator, pr=True, es=True)
            
            if os.path.exists(file_path):
                print(f"[GLB] Export Successful: {file_path}")
                return True
            else:
                print(f"[GLB] Error: Exporter claimed success but file is missing at {file_path}")
        else:
             print("[GLB] CRITICAL: No native glTF exporter found in Maya.")

        # 3. Final Fallback: FBX with CLEAR warning
        fbx_fallback_path = file_path.replace(".glb", "_FALLBACK.fbx")
        print(f"[GLB] Attempting FBX Fallback: {fbx_fallback_path}")
        
        if not cmds.pluginInfo("fbxmaya", q=True, loaded=True):
             cmds.loadPlugin("fbxmaya")
             
        cmds.file(fbx_fallback_path, force=True, options="v=0;", typ="FBX export", pr=True, es=True)
        
        if os.path.exists(fbx_fallback_path):
             print(f"[GLB] FBX Fallback Successful: {fbx_fallback_path}")
        
        return False
        
    except Exception as e:
        print(f"[GLB] Export Fatal Error: {e}")
        return False

if __name__ == "__main__":
    export_glb(r"C:\temp\test.glb")
