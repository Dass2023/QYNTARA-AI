import sys
import maya.OpenMayaUI as omui

print(f"Python: {sys.version}")

try:
    from PySide2 import QtWidgets
    import shiboken2
    print("PySide2 detected.")
    print(f"Shiboken Version: {shiboken2.__version__}")
    
    ptr = omui.MQtUtil.mainWindow()
    print(f"Ptr Type: {type(ptr)}")
    print(f"Ptr Value: {ptr}")
    
    try:
        win = shiboken2.wrapInstance(long(ptr), QtWidgets.QWidget)
        print("Success wrap (long)")
    except Exception as e:
        print(f"Failed wrap (long): {e}")
        
except ImportError:
    pass

try:
    from PySide6 import QtWidgets
    import shiboken6
    print("PySide6 detected.")
    print(f"Shiboken Version: {shiboken6.__version__}")
    
    ptr = omui.MQtUtil.mainWindow()
    print(f"Ptr Type: {type(ptr)}")
    print(f"Ptr Value: {ptr}")
    
    try:
        win = shiboken6.wrapInstance(int(ptr), QtWidgets.QWidget)
        print("Success wrap (int)")
    except Exception as e:
        print(f"Failed wrap (int): {e}")

except ImportError:
    pass
