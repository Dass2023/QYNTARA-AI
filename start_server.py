import uvicorn
import os
import sys

# Setup Logging
log_file = "e:/QYNTARA AI/server_log.txt"

def run():
    try:
        with open(log_file, "w") as f:
            f.write("Starting Qyntara Server...\n")
        
        # Verify imports
        import qyntara_ai.server.api_server
        
        with open(log_file, "a") as f:
            f.write("Import successful. Starting Uvicorn.\n")
            
        uvicorn.run(
            "qyntara_ai.server.api_server:app", 
            host="0.0.0.0", 
            port=8000, 
            reload=False,
            log_level="info"
        )
    except Exception as e:
        with open(log_file, "a") as f:
            f.write(f"CRITICAL ERROR: {e}\n")

if __name__ == "__main__":
    run()
