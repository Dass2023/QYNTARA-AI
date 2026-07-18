import sys
import os

def launch():
    print("[Qyntara] Launching...")
    
    # 1. Setup Path
    try:
        current_file = os.path.abspath(__file__)
        # Go up from scripts/maya/launch_in_maya.py to root
        maya_dir = os.path.dirname(current_file)
        scripts_dir = os.path.dirname(maya_dir)
        root_dir = os.path.dirname(scripts_dir)
    except NameError:
        # Fallback if __file__ is not defined (e.g. exec usage)
        root_dir = r"i:\QYNTARA AI"
        print(f"[Qyntara] __file__ not defined (exec mode), defaulting root to: {root_dir}")
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)

    # 2. Nuclear Reload
    # Remove all qyntara_ai modules from sys.modules to force fresh import
    to_delete = [m for m in list(sys.modules.keys()) if m.startswith("qyntara_ai")]
    for module in to_delete:
        try:
            del sys.modules[module]
            # print(f"Unloaded: {module}")
        except Exception:
            pass
    
    if to_delete:
        print(f"[Qyntara] Cleaned up {len(to_delete)} modules from memory.")

    # 3. Import and Launch
    try:
        # Debug check
        import qyntara_ai.core.geometry as geo
        print(f"[Qyntara] Geometry loaded from: {geo.__file__}")
        
        if hasattr(geo, "check_degenerate_geometry"):
            print("[Qyntara] check_degenerate_geometry found.")
        else:
            print("[Qyntara] CRITICAL: check_degenerate_geometry MISSING!")
            print(f"[Qyntara] Available attributes: {dir(geo)}")

        import qyntara_ai.ui.main_window as qwin
        print(f"[Qyntara] UI Loaded from: {qwin.__file__}")
        
        # 4. Aggressive Instance Cleanup
        # Try to find and close existing windows to prevent "no change" ghost instances
        try:
            for widget in QtWidgets.QApplication.topLevelWidgets():
                if widget.objectName() in ["QyntaraMainWindow", "qyntara_nexus_wid"]:
                    print(f"[Qyntara] Closing existing instance: {widget.objectName()}")
                    widget.close()
                    widget.deleteLater()
        except: pass

        # Force reload of style too just in case
        import importlib
        importlib.reload(qwin)
        
        # Ensure name match for cleanup
        main_win = qwin.show()
        main_win.setObjectName("QyntaraMainWindow")
        
        print("[Qyntara] UI Launched Successfully.")
        
    except Exception as e:
        print(f"[Qyntara] Error: {e}")
        import traceback
        traceback.print_exc()

    sys.stdout.flush()

if __name__ == "__main__":
    launch()
