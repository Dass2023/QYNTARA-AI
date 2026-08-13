import sys
import os
import unittest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mocking dependencies
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.config"] = MagicMock()
sys.modules["chromadb.utils"] = MagicMock() 
sys.modules["chromadb.utils"].embedding_functions = MagicMock()
sys.modules["prometheus_fastapi_instrumentator"] = MagicMock()
sys.modules["celery"] = MagicMock()
sys.modules["celery.result"] = MagicMock()
sys.modules["jose"] = MagicMock()
sys.modules["jose"].jwt = MagicMock()
sys.modules["jose"].JWTError = Exception

from fastapi.testclient import TestClient
from backend.models import ValidationReport, GeometryValidation, UVValidation, MaterialValidation, TopologyValidation
from backend.main import app, get_current_user
from backend.security import Role

class TestAutonomyIntegration(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
        # Override Auth Dependency
        def mock_get_current_user():
            return {
                "sub": "user_123",
                "role": "user",
                "tenant_id": "tenant_default"
            }
        app.dependency_overrides[get_current_user] = mock_get_current_user

    @patch("backend.pipeline.QyntaraPipeline.run_validation")
    @patch("backend.pipeline.QyntaraPipeline.run_autonomous_remediation")
    @patch("backend.pipeline.QyntaraPipeline.run_sam_segmentation")
    @patch("backend.pipeline.QyntaraPipeline.run_autodesk_validation")
    def test_auto_fix_trigger(self, mock_auto, mock_sam, mock_remediate, mock_validate):
        """Verify API triggers remediation on low score."""
        
        # 1. Mock Validation Failure (Score 45 - Repairable)
        fail_report = ValidationReport(
            geometry=GeometryValidation(watertight=False, issues=["Holes"]),
            uv=UVValidation(),
            material=MaterialValidation(),
            topology=TopologyValidation(),
            passed=False,
            score=45.0
        )
        mock_validate.return_value = fail_report
        
        # 2. Mock Remediation Success
        mock_remediate.return_value = (["mesh_fixed.obj"], ["Filled holes"])
        
        # 3. Mock other calls
        mock_sam.return_value = MagicMock()
        mock_auto.return_value = MagicMock()

        # 4. Execute Request
        payload = {
            "meshes": ["broken_mesh.obj"],
            "materials": [],
            "tasks": ["validate"],
            "validation_profile": "GENERIC",
            "auto_fix": True
        }
        
        response = self.client.post("/execute", json=payload)
        
        # 5. Assertions
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        # Verify Remediation Triggered
        mock_remediate.assert_called_once()
        print("\n[Integration] Auto-Fix triggered successfully.")
        
        # Verify Response Status updated
        self.assertEqual(data["status"], "remediated")
        self.assertIn("Auto-Fixed: Filled holes", str(data["validationReport"]["issues"]))
        print("[Integration] Status updated to 'remediated'.")

if __name__ == "__main__":
    unittest.main()
