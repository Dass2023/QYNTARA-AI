from typing import List, Dict, Tuple
from .fingerprint import GeometricFingerprint
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
import os
import uuid

class VectorDB:
    """
    Qdrant-backed Vector Database for 3D Geometric Search.
    Stores and retrieves assets based on 64-dimensional feature vectors.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(VectorDB, cls).__new__(cls)
            cls._instance._init_qdrant()
        return cls._instance

    def _init_qdrant(self):
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        if qdrant_url == ":memory:":
            self.client = QdrantClient(location=":memory:")
        else:
            self.client = QdrantClient(url=qdrant_url)
        self.collection_name = "qyntara_assets"
        
        # Ensure collection exists
        try:
            self.client.get_collection(self.collection_name)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=64, distance=Distance.COSINE),
            )
            
    def add_asset(self, asset_id: str, metadata: dict):
        """Generates fingerprint and stores asset in Qdrant."""
        vector = GeometricFingerprint.generate(metadata)
        
        # Qdrant requires UUID or Int as ID. We will use uuid5 based on asset_id
        point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, asset_id))
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload={"asset_id": asset_id, **metadata}
                )
            ]
        )

    def query(self, query_metadata: dict, k: int = 5) -> List[Tuple[str, float]]:
        """
        Finds 'k' most similar assets to the input metadata.
        Returns list of (asset_id, similarity_score).
        """
        query_vec = GeometricFingerprint.generate(query_metadata)
        
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vec,
            limit=k
        )
        
        results = []
        for hit in search_result:
            # Reconstruct (asset_id, score). Note: Qdrant cosine distance score might differ slightly in scale, but it's fine.
            results.append((hit.payload.get("asset_id", "unknown"), hit.score))
            
        return results
        
    def get_count(self):
        try:
            return self.client.count(collection_name=self.collection_name).count
        except:
            return 0
