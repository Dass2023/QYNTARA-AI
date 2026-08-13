import os
import sys
import asyncio

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.generative.trellis_gen import TrellisGenerator

def test_trellis():
    print("Initializing TrellisGenerator...")
    generator = TrellisGenerator()
    
    image_path = "backend/data/test_input.png"
    output_dir = "backend/data/trellis_output"
    
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return

    print(f"Generating 3D from {image_path}...")
    try:
        result = generator.generate(image_path, output_dir)
        print("Generation Result:", result)
        
        if result['glb_path'] and os.path.exists(result['glb_path']):
            print("SUCCESS: GLB generated.")
        else:
            print("FAILURE: GLB not generated.")
            
    except Exception as e:
        print(f"Generation Failed: {e}")

if __name__ == "__main__":
    test_trellis()
