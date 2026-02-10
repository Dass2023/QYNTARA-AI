"""
Qyntara AI Launcher (Dev Mode)
Run this script in Maya's Script Editor to start/reload the tool.
"""
import sys
import maya.cmds as cmds

def launch():
    # 1. Force Unload all Qyntara Modules (Aggressive Flush)
    to_delete = [m for m in sys.modules if m.startswith('qyntara_ai')]
    for module in to_delete:
        try:
            del sys.modules[module]
            print(f"Unloaded: {module}")
        except: 
            pass

    # 2. Re-Import Main Window
    try:
        import qyntara_ai.ui.main_window as mw
        
        # 3. Close existing windows
        if cmds.window("QyntaraValidatorWindow", exists=True):
            cmds.deleteUI("QyntaraValidatorWindow")
            
        # 4. Show New Window
        global my_qyntara_window
        my_qyntara_window = mw.QyntaraMainWindow()
        my_qyntara_window.show()
        print(">>> Qyntara AI Launched Successfully (v2.1) <<<")
        
    except Exception as e:
        print(f"Launch Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    launch()
