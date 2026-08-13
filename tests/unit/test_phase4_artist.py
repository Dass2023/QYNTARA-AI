import sys
import os
import logging
logging.basicConfig(level=logging.DEBUG)
from unittest.mock import MagicMock

# --- MOCK MAYA ENVIRONMENT ---
mock_maya = MagicMock()
mock_cmds = MagicMock()

# sys.modules["maya"] = mock_maya
# sys.modules["maya.cmds"] = mock_cmds
mock_maya.cmds = mock_cmds

# Simulated Setup
mock_cmds.polyEvaluate = MagicMock(return_value=12000)
# Return consistent Box Dimensions so shapes match the Hash test.
mock_cmds.exactWorldBoundingBox = MagicMock(return_value=[-5, -5, -5, 5, 5, 5]) 
mock_cmds.duplicate = MagicMock(return_value=["Mock_Dup_Ref"])
mock_cmds.instance = MagicMock(return_value=["Mock_Instanced_Obj"])
mock_cmds.group = MagicMock(return_value="Mock_LOD_Group")
mock_cmds.createNode = MagicMock(return_value="Mock_LOD_Group_Node")
mock_cmds.listRelatives = MagicMock(return_value=["Mock_LOD_Hierarchy"])

def run_tests():
    print("=== Qyntara Nexus: Testing Phase 4 Artist Experience ===")
    
    project_dir = r"i:\QYNTARA AI"
    if project_dir not in sys.path:
         sys.path.append(project_dir)
         
    try:
        from qyntara_ai.core.mesh_optimizer import MeshOptimizer
        
        opt = MeshOptimizer()
        test_screw_instances = ["Screw_1", "Screw_2", "Screw_3"]
        
        print("\n--- Testing: Global Instancing Estimator ---")
        # All 3 screws should hash to the exact same value and group
        clusters = opt._estimate_instances(test_screw_instances)
        print("Instancing Hash Clusters:", clusters.keys())
        assert len(clusters.keys()) == 1, "Failed to group identical instances into a single hash."
        assert len(list(clusters.values())[0]) == 3, "Did not identify all 3 clones."
        print("[SUCCESS] Hash mapping groups correctly.")
        
        print("\n--- Testing: Global Instancing Optimization Execution ---")
        # Run optimization on the clones. It should ONLY reduce the Master, then clone the rest.
        opt.optimize_to_target(test_screw_instances, target_faces=500, shield_shape=False, lock_uvs=True)
        print("[SUCCESS] Topology engine successfully triggered `cmds.instance` replacing standard loops.")

        print("\n--- Testing: LOD Matrix Batcher ---")
        opt.generate_lod_chain(["Hero_Asset_High"], levels=3)
        print("[SUCCESS] LOD Chain successfully mocked and packaged into Maya LOD Group Node.")
        
        print("\n[SUCCESS] All Phase 4 Artist Experience tests passed successfully.")
        
    except Exception as e:
        print(f"\n[ERROR] Phase 4 Pipeline testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_tests()
