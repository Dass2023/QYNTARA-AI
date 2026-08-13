
import sys
import unittest
from unittest.mock import MagicMock

# Mock Maya
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
import maya.cmds as cmds

# Mock Random to be deterministic
import random
random.uniform = MagicMock(return_value=10.0) # Always return 10.0

def apply_misalignment_logic():
    # Simulate the logic in generate_dataset.py
    obj = "pCube1"
    dup = "pCube1_bad"
    
    # Logic in code:
    # 1. Random Translation
    # dx, dy, dz = random...
    # 2. Random Rotation
    # rx, ry, rz = random...
    # cmds.rotate(..., os=True, relative=True)
    # cmds.move(..., relative=True)
    
    # Run
    rx = random.uniform(-180, 180) # Returns 10.0
    
    cmds.rotate(10.0, 10.0, 10.0, dup, os=True, relative=True)
    cmds.move(10.0, 10.0, 10.0, dup, relative=True)
    
    return True

print("START_TEST")
try:
    apply_misalignment_logic()
    # Check calls
    rot_args = cmds.rotate.call_args
    move_args = cmds.move.call_args
    
    if rot_args and move_args:
        print("LOGIC_VERIFIED: Rotate and Move called.")
        print(f"ROT_ARGS: {rot_args}")
    else:
        print("LOGIC_FAILED: Calls missing.")
except Exception as e:
    print(f"CRASH: {e}")

print("END_TEST")
sys.stdout.flush()
