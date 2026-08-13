import sys
import os
import shutil
import importlib
from maya import cmds

def force_relaunch():
    print("\n[Qyntara] STARTING NUCLEAR RELOAD sequence...")
    
    # 0. Safety Check: Ensure we are in Maya
    try:
        from maya import cmds
    except ImportError:
        print("[Qyntara] ERROR: This script must be run INSIDE Autodesk Maya.")
        return

    # 1. Close existing Windows
    # Look for widgets with our objectName
    try:
        from PySide2 import QtWidgets
    except ImportError:
        try:
            from PySide6 import QtWidgets
            print("[Qyntara] PySide2 not found, using PySide6 (Maya 2025+).")
        except ImportError:
            print("[Qyntara] CRITICAL: Neither PySide2 nor PySide6 found.")
            print(f"[Qyntara] Sys Path: {sys.path}")
            return

    app = QtWidgets.QApplication.instance()
    top_widgets = app.topLevelWidgets()
    closed_count = 0
    for w in top_widgets:
        if hasattr(w, "windowTitle"):
            title = w.windowTitle()
            if "Qyntara" in title:
                print(f"[Qyntara] Closing detected window: {title}")
                w.close()
                w.deleteLater()
                closed_count += 1
    
    if closed_count == 0:
        print("[Qyntara] No existing windows found (clean slate).")

    # 2. Setup Root Path
    try:
        current_file = os.path.abspath(__file__)
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file))) # Up 3 levels
    except:
        root_dir = r"i:\QYNTARA AI"
    
    print(f"[Qyntara] Root Path: {root_dir}")
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # 3. Aggressive Module Purge
    # Unload EVERYTHING under qyntara_ai
    # Also clear compiled .pyc files if possible? (Hard to do from within Python slightly unsafe, but we can try removing from sys.modules)
    
    to_purge = [m for m in sys.modules.keys() if m.startswith("qyntara_ai")]
    print(f"[Qyntara] Purging {len(to_purge)} modules from memory...")
    for m in to_purge:
        del sys.modules[m]

    # 4. Clear pycache (Optional, skip for safety unless needed, usually sys.modules purge is enough)
    
    # 5. Re-Import
    try:
        import qyntara_ai.ui.main_window as qwin
        # Reloading module just to be 100% sure even if it was purged
        importlib.reload(qwin) 
        
        print(f"[Qyntara] Loaded from: {qwin.__file__}")
        
        # Instantiate
        global my_qyntara_window
        my_qyntara_window = qwin.QyntaraMainWindow()
        my_qyntara_window.show()
        
        print("[Qyntara] SUCCESS: v9.1 PRO Launched.")
        print(f"[Qyntara] Window Title: {my_qyntara_window.windowTitle()}")
        
    except Exception as e:
        print(f"[Qyntara] RELOAD FAILED: {e}")
        import traceback
        traceback.print_exc()

force_relaunch()
