
import sys
import unittest
from unittest.mock import MagicMock

# 1. Setup Mocks BEFORE imports
sys.modules["maya"] = MagicMock()
sys.modules["maya.cmds"] = MagicMock()
sys.modules["maya.api"] = MagicMock()
sys.modules["maya.api.OpenMaya"] = MagicMock()
sys.modules["maya.OpenMayaUI"] = MagicMock()
sys.modules["shiboken2"] = MagicMock()
sys.modules["shiboken6"] = MagicMock()
sys.modules["PySide2"] = MagicMock()
sys.modules["PySide2.QtWidgets"] = MagicMock()
sys.modules["PySide2.QtCore"] = MagicMock()
sys.modules["PySide2.QtGui"] = MagicMock()

# Mock specific cmds needed for validator init/run
mock_cmds = sys.modules["maya.cmds"]
mock_cmds.select = MagicMock()
mock_cmds.polySelectConstraint = MagicMock()
mock_cmds.objectType.return_value = "transform"
mock_cmds.listRelatives.return_value = ["shape1"]

# 2. Add path
sys.path.insert(0, r"e:\QYNTARA AI")

# 3. Import Target
try:
    from qyntara_ai.core.validator import QyntaraValidator
    print("SUCCESS: Validator imported successfully.")
except ImportError as e:
    print(f"FAILURE: Could not import Validator: {e}")
    sys.exit(1)
except Exception as e:
    print(f"FAILURE: Exception during import: {e}")
    sys.exit(1)

# 4. Run Test
try:
    val = QyntaraValidator()
    print("Validator initialized.")
    # Run a simple validation to trigger the code paths that use 'cmds'
    # We mock 'ls' etc to return something so it enters loops
    
    report = val.run_validation(["pCube1"])
    print("Validation run complete.")
    print("Summary:", report['summary'])
    
    # Check if we got through without NameError
    print("TEST PASSED: No NameError encountered for 'cmds'.")
    
except NameError as e:
    print(f"TEST FAILED: NameError detected: {e}")
    print("This likely means 'cmds' is missing from imports in validator.py")
except Exception as e:
    print(f"TEST FAILED: Runtime error: {e}")
