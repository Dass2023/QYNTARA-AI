import pytest
import os
import sys
from PIL import Image
from backend.generative.image_to_3d import ImageTo3DGenerator

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def test_shap_e_img2img():
    generator = ImageTo3DGenerator()
    
    # Skip if model failed to load
    if not generator.pipe:
        pytest.skip("Shap-E Img2Img model could not be loaded")
        
    # Create a dummy image
    img_path = "backend/data/test_input.png"
    img = Image.new('RGB', (256, 256), color = 'red')
    img.save(img_path)
    
    output_path = "backend/data/test_img_gen.obj"
    result = generator.generate(img_path, output_path)
    
    assert result["status"] == "success"
    assert os.path.exists(output_path)
    assert os.path.getsize(output_path) > 0
    print(f"Generated model at: {output_path}")

if __name__ == "__main__":
    test_shap_e_img2img()
