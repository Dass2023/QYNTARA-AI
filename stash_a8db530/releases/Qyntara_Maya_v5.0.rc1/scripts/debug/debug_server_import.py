import sys
import os

print(f"CWD: {os.getcwd()}")
print(f"Path: {sys.path}")

try:
    import qyntara_ai.server.api_server as server
    print("Import successful.")
    print(f"App object: {server.app}")
    if server.app is None:
        print("ERROR: app is None! FastAPI import likely failed inside api_server.")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
