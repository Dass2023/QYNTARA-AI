import trimesh
import numpy as np
from backend.generative.remesher import QuadRemesher

def test_remeshing():
    print("Generating sample noisy mesh...")
    # Create a sphere and add noise to simulate a raw scan/generation
    mesh = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    noise = np.random.normal(0, 0.05, mesh.vertices.shape)
    mesh.vertices += noise
    
    # Save input for comparison
    mesh.export("test_input_noisy.obj")
    
    print("Initializing Remesher...")
    remesher = QuadRemesher(resolution=64) # Lower res for fast test
    
    print("Running Remesh...")
    new_mesh = remesher.remesh(mesh, target_face_count=1000)
    
    print("Verifying Output...")
    if new_mesh.is_watertight:
        print("PASS: Mesh is watertight.")
    else:
        print("FAIL: Mesh is not watertight.")
        
    print(f"Face Count: {len(new_mesh.faces)} (Target: 1000)")
    
    new_mesh.export("test_output_remeshed.obj")
    print("Saved 'test_output_remeshed.obj'")

if __name__ == "__main__":
    test_remeshing()
