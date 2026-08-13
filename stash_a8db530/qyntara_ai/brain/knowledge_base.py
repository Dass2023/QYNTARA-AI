import logging
import uuid
import time
from .connector import VectorDBClient

logger = logging.getLogger(__name__)

class KnowledgeBase:
    """
    Qyntara Cognitive Memory (The Brain).
    
    Responsible for:
    - Storing asset embeddings (Semantic Memory).
    - Querying similar assets by vector or metadata.
    - Interfacing with Vector DBs via VectorDBClient.
    
    Current Implementation: v2.0-Beta (Connector Integrated)
    """
    
    @property
    def memory(self):
        """Mock persistence emulator for tests."""
        if hasattr(self.db, 'mock_store'):
            return self.db.mock_store
        return {}

    def __init__(self, index_name="qyntara-memory", db_path=None):
        self.db = VectorDBClient(index_name=index_name, db_path=db_path)
        logger.info(f"KnowledgeBase initialized using backend: {self.db.backend}")

    def store_embedding(self, asset_id, vector, metadata=None):
        """
        Stores a semantic memory.
        """
        return self.db.upsert(asset_id, vector, metadata)

    def query_similar(self, vector, top_k=5):
        """
        Finds semantically similar assets.
        """
        # In a real scenario, this returns matches with scores
        return self.db.query(vector, top_k)

    def get_stats(self):
        status = self.db.get_status()
        return {
            "status": "ONLINE",
            "provider": status["backend"],
            "index": status["index"]
        }
