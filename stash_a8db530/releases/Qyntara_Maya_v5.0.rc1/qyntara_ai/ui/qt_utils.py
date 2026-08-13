import sys

# Try PySide2 first (Maya 2022-2024)
try:
    from PySide2 import QtWidgets, QtCore, QtGui
    from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QCheckBox
    import maya.OpenMayaUI as omui
    from shiboken2 import wrapInstance
    QT_VERSION = 2
except ImportError:
    # Try PySide6 (Maya 2025+)
    try:
        from PySide6 import QtWidgets, QtCore, QtGui
        from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QCheckBox
        import maya.OpenMayaUI as omui
        from shiboken6 import wrapInstance
        QT_VERSION = 6
    except ImportError:
        # Fallback for dev environment without Maya
        from PySide2 import QtWidgets, QtCore, QtGui
        from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QScrollArea, QCheckBox
        omui = None
        wrapInstance = None
        QT_VERSION = 0

def get_maya_window():
    """
    Get the Maya main window as a QWidget.
    """
    if omui and wrapInstance:
        ptr = omui.MQtUtil.mainWindow()
        if ptr:
            try:
                # Ensure pointer is cast to int address for shiboken
                return wrapInstance(int(ptr), QWidget)
            except Exception as e:
                # Fallback: if wrapping fails, just return None (unparented window)
                print(f"Warning: Could not wrap Maya window: {e}")
                return None
    return None
