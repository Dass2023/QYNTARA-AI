"""
Script to launch Qyntara AI in Maya.
Copy and paste this into the Maya Script Editor (Python Tab) and run.
"""
import sys
import os

# 1. ADD PROJECT TO PYTHON PATH
# Replace this with the actual path if different
project_root = r"e:\QYNTARA AI"

if project_root not in sys.path:
    print(f"Adding {project_root} to sys.path")
    sys.path.insert(0, project_root)

# 2. FORCE RELOAD (Use during development)
try:
    # Force reload modules to pick up changes without restarting Maya
    import qyntara_ai.ui.main_window
    import qyntara_ai.core.validator
    import qyntara_ai.core.fixer
    from importlib import reload
    
    reload(qyntara_ai.core.validator)
    reload(qyntara_ai.core.fixer)
    reload(qyntara_ai.ui.main_window)
    print("Modules reloaded.")
except ImportError:
    pass

# 3. LAUNCH UI
try:
    import qyntara_ai.ui.main_window
    qyntara_ai.ui.main_window.show()
    print("Qyntara AI Launched Successfully.")
except Exception as e:
    print(f"Error launching Qyntara AI: {e}")
    import traceback
    traceback.print_exc()
