import sys
import os

from PySide2.QtWidgets import QApplication
from maya.qyntara_client import QyntaraDockable

def test_ui_initialization():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # 1. Qyntara launches without error (verifies __init__ variables are safe)
    ui = QyntaraDockable()
    
    # 2. Check if session.uv_settings exists
    assert hasattr(ui, 'session'), "SessionState not initialized!"
    assert ui.session.uv_settings == {}
    
    # 3. Check if session.last_result_path exists
    assert ui.session.last_result_path is None

    print("ALL UI TESTS PASSED.")

def test_d013_industry_40_tab_contains_simulated_feed_label():
    from maya.tabs.industry_40_tab import Industry40Tab
    app = QApplication.instance() or QApplication(sys.argv)
    tab = Industry40Tab(None)
    
    # Verify header badge label
    labels = tab.findChildren(QApplication.instance().findChildren.__self__.QLabel) if hasattr(QApplication.instance(), 'findChildren') else []
    # Search all QLabel children in tab
    from PySide2.QtWidgets import QLabel
    labels = tab.findChildren(QLabel)
    
    badge_found = any("SIMULATED SENSOR FEED" in l.text() for l in labels)
    assert badge_found, "D-013 Simulation disclosure badge missing in Industry40Tab header"
    
    # Test update_telemetry prefix
    tab.update_telemetry()
    assert "SIMULATED TELEMETRY" in tab.lbl_telemetry.text()

def test_d014_matrix_window_reentrancy_reuses_existing_dialog():
    app = QApplication.instance() or QApplication(sys.argv)
    ui = QyntaraDockable()
    
    assert ui._matrix_dialog is None
    ui.show_roadmap()
    first_dialog = ui._matrix_dialog
    assert first_dialog is not None
    
    # Second call should reuse existing instance without creating a new object
    ui.show_roadmap()
    second_dialog = ui._matrix_dialog
    assert second_dialog is first_dialog, "D-014 Re-entrancy failed: duplicate IndustryRoadmapDialog instance created!"

def test_d014_matrix_window_reentrancy_handles_stale_deleted_reference():
    app = QApplication.instance() or QApplication(sys.argv)
    ui = QyntaraDockable()
    
    ui.show_roadmap()
    first_dialog = ui._matrix_dialog
    
    # Simulate window close/deletion
    first_dialog.close()
    first_dialog.deleteLater()
    
    # Force stale reference by mocking isVisible to raise RuntimeError
    from unittest.mock import patch
    with patch.object(first_dialog, "isVisible", side_effect=RuntimeError("Internal C++ object already deleted")):
        ui.show_roadmap()
        new_dialog = ui._matrix_dialog
        assert new_dialog is not first_dialog, "D-014 Stale reference recovery failed!"
        assert new_dialog is not None




