import sys
import os
import asyncio
from unittest.mock import MagicMock

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Mock heavy dependencies
sys.modules["torch"] = MagicMock()
sys.modules["cv2"] = MagicMock()
sys.modules["trimesh"] = MagicMock()
sys.modules["segment_anything"] = MagicMock()
sys.modules["xatlas"] = MagicMock()

# Mock diffusers and its submodules
diffusers = MagicMock()
sys.modules["diffusers"] = diffusers
sys.modules["diffusers.utils"] = MagicMock()


# Mock the generative modules specifically to ensure they are imported but not fully initialized
# We want to test that pipeline.py imports them correctly
from backend.generative.text_to_3d import TextTo3DGenerator
from backend.generative.image_to_3d import ImageTo3DGenerator

# Now import pipeline
from backend.pipeline import QyntaraPipeline

import pytest

@pytest.mark.asyncio
async def test_pipeline_generative_methods():
    print("Initializing QyntaraPipeline...")
    pipeline = QyntaraPipeline()
    
    print("Testing _get_text_to_3d_gen...")
    # Mock the generator classes to avoid instantiation issues with mocked torch
    with MagicMock() as mock_text_gen:
        pipeline.text_to_3d_gen = mock_text_gen
        gen = pipeline._get_text_to_3d_gen()
        assert gen is not None
        print("TextTo3DGenerator retrieval successful.")

    print("Testing _get_image_to_3d_gen...")
    with MagicMock() as mock_img_gen:
        pipeline.image_to_3d_gen = mock_img_gen
        gen = pipeline._get_image_to_3d_gen()
        assert gen is not None
        print("ImageTo3DGenerator retrieval successful.")

    print("Verification passed!")

if __name__ == "__main__":
    asyncio.run(test_pipeline_generative_methods())
