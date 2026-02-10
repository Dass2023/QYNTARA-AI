import sys
import types
from importlib import reload

def reload_plugin():
    """
    Recursively reloads all qyntara_ai modules.
    """
    # Find all loaded modules related to qyntara_ai
    modules_to_reload = []
    
    # Sort by depth so we reload dependencies first (heuristically)
    # Ideally, we unload or reload in specific order, but simple iteration usually works for dev.
    
    # Create a list key-value pairs
    qyntara_modules = {k:v for k,v in sys.modules.items() if k.startswith("qyntara_ai") and v is not None}
    
    # Simple reload loop
    print(f"Reloading {len(qyntara_modules)} modules...")
    
    for module_name in qyntara_modules:
        try:
            reload(sys.modules[module_name])
        except Exception as e:
            print(f"Failed to reload {module_name}: {e}")
            
    # Re-import main window to launch
    import qyntara_ai.ui.main_window
    reload(qyntara_ai.ui.main_window)
    
    print("Reload complete. Launching UI...")
    qyntara_ai.ui.main_window.show()

if __name__ == "__main__":
    reload_plugin()
