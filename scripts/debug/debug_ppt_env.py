import sys
import os

log_file = "debug_ppt.txt"

with open(log_file, "w") as f:
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"CWD: {os.getcwd()}\n")
    try:
        import pptx
        f.write(f"Success: Imported pptx version {pptx.__version__}\n")
    except ImportError as e:
        f.write(f"Error: Could not import pptx: {e}\n")
    except Exception as e:
        f.write(f"Error: Unexpected error: {e}\n")

print("Debug script finished.")
