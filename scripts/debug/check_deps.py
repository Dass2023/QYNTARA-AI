import importlib

dependencies = [
    "torch",
    "torchvision",
    "segment_anything",
    "diffusers",
    "skimage",
    "cv2"
]

print("Checking dependencies...")
for dep in dependencies:
    try:
        importlib.import_module(dep)
        print(f"[OK] {dep}")
    except ImportError as e:
        print(f"[MISSING] {dep}: {e}")
    except Exception as e:
        print(f"[ERROR] {dep}: {e}")
