
import sys
import os
import shutil
import time
from unittest.mock import MagicMock

# 1. Mock Maya (Crucial)
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
import maya.cmds as cmds
cmds.duplicate.return_value = ["MOCK_DUP"]
cmds.polyCube.return_value = ["MOCK_CUBE"]
cmds.group.return_value = "MOCK_GRP"
cmds.ls.return_value = []
cmds.rotate.return_value = None
cmds.move.return_value = None
cmds.pluginInfo.return_value = True

sys.path.append(r'e:\QYNTARA AI')

# 2. Imports
from qyntara_ai.ai_assist.generate_dataset import DatasetGenerator
from qyntara_ai.ai_assist.train_model import train_model, load_dataset, HAS_TORCH

def verify_massive():
    print(f"--- START MASSIVE VERIFICATION (Torch={HAS_TORCH}) ---")
    
    # Setup Paths
    base_dir = r"e:\QYNTARA AI"
    massive_dir = os.path.join(base_dir, "massive_dataset")
    
    # Clean prev
    if os.path.exists(massive_dir):
        shutil.rmtree(massive_dir)
    os.makedirs(massive_dir)
    
    # 3. Generate Massive Data
    # DatasetGenerator uses maya cmds which are mocked to be instant.
    # So generating 500 should be very fast (just file IO).
    print("Generating 500 samples...")
    start_time = time.time()
    
    gen = DatasetGenerator(massive_dir)
    # Mock procedural layout to avoid complexity, usually it calls polyCube
    gen.create_procedural_layout = MagicMock(return_value=["Cube_A", "Cube_B"])
    gen.clear_scene = MagicMock()
    
    gen.generate_batch(500)
    
    gen_time = time.time() - start_time
    print(f"Generation Complete in {gen_time:.2f}s")
    
    # 4. Load Dataset
    print("Loading Dataset...")
    data = load_dataset(massive_dir)
    print(f"Loaded {len(data)} items.")
    
    if len(data) == 0:
        print("FAILURE: No data generated.")
        return

    # 5. Train
    print("Starting Training Loop (2 Epochs)...")
    try:
        model = train_model(data, epochs=2)
        print("Training Complete.")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"TRAINING CRASH: {e}")

    print("--- END VERIFICATION ---")

if __name__ == "__main__":
    verify_massive()
