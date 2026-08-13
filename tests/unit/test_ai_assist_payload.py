import pytest
import os
from unittest.mock import MagicMock, patch
from maya.qyntara_client import QyntaraDockable
from maya.job_orchestrator import JobOrchestrator

@pytest.fixture
def client():
    # Bypass Maya UI creation completely for the test to avoid StrictMayaCmdsMock issues
    with patch.object(QyntaraDockable, '__init__', return_value=None):
        c = QyntaraDockable()
        c.job_orchestrator = MagicMock(spec=JobOrchestrator)
        
        # Manually mock the UI elements needed for testing
        c.prompt_input = MagicMock()
        c.prompt_input.toPlainText.return_value = ""
        c.img_path_input = MagicMock()
        c.img_path_input.text.return_value = ""
        c.quality_combo = MagicMock()
        c.quality_combo.currentText.return_value = "DRAFT (Fast)"
        
        c.style_btns = []
        for style in ["Cyberpunk", "Organic", "Hard Surface", "Low Poly"]:
            btn = MagicMock()
            btn.text.return_value = style
            btn.isChecked.return_value = False
            c.style_btns.append(btn)
            
        c.btn_gen_submit = MagicMock()
        c.btn_gen_submit.isEnabled.return_value = True
        
        c.btn_auto_full = MagicMock()
        c.btn_auto_full.isEnabled.return_value = True
        
        c.btn_vibe = MagicMock()
        
        # Mock show_message so tests don't popup dialogues
        c.show_message = MagicMock()
        c.set_status = MagicMock()
        c.progress_dialog = None
        
        return c

def test_prompt_only_generation(client):
    client.prompt_input.toPlainText.return_value = "organic sci-fi helmet"
    client.img_path_input.text.return_value = ""
    
    # Mock quality & style
    client.quality_combo.currentText.return_value = "DRAFT (Fast)"
    
    with patch.object(client, 'submit_job') as mock_submit:
        client.submit_gen_job()
        
        mock_submit.assert_called_once()
        args, kwargs = mock_submit.call_args
        assert kwargs["tasks"] == ["generate_3d"]
        
        settings = kwargs["custom_settings"]["generative_settings"]
        assert settings["prompt"] == "organic sci-fi helmet"
        assert settings["quality"] == "draft"
        assert settings["provider"] == "internal"
        assert kwargs["custom_mesh_path"] is None
        
        # Async Safety check
        client.btn_gen_submit.setEnabled.assert_called_with(False)

@patch('os.path.exists', return_value=True)
@patch('os.path.getsize', return_value=1024)
def test_image_context_generation(mock_size, mock_exists, client):
    client.prompt_input.toPlainText.return_value = ""
    client.img_path_input.text.return_value = "C:/valid_image.png"
    
    with patch.object(client, 'submit_job') as mock_submit:
        client.submit_gen_job()
        
        mock_submit.assert_called_once()
        args, kwargs = mock_submit.call_args
        assert kwargs["tasks"] == ["generate_3d"]
        assert kwargs["custom_mesh_path"] == "C:/valid_image.png"

def test_style_selection(client):
    client.prompt_input.toPlainText.return_value = "test prompt"
    # Select Cyberpunk style
    for btn in client.style_btns:
        if btn.text() == "Cyberpunk":
            btn.isChecked.return_value = True
            break
            
    with patch.object(client, 'submit_job') as mock_submit:
        client.submit_gen_job()
        settings = mock_submit.call_args[1]["custom_settings"]["generative_settings"]
        assert settings["style"] == "Cyberpunk"

def test_quality_draft(client):
    client.prompt_input.toPlainText.return_value = "test prompt"
    client.quality_combo.currentText.return_value = "DRAFT (Fast)"
    with patch.object(client, 'submit_job') as mock_submit:
        client.submit_gen_job()
        settings = mock_submit.call_args[1]["custom_settings"]["generative_settings"]
        assert settings["quality"] == "draft"

def test_quality_high_fidelity(client):
    client.prompt_input.toPlainText.return_value = "test prompt"
    client.quality_combo.currentText.return_value = "HIGH FIDELITY (Slow)"
    with patch.object(client, 'submit_job') as mock_submit:
        client.submit_gen_job()
        settings = mock_submit.call_args[1]["custom_settings"]["generative_settings"]
        assert settings["quality"] == "high"

@patch('os.path.exists', return_value=True)
@patch('os.path.getsize', return_value=1024)
def test_combined_image_style_quality(mock_size, mock_exists, client):
    client.prompt_input.toPlainText.return_value = "test prompt"
    client.img_path_input.text.return_value = "test.jpg"
    client.quality_combo.currentText.return_value = "HIGH FIDELITY (Slow)"
    client.style_btns[1].isChecked.return_value = True # Organic
    
    with patch.object(client, 'submit_job') as mock_submit:
        client.submit_gen_job()
        kwargs = mock_submit.call_args[1]
        settings = kwargs["custom_settings"]["generative_settings"]
        assert settings["prompt"] == "test prompt"
        assert settings["quality"] == "high"
        assert settings["style"] == "Organic"
        assert kwargs["custom_mesh_path"] == "test.jpg"

@patch('maya.cmds.ls', return_value=[]) # No selection
def test_auto_full_pipeline(mock_ls, client):
    client.prompt_input.toPlainText.return_value = "a spaceship"
    client.quality_combo.currentText.return_value = "HIGH FIDELITY (Slow)"
    client.img_path_input.text.return_value = ""
    with patch.object(client, 'submit_job') as mock_submit:
        client.run_full_pipeline()
        kwargs = mock_submit.call_args[1]
        assert "generate_3d" in kwargs["tasks"]
        assert "optimization_export" in kwargs["tasks"]
        settings = kwargs["custom_settings"]["generative_settings"]
        assert settings["prompt"] == "a spaceship"
        client.btn_auto_full.setEnabled.assert_called_with(False)

def test_duplicate_click_protection(client):
    client.prompt_input.toPlainText.return_value = "test"
    with patch.object(client, 'submit_job'):
        client.submit_gen_job()
        client.btn_gen_submit.setEnabled.assert_called_with(False)

def test_worker_failure_restores_ui(client):
    client._on_orchestrator_failed({"message": "error"})
    client.btn_gen_submit.setEnabled.assert_called_with(True)

def test_worker_success_restores_ui(client):
    # mock process_backend_result to avoid Maya errors
    client.process_backend_result = MagicMock()
    client._on_orchestrator_completed({})
    client.btn_gen_submit.setEnabled.assert_called_with(True)

def test_worker_cancel_restores_ui(client):
    client._on_progress_cancelled()
    client.btn_gen_submit.setEnabled.assert_called_with(True)

@patch('os.path.exists', return_value=False)
def test_invalid_image_path(mock_exists, client):
    client.img_path_input.text.return_value = "non_existent.png"
    with patch.object(client, 'show_message') as mock_msg:
        client.submit_gen_job()
        mock_msg.assert_called_once()
        assert "not found" in mock_msg.call_args[0][1]

@patch('os.path.exists', return_value=True)
@patch('os.path.getsize', return_value=1024)
def test_unsupported_image(mock_size, mock_exists, client):
    client.img_path_input.text.return_value = "invalid.pdf"
    with patch.object(client, 'show_message') as mock_msg:
        client.submit_gen_job()
        mock_msg.assert_called_once()
        assert "Unsupported" in mock_msg.call_args[0][1]

@patch('os.path.exists', return_value=True)
@patch('os.path.getsize', return_value=60 * 1024 * 1024) # 60MB
def test_oversized_image(mock_size, mock_exists, client):
    client.img_path_input.text.return_value = "large.png"
    with patch.object(client, 'show_message') as mock_msg:
        client.submit_gen_job()
        mock_msg.assert_called_once()
        assert "too large" in mock_msg.call_args[0][1]

def test_empty_prompt_and_image(client):
    client.prompt_input.toPlainText.return_value = "   "
    client.img_path_input.text.return_value = ""
    with patch.object(client, 'show_message') as mock_msg:
        client.submit_gen_job()
        mock_msg.assert_called_once()
        assert "enter a prompt" in mock_msg.call_args[0][1]

def test_backend_filename_collision():
    # Verify the backend pipeline doesn't use hardcoded paths
    with open(os.path.join(os.path.dirname(__file__), '../../backend/pipeline.py'), 'r') as f:
        content = f.read()
        assert "uuid.uuid4()" in content
        assert "gen_model.obj" not in content.replace("gen_model_{gen_id}.obj", "")
