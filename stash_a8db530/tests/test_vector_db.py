import sys
import os
import unittest
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Mock chromadb BEFORE import
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.utils"] = MagicMock()
sys.modules["chromadb.utils.embedding_functions"] = MagicMock()

from backend.memory.vector_store import VectorStore

class TestVectorStore(unittest.TestCase):
    def setUp(self):
        self.vs = VectorStore()
        # Mock the collection return
        self.vs.collection = MagicMock()
        
    def test_add_item(self):
        print("\n[Test] VectorStore.add_item")
        self.vs.add_item("test_id", "test text", {"meta":"data"})
        self.vs.collection.upsert.assert_called_once()
        print("PASS: add_item called upsert.")
        
    def test_search(self):
        print("\n[Test] VectorStore.search")
        # Setup mock return for query
        # Chroma format: dict of lists
        self.vs.collection.query.return_value = {
            'ids': [['id1']],
            'metadatas': [[{'name': 'Test Asset'}]],
            'distances': [[0.1]]
        }
        
        results = self.vs.search("query")
        # Check result parsing
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['id'], 'id1')
        self.assertAlmostEqual(results[0]['score'], 0.9) # 1.0 - 0.1
        print("PASS: search parsed results correctly.")

if __name__ == "__main__":
    unittest.main()
