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

# Setup simulated mesh data
mock_cmds.polyEvaluate = lambda *args, **kwargs: 25000  # High poly count
mock_cmds.objExists = lambda *args, **kwargs: False
mock_cmds.pluginInfo = lambda *args, **kwargs: True     # Force plugin load Success

class MockPoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class MockPointArray:
    def __init__(self):
        self.pts = []
    def append(self, pt):
        self.pts.append(pt)

mock_om.MPointArray = MockPointArray
mock_om.MPoint = lambda pt: MockPoint(pt.x, pt.y, pt.z)
mock_om.MSpace = MagicMock()
mock_om.MSpace.kWorld = "kWorld"

class MockMeshFn:
    def getPoints(self, *args):
        # Return some slightly off-grid points
        return [
            MockPoint(0.02, 1.0, 0.0),
            MockPoint(1.0, 1.98, 0.0),
            MockPoint(0.5, 0.5, 0.5)
        ]
    def setPoints(self, *args): pass
mock_om.MFnMesh = lambda *args: MockMeshFn()

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
    print("=== Qyntara Nexus: Testing Core Solvers ===")
    
    project_dir = r"i:\QYNTARA AI"
    if project_dir not in sys.path:
         sys.path.append(project_dir)
         
    try:
        from qyntara_ai.core.solvers import CoreSolvers
        
        solvers = CoreSolvers()
        test_meshes = ["HighPoly_Scan", "Organic_Creature"]
        
        print("\n--- Testing: qem_curvature_reduce ---")
        qem_res = solvers.qem_curvature_reduce(test_meshes, target_faces=5000)
        print("Result:", qem_res)
        assert "QEM Reduced" in qem_res
        
        print("\n--- Testing: transformer_auto_retopology ---")
        tr_res = solvers.transformer_auto_retopology(test_meshes, target_faces=5000)
        print("Result:", tr_res)
        assert "Transformer Auto-Retopo" in tr_res
        
        print("\n--- Testing: planar_primitive_snap ---")
        snap_res = solvers.planar_primitive_snap(test_meshes)
        print("Result:", snap_res)
        assert "Planar Snap: Aligned" in snap_res
        
        print("\n[SUCCESS] All Core Solver tests passed successfully.")
        
    except Exception as e:
        print(f"\n[ERROR] Core Solver testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_tests()
