import sys
import unittest
from unittest.mock import MagicMock, patch

# 1. Mock Maya Dependencies BEFORE importing Qyntara
sys.modules['maya'] = MagicMock()
sys.modules['maya.cmds'] = MagicMock()
sys.modules['maya.api'] = MagicMock()
sys.modules['maya.api.OpenMaya'] = MagicMock()

import maya.cmds as cmds
import maya.api.OpenMaya as om

# 2. Add Project to Path
sys.path.insert(0, r"e:/QYNTARA AI")

# 3. Import Qyntara Modules
try:
    from qyntara_ai.ui.main_window import QyntaraMainWindow
    from qyntara_ai.core.fixer import QyntaraFixer
except ImportError as e:
    print(f"Failed to import Qyntara modules: {e}")
    sys.exit(1)

class TestAutoFixLogic(unittest.TestCase):

    def setUp(self):
        # Reset mocks
        cmds.reset_mock()
        
        # Instantiate Main Window (headless)
        # We mock QtWidgets because we don't have a QApplication
        with patch('qyntara_ai.ui.qt_utils.QtWidgets.QWidget'), \
             patch('qyntara_ai.ui.qt_utils.QtWidgets.QMainWindow'), \
             patch('qyntara_ai.ui.style.STYLESHEET', ""): 
             # We might need to mock more qt widgets if __init__ creates them
             # Actually, simpler to just instantiate the class and mock its UI components
             pass

    def test_fix_order_priority(self):
        """
        Verifies that Auto-Fix respects the priority: 
        Topology (Merge) -> Transforms -> Normals -> UVs
        """
        print("\n--- Testing Auto-Fix Priority Order ---")

        # Mock the QyntaraMainWindow purely for its methods, without triggering __init__ UI creation which needs Qt
        # We can just test the logic method directly if we extract it or mock the instance
        
        # Better approach: Create a dummy class or just test the logic loop if we could.
        # But the logic is inside auto_fix_all.
        
        # Let's verify the `fix_map` in `main_window.py` is ordered correctly.
        # We can inspect the code or just import the class and look at the method source?
        # No, let's execute the method on a mocked instance.
        
        window_mock = MagicMock()
        window_mock.log = MagicMock()
        
        # Create a fake report with disorder
        # We want to ensure 'geo_open_edges' runs BEFORE 'geo_normals'
        fake_report = {
            "details": [
                {"rule_id": "uv_flipped", "violations": [{"object": "pCube1"}]},
                {"rule_id": "geo_normals", "violations": [{"object": "pCube1"}]},
                {"rule_id": "geo_open_edges", "violations": [{"object": "pCube1"}]}, # Should be fixed first
                {"rule_id": "xform_frozen", "violations": [{"object": "pCube1"}]}, # Should be second
            ]
        }
        window_mock.last_report = fake_report
        
        # We need to access the REAL auto_fix_all code. 
        # Since we can't easily instantiate QMainWindow without Qt, 
        # we will grab the unbound function and bind it to our mock.
        
        real_auto_fix = QyntaraMainWindow.auto_fix_all
        
        # Mock the QyntaraFixer methods to track call order
        manager = MagicMock()
        
        # We need to patch the Fixer methods referenced IN THE MAP inside main_window
        # Since the map points to QyntaraFixer.method, patching QyntaraFixer.method works
        
        with patch.object(QyntaraFixer, 'fix_open_edges', side_effect=lambda x: manager.fix_open_edges()) as mock_edges, \
             patch.object(QyntaraFixer, 'fix_normals', side_effect=lambda x: manager.fix_normals()) as mock_normals, \
             patch.object(QyntaraFixer, 'fix_freeze_all', side_effect=lambda x: manager.fix_freeze_all()) as mock_freeze, \
             patch.object(QyntaraFixer, 'fix_flipped_uvs', side_effect=lambda x: manager.fix_flipped_uvs()) as mock_uvs:
            
            # Execute the method on our fake window object
            real_auto_fix(window_mock)
            
            # Verify Calls
            print(f"Calls made: {manager.mock_calls}")
            
            # Expected Order: OpenEdges -> Frozen -> Normals -> UVs
            expected_order = [
                'fix_open_edges', 
                'fix_freeze_all', 
                'fix_normals', 
                'fix_flipped_uvs'
            ]
            
            actual_calls = [c[0] for c in manager.mock_calls]
            
            # Filter only expected ones (in case logging calls etc happen)
            actual_calls = [c for c in actual_calls if c in expected_order]
            
            print(f"Actual Execution Order: {actual_calls}")
            
            self.assertEqual(actual_calls, expected_order, 
                "Auto-Fix did NOT execute in safe priority order!")
            print("SUCCESS: Fixes executed in safe topological order.")

    def test_fixer_function_logic(self):
        """
        Verifies that specific fixers use the correct Maya commands (e.g. Merge vs Close).
        """
        print("\n--- Testing Fixer Implementation Details ---")
        
        # 1. Test fix_open_edges uses MergeVertex
        mock_report = {"violations": [{"object": "pCube1", "components": ["e[1]"]}]}
        
        # Setup mocks for this specific call
        cmds.polyListComponentConversion.return_value = ["vtx[1]", "vtx[2]"]
        cmds.ls.return_value = ["vtx[1]", "vtx[2]"]
        
        QyntaraFixer.fix_open_edges(mock_report)
        
        # Verify polyMergeVertex was called
        cmds.polyMergeVertex.assert_called()
        # Verify polyCloseBorder was NOT called
        cmds.polyCloseBorder.assert_not_called()
        print("SUCCESS: fix_open_edges uses polyMergeVertex (Safe).")
        
        # 2. Test fix_shadow_terminator uses Hard Edges
        cmds.reset_mock()
        QyntaraFixer.fix_shadow_terminator({"violations": [{"object": "pSphere1"}]})
        
        cmds.polySoftEdge.assert_called_with("pSphere1", angle=30, ch=1)
        cmds.polySmooth.assert_not_called()
        print("SUCCESS: fix_shadow_terminator uses polySoftEdge (Non-Destructive).")

if __name__ == '__main__':
    unittest.main()
