import trimesh
import os
import requests
import json
import numpy as np
import time

def test_quad_remesher():
    print("\n--- Testing QuadRemesher ---")
    from generative.remesher import QuadRemesher
    
    # Load sample mesh
    mesh_path = "data/test_cube.obj"
    mesh = trimesh.load(mesh_path)
    
    remesher = QuadRemesher()
    
    # Test 1: Basic Remesh
    print("Test 1: Basic Remesh...")
    result = remesher.remesh(mesh, config_dict={"target_quad_count": 1000})
    print(f"Status: {result.status}")
    if result.status == "SUCCESS":
        print(f"Metrics: {result.metrics}")
        # Verify result mesh
        out_mesh = result.output_mesh
        print(f"Output Mesh: {len(out_mesh.vertices)} vertices, {len(out_mesh.faces)} faces")
    else:
        print(f"Error: {result.message}")

    # Test 2: Symmetry
    print("\nTest 2: Symmetry Remesh (X-axis)...")
    result_sym = remesher.remesh(mesh, config_dict={
        "target_quad_count": 1000,
        "symmetry": {"enabled": True, "axis": "x"}
    })
    print(f"Status: {result_sym.status}")
    if result_sym.status == "SUCCESS":
        print(f"Symmetry Error: {result_sym.metrics.get('symmetry_error')}")

def test_mesh_optimizer():
    print("\n--- Testing MeshOptimizer ---")
    from generative.mesh_optimizer import MeshOptimizer
    
    mesh_path = "data/test_cube.obj"
    mesh = trimesh.load(mesh_path)
    optimizer = MeshOptimizer()
    
    # Test 1: Reduction
    print("Test 1: Triangle Reduction (0.5 ratio)...")
    res_red = optimizer.reduce_triangles(mesh, {"target_ratio": 0.5})
    print(f"Status: {res_red.status}")
    if res_red.status == "SUCCESS":
        print(f"Reduced faces: {res_red.triangle_count} (Original: {res_red.original_face_count})")

    # Test 2: LOD Chain
    print("\nTest 2: LOD Chain Generation...")
    res_lod = optimizer.generate_lods(mesh_path, {"lod_count": 3})
    print(f"Status: {res_lod.status}")
    if res_lod.status == "SUCCESS":
        print(f"LOD Levels: {len(res_lod.levels)}")
        for lvl in res_lod.levels:
            print(f"  Level {lvl.level}: {lvl.triangle_count} tris, path: {lvl.file_path}")

    # Test 3: Culling
    print("\nTest 3: Geometry Culling...")
    res_cull = optimizer.cull_geometry(mesh, {"remove_below_ground": True})
    print(f"Status: {res_cull.status}")

def test_api_endpoints():
    print("\n--- Testing API Endpoints ---")
    BASE_URL = "http://localhost:8000"
    HEADERS = {"x-qyntara-key": "QYNTARA-X-777", "Content-Type": "application/json"}
    
    # Test 1: /execute (Remesh)
    print("Test 1: POST /execute (remesh)...")
    payload = {
        "meshes": ["backend/data/test_cube.obj"],
        "materials": [],
        "tasks": ["remesh"],
        "remesh_settings": {"target_faces": 2000}
    }
    try:
        r = requests.post(f"{BASE_URL}/execute", json=payload, headers=HEADERS)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            remesh_out = data.get("remeshOutput")
            if remesh_out:
                print(f"Remesh Output Status: {remesh_out.get('status')}")
                print(f"Metrics: {remesh_out.get('metrics', {}).get('quad_count')} quads")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

    # Test 2: /optimize (Reduction)
    print("\nTest 2: POST /optimize (reduce)...")
    payload_opt = {
        "mesh_path": "backend/data/test_cube.obj",
        "mode": "reduce",
        "settings": {"target_ratio": 0.3}
    }
    try:
        r = requests.post(f"{BASE_URL}/optimize", json=payload_opt, headers=HEADERS)
        print(f"Status Code: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Optimize Output Status: {data.get('status')}")
            print(f"Reduced triangles: {data.get('reduced_count')}")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Ensure we are in backend dir context if imports are relative
    # But usually generative.remesher works if backend is in PYTHONPATH
    import sys
    sys.path.append(os.getcwd())
    
    test_quad_remesher()
    test_mesh_optimizer()
    test_api_endpoints()
