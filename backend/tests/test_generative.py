import pytest
import os
import sys
from backend.generative.text_to_3d import TextTo3DGenerator

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

def test_shap_e_generation():
    generator = TextTo3DGenerator()
    
    # Skip if model failed to load (e.g. no GPU or network issue)
    if not generator.pipe:
        pytest.skip("Shap-E model could not be loaded")
        
    output_path = "backend/data/test_gen.obj"
    result_path = generator.generate("a simple chair", output_path)
    
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 0
    print(f"Generated model at: {result_path}")

if __name__ == "__main__":
    test_shap_e_generation()
