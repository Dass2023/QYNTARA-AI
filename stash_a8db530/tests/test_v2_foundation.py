import unittest
import os
import shutil
import time
import sys

# Add project root
sys.path.insert(0, r"i:\QYNTARA AI")

from qyntara_ai.brain.knowledge_base import KnowledgeBase
from qyntara_ai.brain.rlhf import ReinforcementLoop
from qyntara_ai.cloud.orchestrator import CloudOrchestrator

class TestV2Foundation(unittest.TestCase):
    
    def setUp(self):
        # Use temp dir for tests
        self.test_dir = r"i:\QYNTARA AI\tests\temp_brain"
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.kb_path = os.path.join(self.test_dir, "test_mem.json")
        self.rl_path = os.path.join(self.test_dir, "test_rl.json")
        
    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_knowledge_base(self):
        print("\nTesting Cognitive Memory...")
        kb = KnowledgeBase(db_path=self.kb_path)
        
        # Test Store
        kb.store_embedding("asset_001", [0.1, 0.2, 0.3], {"tags": ["chair"]})
        kb.store_embedding("asset_002", [0.9, 0.8, 0.7], {"tags": ["table"]})
        
        self.assertEqual(len(kb.memory), 2)
        
        # Test Persistence
        kb2 = KnowledgeBase(db_path=self.kb_path)
        self.assertEqual(len(kb2.memory), 2)
        
        # Test Query
        res = kb.query_similar([0.1, 0.2, 0.3], top_k=1)
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]["id"], "asset_002") # Logic is "Recent" in mock
        
        print("KnowledgeBase OK.")

    def test_rlhf_loop(self):
        print("\nTesting Reinforcement Loop...")
        rl = ReinforcementLoop(log_path=self.rl_path)
        
        # Test Feedback
        rl.record_feedback("asset_001", "ACCEPT", {"model": "v1.0"})
        rl.record_feedback("asset_002", "REJECT", {"model": "v1.0"})
        rl.record_feedback("asset_003", "ACCEPT", {"model": "v1.0"})
        
        # Test Score
        score = rl.calculate_model_score("v1.0")
        self.assertAlmostEqual(score, 66.666, places=1)
        
        print(f"Model Score: {score:.1f}%")
        print("RLHF Loop OK.")

    def test_cloud_grid(self):
        print("\nTesting Cloud Grid...")
        cloud = CloudOrchestrator()
        
        # Test Provision
        res = cloud.request_gpu_instance("lrm-v2")
        self.assertEqual(res["status"], "RUNNING")
        
        stats = cloud.get_cluster_stats()
        self.assertEqual(stats["active_pods"], 1)
        
        # Test Release
        cloud.release_instance(res["pod_id"])
        stats = cloud.get_cluster_stats()
        self.assertEqual(stats["active_pods"], 0)
        
        print("Cloud Grid OK.")

if __name__ == '__main__':
    unittest.main()
