import sys
import os

# Add backend to path
sys.path.append(os.getcwd())

print("Checking Trellis dependencies...")

try:
    import torch
    print(f"[OK] torch: {torch.__version__} (CUDA: {torch.cuda.is_available()})")
except ImportError as e:
    print(f"[FAIL] torch: {e}")

try:
    import spconv
    print(f"[OK] spconv: {spconv.__version__}")
except ImportError as e:
    print(f"[FAIL] spconv: {e}")
    print("  -> spconv is required for Trellis. Install with: pip install spconv-cu120 (or matching CUDA version)")

try:
    import rembg
    print(f"[OK] rembg: {rembg.__version__}")
except ImportError as e:
    print(f"[WARN] rembg: {e} (Optional but recommended)")

print("\nAttempting to import Trellis Pipeline...")
try:
    # Import directly to avoid __init__ triggering open3d import from text_to_3d
    from backend.trellis.trellis.pipelines.trellis_image_to_3d import TrellisImageTo3DPipeline
    print(f"[OK] TrellisImageTo3DPipeline imported successfully (Direct Import).")
except Exception as e:
    print(f"[FAIL] Trellis Import: {e}")
