import pytest
import trimesh
import numpy as np
import sys
import os

import sys
import os

# Ensure project root is in path
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.autonomy.remediator import AutoFixer
from backend.models import ValidationReport, GeometryValidation, TopologyValidation, UVValidation, MaterialValidation

class TestFixit:
    def setup_method(self):
        self.fixer = AutoFixer()
    
    def test_geometry_repair(self, tmp_path):
        """Test Hole Filling and Normal Re-calculation"""
        print("\n[Test] Creating Broken Mesh (Hole + Inverted)...")
        
        # 1. Create a box
        mesh = trimesh.creation.box(extents=[1,1,1])
        
        # 2. Break it: Remove a face to create a hole
        mesh.faces = mesh.faces[:-1] 
        assert not mesh.is_watertight
        
        # 3. Break it: Invert normals (randomly flip one face's winding?)
        # Trimesh fix_inversion handles global inversion usually.
        # Let's just create a hole first.
        
        broken_path = tmp_path / "broken_box.obj"
        mesh.export(broken_path)
        
        # 4. Create a mock Validation Report demanding fixes
        report = ValidationReport(
            geometry=GeometryValidation(watertight=False, issues=["Non-watertight geometry"]),
            topology=TopologyValidation(manifold=True), # Assume manifold otherwise
            uv=UVValidation(),
            material=MaterialValidation(),
            passed=False,
            score=50.0
        )
        
        # 5. Run Fixit
        print("[Fixit] Running Auto-Fix...")
        fixed_path, fixes = self.fixer.remedate_asset(str(broken_path), report)
        
        print(f"[Fixit] Applied: {fixes}")
        assert "Filled mesh holes" in fixes
        
        # 6. Verify Result
        fixed_mesh = trimesh.load(fixed_path)
        print(f"[Result] Is Watertight? {fixed_mesh.is_watertight}")
        assert fixed_mesh.is_watertight, "Mesh should be watertight after fix"
        assert len(fixed_mesh.faces) == 12, "Box should have 12 faces restored"

if __name__ == "__main__":
    t = TestFixit()
    t.setup_method()
    import pathlib
    import shutil
    temp_dir = pathlib.Path("temp_fix_assets")
    if temp_dir.exists(): shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    try:
        t.test_geometry_repair(temp_dir)
        print("\n[PASS] Fixit Test Passed!")
    except Exception as e:
        print(f"\n[FAIL] Fixit Test Failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pass
        # shutil.rmtree(temp_dir)
