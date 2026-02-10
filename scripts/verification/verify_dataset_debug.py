
import sys
import os
import traceback
from unittest.mock import MagicMock

log_file = r"e:\QYNTARA AI\verify_result.txt"

try:
    # Mock Maya
    sys.modules['maya'] = MagicMock()
    sys.modules['maya.cmds'] = MagicMock()
    import maya.cmds as cmds

    # Mock returns
    cmds.duplicate.return_value = ["MOCK_DUP"]
    cmds.polyCube.return_value = ["MOCK_CUBE"]
    cmds.group.return_value = "MOCK_GRP"
    cmds.ls.return_value = [] 
    cmds.pluginInfo.return_value = True

    # Add path
    sys.path.append(r'e:\QYNTARA AI')

    # Import
    from qyntara_ai.ai_assist.generate_dataset import DatasetGenerator

    # Setup
    output_dir = r"e:\QYNTARA AI\test_dataset_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    gen = DatasetGenerator(output_dir)
    # Mock procedural gen to return strings
    gen.create_procedural_layout = MagicMock(return_value=["Cube_01", "Cube_02"])
    gen.clear_scene = MagicMock()

    # Run
    gen.generate_batch(batch_size=1)

    # Check Meta
    import json
    scene_dir = os.path.join(output_dir, "scene_000")
    meta_path = os.path.join(scene_dir, "meta.json")

    if os.path.exists(meta_path):
        with open(meta_path, 'r') as f:
            data = json.load(f)
            obj = data["objects"][0]
            
            if "rotation_offset" in obj and "translation_offset" in obj:
                with open(log_file, 'w') as log:
                    log.write("SUCCESS: Rotation Offset Found: " + str(obj["rotation_offset"]))
            else:
                 with open(log_file, 'w') as log:
                    log.write("FAILURE: Missing keys in " + str(obj.keys()))
    else:
        with open(log_file, 'w') as log:
            log.write("FAILURE: Meta file not found at " + meta_path)

except Exception:
    with open(log_file, 'w') as log:
        log.write("CRASH: " + traceback.format_exc())
