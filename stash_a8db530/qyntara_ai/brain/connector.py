import os
import json
import logging
import time

logger = logging.getLogger(__name__)

# Try to import real clients, handle missing libs gracefully
try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    from pymilvus import connections, Collection
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False

from backend.config import settings

class VectorDBClient:
    """
    Unified Interface for Vector Database Operations.
    Automatically selects the best available backend:
    1. Pinecone (if PINECONE_API_KEY env var set)
    2. Milvus (if MILVUS_HOST env var set)
    3. Mock (Local JSON fallback)
    """
    
    def __init__(self, index_name="qyntara-memory", db_path=None):
        self.index_name = index_name
        self.db_path = db_path
        self.backend = "MOCK"
        self.client = None
        self.index = None
        
        # 1. Try Pinecone
        if PINECONE_AVAILABLE and settings.PINECONE_API_KEY:
            try:
                pinecone.init(api_key=settings.PINECONE_API_KEY, environment=settings.PINECONE_ENV)
                if index_name not in pinecone.list_indexes():
                    pinecone.create_index(index_name, dimension=1536) # OpenAI embedding dim
                self.index = pinecone.Index(index_name)
                self.backend = "PINECONE"
                logger.info(f"Connected to Pinecone Index: {index_name}")
            except Exception as e:
                logger.error(f"Pinecone Init Failed: {e}")
        
        # 2. Try Milvus (if Pinecone failed/skipped)
        if self.backend == "MOCK":
            if MILVUS_AVAILABLE and settings.MILVUS_HOST:
                try:
                    connections.connect("default", host=settings.MILVUS_HOST, port="19530")
                    # Simplified Milvus setup logic would go here
                    self.backend = "MILVUS"
                    logger.info(f"Connected to Milvus at {milvus_host}")
                except Exception as e:
                    logger.error(f"Milvus Init Failed: {e}")

        # 3. Fallback to Mock
        if self.backend == "MOCK":
            logger.warning("No External Vector DB configured. Using Local JSON Mock.")
            self.mock_store = {} 
            if self.db_path and os.path.exists(self.db_path):
                try:
                    with open(self.db_path, 'r') as f:
                        self.mock_store = json.load(f)
                    logger.info(f"Loaded {len(self.mock_store)} items from mock store: {self.db_path}")
                except Exception as e:
                    logger.error(f"Failed to load mock store: {e}")

    def upsert(self, item_id, vector, metadata=None):
        """
        Insert or Update a vector.
        """
        if self.backend == "PINECONE":
            try:
                self.index.upsert([(item_id, vector, metadata)])
                return True
            except Exception as e:
                logger.error(f"Pinecone Upsert Error: {e}")
                return False

        elif self.backend == "MILVUS":
            # Stub for Milvus insert
            pass

        else: # MOCK
            self.mock_store[item_id] = {"vector": vector, "metadata": metadata or {}}
            if self.db_path:
                try:
                    with open(self.db_path, 'w') as f:
                        json.dump(self.mock_store, f)
                except Exception as e:
                    logger.error(f"Failed to save mock store: {e}")
            return True

    def query(self, vector, top_k=5, filter=None):
        """
        Query nearest neighbors.
        """
        if self.backend == "PINECONE":
            try:
                res = self.index.query(vector=vector, top_k=top_k, include_metadata=True, filter=filter)
                return [
                    {"id": m.id, "score": m.score, "metadata": m.metadata}
                    for m in res.matches
                ]
            except Exception as e:
                logger.error(f"Pinecone Query Error: {e}")
                return []

        elif self.backend == "MILVUS":
            return []

        else: # MOCK
            # Simulated similarity: Returns the most recent items (Recent-As-Similar logic)
            results = []
            mock_items = list(self.mock_store.items())
            for uid, data in reversed(mock_items):
                if len(results) >= top_k:
                    break
                results.append({
                    "id": uid,
                    "score": 0.9, # Fake score
                    "metadata": data["metadata"]
                })
            return results

    def get_status(self):
        return {
            "backend": self.backend,
            "status": "ONLINE" if self.backend != "MOCK" else "OFFLINE (Mock)",
            "index": self.index_name
        }
