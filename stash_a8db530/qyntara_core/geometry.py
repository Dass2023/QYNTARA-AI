"""
Qyntara Core Engine - Geometry Processing
=========================================

DCC-agnostic mesh processing operations.
These work identically in Maya, 3ds Max, Blender, Unity, Unreal.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import numpy as np
from typing import List, Tuple, Optional
from .datatypes import QMesh

try:
    import scipy.spatial
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


class MeshProcessor:
    """
    DCC-agnostic mesh operations - the core of Qyntara's "secret sauce"
    
    All geometry operations work on QMesh, ensuring identical results
    across Maya, Max, Blender, and game engines.
    """
    
    @staticmethod
    def validate_mesh(mesh: QMesh) -> List[str]:
        """
        Detect common topology issues.
        
        Returns:
            List of issues found (empty if valid)
        
        Example:
            >>> issues = MeshProcessor.validate_mesh(my_mesh)
            >>> if issues:
            ...     print("Problems found:", issues)
        """
        issues = []
        
        # Check for degenerate faces (zero area)
        for i, face in enumerate(mesh.faces):
            face = face[face != -1]
            if len(face) < 3:
                issues.append(f"Face {i}: Less than 3 vertices")
                continue
            
            # Get vertex positions
            verts = mesh.vertices[face[:3]]
            
            # Compute area via cross product
            edge1 = verts[1] - verts[0]
            edge2 = verts[2] - verts[0]
            area = np.linalg.norm(np.cross(edge1, edge2)) / 2
            
            if area < 1e-6:
                issues.append(f"Face {i}: Degenerate (zero area)")
        
        # Check for n-gons (faces with > 4 vertices)
        for i, face in enumerate(mesh.faces):
            face = face[face != -1]
            if len(face) > 4:
                issues.append(f"Face {i}: N-gon with {len(face)} vertices")
        
        # Check for flipped normals
        if mesh.normals is not None:
            # Compute geometric normals and compare
            for i, face in enumerate(mesh.faces):
                face = face[face != -1][:3]
                verts = mesh.vertices[face]
                
                # Geometric normal
                edge1 = verts[1] - verts[0]
                edge2 = verts[2] - verts[0]
                geom_normal = np.cross(edge1, edge2)
                geom_normal /= (np.linalg.norm(geom_normal) + 1e-6)
                
                # Average vertex normals for this face
                avg_normal = np.mean(mesh.normals[face], axis=0)
                avg_normal /= (np.linalg.norm(avg_normal) + 1e-6)
                
                # Check if they point in opposite directions
                if np.dot(geom_normal, avg_normal) < 0:
                    issues.append(f"Face {i}: Flipped normal detected")
        
        # Check for isolated vertices (not referenced by any face)
        used_vertices = set(mesh.faces[mesh.faces != -1].flatten())
        isolated = set(range(mesh.vertex_count)) - used_vertices
        if isolated:
            issues.append(f"{len(isolated)} isolated vertices found")
        
        return issues
    
    @staticmethod
    def compute_bounding_box(mesh: QMesh) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute axis-aligned bounding box.
        
        Returns:
            (min_point, max_point) as (3,) arrays
        """
        min_point = np.min(mesh.vertices, axis=0)
        max_point = np.max(mesh.vertices, axis=0)
        return min_point, max_point
    
    @staticmethod
    def center_mesh(mesh: QMesh) -> QMesh:
        """
        Move mesh so its bounding box center is at origin.
        
        Returns:
            New centered QMesh
        """
        min_pt, max_pt = MeshProcessor.compute_bounding_box(mesh)
        center = (min_pt + max_pt) / 2
        
        new_vertices = mesh.vertices - center
        
        return QMesh(
            vertices=new_vertices,
            faces=mesh.faces.copy(),
            normals=mesh.normals.copy() if mesh.normals is not None else None,
            uvs=[uv.copy() for uv in mesh.uvs] if mesh.uvs else None,
            vertex_colors=mesh.vertex_colors.copy() if mesh.vertex_colors is not None else None,
            material_ids=mesh.material_ids.copy() if mesh.material_ids is not None else None,
            name=mesh.name
        )
    
    @staticmethod
    def scale_mesh(mesh: QMesh, scale: float) -> QMesh:
        """
        Uniformly scale mesh.
        
        Args:
            scale: Scale factor (2.0 = double size)
        
        Returns:
            New scaled QMesh
        """
        return QMesh(
            vertices=mesh.vertices * scale,
            faces=mesh.faces.copy(),
            normals=mesh.normals.copy() if mesh.normals is not None else None,
            uvs=[uv.copy() for uv in mesh.uvs] if mesh.uvs else None,
            vertex_colors=mesh.vertex_colors.copy() if mesh.vertex_colors is not None else None,
            material_ids=mesh.material_ids.copy() if mesh.material_ids is not None else None,
            name=mesh.name
        )
    
    @staticmethod
    def merge_vertices(mesh: QMesh, threshold: float = 1e-5) -> QMesh:
        """
        Merge vertices that are within threshold distance.
        
        Args:
            threshold: Distance threshold for merging
        
        Returns:
            New QMesh with merged vertices
        """
        if not HAS_SCIPY:
            raise ImportError("scipy required for merge_vertices. Install with: pip install scipy")
        
        # Build KD-tree for fast nearest-neighbor search
        tree = scipy.spatial.cKDTree(mesh.vertices)
        
        # Find pairs of vertices within threshold
        pairs = tree.query_pairs(threshold)
        
        # Build equivalence classes (union-find)
        parent = list(range(mesh.vertex_count))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        for i, j in pairs:
            union(i, j)
        
        # Build new vertex list (one per equivalence class)
        vertex_map = {}  # old index -> new index
        new_vertices = []
        
        for i in range(mesh.vertex_count):
            root = find(i)
            if root not in vertex_map:
                vertex_map[root] = len(new_vertices)
                new_vertices.append(mesh.vertices[root])
            vertex_map[i] = vertex_map[root]
        
        # Remap faces
        new_faces = []
        for face in mesh.faces:
            new_face = [vertex_map.get(v, v) if v != -1 else -1 for v in face]
            new_faces.append(new_face)
        
        return QMesh(
            vertices=np.array(new_vertices, dtype=np.float32),
            faces=np.array(new_faces, dtype=np.int32),
            name=mesh.name
        )
    
    @staticmethod
    def remove_duplicate_faces(mesh: QMesh) -> QMesh:
        """
        Remove faces that reference the same vertices (in any order).
        
        Returns:
            New QMesh with duplicates removed
        """
        unique_faces = []
        seen_sets = set()
        
        for face in mesh.faces:
            # Ignore padding
            face = face[face != -1]
            
            # Convert to set for order-independent comparison
            face_set = frozenset(face)
            
            if face_set not in seen_sets:
                seen_sets.add(face_set)
                unique_faces.append(face)
        
        # Pad faces back to uniform length
        max_len = max(len(f) for f in unique_faces)
        padded_faces = []
        for face in unique_faces:
            padded = list(face) + [-1] * (max_len - len(face))
            padded_faces.append(padded)
        
        return QMesh(
            vertices=mesh.vertices.copy(),
            faces=np.array(padded_faces, dtype=np.int32),
            normals=mesh.normals.copy() if mesh.normals is not None else None,
            uvs=[uv.copy() for uv in mesh.uvs] if mesh.uvs else None,
            vertex_colors=mesh.vertex_colors.copy() if mesh.vertex_colors is not None else None,
            name=mesh.name
        )
    
    @staticmethod
    def compute_face_areas(mesh: QMesh) -> np.ndarray:
        """
        Compute area of each face.
        
        Returns:
            Array of face areas
        """
        areas = np.zeros(mesh.face_count, dtype=np.float32)
        
        for i, face in enumerate(mesh.faces):
            face = face[face != -1]
            if len(face) < 3:
                continue
            
            # Triangulate and sum triangle areas
            total_area = 0.0
            for j in range(1, len(face) - 1):
                verts = mesh.vertices[[face[0], face[j], face[j+1]]]
                edge1 = verts[1] - verts[0]
                edge2 = verts[2] - verts[0]
                area = np.linalg.norm(np.cross(edge1, edge2)) / 2
                total_area += area
            
            areas[i] = total_area
        
        return areas
    
    @staticmethod
    def optimize_topology(mesh: QMesh, target_tri_count: int) -> QMesh:
        """
        Neural mesh optimization (placeholder for v5.0 AI feature).
        
        In v4.6.1 LTS: Simple decimation
        In v5.0: Graph Neural Network optimization
        
        Args:
            target_tri_count: Target number of triangles
        
        Returns:
            Optimized QMesh
        """
        # v4.6.1 LTS: Placeholder (returns original mesh)
        # TODO v5.0: Implement GNN-based optimization
        import warnings
        warnings.warn("optimize_topology is a stub in v4.6.1. Full AI implementation in v5.0")
        return mesh
    
    @staticmethod
    def auto_uv_unwrap(mesh: QMesh) -> QMesh:
        """
        AI-powered UV unwrapping (placeholder for v5.0 feature).
        
        In v4.6.1 LTS: Not implemented
        In v5.0: Neural UV optimization
        
        Returns:
            QMesh with generated UVs
        """
        # v4.6.1 LTS: Placeholder
        # TODO v5.0: Implement neural UV unwrapping
        raise NotImplementedError("auto_uv_unwrap will be implemented in v5.0")


class MeshStats:
    """Compute mesh statistics for analysis"""
    
    @staticmethod
    def compute_stats(mesh: QMesh) -> dict:
        """
        Compute comprehensive mesh statistics.
        
        Returns:
            Dictionary with mesh metrics
        """
        min_pt, max_pt = MeshProcessor.compute_bounding_box(mesh)
        bbox_size = max_pt - min_pt
        
        areas = MeshProcessor.compute_face_areas(mesh)
        
        return {
            'vertex_count': mesh.vertex_count,
            'face_count': mesh.face_count,
            'topology_type': mesh.topology_type.name,
            'is_triangulated': mesh.is_triangulated,
            'bounding_box': {
                'min': min_pt.tolist(),
                'max': max_pt.tolist(),
                'size': bbox_size.tolist(),
                'volume': float(np.prod(bbox_size))
            },
            'surface_area': float(np.sum(areas)),
            'has_normals': mesh.normals is not None,
            'has_uvs': mesh.uvs is not None and len(mesh.uvs) > 0,
            'has_vertex_colors': mesh.vertex_colors is not None,
            'uv_set_count': len(mesh.uvs) if mesh.uvs else 0
        }
