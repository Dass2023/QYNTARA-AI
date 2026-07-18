import math
import hashlib

class GeometricFingerprint:
    """
    Generates a deterministic 64-dimensional vector from 3D asset metadata.
    Used for similarity search and classification.
    """
    
    @staticmethod
    def generate(metadata: dict) -> list:
        # Layout: 64 floats
        vector = [0.0] * 64
        
        # [0-5] Global Scale & Complexity
        polycount = metadata.get("polycount", 0)
        vector[0] = math.log10(polycount + 1) / 6.0  # Normalized log-scale
        
        bbox_diag = metadata.get("bbox_diagonal", 0.0)
        vector[1] = min(bbox_diag, 100.0) / 100.0    # Capped at 100m
        
        # [6-8] Aspect Ratios (Shape Profile)
        # Mock assumption for now since we rely on metadata proxy
        # In real implementation: checks X/Y, Y/Z, X/Z ratios of AABB
        vector[6] = 1.0 # Cube-like default
        if "bbox_height" in metadata:
             h = metadata["bbox_height"]
             vector[6] = min(h, 10.0) / 10.0
             
        # [10-15] Topology Features
        vector[10] = 1.0 if metadata.get("is_manifold", False) else 0.0
        vector[11] = 1.0 if metadata.get("has_lods", False) else 0.0
        vector[12] = 1.0 if metadata.get("has_uvs", True) else 0.0
        
        # [20-30] Semantic Encoding (Hash of names/tags)
        # Allows "Car" and "Vehicle" to map nearby if we had embeddings
        # Here we just hash the industry key if present
        ind_key = metadata.get("industry_context", "unknown")
        ind_hash = int(hashlib.md5(ind_key.encode()).hexdigest(), 16)
        
        # Distribute hash bits into vector
        for i in range(10):
            bit = (ind_hash >> i) & 1
            vector[20 + i] = float(bit)

        # [31-40] Specific Feature Flags
        if "stress_concentrators" in metadata: vector[31] = 1.0 # Aerospace
        if "telemetry_unit" in metadata: vector[32] = 1.0 # IoT Sensor
        if "meters_per_unit" in metadata: vector[33] = 1.0 # Omniverse/USD

        return vector

    @staticmethod
    def cosine_similarity(v1: list, v2: list) -> float:
        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm_v1 = math.sqrt(sum(a * a for a in v1))
        norm_v2 = math.sqrt(sum(b * b for b in v2))
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0.0
            
        return dot_product / (norm_v1 * norm_v2)
