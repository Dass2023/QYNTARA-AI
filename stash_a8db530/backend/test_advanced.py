import asyncio
import os
import sys
import trimesh

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pipeline import QyntaraPipeline

async def test_advanced():
    print("--- Testing Advanced Features ---")
    
    async def print_progress(msg):
        print(f"[Pipeline] {msg}")

    pipeline = QyntaraPipeline(on_progress=print_progress)
    
    # Create a dummy mesh (Cube)
    mesh_path = "backend/data/test_cube.obj"
    mesh = trimesh.creation.box(extents=[1, 1, 1])
    mesh.export(mesh_path)
    print(f"Created test mesh: {mesh_path}")
    
    # Test 1: Quad Remeshing
    print("\n1. Testing Quad Remeshing...")
    try:
        # Note: This uses the 'backend.generative.remesher.QuadRemesher'
        # Ensure 'voxel_quad_opt' logic works or falls back gracefully
        result = await pipeline.run_quad_remeshing([mesh_path], {"target_faces": 1000})
        
        if result.mesh_path and os.path.exists(result.mesh_path):
            print(f"SUCCESS: Remeshed model saved to {result.mesh_path}")
            # Load and check faces
            remeshed = trimesh.load(result.mesh_path)
            print(f"Faces: {len(remeshed.faces)}")
        else:
            print(f"FAILED: Remeshing failed or file not found.")
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Material Assignment
    print("\n2. Testing Material Assignment...")
    try:
        material_name = "gold_polished"
        result_path = await pipeline.run_material_assignment([mesh_path], material_name)
        
        if result_path != "Failed" and os.path.exists(result_path):
            print(f"SUCCESS: Material '{material_name}' assigned.")
            print(f"Saved to: {result_path}")
        else:
            print(f"FAILED: Material assignment failed.")
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_advanced())
