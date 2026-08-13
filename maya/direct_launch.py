import sys
import os
import importlib

# 1. Add the source directory to sys.path if not present
SOURCE_DIR = r"i:\QYNTARA AI\maya"
if SOURCE_DIR not in sys.path:
    sys.path.insert(0, SOURCE_DIR)

# Forcibly remove old modules from cache to ensure clean reload
modules_to_clear = ['qyntara_client', 'master_prompt', 'nexus_api_client', 'legacy_core']
for m in list(sys.modules.keys()):
    if any(m == x or m.startswith(x + '.') for x in modules_to_clear):
        del sys.modules[m]

import qyntara_client
import master_prompt
print("\n" + "="*50)
print("   FORCING QYNTARA UI RELOAD FROM SOURCE")
print(f"   Source: {SOURCE_DIR}")
print("="*50 + "\n")

qyntara_client.show()
