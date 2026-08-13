import torch
import sys

print(f"Python Version: {sys.version}")
print(f"PyTorch Version: {torch.__version__}")
try:
    available = torch.cuda.is_available()
    print(f"CUDA Available: {available}")
    if available:
        print(f"Device Name: {torch.cuda.get_device_name(0)}")
        print(f"Current Device: {torch.cuda.current_device()}")
    else:
        print("CUDA NOT Available. Running on CPU.")
except Exception as e:
    print(f"Error checking CUDA: {e}")
