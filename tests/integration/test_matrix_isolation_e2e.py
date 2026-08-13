import pytest
import os
from unittest.mock import patch, MagicMock
try:
    from PySide2 import QtWidgets
except ImportError:
    from PySide6 import QtWidgets

from maya.qyntara_client import IndustryRoadmapDialog
from maya.nexus_api_client import NexusAPIClient

@pytest.fixture
def app():
    return QtWidgets.QApplication.instance() or QtWidgets.QApplication([])

@pytest.fixture
def mock_parent():
    parent = MagicMock()
    parent.api_client = NexusAPIClient(base_url="http://localhost:8000")
    parent.api_client.token = "valid_integration_token"
    return parent

def test_e2e_matrix_isolation_and_html_content_parity(app, mock_parent):
    dialog = IndustryRoadmapDialog(mock_parent)
    
    with patch.object(mock_parent.api_client, "simulate_industry") as mock_sim:
        # STEP 1: Select Gaming & Execute
        dialog.update_details(0) # Gaming
        mock_sim.return_value = ({"results": [
            {"status": "PASS", "check_name": "GPU Frame-Time", "message": "Frame Time Optimal (~2.5ms)"},
            {"status": "FAIL", "check_name": "Platform Compliance (Mobile)", "message": "Exceeds Polycount Limit"}
        ]}, 200)
        dialog.run_cloud_analysis("Gaming")
        
        # STEP 2: Switch to Film -> Attempt Report -> Verify BLOCKED
        dialog.update_details(1) # Film / VFX
        path, err = dialog.generate_industry_report("Film / VFX")
        assert path is None
        assert "[REPORT BLOCKED]" in err
        
        # STEP 3: Execute Film Diagnostics
        mock_sim.return_value = ({"results": [
            {"status": "WARNING", "check_name": "Subdivision Artifact", "message": "High pinching risk on shoulder"}
        ]}, 200)
        dialog.run_cloud_analysis("Film / VFX")
        
        # STEP 4: Generate Film Report & Validate Content Parity
        film_path, film_html = dialog.generate_industry_report("Film / VFX")
        assert film_path is not None
        assert os.path.exists(film_path)
        assert "FILM / VFX CLOUD DIAGNOSTICS" in film_html
        assert "Subdivision Artifact" in film_html
        assert "High pinching risk on shoulder" in film_html
        assert "GPU Frame-Time" not in film_html # Must NOT contain Gaming metrics!
        
        # STEP 5: Switch back to Gaming -> Generate Gaming Report & Validate Content Parity
        dialog.update_details(0) # Gaming
        gaming_path, gaming_html = dialog.generate_industry_report("Gaming")
        assert gaming_path is not None
        assert os.path.exists(gaming_path)
        assert "GAMING CLOUD DIAGNOSTICS" in gaming_html
        assert "GPU Frame-Time" in gaming_html
        assert "Platform Compliance (Mobile)" in gaming_html
        assert "Subdivision Artifact" not in gaming_html # Must NOT contain Film metrics!
