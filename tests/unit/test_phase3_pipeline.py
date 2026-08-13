import sys
import os
import logging
logging.basicConfig(level=logging.DEBUG)
from unittest.mock import MagicMock

# --- MOCK MAYA ENVIRONMENT ---
mock_maya = MagicMock()
mock_cmds = MagicMock()
mock_om = MagicMock()

# sys.modules["maya"] = mock_maya
# sys.modules["maya.cmds"] = mock_cmds
mock_maya.cmds = mock_cmds
# sys.modules["maya.api.OpenMaya"] = mock_om
# sys.modules["maya.api"] = MagicMock()
# sys.modules["maya.mel"] = MagicMock()

# Setup simulated mesh tracking
mock_cmds.ls = MagicMock(return_value=["mock_edge_1", "mock_edge_2"])
mock_cmds.objExists = MagicMock(return_value=True)
mock_cmds.pluginInfo = lambda *args, **kwargs: True  # Pretend Arnold/Unfold3D are loaded

def run_tests():
    print("=== Qyntara Nexus: Testing Phase 3 Pipeline ===")
    
    project_dir = r"i:\QYNTARA AI"
    if project_dir not in sys.path:
         sys.path.append(project_dir)
         
    try:
        from qyntara_ai.core import uv_tools, baking
        
        test_meshes = ["Hero_Asset"]
        
        print("\n--- Testing: AI Seam Placement ---")
        seam_res = uv_tools.ai_seam_placement(test_meshes)
        print("Result:", seam_res)
        assert "AI Seam Placement" in seam_res
        
        print("\n--- Testing: Neural Packing ---")
        pack_res = uv_tools.neural_packing(test_meshes, udims=True, resolution=4096)
        print("Result:", pack_res)
        assert "Neural Packing Complete" in pack_res
        
        print("\n--- Testing: BakeMaster Engine ---")
        # Testing 1 High source to 2 Low targets
        bake_res = baking.execute_bakemaster("HighPoly_Source", ["LOD0", "LOD1"], resolution=2048, bake_ao=False)
        print("Result:", bake_res)
        assert "Projected Normals onto LOD0" in bake_res
        
        print("\n[SUCCESS] All Phase 3 Pipeline tests passed successfully.")
        
    except Exception as e:
        print(f"\n[ERROR] Phase 3 Pipeline testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_tests()
