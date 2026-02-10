import asyncio
import os
import sys
import cv2
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pipeline import QyntaraPipeline

async def test_floorplan():
    print("--- Testing Floor Plan Extrusion ---")
    
    async def print_progress(msg):
        print(f"[Pipeline] {msg}")

    pipeline = QyntaraPipeline(on_progress=print_progress)
    
    # Create a dummy floorplan image (White background, Black walls)
    img_path = "backend/data/test_floorplan.png"
    img = np.ones((512, 512, 3), dtype=np.uint8) * 255 # White
    
    # Draw a simple room (Black rectangle) - Thicker walls
    cv2.rectangle(img, (100, 100), (400, 400), (0, 0, 0), 20)
    # Draw an inner wall
    cv2.line(img, (250, 100), (250, 400), (0, 0, 0), 20)
    
    cv2.imwrite(img_path, img)
    print(f"Created test floorplan: {img_path}")
    
    try:
        # Run Extrusion
        # Threshold 127 is good for black/white
        result = await pipeline.run_floorplan_extrusion(img_path, height=3.0, threshold=127, pixels_per_meter=50.0)
        
        if result.get("status") == "success":
            print(f"SUCCESS: Floor plan extruded.")
            print(f"Mesh: {result.get('mesh_path')}")
            print(f"DXF: {result.get('dxf_path')}")
            print(f"Walls: {result.get('wall_count')}")
            
            # Verify files exist
            mesh_full_path = f"backend/data/{result.get('mesh_path')}"
            dxf_full_path = f"backend/data/{result.get('dxf_path')}"
            
            if os.path.exists(mesh_full_path):
                print(f"Verified Mesh File: {mesh_full_path}")
            else:
                print(f"ERROR: Mesh file missing: {mesh_full_path}")
                
            if os.path.exists(dxf_full_path):
                print(f"Verified DXF File: {dxf_full_path}")
            else:
                print(f"ERROR: DXF file missing: {dxf_full_path}")
                
        else:
            print(f"FAILED: {result.get('message')}")
            
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_floorplan())
