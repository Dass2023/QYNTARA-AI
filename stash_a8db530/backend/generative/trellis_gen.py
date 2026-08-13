import os
import sys
import torch
from PIL import Image
import numpy as np
from unittest.mock import MagicMock

# Mock open3d if not available
try:
    import open3d
except ImportError:
    print("Warning: open3d not found. Mocking it.")
    sys.modules["open3d"] = MagicMock()
    sys.modules["open3d.core"] = MagicMock()
    sys.modules["open3d.camera"] = MagicMock()
    sys.modules["open3d.geometry"] = MagicMock()
    sys.modules["open3d.io"] = MagicMock()
    sys.modules["open3d.pipelines"] = MagicMock()
    sys.modules["open3d.utility"] = MagicMock()
    sys.modules["open3d.visualization"] = MagicMock()

# Add TRELLIS to path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
trellis_dir = os.path.join(backend_dir, "trellis")
if trellis_dir not in sys.path:
    sys.path.append(trellis_dir)

# Set environment variables for TRELLIS
os.environ['SPCONV_ALGO'] = 'native'
os.environ['ATTN_BACKEND'] = 'sdpa'

try:
    from trellis.pipelines import TrellisImageTo3DPipeline
    from trellis.utils import postprocessing_utils
except ImportError as e:
    print(f"Error importing TRELLIS: {e}")
    TrellisImageTo3DPipeline = None

class TrellisGenerator:
    def __init__(self, device="cuda"):
        self.device = device
        self.pipeline = None
        if TrellisImageTo3DPipeline is None:
            print("TRELLIS pipeline not available.")
            return

    def load_model(self):
        if self.pipeline is None:
            print("Loading TRELLIS model...")
            try:
                self.pipeline = TrellisImageTo3DPipeline.from_pretrained("microsoft/TRELLIS-image-large")
                self.pipeline.cuda()
                print("TRELLIS model loaded.")
            except Exception as e:
                print(f"Failed to load TRELLIS model: {e}")
                self.pipeline = None

    def generate(self, image_path: str, output_dir: str, seed: int = 42) -> dict:
        if self.pipeline is None:
            self.load_model()
        
        if self.pipeline is None:
            raise RuntimeError("TRELLIS model failed to load.")

        image = Image.open(image_path)
        
        # Run pipeline
        outputs = self.pipeline.run(
            image,
            seed=seed
        )
        
        # Save outputs
        os.makedirs(output_dir, exist_ok=True)
        
        # GLB Export
        glb_path = os.path.join(output_dir, "generated.glb")
        try:
            glb = postprocessing_utils.to_glb(
                outputs['gaussian'][0],
                outputs['mesh'][0],
                simplify=0.95,
                texture_size=1024,
            )
            glb.export(glb_path)
        except Exception as e:
            print(f"Failed to export GLB: {e}")
            glb_path = None

        # PLY Export (Gaussians)
        ply_path = os.path.join(output_dir, "generated.ply")
        try:
            outputs['gaussian'][0].save_ply(ply_path)
        except Exception as e:
            print(f"Failed to export PLY: {e}")
            ply_path = None
            
        return {
            "glb_path": glb_path,
            "ply_path": ply_path
        }
