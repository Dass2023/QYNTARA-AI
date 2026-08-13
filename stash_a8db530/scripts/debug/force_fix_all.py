import maya.cmds as cmds
import qyntara_ai.ui.main_window as mw
from maya.app.general.mayaMixin import MayaQWidgetDockableMixin

def run_global_fix():
    print("--- QYNTARA AI: FORCING GLOBAL FIX ---")
    
    # 1. Clear Selection to ensure Global Scope
    cmds.select(clear=True)
    print("1. Selection Cleared (Global Mode Enabled).")
    
    # 2. Find Active Window
    # We attempt to find the existing Qyntara Window to reuse its state/validator
    win = None
    
    # Strategy A: Check if we can find the widget by object name
    try:
        from PySide2 import QtWidgets
        app = QtWidgets.QApplication.instance()
        for widget in app.topLevelWidgets():
            if widget.objectName() == "QyntaraMainWindow":
                win = widget
                break
    except: pass
    
    # Strategy B: Re-launch if not found (Safe)
    if not win:
        print("2. Window not found. Re-launching...")
        win = mw.show()
    else:
        print("2. Attached to existing Qyntara Window.")
        
    # 3. Trigger Auto-Fix
    if win:
        if not win.btn_fix.isEnabled():
            print("3. Auto-Fix button is disabled. Running Validation first...")
            win.run_validation()
            
        if win.btn_fix.isEnabled():
            print("4. Executing Auto-Fix...")
            win.auto_fix() # This will now see 'Selection: None' and run Global
            print("SUCCESS: Global Auto-Fix Triggered.")
        else:
            print("WARNING: Auto-Fix still disabled. Are there any errors?")
            
run_global_fix()
