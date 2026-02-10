import asyncio
import os
import sys
import cv2
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.pipeline import QyntaraPipeline

async def test_segmentation():
    print("--- Testing Real AI Segmentation ---")
    
    async def print_progress(msg):
        print(f"[Pipeline] {msg}")

    pipeline = QyntaraPipeline(on_progress=print_progress)
    
    # Create a dummy image
    img_path = "backend/data/test_seg.png"
    img = np.zeros((512, 512, 3), dtype=np.uint8)
    cv2.circle(img, (256, 256), 100, (255, 255, 255), -1) # White circle
    cv2.imwrite(img_path, img)
    
    print(f"Created test image: {img_path}")
    
    # Test 1: Batch Segmentation (run_segmentation -> run_sam_segmentation)
    print("\n1. Testing Batch Segmentation...")
    try:
        result = await pipeline.run_segmentation([img_path])
        if result.object_masks:
            print(f"SUCCESS: Generated {len(result.object_masks)} masks.")
            print(f"Masks: {result.object_masks}")
        else:
            print("FAILED: No masks generated.")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

    # Test 2: Interactive Segmentation (run_2d_segmentation)
    print("\n2. Testing Interactive Segmentation...")
    try:
        # Click on the circle center
        click_point = [256, 256] 
        result = await pipeline.run_2d_segmentation(img_path, click_point, "left")
        
        if result.get("status") == "success":
            print(f"SUCCESS: Segmented object. Color: {result.get('color')}")
        else:
            print(f"FAILED: {result.get('message')}")
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_segmentation())
