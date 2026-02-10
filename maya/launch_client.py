
"""
QYNTARA AI - LAUNCH SCRIPT
Run this file to start the client with a FRESH load of the code.
"""
import sys
import maya.cmds as cmds
import importlib

print("\n--- QYNTARA LAUNCHER ---")

# 1. Close Existing Window
if cmds.window("QyntaraWin", exists=True):
    cmds.deleteUI("QyntaraWin")
    print("Closed existing window.")

# 2. Add Project to Path (Force Front)
PROJECT_PATH = "I:/QYNTARA AI/maya"
if PROJECT_PATH not in sys.path:
    sys.path.insert(0, PROJECT_PATH)
    print(f"Added path: {PROJECT_PATH}")
else:
    # Ensure it's at the front to override any Documents scripts
    sys.path.remove(PROJECT_PATH)
    sys.path.insert(0, PROJECT_PATH)
    print(f"Prioritized path: {PROJECT_PATH}")

# 3. NUCLEAR REMOVAL of Cached Modules
# This forces Maya to read the files from disk again
MODULES_TO_WIPE = [
    "material_framework",
    "universal_framework", 
    "master_prompt",
    "agent_logic",
    "qyntara_client"
]

for mod in MODULES_TO_WIPE:
    if mod in sys.modules:
        del sys.modules[mod]
        print(f"Wiped from memory: {mod}")

# 4. Import and Launch
try:
    import qyntara_client
    print(f"Loaded Client from: {qyntara_client.__file__}")
    qyntara_client.main()
    print("Launch Successful.")
except Exception as e:
    print(f"LAUNCH ERROR: {e}")
    cmds.confirmDialog(title="Launch Error", message=str(e), button=["OK"])
