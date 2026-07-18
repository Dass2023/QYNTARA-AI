import uvicorn
import os
import sys

# Ensure root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(root_dir)

# Setup Logging (Relative Path)
log_file = os.path.join(root_dir, "server_log.txt")

def run():
    try:
        with open(log_file, "w") as f:
            f.write("Starting Qyntara Server (v9.1 PRO)...\n")
        
        # Verify imports - Pointing to the NEW backend structure
        import backend.main
        
        with open(log_file, "a") as f:
            f.write(f"Import successful. Root: {root_dir}. Starting Uvicorn.\n")
            
        uvicorn.run(
            "backend.main:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            log_level="info"
        )
    except Exception as e:
        # Fallback print if file write fails (e.g. permissions)
        print(f"CRITICAL ERROR: {e}")
        try:
            with open(log_file, "a") as f:
                f.write(f"CRITICAL ERROR: {e}\n")
        except:
            pass

if __name__ == "__main__":
    run()
