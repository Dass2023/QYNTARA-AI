import pytest
from unittest.mock import patch, MagicMock
try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets

from maya.qyntara_client import IndustryRoadmapDialog
from maya.nexus_api_client import NexusAPIClient
from maya.industry_mapping import UI_LABEL_TO_INDUSTRY_KEY, get_canonical_key

@pytest.fixture
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.api_client = NexusAPIClient(base_url="http://localhost:8000")
    parent.api_client.token = "valid_mapping_integration_token"
    return parent

def test_all_12_industries_end_to_end_key_chain(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    dialog.parent = lambda: mock_parent
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        for ui_label, expected_canonical_key in UI_LABEL_TO_INDUSTRY_KEY.items():
            # Set return value matching expected canonical key
            mock_sim.return_value = ({
                "status": "success",
                "industry": expected_canonical_key,
                "results": [{"status": "PASS", "check_name": f"{expected_canonical_key}_check", "message": "OK"}]
            }, 200)
            
            # Run cloud analysis using UI label
            dialog.run_cloud_analysis(ui_label)
            
            # 1. Verify API was called with exact canonical key (not UI label)
            args, kwargs = mock_sim.call_args
            actual_request_key = args[0]
            assert actual_request_key == expected_canonical_key, f"Expected API request key '{expected_canonical_key}', got '{actual_request_key}' for label '{ui_label}'"
            
            # 2. Verify stored result entry carries canonical key
            assert expected_canonical_key in dialog.results_by_industry
            stored_entry = dialog.results_by_industry[expected_canonical_key]
            assert stored_entry["industry"] == expected_canonical_key
            assert stored_entry["ui_label"] == ui_label
            
            # 3. Generate HTML report and verify canonical key & UI label in HTML output
            report_path, html_content = dialog.generate_industry_report(ui_label)
            assert report_path is not None
            assert f"qyntara_cloud_report_{expected_canonical_key}.html" in report_path
            assert f"{ui_label.upper()} CLOUD DIAGNOSTICS" in html_content
