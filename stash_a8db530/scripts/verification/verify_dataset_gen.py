
import sys
import os
from unittest.mock import MagicMock

# Mock Maya
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
import maya.cmds as cmds

# Mock random to ensure valid float returns if needed, though standard random works fine.
# But we need cmds.duplicate to return a name
cmds.duplicate.return_value = ["MOCK_DUP"]
cmds.polyCube.return_value = ["MOCK_CUBE"]
cmds.group.return_value = "MOCK_GRP"
cmds.ls.return_value = [] # for checks

# Mock File System interactions for Safe Execution
# We will use real file system for the generator output since checking the file is the goal.
# But we need commands like pluginInfo etc to not crash.
cmds.pluginInfo.return_value = True

# Add path
sys.path.append(r'e:\QYNTARA AI')

from qyntara_ai.ai_assist.generate_dataset import DatasetGenerator

print("--- START DATASET GEN VERIFICATION ---")

# Use a temp test folder
output_dir = r"e:\QYNTARA AI\test_dataset_output"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

gen = DatasetGenerator(output_dir)
# Mocking create_procedural_layout to avoid deep maya calls
gen.create_procedural_layout = MagicMock(return_value=["Cube_01", "Cube_02"])
gen.clear_scene = MagicMock()

# Run Batch
gen.generate_batch(batch_size=1)

# Verify Meta
import json
scene_dir = os.path.join(output_dir, "scene_000")
meta_path = os.path.join(scene_dir, "meta.json")

if os.path.exists(meta_path):
    with open(meta_path, 'r') as f:
        data = json.load(f)
        objects = data.get("objects", [])
        if objects:
            obj = objects[0]
            print(f"Meta Keys Found: {list(obj.keys())}")
            
            has_rot = "rotation_offset" in obj
            has_trans = "translation_offset" in obj
            
            if has_rot and has_trans:
                print(f"Rotation Offset: {obj['rotation_offset']}")
                print(f"Translation Offset: {obj['translation_offset']}")
                print("TEST PASSED: Metadata contains 6-DOF fields.")
            else:
                print("TEST FAILED: Missing offset fields.")
        else:
            print("TEST FAILED: No objects in meta.")
else:
    print(f"TEST FAILED: Meta file not found at {meta_path}")

print("--- END VERIFICATION ---")
