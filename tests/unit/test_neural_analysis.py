import sys
import os
import json
import logging
logging.basicConfig(level=logging.DEBUG)
from unittest.mock import MagicMock

# --- MOCK MAYA ENVIRONMENT ---
mock_maya = MagicMock()
mock_cmds = MagicMock()
mock_om = MagicMock()

# sys.modules["maya"] = mock_maya
# sys.modules["maya.cmds"] = mock_cmds
mock_maya.cmds = mock_cmds  # <--- Essential fix
# sys.modules["maya.api.OpenMaya"] = mock_om
# sys.modules["maya.api"] = MagicMock()

# Setup basic mock returns
mock_cmds.polyEvaluate = lambda *args, **kwargs: 1000
mock_cmds.objExists = lambda *args, **kwargs: False
mock_cmds.exactWorldBoundingBox = lambda *args, **kwargs: [0,0,0,1,1,1]

mock_om.MFn.kMesh = "kMesh"
class MockDag:
    def extendToShape(self): pass
    def apiType(self): return mock_om.MFn.kMesh
mock_dag = MockDag()

class MockSelectionList:
    def add(self, *args): pass
    def getDagPath(self, *args): return mock_dag
mock_om.MSelectionList = MockSelectionList

def run_tests():
    print("=== Qyntara Nexus: Testing Neural Analysis Layer ===")
    
    # Ensure project is in path
    project_dir = r"i:\QYNTARA AI"
    if project_dir not in sys.path:
         sys.path.append(project_dir)
         
    try:
        from qyntara_ai.core.neural_analysis import NeuralAnalysisLayer
        
        layer = NeuralAnalysisLayer()
        test_meshes = ["pSphere1", "Vehicle_Mesh"]
        
        print("\n--- Testing: detect_keypoints ---")
        kp_res = layer.detect_keypoints(test_meshes)
        print("Result:", kp_res)
        assert "Tagged" in kp_res
        
        print("\n--- Testing: semantic_segmentation ---")
        seg_res = layer.semantic_segmentation(test_meshes)
        print("Result:", seg_res)
        assert "Segmented" in seg_res
        
        print("\n--- Testing: extract_visibility_dna ---")
        vis_res = layer.extract_visibility_dna(test_meshes)
        print("Result:", vis_res)
        assert "Identified" in vis_res
        
        print("\n--- Testing: run_full_analysis ---")
        full_res = layer.run_full_analysis(test_meshes)
        print("Result Summary:", full_res["summary"])
        assert "Complete" in full_res["summary"]
        
        print("\n[SUCCESS] All Neural Analysis tests passed successfully.")
        
    except Exception as e:
        print(f"\n[ERROR] Neural Analysis testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_tests()
