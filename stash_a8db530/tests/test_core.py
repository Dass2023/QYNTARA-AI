"""
Qyntara Core Engine - Unit Tests
================================

Comprehensive test suite for Core Engine foundation.

Run with: pytest tests/test_core.py -v --cov=qyntara_core

Author: Dass2023
License: MIT
Version: 5.0.0
"""

import pytest
import numpy as np
import tempfile
from pathlib import Path

from qyntara_core.datatypes import (
    QMesh, QMaterial, QCamera, QLight, QScene, TopologyType
)
from qyntara_core.geometry import MeshProcessor, MeshStats


class TestQMesh:
    """Test QMesh data type"""
    
    def test_create_triangle_mesh(self):
        """Test creating a simple triangle mesh"""
        vertices = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces, name="Triangle")
        
        assert mesh.vertex_count == 3
        assert mesh.face_count == 1
        assert mesh.is_triangulated
        assert mesh.topology_type == TopologyType.TRIANGLES
    
    def test_create_quad_mesh(self):
        """Test creating a quad mesh"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2, 3]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces, name="Quad")
        
        assert mesh.vertex_count == 4
        assert mesh.face_count == 1
        assert not mesh.is_triangulated
        assert mesh.topology_type == TopologyType.QUADS
    
    def test_triangulate_quad(self):
        """Test quad triangulation"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2, 3]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        tri_mesh = mesh.triangulate()
        
        assert tri_mesh.is_triangulated
        assert tri_mesh.face_count == 2  # Quad becomes 2 triangles
        assert tri_mesh.vertex_count == 4  # Same vertices
    
    def test_compute_smooth_normals(self):
        """Test smooth normal computation"""
        # Create pyramid
        vertices = np.array([
            [0, 0, 0],   # Base center
            [1, 0, 0],   # Base corner 1
            [0, 0, 1],   # Base corner 2
            [0, 1, 0.5]  # Apex
        ], dtype=np.float32)
        faces = np.array([
            [0, 1, 3],  # Side face 1
            [0, 3, 2],  # Side face 2
            [1, 2, 3],  # Side face 3
        ], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        mesh.compute_normals(smooth=True)
        
        assert mesh.normals is not None
        assert mesh.normals.shape == (4, 3)
        
        # Normals should be unit length
        norms = np.linalg.norm(mesh.normals, axis=1)
        np.testing.assert_array_almost_equal(norms, np.ones(4), decimal=5)
    
    def test_invalid_vertices_shape(self):
        """Test error on invalid vertex shape"""
        with pytest.raises(ValueError, match="Vertices must be"):
            vertices = np.array([[0, 0]], dtype=np.float32)  # Only 2D
            faces = np.array([[0, 1, 2]], dtype=np.int32)
            QMesh(vertices=vertices, faces=faces)


class TestQMaterial:
    """Test QMaterial data type"""
    
    def test_create_procedural_material(self):
        """Test creating procedural PBR material"""
        mat = QMaterial(
            name="Gold",
            base_color=np.array([1.0, 0.766, 0.336], dtype=np.float32),
            metallic=1.0,
            roughness=0.1
        )
        
        assert mat.name == "Gold"
        assert mat.metallic == 1.0
        assert mat.roughness == 0.1
        assert not mat.is_textured("base_color")
    
    def test_create_textured_material(self):
        """Test creating textured material"""
        mat = QMaterial(
            name="Wood",
            base_color="textures/wood_albedo.png",
            metallic=0.0,
            roughness="textures/wood_roughness.png",
            normal_map="textures/wood_normal.png"
        )
        
        assert mat.is_textured("base_color")
        assert mat.is_textured("roughness")
        assert mat.normal_map == "textures/wood_normal.png"


class TestQScene:
    """Test QScene data type"""
    
    def test_create_empty_scene(self):
        """Test creating empty scene"""
        scene = QScene()
        
        assert len(scene.meshes) == 0
        assert len(scene.materials) == 0
        assert scene.total_vertices == 0
        assert scene.total_faces == 0
    
    def test_scene_with_content(self):
        """Test scene with meshes and materials"""
        mesh1 = QMesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.int32)
        )
        mesh2 = QMesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0]], dtype=np.float32),
            faces=np.array([[0, 1]], dtype=np.int32)
        )
        mat = QMaterial(name="TestMat")
        
        scene = QScene(meshes=[mesh1, mesh2], materials=[mat])
        
        assert len(scene.meshes) == 2
        assert len(scene.materials) == 1
        assert scene.total_vertices == 5
        assert scene.total_faces == 2
    
    def test_validate_scene(self):
        """Test scene validation"""
        # Create mesh with invalid material ID
        mesh = QMesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.int32),
            material_ids=np.array([5], dtype=np.int32)  # Material 5 doesn't exist
        )
        
        scene = QScene(meshes=[mesh], materials=[])
        issues = scene.validate()
        
        assert len(issues) > 0
        assert any("material" in issue.lower() for issue in issues)
    
    def test_get_material_by_name(self):
        """Test finding material by name"""
        mat1 = QMaterial(name="Gold")
        mat2 = QMaterial(name="Silver")
        
        scene = QScene(materials=[mat1, mat2])
        
        found = scene.get_material_by_name("Silver")
        assert found is not None
        assert found.name == "Silver"
        
        not_found = scene.get_material_by_name("Bronze")
        assert not_found is None


class TestMeshProcessor:
    """Test MeshProcessor operations"""
    
    def test_validate_clean_mesh(self):
        """Test validation of clean mesh"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        issues = MeshProcessor.validate_mesh(mesh)
        
        assert len(issues) == 0
    
    def test_validate_degenerate_mesh(self):
        """Test detection of degenerate faces"""
        # All vertices at same point
        vertices = np.array([
            [0, 0, 0], [0, 0, 0], [0, 0, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        issues = MeshProcessor.validate_mesh(mesh)
        
        assert len(issues) > 0
        assert any("zero area" in issue.lower() for issue in issues)
    
    def test_validate_ngon(self):
        """Test detection of n-gons"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [2, 0, 0], [2, 1, 0], [1, 1, 0], [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2, 3, 4, 5]], dtype=np.int32)  # 6-sided polygon
        
        mesh = QMesh(vertices=vertices, faces=faces)
        issues = MeshProcessor.validate_mesh(mesh)
        
        assert len(issues) > 0
        assert any("n-gon" in issue.lower() for issue in issues)
    
    def test_compute_bounding_box(self):
        """Test bounding box computation"""
        vertices = np.array([
            [-1, -2, -3],
            [1, 2, 3],
            [0, 0, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        min_pt, max_pt = MeshProcessor.compute_bounding_box(mesh)
        
        np.testing.assert_array_equal(min_pt, [-1, -2, -3])
        np.testing.assert_array_equal(max_pt, [1, 2, 3])
    
    def test_center_mesh(self):
        """Test mesh centering"""
        vertices = np.array([
            [10, 10, 10],
            [11, 10, 10],
            [10, 11, 10]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        centered = MeshProcessor.center_mesh(mesh)
        
        # Center should be at origin
        min_pt, max_pt = MeshProcessor.compute_bounding_box(centered)
        center = (min_pt + max_pt) / 2
        
        np.testing.assert_array_almost_equal(center, [0, 0, 0], decimal=5)
    
    def test_scale_mesh(self):
        """Test mesh scaling"""
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        scaled = MeshProcessor.scale_mesh(mesh, scale=2.0)
        
        expected = vertices * 2.0
        np.testing.assert_array_equal(scaled.vertices, expected)
    
    def test_remove_duplicate_faces(self):
        """Test duplicate face removal"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([
            [0, 1, 2],
            [0, 1, 2],  # Duplicate
            [0, 2, 1],  # Same face, different order
        ], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        cleaned = MeshProcessor.remove_duplicate_faces(mesh)
        
        # Should only have 1 unique face
        assert cleaned.face_count == 1
    
    def test_compute_face_areas(self):
        """Test face area computation"""
        # Unit triangle (area = 0.5)
        vertices = np.array([
            [0, 0, 0],
            [1, 0, 0],
            [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        areas = MeshProcessor.compute_face_areas(mesh)
        
        assert len(areas) == 1
        np.testing.assert_almost_equal(areas[0], 0.5, decimal=5)


class TestMeshStats:
    """Test MeshStats"""
    
    def test_compute_stats(self):
        """Test comprehensive stats computation"""
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2, 3]], dtype=np.int32)
        uvs = [np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)]
        
        mesh = QMesh(vertices=vertices, faces=faces, uvs=uvs)
        mesh.compute_normals(smooth=True)
        
        stats = MeshStats.compute_stats(mesh)
        
        assert stats['vertex_count'] == 4
        assert stats['face_count'] == 1
        assert stats['topology_type'] == 'QUADS'
        assert not stats['is_triangulated']
        assert stats['has_normals']
        assert stats['has_uvs']
        assert stats['uv_set_count'] == 1
        assert 'bounding_box' in stats
        assert 'surface_area' in stats


class TestGLTFConverter:
    """Test glTF converter"""
    
    def test_gltf_export_import_roundtrip(self):
        """Test glTF export and import roundtrip"""
        from qyntara_core.io import GLTFConverter
        
        # Create test mesh
        vertices = np.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0]
        ], dtype=np.float32)
        faces = np.array([[0, 1, 2]], dtype=np.int32)
        normals = np.array([
            [0, 0, 1], [0, 0, 1], [0, 0, 1]
        ], dtype=np.float32)
        
        mesh = QMesh(vertices=vertices, faces=faces, normals=normals, name="Triangle")
        mat = QMaterial(name="TestMat", metallic=0.5, roughness=0.3)
        scene = QScene(meshes=[mesh], materials=[mat])
        
        # Export to GLB
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.glb"
            GLTFConverter.export(scene, str(filepath), binary=True)
            
            # Import back
            loaded = GLTFConverter.import_file(str(filepath))
            
            # Verify
            assert len(loaded.meshes) == 1
            assert loaded.meshes[0].vertex_count == 3
            assert loaded.meshes[0].face_count == 1
            assert loaded.meshes[0].is_triangulated
            
            # Verify vertices match (approximately)
            np.testing.assert_array_almost_equal(
                loaded.meshes[0].vertices,
                vertices,
                decimal=4
            )
    
    def test_gltf_json_export(self):
        """Test glTF JSON format export"""
        from qyntara_core.io import GLTFConverter
        
        mesh = QMesh(
            vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
            faces=np.array([[0, 1, 2]], dtype=np.int32)
        )
        scene = QScene(meshes=[mesh])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = Path(tmpdir) / "test.gltf"
            GLTFConverter.export(scene, str(filepath), binary=False)
            
            # Check files exist
            assert filepath.exists()
            assert (Path(tmpdir) / "test.bin").exists()
            
            # Load and verify JSON
            import json
            with open(filepath, 'r') as f:
                gltf_json = json.load(f)
            
            assert gltf_json['asset']['version'] == '2.0'
            assert len(gltf_json['meshes']) == 1


# Performance benchmarks (optional)
class TestPerformance:
    """Performance benchmarks"""
    
    def test_large_mesh_processing(self):
        """Test processing a large mesh"""
        import time
        
        # Create mesh with 10K vertices
        np.random.seed(42)
        vertices = np.random.randn(10000, 3).astype(np.float32)
        faces = np.random.randint(0, 10000, size=(5000, 3)).astype(np.int32)
        
        mesh = QMesh(vertices=vertices, faces=faces)
        
        # Time bounding box computation
        start = time.time()
        min_pt, max_pt = MeshProcessor.compute_bounding_box(mesh)
        elapsed = time.time() - start
        
        assert elapsed < 0.1  # Should be fast (<100ms)
        
        # Time validation
        start = time.time()
        issues = MeshProcessor.validate_mesh(mesh)
        elapsed = time.time() - start
        
        assert elapsed < 1.0  # Should be reasonable (<1s for 10K verts)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=qyntara_core", "--cov-report=term-missing"])
