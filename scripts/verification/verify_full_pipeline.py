import requests
import json
import time
import os
import sys

# Force UTF-8 stdout if possible, but simplest is avoiding special chars
# sys.stdout.reconfigure(encoding='utf-8') 

API_URL = "http://localhost:8000"

def run_step(step_name, tasks, input_mesh=None, settings={}):
    print(f"\n--- STEP: {step_name} ---")
    payload = {
        "meshes": [input_mesh] if input_mesh else [],
        "materials": [],
        "tasks": tasks,
        "engineTarget": "unreal",
        "uv_settings": {"mode": "auto", "resolution": 1024},
        "remesh_settings": {"target_faces": 2000},
        "material_settings": {"target_profile": "UNREAL"},
        "export_settings": {"format": "glb"},
        "validation_profile": "GENERIC",
        "generative_settings": {
            "prompt": "a sci-fi crate",
            "quality": "draft", 
            "provider": "internal"
        }
    }
    payload.update(settings)

    try:
        start_time = time.time()
        print(f"Sending Request (Tasks: {tasks})...")
        r = requests.post(f"{API_URL}/execute", json=payload, timeout=600)
        duration = time.time() - start_time
        
        if r.status_code == 200:
            res = r.json()
            print(f"[SUCCESS] {step_name} completed in {duration:.2f}s")
            return res
        else:
            print(f"[FAIL] {step_name} failed: {r.status_code} {r.text}")
            return None
    except Exception as e:
        print(f"[FAIL] {step_name} exception: {e}")
        return None

def main():
    print("STARTING QYNTARA AUTO FULL PIPELINE VERIFICATION")
    
    try:
        requests.get(f"{API_URL}/stats")
    except:
        print("[FATAL] Backend Server is offline. Please start it.")
        return

    # 1. GENERATE
    res_gen = run_step("GENERATE", ["generative"])
    if not res_gen: return
    
    gen_mesh = res_gen.get("generative3DOutput", {}).get("generated_mesh_path")
    if not gen_mesh:
        print("[FAIL] No mesh generated.")
        return
    else:
        print(f"Generated Asset: {gen_mesh}")

    # 2. REMESH
    res_remesh = run_step("REMESH", ["remesh"], input_mesh=gen_mesh)
    if not res_remesh: return
    
    remesh_mesh = res_remesh.get("remeshOutput", {}).get("mesh_path")
    if not remesh_mesh:
        print("[WARN] Remesh output missing? using gen_mesh.")
        remesh_mesh = gen_mesh
    else:
        print(f"Remeshed Asset: {remesh_mesh}")

    # 3. UV
    res_uv = run_step("UV", ["uv"], input_mesh=remesh_mesh)
    if not res_uv: return

    # 4. MATERIAL
    res_mat = run_step("MATERIAL", ["material_ai"], input_mesh=remesh_mesh)
    
    # 5. VALIDATE
    res_val = run_step("VALIDATE", ["validate"], input_mesh=remesh_mesh)
    if res_val:
        report = res_val.get("validationReport", {})
        print(f"Validation Score: {100 if report.get('passed') else 50}")

    # 6. EXPORT
    res_exp = run_step("EXPORT", ["optimization_export"], input_mesh=remesh_mesh)

    print("\nPIPELINE VERIFICATION COMPLETE")

if __name__ == "__main__":
    main()
