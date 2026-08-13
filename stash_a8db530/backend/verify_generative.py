import os
import sys
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.generative.text_to_3d import TextTo3DGenerator
    from backend.generative.image_to_3d import ImageTo3DGenerator
except ImportError as e:
    print(f"Import Error: {e}")
    print("Ensure you are running this from the project root or have installed requirements.")
    sys.exit(1)

def verify_text_to_3d():
    print("\n--- Verifying Text-to-3D (Shap-E) ---")
    try:
        generator = TextTo3DGenerator()
        if not generator.pipe:
            print("FAILED: Model could not be loaded.")
            return False
            
        output_path = "backend/data/test_gen_text.obj"
        print("Generating sample 'chair'...")
        start = time.time()
        result_path = generator.generate("a futuristic chair", output_path)
        end = time.time()
        
        if os.path.exists(result_path):
            print(f"SUCCESS: Model generated at {result_path}")
            print(f"Time taken: {end - start:.2f}s")
            return True
        else:
            print("FAILED: Output file not found.")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_image_to_3d():
    print("\n--- Verifying Image-to-3D (Shap-E Img2Img) ---")
    try:
        generator = ImageTo3DGenerator()
        if not generator.pipe:
            print("FAILED: Model could not be loaded.")
            return False
            
        # Create a dummy image for testing if none exists
        dummy_img_path = "backend/data/test_input.png"
        if not os.path.exists(dummy_img_path):
            from PIL import Image
            img = Image.new('RGB', (256, 256), color = 'red')
            img.save(dummy_img_path)
            
        output_path = "backend/data/test_gen_image.obj"
        print(f"Generating 3D from {dummy_img_path}...")
        start = time.time()
        result = generator.generate(dummy_img_path, output_path)
        end = time.time()
        
        if result.get("status") == "success" and os.path.exists(output_path):
            print(f"SUCCESS: Model generated at {output_path}")
            print(f"Time taken: {end - start:.2f}s")
            return True
        else:
            print(f"FAILED: {result.get('error')}")
            return False
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting Generative AI Verification...")
    print("This may take a while if models need to be downloaded.")
    
    text_success = verify_text_to_3d()
    img_success = verify_image_to_3d()
    
    if text_success and img_success:
        print("\nALL CHECKS PASSED: Generative AI is ready.")
    else:
        print("\nSOME CHECKS FAILED. See logs above.")
