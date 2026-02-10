
import sys
import importlib
from maya import cmds

def deep_reload():
    print("--- RELOADING QYNTARA MODULES ---")
    
    # close windows first
    if cmds.window("QyntaraMainWindow", exists=True):
        cmds.deleteUI("QyntaraMainWindow")
        
    modules_to_reload = [
        "qyntara_ai.core.fixer",
        "qyntara_ai.core.baking",
        "qyntara_ai.core.geometry",
        "qyntara_ai.core.uv_engine", # Critical for UV2 Fix
        "qyntara_ai.core.validator", # Critical: Updates registry refs
        "qyntara_ai.ui.main_window"
    ]
    
    for mod_name in modules_to_reload:
        if mod_name in sys.modules:
            try:
                importlib.reload(sys.modules[mod_name])
                print(f"Reloaded: {mod_name}")
            except Exception as e:
                print(f"Failed to reload {mod_name}: {e}")
                
    print("--- RELOAD COMPLETE. PLEASE RE-LAUNCH TOOL ---")

deep_reload()
