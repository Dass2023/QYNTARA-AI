import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Celery, Redis, Chroma, etc.
sys.modules["celery"] = MagicMock()
sys.modules["celery.result"] = MagicMock()
sys.modules["redis"] = MagicMock()
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.utils"] = MagicMock()
sys.modules["chromadb.utils.embedding_functions"] = MagicMock()
sys.modules["prometheus_fastapi_instrumentator"] = MagicMock()

# Mock Jose
mock_jose = MagicMock()
sys.modules["jose"] = mock_jose

# Implement fake JWT logic
token_store = {}

def mock_encode(claims, key, algorithm):
    token = f"token_{len(token_store)}"
    token_store[token] = claims
    return token

def mock_decode(token, key, algorithms):
    if token in token_store:
        return token_store[token]
    raise Exception("Invalid Token")

mock_jose.jwt.encode.side_effect = mock_encode
mock_jose.jwt.decode.side_effect = mock_decode
mock_jose.JWTError = Exception

# Import application code
from backend.main import app
from backend.security import create_access_token, Role
from backend.config import settings
from fastapi.testclient import TestClient

class TestSecurityGovernance(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_login_audit(self):
        """Verify login generates audit logs and returns role."""
        print("\n[Test] Login Audit & RBAC")
        
        with patch("backend.audit_log.AuditLog.log") as mock_log:
            # Login with correct key
            response = self.client.post("/login", data={"api_key": settings.API_KEY, "client_id": "test_user"})
            
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["role"], "admin")
            self.assertIn("access_token", data)
            
            # Verify Audit Log was called
            mock_log.assert_called_with(
                "test_user", "admin", "LOGIN", "auth", "SUCCESS", tenant_id="primary_studio"
            )
            print("PASS: Login audited and role returned.")

    def test_rbac_enforcement(self):
        """Verify VIEWER cannot access EXECUTE endpoint."""
        print("\n[Test] RBAC Enforcement")
        
        # 1. Create a Viewer Token
        viewer_token = create_access_token(
            data={"sub": "viewer_1"},
            role=Role.VIEWER,
            tenant_id="tenant_a"
        )
        
        # 2. Attempt to Execute (Should Fail)
        headers = {"Authorization": f"Bearer {viewer_token}"}
        payload = {
            "meshes": ["mesh1"], 
            "materials": ["mat1"],
            "tasks": ["validate"]
        }
        
        response = self.client.post("/execute", json=payload, headers=headers)
        
        if response.status_code == 403:
            print("PASS: Viewer was denied access to /execute (403).")
        else:
            print(f"FAIL: Viewer could access executed! Status: {response.status_code} Body: {response.text}")
            self.fail(f"FAIL: Viewer could access executed! Status: {response.status_code}")
            
    def test_audit_logging_execution(self):
        """Verify successful execution logs an audit event."""
        print("\n[Test] Execution Audit")
        
        # 1. Create User Token
        user_token = create_access_token(
            data={"sub": "worker_1"},
            role=Role.USER,
            tenant_id="tenant_b"
        )
        
        with patch("backend.audit_log.AuditLog.log") as mock_log:
            headers = {"Authorization": f"Bearer {user_token}"}
            payload = {
                "meshes": ["mesh1"], 
                "materials": ["mat1"],
                "tasks": ["validate"]
            }
            
            response = self.client.post("/execute", json=payload, headers=headers)
            
            # Should be 200 OK
            self.assertEqual(response.status_code, 200)
            
            # Verify Audit Log
            # Arguments: user_id, role, action, resource, status, details, tenant
            args, kwargs = mock_log.call_args
            
            self.assertEqual(kwargs['user_id'], "worker_1")
            self.assertEqual(kwargs['role'], "user")
            self.assertEqual(kwargs['action'], "EXECUTE_PIPELINE")
            self.assertEqual(kwargs['tenant_id'], "tenant_b")
            
            print("PASS: Execution event audited with Tenant ID.")

if __name__ == "__main__":
    unittest.main()
