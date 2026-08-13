import pytest
import json
import urllib.request
import urllib.error
from unittest.mock import patch, MagicMock
from maya.nexus_api_client import NexusAPIClient, AuthExpiredError, APIConnectionError

@pytest.fixture
def client():
    c = NexusAPIClient(base_url="http://fake.api")
    c.token = "fake_token"
    return c

def test_request_construction(client):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = b'{"status": "ok"}'
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response

        data, status = client._request("/test", method="GET")
        
        assert status == 200
        assert data == b'{"status": "ok"}'
        
        # Verify the Request object
        args, kwargs = mock_urlopen.call_args
        req = args[0]
        assert req.full_url == "http://fake.api/test"
        assert req.method == "GET"

def test_auth_header_injection(client):
    client.token = "fake_token"
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        client._request("/secure", method="GET")
        
        req = mock_urlopen.call_args[0][0]
        assert req.get_header("Authorization") == "Bearer fake_token"

def test_http_401_normalization(client):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://fake.api/secure",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None
        )
        
        with pytest.raises(AuthExpiredError):
            client._request("/secure", method="GET")

def test_connection_error_normalization(client):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        
        with pytest.raises(APIConnectionError):
            client._request("/test")

def test_login_success(client):
    with patch.object(client, "_request") as mock_req:
        mock_req.return_value = (b'{"access_token": "new_token"}', 200)
        
        success = client.login("my_key")
        
        assert success is True
        assert client.token == "new_token"
        mock_req.assert_called_with(
            "/login",
            method="POST",
            data=b'{"api_key": "my_key"}',
            headers={"Content-Type": "application/json"},
            timeout=5
        )

def test_json_get(client):
    with patch.object(client, "_request") as mock_req:
        mock_req.return_value = (b'{"key": "value"}', 200)
        
        data, status = client.request_json("/data")
        assert data == {"key": "value"}
        assert status == 200

def test_json_post(client):
    with patch.object(client, "_request") as mock_req:
        mock_req.return_value = (b'{"success": true}', 200)
        
        data, status = client.post_json("/submit", {"payload": 123})
        
        assert data == {"success": True}
        assert status == 200
        mock_req.assert_called_with(
            "/submit",
            method="POST",
            data=b'{"payload": 123}',
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            timeout=30
        )

def test_download_file(client, tmp_path):
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = b'fake_data'
        mock_urlopen.return_value.__enter__.return_value = mock_response
        
        target = tmp_path / "test.obj"
        success = client.download_file("/static/test.obj", str(target))
        
        assert success is True
        assert target.read_bytes() == b'fake_data'
        req = mock_urlopen.call_args[0][0]
        assert req.full_url == "http://fake.api/static/test.obj"

def test_upload_multipart(client):
    with patch.object(client, "_request") as mock_req:
        mock_req.return_value = (b'{"path": "/static/uploads/test.obj"}', 200)
        
        # We need a dummy file
        import tempfile, os
        fd, path = tempfile.mkstemp()
        with os.fdopen(fd, 'wb') as f:
            f.write(b'file_data')
            
        try:
            result_path = client.upload_multipart("/upload", path)
            assert result_path == "/static/uploads/test.obj"
            
            # Verify it set multipart header
            args, kwargs = mock_req.call_args
            assert "multipart/form-data" in kwargs["headers"]["Content-Type"]
            assert kwargs["method"] == "POST"
        finally:
            os.remove(path)

def test_predict_risk(client):
    with patch.object(client, "post_json") as mock_post:
        mock_post.return_value = ({"risk_score": 0.8, "prediction": "Fail", "reasons": "NGons"}, 200)
        
        score, pred, reason = client.predict_risk(5000, True)
        assert score == 0.8
        assert pred == "Fail"
        assert reason == "NGons"
        mock_post.assert_called_with("/ai/predict", {"polycount": 5000, "has_ngons": True})

def test_generate_seam_uv(client):
    with patch.object(client, "post_json") as mock_post:
        mock_post.return_value = ({"cut_edges": [1, 2, 3]}, 200)
        
        edges = client.generate_seam_uv("/path/to/mesh.obj")
        assert edges == [1, 2, 3]
        mock_post.assert_called_with("/ai/seam-gpt", {"mesh_path": "/path/to/mesh.obj"})

def test_fetch_stats(client):
    with patch.object(client, "request_json") as mock_req:
        mock_req.return_value = ({"active_jobs": 5}, 200)
        
def test_simulate_industry(client):
    client.token = "test_token"
    with patch.object(client, "post_json") as mock_post:
        mock_post.return_value = ({"results": [{"status": "PASS", "check_name": "x", "message": "y"}]}, 200)
        
        data, status = client.simulate_industry("aerospace", {"stress_concentrators": 0})
        
        assert status == 200
        assert data["results"][0]["status"] == "PASS"
        mock_post.assert_called_with(
            "/validate/core", 
            {"industry": "aerospace", "metadata": {"stress_concentrators": 0}},
            timeout=3
        )
