import sys
import os

with open("env_info.txt", "w") as f:
    try:
        import fastapi
        f.write(f"FastAPI found at: {os.path.dirname(fastapi.__file__)}\n")
    except ImportError:
        f.write("FastAPI NOT found\n")
    
    f.write(f"Python Executable: {sys.executable}\n")
    f.write(f"Sys Path: {sys.path}\n")
