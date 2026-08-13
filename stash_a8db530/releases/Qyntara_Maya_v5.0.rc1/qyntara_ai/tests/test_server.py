import unittest
from fastapi.testclient import TestClient
import sys
import os
import json
from unittest.mock import MagicMock

# Mock Redis
sys.modules['redis'] = MagicMock()
mock_redis = MagicMock()
sys.modules['redis'].Redis.return_value = mock_redis

# Add path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from qyntara_ai.server.api_server import app

class TestServer(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        
    def test_submit_validation(self):
        # Setup mock
        mock_redis.set.return_value = True
        mock_redis.rpush.return_value = True
        
        response = self.client.post("/validate/", json={"file_path": "test_scene.mb"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("job_id", data)
        self.assertEqual(data["status"], "queued")
        
    def test_get_job_status(self):
        # Setup mock data for Redis get
        job_id = "test-uuid"
        mock_data = {
            "id": job_id,
            "file_path": "test.mb",
            "status": "completed",
            "report": {"summary": {"failed": 0}}
        }
        mock_redis.get.return_value = json.dumps(mock_data).encode('utf-8')
        
        response = self.client.get(f"/jobs/{job_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")

if __name__ == '__main__':
    unittest.main()
