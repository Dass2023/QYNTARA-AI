
"""
QYNTARA AI - FORCE RELOAD SCRIPT
Run this in Maya's Script Editor to force an update of the UI code 
without restarting Maya.
"""
import sys
import os
import importlib
import maya.cmds as cmds

import maya.cmds as cmds

# Explicit Project Path (Robust for Copy-Paste)
PROJECT_ROOT = "I:/QYNTARA AI/maya"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Modules to reload (Order matters: lowest dependency first)
modules = [
    "material_framework",
    "universal_framework",
    "qyntara_client"
]

def run():
    print("--- RELOADING QYNTARA CLIENT ---")
    
    # 1. Close existing windows
    if cmds.window("QyntaraWin", exists=True):
        cmds.deleteUI("QyntaraWin")
        
    # 2. Force Reload
    for mod_name in modules:
        if mod_name in sys.modules:
            print(f"Reloading: {mod_name}")
            importlib.reload(sys.modules[mod_name])
        else:
            print(f"Importing new: {mod_name}")
            importlib.import_module(mod_name)

    # 3. Launch
    import qyntara_client
    print("Launching Interface...")
    qyntara_client.main()

if __name__ == "__main__":
    run()
