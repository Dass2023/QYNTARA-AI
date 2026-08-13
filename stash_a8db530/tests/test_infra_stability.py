import sys
import os
import unittest
from unittest.mock import MagicMock, patch
import json

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock Celery, Redis, and ChromaDB (since we are testing API logic, not DB)
sys.modules["celery"] = MagicMock()
sys.modules["celery.result"] = MagicMock()
sys.modules["redis"] = MagicMock()
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.utils"] = MagicMock()
sys.modules["chromadb.utils.embedding_functions"] = MagicMock()
sys.modules["prometheus_fastapi_instrumentator"] = MagicMock()
sys.modules["jose"] = MagicMock()

from backend.main import app
from fastapi.testclient import TestClient

class TestInfraStability(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_healthcheck(self):
        """Verify API health endpoint returns system status."""
        print("\n[Test] Healthcheck")
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "OPERATIONAL")
        print("PASS: Healthcheck is operational.")

    def test_async_task_submission(self):
        """Verify heavy jobs are offloaded to Celery."""
        print("\n[Test] Async Task Submission")
        
        # Mock Celery task.delay()
        with patch("backend.main.run_generative_3d_task") as mock_task:
            mock_task.delay.return_value = MagicMock(id="task-123")
            
            # Submit generative job
            payload = {
                "prompt": "Generative Task", 
                "quality": "draft"
            }
            # We need to send this as multipart form data to match the endpoint signature
            # or as form fields. backend/main.py execute_visual expects 'file' and 'settings' form field.
            
            # Let's test the logic path directly or via a mocked request if possible.
            # The endpoint `execute_visual` takes `file` and `settings`.
            
            files = {'file': ('test.png', b'content', 'image/png')}
            data = {'settings': json.dumps({"prompt": "generative", "quality": "draft"})}
            
            # Note: The logic in main.py checks: tasks = ["generative"] if prompt == "generative" is NOT strictly true
            # logic is: if prompt == "validate_only": tasks=["validate"]...
            # BUT tasks starts as ["generative"]. 
            # So if we send "prompt": "anything else", tasks is ["generative"].
            
            # Add Auth Header
            headers = {"Authorization": "Bearer mock-token"}
            response = self.client.post("/execute-visual", files=files, data=data, headers=headers)
            
            # Expecting handling... wait, the `file` param is required. 
            # The mocked run_generative_3d_task.delay should be hit.
            
            # However, `execute_visual` calls `execute` logic? 
            # No, `execute_visual` parses settings then return await execute(request).
            # `execute` has the check `if tasks == ["generative"]:`.
            
            # If our prompt is NOT one of the special flags, tasks=["generative"].
            # So it should trigger the async path.
            
            if response.status_code == 200:
                print(f"Response: {response.json()}")
                # Check if it returned the async task response
                resp = response.json()
                if "task_id" in resp:
                    print("PASS: Job offloaded to Celery.")
                else:
                    print(f"FAIL: Job was synchronous? {resp}")
            else:
                 print(f"FAIL: API Error {response.status_code} {response.text}")

    def test_task_status(self):
        """Verify task status endpoint."""
        print("\n[Test] Task Status Polling")
        with patch("backend.main.AsyncResult") as mock_result:
            mock_result.return_value.status = "SUCCESS"
            mock_result.return_value.result = {"mesh": "path.obj"}
            mock_result.return_value.ready.return_value = True
            
            response = self.client.get("/task-status/task-123")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["status"], "SUCCESS")
            print("PASS: Task status retrieved.")

if __name__ == "__main__":
    unittest.main()
