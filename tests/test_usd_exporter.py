import unittest
import os
import sys

# Ensure backend path is in sys.path
sys.path.append(os.getcwd())

from backend.exporters.usd_exporter import UsdExporter

class TestUsdExporter(unittest.TestCase):
    def test_export_cube(self):
        obj_path = "backend/data/test_cube.obj"
        output_path = "backend/data/test_export.usda"
        
        # Ensure input exists
        if not os.path.exists(obj_path):
            print(f"Creating dummy OBJ at {obj_path}")
            with open(obj_path, 'w') as f:
                f.write("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 3\n")
        
        exporter = UsdExporter()
        success = exporter.export_to_usda(obj_path, output_path)
        
        self.assertTrue(success, "Export returned False")
        self.assertTrue(os.path.exists(output_path), "Output file not created")
        
        with open(output_path, 'r') as f:
            content = f.read()
            self.assertIn("#usda 1.0", content)
            self.assertIn("def Mesh", content)
            self.assertIn("faceVertexCounts", content)
            
        print(f"USD Export content preview:\n{content[:200]}...")

if __name__ == "__main__":
    unittest.main()
