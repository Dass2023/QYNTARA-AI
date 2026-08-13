"""
Qyntara AI - Maya Environment Debugger
======================================

Run this script INSIDE Maya Script Editor to diagnose environment issues.
It checks Python paths, dependencies, and Qyntara integration status.

Usage (Maya Script Editor - Python Tab):
    import sys
    sys.path.insert(0, r"i:\QYNTARA AI")
    import tests.debug_maya_env
    from importlib import reload
    reload(tests.debug_maya_env)
    tests.debug_maya_env.run_diagnostics()

Author: Dass2023
Version: 5.0.0
"""

import sys
import os
import platform
import importlib

def run_diagnostics():
    print("\n" + "="*60)
    print("QYNTARA AI - MAYA DIAGNOSTICS")
    print("="*60)
    
    # 1. Python Environment
    print(f"\n[1] Python Environment")
    print(f"    Version: {sys.version.split()[0]}")
    print(f"    Platform: {platform.system()} {platform.release()}")
    print(f"    Executable: {sys.executable}")
    
    # 2. Maya Environment
    print(f"\n[2] Maya Environment")
    try:
        import maya.cmds as cmds
        import maya.standalone
        version = cmds.about(version=True)
        print(f"    [OK] Maya Version: {version}")
        print(f"    [OK] API Version: {cmds.about(apiVersion=True)}")
    except ImportError:
        print("    [!] Not running inside Maya (maya.cmds not found)")
    
    # 3. Path Configuration
    print(f"\n[3] Path Configuration")
    project_path = r"i:\QYNTARA AI"
    path_found = False
    for p in sys.path:
        if os.path.normpath(p) == os.path.normpath(project_path):
            path_found = True
            break
            
    if path_found:
        print(f"    [OK] Project path found in sys.path")
    else:
        print(f"    [CRITICAL] Project path NOT in sys.path")
        print(f"    ACTION: sys.path.insert(0, r'{project_path}')")
    
    # 4. Qt Bindings (Pyside)
    print(f"\n[4] Qt Utilities")
    qt_binding = None
    try:
        from PySide2 import QtWidgets, QtCore
        qt_binding = "PySide2"
        print(f"    [OK] Found PySide2")
    except ImportError:
        try:
            from PySide6 import QtWidgets, QtCore
            qt_binding = "PySide6"
            print(f"    [OK] Found PySide6")
        except ImportError:
            print("    [CRITICAL] No Qt bindings (PySide2/6) found!")
            
    # 5. Qyntara Core
    print(f"\n[5] Qyntara Core")
    try:
        import qyntara_core
        print(f"    [OK] qyntara_core imported")
        print(f"    Location: {os.path.dirname(qyntara_core.__file__)}")
    except ImportError as e:
        print(f"    [FAIL] Could not import qyntara_core: {e}")

    # 6. Qyntara Maya Adapter
    print(f"\n[6] Qyntara Maya Adapter")
    try:
        import qyntara_dcc.maya as qmaya
        print(f"    [OK] qyntara_dcc.maya imported")
        
        if hasattr(qmaya, 'MayaAdapter'):
             print(f"    [OK] MayaAdapter class found")
        else:
             print(f"    [FAIL] MayaAdapter class missing in module")
             
    except ImportError as e:
        print(f"    [FAIL] Could not import qyntara_dcc.maya: {e}")
    except Exception as e:
        print(f"    [FAIL] Error loading adapter: {e}")

    print("\n" + "="*60)
    print("DIAGNOSTICS COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    run_diagnostics()
