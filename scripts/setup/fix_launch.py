import sys
import os

# --- Configuration ---
# Hardcoding the path is safer for Script Editor copy-paste usage 
# where __file__ might not be defined.
PROJECT_ROOT = r"e:\QYNTARA AI"

# 1. Setup Path
# Ensure the project root is in sys.path so imports work
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
    print(f"[Qyntara] Added {PROJECT_ROOT} to sys.path")

# 2. Unload all Qyntara modules from memory
# This ensures a fresh reload of the code
# Aggressively clear everything related to qyntara_ai to force re-import
keys = [k for k in list(sys.modules.keys()) if "qyntara_ai" in k]
for k in keys:
    try:
        del sys.modules[k]
        print(f"Unloaded: {k}")
    except Exception:
        pass
print(f"[Qyntara] Unloaded {len(keys)} modules.")

# 3. Reload Main Window
try:
    #    # Reload Core Modules
    if 'qyntara_ai.ui.main_window' in sys.modules:
        del sys.modules['qyntara_ai.ui.main_window']
        
    import qyntara_ai.ui.main_window as mw
    import importlib
    importlib.reload(mw) # the main window module specifically to be sure
    importlib.reload(mw)

    # Close existing window if open
    window_name = "QyntaraValidatorWindow"
    from maya import cmds
    if cmds.window(window_name, exists=True):
        cmds.deleteUI(window_name)
    
    # 4. Launch New Version
    win = mw.QyntaraMainWindow()
    win.show()
    print("[Qyntara] Interface launched successfully.")

except ModuleNotFoundError as e:
    print(f"[Qyntara] CRITICAL IMPORT ERROR: {e}")
    print(f"[Qyntara] Current sys.path: {sys.path}")
except Exception as e:
    print(f"[Qyntara] Error launching window: {e}")
    import traceback
    traceback.print_exc()
