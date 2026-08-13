import sys
import os
import importlib

# 1. Add the source directory to sys.path if not present
SOURCE_DIR = r"i:\QYNTARA AI\maya"
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

# 2. Import and Force Reload
import qyntara_client
importlib.reload(qyntara_client)

# 3. Launch UI
print("\n" + "="*50)
print("   FORCING QYNTARA UI RELOAD FROM SOURCE")
print(f"   Source: {SOURCE_DIR}")
print("="*50 + "\n")

qyntara_client.show()
