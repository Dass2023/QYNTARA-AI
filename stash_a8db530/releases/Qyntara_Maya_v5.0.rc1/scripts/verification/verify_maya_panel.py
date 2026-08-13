"""
Manual Verification Script: Industry 5.0 Panel

This script launches the Qyntara Validator UI in a standalone PySide environment (if available).
Run this script to verify the 'INDUSTRY 5.0' tab is present and functional.
"""

import sys
import os

# Set project root (adjust if needed)
PROJECT_ROOT = r"i:\QYNTARA AI"
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)
    # Add maya submodule path explicitly if needed, but QyntaraMainWindow uses relative imports
    # so we need to be careful about where we import from.
    # qyntara_ai is a package in root.

try:
    from PySide2 import QtWidgets
except ImportError:
    try:
        from PySide6 import QtWidgets
    except ImportError:
        print("PySide not found. This test requires a Maya environment or PySide installed.")
        sys.exit(1)

# Import the VALIDATOR Main Window, not the deprecated dockable client
from qyntara_ai.ui.main_window import QyntaraMainWindow

def main():
    app = QtWidgets.QApplication.instance()
    if not app:
        app = QtWidgets.QApplication(sys.argv)
    
    # Initialize Main Window (Validator Style)
    window = QyntaraMainWindow()
    window.show()
    
    print("Launched Qyntara Validator UI.")
    print("Verify Tab Order:")
    print("  [0] INDUSTRY 4.0 (Smart Factory)")
    print("  [1] INDUSTRY 5.0 (Predictive AI)")
    print("  [2] Validation")
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
