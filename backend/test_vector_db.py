from backend.qyntara_core.vector_db import VectorDB

def test_vector_db():
    print("--- Testing Vector Database & Geometric Search ---")
    db = VectorDB()
    
    # 1. Add "Cube-like" Assets
    db.add_asset("Cube_01", {"polycount": 12, "bbox_diagonal": 1.73, "bbox_height": 1.0, "is_manifold": True})
    db.add_asset("Cube_02", {"polycount": 12, "bbox_diagonal": 1.75, "bbox_height": 1.01, "is_manifold": True})
    
    # 2. Add "Sphere-like" Assets
    db.add_asset("Sphere_01", {"polycount": 5000, "bbox_diagonal": 1.0, "bbox_height": 1.0, "is_manifold": True})
    db.add_asset("Sphere_HighRes", {"polycount": 50000, "bbox_diagonal": 1.0, "bbox_height": 1.0, "is_manifold": True})
    
    # 3. Add "Complex" Asset
    db.add_asset("Engine_Block", {"polycount": 150000, "bbox_diagonal": 12.0, "is_manifold": True, "industry_context": "automotive"})
    
    print(f"Database Size: {db.get_count()} vectors.")
    
    # --- SEARCH TEST 1: Find Similar to Cube ---
    query_cube = {"polycount": 12, "bbox_diagonal": 1.74, "bbox_height": 1.0}
    results = db.query(query_cube, k=3)
    
    print("\nQuery: 'Cube-like' Asset")
    for asset_id, score in results:
        print(f"  > Found: {asset_id} (Similarity: {score:.4f})")
        
    top_match = results[0][0]
    if "Cube" in top_match:
        print(">> SUCCESS: Vector Search correctly identified geometric sibling.")
    else:
        print(f">> FAIL: Expected Cube, got {top_match}")

    # --- SEARCH TEST 2: Find Similar to Engine ---
    query_engine = {"polycount": 140000, "bbox_diagonal": 11.5, "industry_context": "automotive"}
    results = db.query(query_engine, k=1)
    print("\nQuery: 'Engine-like' Asset")
    print(f"  > Found: {results[0][0]} (Similarity: {results[0][1]:.4f})")
    
    if results[0][0] == "Engine_Block":
        print(">> SUCCESS: Semantic + Geometric match confirmed.")
    
if __name__ == "__main__":
    test_vector_db()
