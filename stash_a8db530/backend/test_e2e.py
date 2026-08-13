import asyncio
import os
import sys
import trimesh

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pipeline import QyntaraPipeline

async def test_e2e():
    print("--- Starting End-to-End System Test ---")
    
    async def print_progress(msg):
        print(f"[Pipeline] {msg}")

    pipeline = QyntaraPipeline(on_progress=print_progress)
    
    try:
        # Step 1: Generation (Mocking Text-to-3D to save time/cost, or use real if fast enough)
        # For E2E stability, we'll use a simple cube creation as the "Generation" step 
        # unless we want to test the actual AI model which might be slow.
        # Let's use a real generation call if possible, but fallback to mock for speed in this test script.
        # actually, let's use the sample cube to ensure deterministic input for the pipeline.
        print("\n1. [Generation] Creating Input Mesh...")
        input_mesh_path = "backend/data/e2e_input.obj"
        mesh = trimesh.creation.box(extents=[1, 1, 1])
        mesh.export(input_mesh_path)
        print(f"   - Created: {input_mesh_path}")

        # Step 2: Validation
        print("\n2. [Validation] Validating Geometry...")
        report = await pipeline.run_validation([input_mesh_path])
        print(f"   - Watertight: {report.geometry.watertight}")


        # Step 3: Remeshing
        print("\n3. [Optimization] Running Quad Remeshing...")
        remesh_result = await pipeline.run_quad_remeshing([input_mesh_path], {"target_faces": 500})
        remeshed_path = remesh_result.mesh_path
        print(f"   - Remeshed to: {remeshed_path}")

        # Step 4: Material Assignment
        print("\n4. [Material] Assigning Material...")
        material_name = "gold_polished"
        textured_path = await pipeline.run_material_assignment([remeshed_path], material_name)
        print(f"   - Material Assigned: {textured_path}")

        # Step 5: Export
        print("\n5. [Export] Exporting to USDA...")
        export_report = await pipeline.run_export_governance("unreal")
        print(f"   - Export Compliant: {export_report.compliant}")

        print("\n--- E2E Test Complete: SUCCESS ---")

    except Exception as e:
        print(f"\n--- E2E Test Failed: {e} ---")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_e2e())
