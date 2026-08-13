
import sys
import unittest
import os
from unittest.mock import MagicMock

# Mock PyTorch presence to force Mock Mode if real torch missing, 
# But we actually want to test the LOGIC. The logic in train_model.py has a MockPointNet.
# The MockPointNet needs to be updated to reflect regression prints (MSE Loss) instead of Accuracy.

# Let's run train_model.py directly?
# But we need to ensure it uses a dummy dataset if none exists.
# The `run_training` function in train_model.py handles dataset generation.
# So we can just invoke it.

# However, we must ensure `maya` is mocked because `train_model` imports `generate_dataset` which imports `maya.cmds`.
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
import maya.cmds as cmds
cmds.duplicate.return_value = ["dup"] # Fix for dataset gen
cmds.polyCube.return_value = ["cube"]
cmds.group.return_value = "grp"
cmds.ls.return_value = []
cmds.pluginInfo.return_value = True

sys.path.append(r'e:\QYNTARA AI')
from qyntara_ai.ai_assist import train_model

print("--- START TRAINING VERIFICATION ---")
try:
    # Force Mock Mode by setting HAS_TORCH = False if it isn't already?
    # Actually, if torch is missing, it auto-sets.
    # If torch IS present, it runs real training.
    # We want to verify the script runs.
    
    # Let's just run it.
    train_model.run_training()
    print("Execution completed without crash.")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"CRASH: {e}")

print("--- END VERIFICATION ---")
sys.stdout.flush()
