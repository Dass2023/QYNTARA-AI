import pytest
from unittest.mock import patch, MagicMock
try:
    from PySide2 import QtWidgets, QtCore
except ImportError:
    from PySide6 import QtWidgets, QtCore

from maya.qyntara_client import IndustryRoadmapDialog
from maya.nexus_api_client import NexusAPIClient

@pytest.fixture
def app():
    """Ensure QApplication instance exists for PySide widgets."""
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.api_client = NexusAPIClient(base_url="http://localhost:8000")
    parent.api_client.token = "valid_test_token"
    return parent

def test_initial_state_has_no_reports(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    assert hasattr(dialog, 'results_by_industry')
    assert dialog.results_by_industry == {}
    assert dialog.btn_report.isVisible() is False

def test_gaming_analysis_stores_scoped_result(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "LOD", "message": "OK"}]}, 200)
        
        dialog.run_cloud_analysis("Gaming")
        
        assert "gaming" in dialog.results_by_industry
        assert dialog.results_by_industry["gaming"]["industry"] == "gaming"
        assert dialog.btn_report.isVisible() is True

def test_industry_switch_hides_un_analyzed_report_button(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "LOD", "message": "OK"}]}, 200)
        
        # Analyze Gaming
        dialog.run_cloud_analysis("Gaming")
        assert dialog.btn_report.isVisible() is True
        
        # Switch to Film (Row index 1)
        dialog.update_details(1)
        
        # Report button MUST be hidden for Film because Film analysis hasn't run
        assert dialog.btn_report.isVisible() is False
        assert "film" not in dialog.results_by_industry
        # Gaming result MUST still exist in memory
        assert "gaming" in dialog.results_by_industry

def test_un_analyzed_report_generation_blocked(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "LOD", "message": "OK"}]}, 200)
        
        # Analyze Gaming
        dialog.run_cloud_analysis("Gaming")
        
        # Attempt to generate report for Film
        path, err = dialog.generate_industry_report("Film / VFX")
        assert path is None
        assert "[REPORT BLOCKED]" in err
        assert "No diagnostic results exist for Film / VFX" in err
        assert "[REPORT BLOCKED]" in dialog.lbl_result.text()

def test_film_analysis_does_not_overwrite_gaming_result(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        # Gaming run
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "LOD", "message": "Gaming OK"}]}, 200)
        dialog.run_cloud_analysis("Gaming")
        
        # Switch to Film & run Film
        dialog.update_details(1)
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "Subd", "message": "Film OK"}]}, 200)
        dialog.run_cloud_analysis("Film / VFX")
        
        assert "gaming" in dialog.results_by_industry
        assert "film" in dialog.results_by_industry
        assert dialog.results_by_industry["gaming"]["results"][0]["message"] == "Gaming OK"
        assert dialog.results_by_industry["film"]["results"][0]["message"] == "Film OK"

def test_switch_back_restores_results_and_report_button(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        # Run Gaming
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "LOD", "message": "Gaming OK"}]}, 200)
        dialog.run_cloud_analysis("Gaming")
        
        # Switch to Film (un-analyzed)
        dialog.update_details(1)
        assert dialog.btn_report.isVisible() is False
        
        # Switch back to Gaming (Row index 0)
        dialog.update_details(0)
        assert dialog.btn_report.isVisible() is True
        assert "Gaming" in dialog.lbl_result.text()
        assert "Gaming OK" in dialog.lbl_result.text()

def test_all_12_industries_independent_isolation(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    labels = list(dialog.data.keys())
    assert len(labels) == 12
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        for idx, label in enumerate(labels):
            dialog.update_details(idx)
            mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": f"Check_{idx}", "message": f"Msg_{label}"}]}, 200)
            dialog.run_cloud_analysis(label)
            
        assert len(dialog.results_by_industry) == 12
        
        # Verify each industry has its exact isolated content
        for idx, label in enumerate(labels):
            key = label.lower().split(" ")[0]
            if "film" in label.lower(): key = "film"
            if "xr" in label.lower(): key = "xr"
            if "e-commerce" in label.lower(): key = "ecommerce"
            if "3d" in label.lower(): key = "printing"
            if "4.0" in label.lower(): key = "industry4"
            if "5.0" in label.lower(): key = "industry5"
            if "omniverse" in label.lower(): key = "omniverse"
            
            assert key in dialog.results_by_industry
            assert dialog.results_by_industry[key]["results"][0]["message"] == f"Msg_{label}"

def test_rapid_random_switching_isolation(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    indices = [0, 5, 2, 11, 0, 7, 5]
    labels = list(dialog.data.keys())
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        for idx in indices:
            label = labels[idx]
            dialog.update_details(idx)
            mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": f"Check_{idx}", "message": f"Data_{label}"}]}, 200)
            dialog.run_cloud_analysis(label)
            
    # Verify no corruption occurred during random switching
    for idx in set(indices):
        label = labels[idx]
        key = label.lower().split(" ")[0]
        if "film" in label.lower(): key = "film"
        if "xr" in label.lower(): key = "xr"
        if "e-commerce" in label.lower(): key = "ecommerce"
        if "3d" in label.lower(): key = "printing"
        if "4.0" in label.lower(): key = "industry4"
        if "5.0" in label.lower(): key = "industry5"
        if "omniverse" in label.lower(): key = "omniverse"
        
        assert dialog.results_by_industry[key]["results"][0]["message"] == f"Data_{label}"

def test_d012_all_12_industries_html_header_labels(app, mock_parent):
    from maya.industry_mapping import UI_LABEL_TO_INDUSTRY_KEY, get_ui_label
    dialog = IndustryRoadmapDialog(mock_parent)
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        for ui_label, canonical_key in UI_LABEL_TO_INDUSTRY_KEY.items():
            mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "Check", "message": "OK"}]}, 200)
            dialog.run_cloud_analysis(ui_label)
            
            path, html_content = dialog.generate_industry_report(canonical_key)
            expected_header = f"<h1>{ui_label.upper()} CLOUD DIAGNOSTICS</h1>"
            assert expected_header in html_content, f"Failed for industry {ui_label} ({canonical_key})"
            assert path.endswith(f"qyntara_report_{canonical_key}.html")

def test_d009_reset_results_clears_industry_entry_and_hides_report_button(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.update_details(0) # Gaming
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "Check1", "message": "OK"}]}, 200)
        dialog.run_cloud_analysis("Gaming")
        
        assert "gaming" in dialog.results_by_industry
        assert dialog.btn_report.isVisible()
        
        dialog.reset_industry_results("Gaming")
        
        assert "gaming" not in dialog.results_by_industry
        assert not dialog.btn_report.isVisible()
        assert dialog.lbl_result.text() == ""

def test_d009_reset_before_any_analysis(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.update_details(0)
    
    # Executing reset on an unanalyzed industry should not error and keep btn_report hidden
    dialog.reset_industry_results("Gaming")
    assert "gaming" not in dialog.results_by_industry
    assert not dialog.btn_report.isVisible()

def test_d009_repeated_reset_operations(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.update_details(0)
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "Check1", "message": "OK"}]}, 200)
        dialog.run_cloud_analysis("Gaming")
        
    dialog.reset_industry_results("Gaming")
    dialog.reset_industry_results("Gaming") # Second call
    assert "gaming" not in dialog.results_by_industry
    assert not dialog.btn_report.isVisible()

def test_d009_reset_isolation_preserves_other_industries(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        mock_sim.return_value = ({"results": [{"status": "PASS", "check_name": "Check", "message": "OK"}]}, 200)
        dialog.run_cloud_analysis("Gaming")
        dialog.run_cloud_analysis("Film / VFX")
        
    assert "gaming" in dialog.results_by_industry
    assert "film" in dialog.results_by_industry
    
    # Reset ONLY gaming
    dialog.reset_industry_results("Gaming")
    
    assert "gaming" not in dialog.results_by_industry
    assert "film" in dialog.results_by_industry # Film remains intact (D-002 preserved)


