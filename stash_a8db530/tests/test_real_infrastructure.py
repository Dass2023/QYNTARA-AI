import unittest
import os
import sys

# Add project root
sys.path.insert(0, r"i:\QYNTARA AI")

from qyntara_ai.brain.connector import VectorDBClient
from qyntara_ai.cloud.k8s_client import KubernetesConnector

class TestRealInfrastructure(unittest.TestCase):
    
    def setUp(self):
        # Ensure no real keys leak into test environment unintentionally
        if "PINECONE_API_KEY" in os.environ:
            del os.environ["PINECONE_API_KEY"]
        if "KUBECONFIG" in os.environ:
            del os.environ["KUBECONFIG"]

    def test_vector_db_fallback(self):
        print("\nTesting Vector DB Connector Fallback...")
        client = VectorDBClient()
        
        # Should default to MOCK
        self.assertEqual(client.backend, "MOCK")
        
        # Test Operation
        res = client.upsert("test_item", [0.1, 0.2])
        self.assertTrue(res)
        
        query = client.query([0.1, 0.2])
        self.assertEqual(len(query), 1)
        self.assertEqual(query[0]["id"], "test_item")
        print("Vector DB Fallback OK.")

    def test_k8s_fallback(self):
        print("\nTesting K8s Connector Fallback...")
        # Force mock by ensuring no config loads (mocked in setUp usually, but here relies on env)
        k8s = KubernetesConnector()
        
        # Should default to MOCK (unless creating this test accidentally runs inside a cluster!)
        # Safe assumption for local dev:
        if k8s.backend == "KUBERNETES":
            print("WARNING: Real K8s Environment Detected! Skipping fallback test.")
        else:
            self.assertEqual(k8s.backend, "MOCK")
            
            # Test Operation
            job = k8s.create_gpu_pod("job_123")
            self.assertEqual(job["status"], "RUNNING")
            self.assertIn("127.0.0.1", job["ip"])
            
            # Test Delete
            deleted = k8s.delete_pod(job["pod_id"])
            self.assertTrue(deleted)
            
            print("K8s Connector Fallback OK.")

if __name__ == '__main__':
    unittest.main()
