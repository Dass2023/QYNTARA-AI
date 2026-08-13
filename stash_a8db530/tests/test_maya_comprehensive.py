"""
Qyntara Core Engine - Comprehensive Maya Test Suite
===================================================

Production validation suite for Maya adapter.
Tests all aspects: mesh extraction, processing, export, and roundtrip.

Run in Maya Script Editor:
    exec(open(r"i:\QYNTARA AI\tests\test_maya_comprehensive.py").read())

Author: Dass2023
License: MIT
Version: 5.0.0
"""

import maya.cmds as cmds
import maya.api.OpenMaya as om
import sys
import os
import time

# Add Qyntara to path
qyntara_path = r"i:\QYNTARA AI"
if qyntara_path not in sys.path:
    sys.path.insert(0, qyntara_path)

from qyntara_dcc.maya import MayaAdapter
from qyntara_core.geometry import MeshProcessor, MeshStats
from qyntara_core.io import GLTFConverter, USDConverter
from qyntara_core import QScene, QMesh
import numpy as np


class MayaTestSuite:
    """Comprehensive test suite for Maya adapter"""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def log_result(self, test_name, passed, message=""):
        """Log test result"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✅ PASS"
        else:
            self.failed_tests += 1
            status = "❌ FAIL"
        
        result = f"{status} | {test_name}"
        if message:
            result += f"\n       {message}"
        
        self.results.append(result)
        print(result)
    
    def test_create_test_geometry(self):
        """Test 1: Create test geometry"""
        try:
            # Create various test objects
            sphere = cmds.polySphere(name="test_sphere", r=1, sx=20, sy=20)[0]
            cube = cmds.polyCube(name="test_cube", w=1, h=1, d=1)[0]
            cylinder = cmds.polyCylinder(name="test_cylinder", r=0.5, h=2, sx=16)[0]
            
            # Add UVs
            cmds.polyAutoProjection(sphere, cube, cylinder)
            
            # Select sphere for testing
            cmds.select(sphere)
            
            self.log_result(
                "Create Test Geometry",
                True,
                f"Created: {sphere}, {cube}, {cylinder}"
            )
            return True
        except Exception as e:
            self.log_result("Create Test Geometry", False, str(e))
            return False
    
    def test_extract_mesh(self):
        """Test 2: Extract mesh from Maya"""
        try:
            selection = cmds.ls(selection=True)
            if not selection:
                cmds.select("test_sphere")
            
            qmesh = MayaAdapter.get_selected_mesh()
            
            # Validate
            assert qmesh.vertex_count > 0, "No vertices"
            assert qmesh.face_count > 0, "No faces"
            assert qmesh.normals is not None, "No normals"
            assert qmesh.uvs is not None, "No UVs"
            
            self.log_result(
                "Extract Mesh",
                True,
                f"Vertices: {qmesh.vertex_count}, Faces: {qmesh.face_count}, UVs: {len(qmesh.uvs)} sets"
            )
            return qmesh
        except Exception as e:
            self.log_result("Extract Mesh", False, str(e))
            return None
    
    def test_mesh_validation(self, qmesh):
        """Test 3: Validate mesh quality"""
        try:
            issues = MeshProcessor.validate_mesh(qmesh)
            
            passed = len(issues) == 0
            msg = "Clean mesh" if passed else f"Found {len(issues)} issues"
            
            self.log_result("Mesh Validation", passed, msg)
            return passed
        except Exception as e:
            self.log_result("Mesh Validation", False, str(e))
            return False
    
    def test_compute_stats(self, qmesh):
        """Test 4: Compute mesh statistics"""
        try:
            stats = MeshStats.compute_stats(qmesh)
            
            required_fields = ['vertex_count', 'face_count', 'surface_area', 'bounding_box']
            for field in required_fields:
                assert field in stats, f"Missing field: {field}"
            
            self.log_result(
                "Compute Statistics",
                True,
                f"Surface area: {stats['surface_area']:.2f}, Topology: {stats['topology_type']}"
            )
            return stats
        except Exception as e:
            self.log_result("Compute Statistics", False, str(e))
            return None
    
    def test_mesh_processing(self, qmesh):
        """Test 5: Process mesh (center, scale, triangulate)"""
        try:
            # Center
            centered = MeshProcessor.center_mesh(qmesh)
            min_pt, max_pt = MeshProcessor.compute_bounding_box(centered)
            center = (min_pt + max_pt) / 2
            center_dist = np.linalg.norm(center)
            
            assert center_dist < 0.01, f"Not centered: {center_dist}"
            
            # Scale
            scaled = MeshProcessor.scale_mesh(centered, scale=0.5)
            assert np.max(np.abs(scaled.vertices)) < np.max(np.abs(qmesh.vertices)), "Scaling failed"
            
            # Triangulate
            if not qmesh.is_triangulated:
                tri = qmesh.triangulate()
                assert tri.is_triangulated, "Triangulation failed"
            
            self.log_result(
                "Mesh Processing",
                True,
                f"Center distance: {center_dist:.6f}, Scaled successfully, Triangulated"
            )
            return scaled
        except Exception as e:
            self.log_result("Mesh Processing", False, str(e))
            return None
    
    def test_create_in_maya(self, qmesh):
        """Test 6: Create mesh back in Maya"""
        try:
            new_name = MayaAdapter.create_mesh_from_qmesh(qmesh, name="qmesh_processed")
            
            # Verify it exists
            assert cmds.objExists(new_name), f"Object {new_name} not created"
            
            # Verify it's selected
            selection = cmds.ls(selection=True)
            assert new_name in selection, "Not selected"
            
            # Get vertex count
            vert_count = cmds.polyEvaluate(new_name, vertex=True)
            
            self.log_result(
                "Create in Maya",
                True,
                f"Created {new_name} with {vert_count} vertices"
            )
            return new_name
        except Exception as e:
            self.log_result("Create in Maya", False, str(e))
            return None
    
    def test_export_gltf(self, qmesh):
        """Test 7: Export to glTF/GLB"""
        try:
            scene = QScene(meshes=[qmesh])
            export_path = r"C:\temp\qyntara_maya_test.glb"
            
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            start = time.time()
            GLTFConverter.export(scene, export_path, binary=True)
            elapsed = time.time() - start
            
            # Verify file exists
            assert os.path.exists(export_path), "GLB file not created"
            
            file_size = os.path.getsize(export_path)
            
            self.log_result(
                "Export glTF/GLB",
                True,
                f"Exported to {export_path} ({file_size/1024:.1f} KB) in {elapsed:.2f}s"
            )
            return export_path
        except Exception as e:
            self.log_result("Export glTF/GLB", False, str(e))
            return None
    
    def test_export_usd(self, qmesh):
        """Test 8: Export to USD"""
        try:
            scene = QScene(meshes=[qmesh])
            export_path = r"C:\temp\qyntara_maya_test.usdc"
            
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            start = time.time()
            USDConverter.export(scene, export_path, binary=True)
            elapsed = time.time() - start
            
            # Verify file exists
            assert os.path.exists(export_path), "USDC file not created"
            
            file_size = os.path.getsize(export_path)
            
            self.log_result(
                "Export USD",
                True,
                f"Exported to {export_path} ({file_size/1024:.1f} KB) in {elapsed:.2f}s"
            )
            return export_path
        except ImportError:
            self.log_result("Export USD", False, "USD library not installed (pip install usd-core)")
            return None
        except Exception as e:
            self.log_result("Export USD", False, str(e))
            return None
    
    def test_roundtrip_gltf(self, export_path):
        """Test 9: GLB roundtrip (export + import)"""
        try:
            # Import the GLB we just exported
            imported_scene = GLTFConverter.import_file(export_path)
            
            assert len(imported_scene.meshes) > 0, "No meshes imported"
            
            imported_mesh = imported_scene.meshes[0]
            assert imported_mesh.vertex_count > 0, "Imported mesh has no vertices"
            
            self.log_result(
                "GLB Roundtrip",
                True,
                f"Imported {len(imported_scene.meshes)} meshes, {imported_mesh.vertex_count} vertices"
            )
            return True
        except Exception as e:
            self.log_result("GLB Roundtrip", False, str(e))
            return False
    
    def test_scene_export(self):
        """Test 10: Export entire Maya scene"""
        try:
            # Select all test objects
            cmds.select("test_*")
            
            scene = MayaAdapter.get_scene()
            
            assert len(scene.meshes) > 0, "No meshes in scene"
            
            total_verts = scene.total_vertices
            total_faces = scene.total_faces
            
            self.log_result(
                "Scene Export",
                True,
                f"Exported {len(scene.meshes)} meshes, {total_verts:,} vertices, {total_faces:,} faces"
            )
            return scene
        except Exception as e:
            self.log_result("Scene Export", False, str(e))
            return None
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("\n" + "="*70)
        print("QYNTARA CORE ENGINE - MAYA COMPREHENSIVE TEST SUITE")
        print("="*70 + "\n")
        
        # Test 1: Create geometry
        if not self.test_create_test_geometry():
            print("\n⚠️  Cannot proceed without test geometry")
            return False
        
        # Test 2: Extract mesh
        qmesh = self.test_extract_mesh()
        if qmesh is None:
            print("\n⚠️  Cannot proceed without extracted mesh")
            return False
        
        # Test 3-5: Validation and processing
        self.test_mesh_validation(qmesh)
        self.test_compute_stats(qmesh)
        processed_mesh = self.test_mesh_processing(qmesh)
        
        # Test 6: Create in Maya
        if processed_mesh:
            self.test_create_in_maya(processed_mesh)
        
        # Test 7-8: Export formats
        gltf_path = self.test_export_gltf(qmesh)
        self.test_export_usd(qmesh)
        
        # Test 9: Roundtrip
        if gltf_path:
            self.test_roundtrip_gltf(gltf_path)
        
        # Test 10: Scene export
        self.test_scene_export()
        
        # Print summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests} ✅")
        print(f"Failed: {self.failed_tests} ❌")
        print(f"Success Rate: {(self.passed_tests/self.total_tests*100):.1f}%")
        print("="*70 + "\n")
        
        if self.failed_tests == 0:
            print("🎉 ALL TESTS PASSED! Maya adapter is production-ready.\n")
            return True
        else:
            print(f"⚠️  {self.failed_tests} test(s) failed. Review errors above.\n")
            return False


# Auto-run when executed
if __name__ == "__main__":
    suite = MayaTestSuite()
    suite.run_all_tests()
