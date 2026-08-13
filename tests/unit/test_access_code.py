import os
import sys
import unittest
from unittest.mock import patch
from maya.qyntara_client import QyntaraDockable
from PySide2.QtWidgets import QApplication

class TestAccessCode(unittest.TestCase):
    def setUp(self):
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

    @patch.dict(os.environ, {"QYNTARA_ACCESS_CODE": ""}, clear=False)
    def test_access_code_empty(self):
        ui = QyntaraDockable()
        ui.auth_input.setText.assert_any_call("")

    @patch.dict(os.environ, {"QYNTARA_ACCESS_CODE": "TEST_TOKEN_123"}, clear=False)
    def test_access_code_provided(self):
        ui = QyntaraDockable()
        ui.auth_input.setText.assert_any_call("TEST_TOKEN_123")

    @patch.dict(os.environ, clear=True)
    def test_access_code_missing_env(self):
        # Even if completely missing, it should default to empty string safely
        ui = QyntaraDockable()
        ui.auth_input.setText.assert_any_call("")
