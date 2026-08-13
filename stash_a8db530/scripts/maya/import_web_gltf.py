import maya.cmds as cmds
import os

def import_glb(file_path):
    """
    Imports glTF/GLB files into Maya.
    Uses 'GLTF Export' (which handles import too) or 'mayaUsdPlugin'.
    """
    if not os.path.exists(file_path):
        print(f"[GLB Import] Error: File not found: {file_path}")
        return False

    print(f"[GLB Import] Importing: {file_path}")

    try:
        # 1. Translator Discovery
        translators = cmds.file(q=True, tt=True)
        gltf_translator = None
        for t in ["GLTF Export", "mayaGLTF", "gltf"]:
            if t in translators:
                gltf_translator = t
                break
        
        # If not found, try loading plugin
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

        # 2. Execute Import
        if gltf_translator:
            print(f"[GLB Import] Using translator: {gltf_translator}")
            # i=True for import, typ for translator
            # Using i=True instead of open=True to add to current scene
            cmds.file(file_path, i=True, typ=gltf_translator, pr=True, options="v=0;")
            print(f"[GLB Import] Successfully imported: {file_path}")
            return True
        else:
            print("[GLB Import] CRITICAL: No native glTF importer found.")
            return False

    except Exception as e:
        print(f"[GLB Import] Fatal Error: {e}")
        return False

if __name__ == "__main__":
    # Example usage
    import_glb(r"C:\temp\test_import.glb")
