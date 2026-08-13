import pytest
import urllib.error
from unittest.mock import patch, MagicMock
from maya.nexus_api_client import (
    NexusAPIClient,
    AuthState,
    AuthError,
    AuthRequiredError,
    AuthExpiredError,
    AuthFailedError,
    APIConnectionError
)

def test_auth_state_unauthenticated():
    client = NexusAPIClient(base_url="http://localhost:8000")
    assert client.token is None
    assert client.is_authenticated() is False
    assert client.get_auth_state() == AuthState.AUTH_REQUIRED

def test_auth_state_authenticated():
    client = NexusAPIClient(base_url="http://localhost:8000")
    client.token = "valid_jwt_token"
    assert client.is_authenticated() is True
    assert client.get_auth_state() == AuthState.AUTHENTICATED

def test_missing_token_raises_auth_required_error():
    client = NexusAPIClient(base_url="http://localhost:8000")
    with pytest.raises(AuthRequiredError) as exc_info:
        client.simulate_industry("gaming", {"polycount": 10000})
    assert exc_info.value.state == AuthState.AUTH_REQUIRED
    assert "Authentication Required" in str(exc_info.value)

def test_expired_token_raises_auth_expired_error():
    client = NexusAPIClient(base_url="http://localhost:8000")
    client.token = "expired_or_invalid_jwt"
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="http://localhost:8000/validate/core",
            code=401,
            msg="Unauthorized",
            hdrs={},
            fp=None
        )
        with pytest.raises(AuthExpiredError) as exc_info:
            client.simulate_industry("gaming", {"polycount": 10000})
        assert exc_info.value.state == AuthState.AUTH_EXPIRED
        assert "Session Expired" in str(exc_info.value)

def test_connection_failure_raises_api_connection_error():
    client = NexusAPIClient(base_url="http://localhost:8000")
    client.token = "valid_token"
    
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_urlopen.side_effect = urllib.error.URLError("Connection refused")
        with pytest.raises(APIConnectionError) as exc_info:
            client.simulate_industry("gaming", {"polycount": 10000})
        assert "Could not connect to QYNTARA Core" in str(exc_info.value)

def test_authenticated_diagnostics_success():
    client = NexusAPIClient(base_url="http://localhost:8000")
    client.token = "valid_jwt_token"
    
    with patch.object(client, "post_json") as mock_post:
        mock_post.return_value = ({"status": "success", "results": []}, 200)
        data, status = client.simulate_industry("gaming", {"polycount": 10000})
        assert status == 200
        assert data["status"] == "success"
        mock_post.assert_called_with(
            "/validate/core",
            {"industry": "gaming", "metadata": {"polycount": 10000}},
            timeout=3
        )
