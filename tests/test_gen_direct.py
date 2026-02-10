import sys
import os
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Imports moved to functions to avoid top-level failures
# from backend.generative.trellis_gen import TrellisGenerator
# from backend.generative.text_to_3d import TextTo3DGenerator
# from backend.generative.image_to_3d import ImageTo3DGenerator

def test_trellis():
    print("\n--- Testing TrellisGenerator Directly ---")
    try:
        from backend.generative.trellis_gen import TrellisGenerator
    except ImportError as e:
        print(f"SKIPPING TRELLIS: Could not import TrellisGenerator: {e}")
        return
    
    # Create dummy image
    os.makedirs("backend/data/uploads", exist_ok=True)
    from PIL import Image
    img_path = 'backend/data/uploads/test_gen.jpg'
    if not os.path.exists(img_path):
        img = Image.new('RGB', (512, 512), color = 'blue')
        img.save(img_path)
    
    try:
        gen = TrellisGenerator()
        print("Loading model...")
        gen.load_model()
        
        print("Generating 3D...")
        output_dir = 'backend/data/test_gen_out_trellis'
        
        output = gen.generate(img_path, output_dir)
        print(f"Generation Result: {output}")
        
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()

def test_text_to_3d():
    print("\n--- Testing TextTo3DGenerator Directly ---")
    try:
        from backend.generative.text_to_3d import TextTo3DGenerator
    except ImportError as e:
        print(f"SKIPPING TEXT-TO-3D: Could not import TextTo3DGenerator: {e}")
        return
    prompt = input("Enter prompt (default: 'a futuristic chair'): ") or "a futuristic chair"
    output_path = "backend/data/text_gen_out.obj"
    
    try:
        gen = TextTo3DGenerator()
        result = gen.generate(prompt, output_path)
        print(f"Generation Result: {result}")
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()

def test_image_to_3d():
    print("\n--- Testing ImageTo3DGenerator Directly ---")
    try:
        from backend.generative.image_to_3d import ImageTo3DGenerator
    except ImportError as e:
        print(f"SKIPPING IMAGE-TO-3D: Could not import ImageTo3DGenerator: {e}")
        return
    image_path = input("Enter image path (default: 'backend/data/uploads/test_gen.jpg'): ") or "backend/data/uploads/test_gen.jpg"
    
    if not os.path.exists(image_path):
        print(f"Image not found at {image_path}. Creating dummy...")
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        from PIL import Image
        img = Image.new('RGB', (512, 512), color = 'red')
        img.save(image_path)
        
    output_path = "backend/data/image_gen_out.obj"
    
    try:
        gen = ImageTo3DGenerator()
        result = gen.generate(image_path, output_path)
        print(f"Generation Result: {result}")
    except Exception as e:
        print(f"CRITICAL FAILURE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Direct 3D Generation Test")
    parser.add_argument("--mode", type=str, choices=['1', '2', '3', 'all'], help="Generation mode: 1=Text-to-3D, 2=Image-to-3D (Shap-E), 3=Image-to-3D (Trellis)")
    args = parser.parse_args()

    if args.mode:
        choice = args.mode
    else:
        print("Select Generation Mode:")
        print("1. Text to 3D (Shap-E)")
        print("2. Image to 3D (Shap-E)")
        print("3. Image to 3D (Trellis)")
        print("all. Run All")
        choice = input("Enter choice (1-3 or all): ")
    
    if choice == '1' or choice == 'all':
        test_text_to_3d()
    if choice == '2' or choice == 'all':
        test_image_to_3d()
    if choice == '3' or choice == 'all':
        test_trellis()


