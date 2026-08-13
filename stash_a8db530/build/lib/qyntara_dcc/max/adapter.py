"""
Qyntara DCC Adapters - 3ds Max Adapter
======================================

Translation layer between 3ds Max's API and Qyntara Core Engine.

Uses MaxPlus (Python API for 3ds Max) for modern 3ds Max versions (2015+),
with fallback to MaxScript for older versions.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import numpy as np
from typing import Optional, List

try:
    import MaxPlus
    HAS_MAXPLUS = True
except ImportError:
    HAS_MAXPLUS = False
    print("[3dsMax Adapter] MaxPlus not available - running outside 3ds Max")

from qyntara_core.datatypes import QMesh, QMaterial, QScene


class MaxAdapter:
    """
    Translate between 3ds Max's native API and QMesh.
    
    This adapter allows 3ds Max to use the Core Engine with identical
    behavior to Maya, Blender, and game engines.
    
    Example (run in 3ds Max Script Editor):
        >>> from qyntara_dcc.max import MaxAdapter
        >>> from qyntara_core.geometry import MeshProcessor
        >>> 
        >>> # Get selected mesh
        >>> qmesh = MaxAdapter.get_selected_mesh()
        >>> 
        >>> # Process with Core Engine
        >>> centered = MeshProcessor.center_mesh(qmesh)
        >>> 
        >>> # Create in Max
        >>> MaxAdapter.create_mesh_from_qmesh(centered)
    """
    
    @staticmethod
    def get_selected_mesh() -> QMesh:
        """
        Extract selected 3ds Max mesh to QMesh.
        
        Returns:
            QMesh representation of selected mesh
        
        Raises:
            ValueError: If no mesh is selected
            RuntimeError: If not running in 3ds Max
        """
        if not HAS_MAXPLUS:
            raise RuntimeError("MaxPlus not available - must run inside 3ds Max")
        
        # Get selection
        selection = MaxPlus.SelectionManager.GetNodes()
        
        if not selection:
            raise ValueError("No object selected in 3ds Max")
        
        node = selection[0]
        obj = node.GetObject()
        
        # Check if it's a mesh
        if not obj.IsSubClassOf(MaxPlus.ClassIds.TriObject):
            # Try to convert to editable mesh
            tri_obj = obj.ConvertToType(0, MaxPlus.ClassIds.TriObject)
            if tri_obj is None:
                raise ValueError("Selected object cannot be converted to mesh")
            obj = tri_obj
        
        # Get mesh data
        mesh = obj.GetMesh()
        
        # Extract vertices
        num_verts = mesh.GetNumVerts()
        vertices = []
        
        for i in range(num_verts):
            vert = mesh.GetVert(i)
            # Max uses Z-up, convert to Y-up for Qyntara
            vertices.append([vert.X, vert.Z, -vert.Y])
        
        vertices = np.array(vertices, dtype=np.float32)
        
        # Extract faces
        num_faces = mesh.GetNumFaces()
        faces = []
        
        for i in range(num_faces):
            face = mesh.GetFace(i)
            # Max triangulates automatically, so all faces are tris
            faces.append([face.V[0], face.V[1], face.V[2]])
        
        faces = np.array(faces, dtype=np.int32)
        
        # Extract normals (if available)
        normals = None
        mesh.BuildNormals()
        if mesh.GetNumVertNorms() > 0:
            normals = []
            for i in range(num_verts):
                norm = mesh.GetNormal(i)
                # Convert to Y-up
                normals.append([norm.X, norm.Z, -norm.Y])
            normals = np.array(normals, dtype=np.float32)
        
        # Extract UVs (map channel 1 is the default UV channel)
        uvs = None
        if mesh.GetNumMapVerts(1) > 0:
            num_uv_verts = mesh.GetNumMapVerts(1)
            uv_array = []
            
            for i in range(num_uv_verts):
                uv_vert = mesh.GetMapVert(1, i)
                uv_array.append([uv_vert.X, uv_vert.Y])
            
            uvs = [np.array(uv_array, dtype=np.float32)]
        
        # Get node name
        name = node.GetName()
        
        return QMesh(
            vertices=vertices,
            faces=faces,
            normals=normals,
            uvs=uvs if uvs else None,
            name=name
        )
    
    @staticmethod
    def create_mesh_from_qmesh(qmesh: QMesh, name: Optional[str] = None) -> str:
        """
        Create 3ds Max mesh from QMesh.
        
        Args:
            qmesh: QMesh to convert
            name: Optional name for new mesh
        
        Returns:
            Name of created mesh node
        """
        if not HAS_MAXPLUS:
            raise RuntimeError("MaxPlus not available - must run inside 3ds Max")
        
        if name is None:
            name = qmesh.name or "QMesh"
        
        # Ensure triangulated for Max
        if not qmesh.is_triangulated:
            qmesh = qmesh.triangulate()
        
        # Create new TriObject
        tri_obj = MaxPlus.Factory.CreateTriObject()
        mesh = tri_obj.GetMesh()
        
        # Set vertex count
        mesh.SetNumVerts(qmesh.vertex_count)
        
        # Add vertices (convert Y-up to Z-up)
        for i, vert in enumerate(qmesh.vertices):
            x, y, z = vert
            # Qyntara uses Y-up, Max uses Z-up
            max_pos = MaxPlus.Point3(x, -z, y)
            mesh.SetVert(i, max_pos)
        
        # Set face count
        mesh.SetNumFaces(qmesh.face_count)
        
        # Add faces
        for i, face in enumerate(qmesh.faces):
            # Create face with 3 vertices
            mesh.faces[i].SetVerts(int(face[0]), int(face[1]), int(face[2]))
            mesh.faces[i].SetEdgeVisFlags(1, 1, 1)  # All edges visible
        
        # Set normals if available
        if qmesh.normals is not None:
            mesh.BuildNormals()
            # Max computes normals automatically, but we can override if needed
        
        # Set UVs if available
        if qmesh.uvs and len(qmesh.uvs) > 0:
            uv_set = qmesh.uvs[0]
            
            # Set UV vertex count (map channel 1)
            mesh.SetNumMapVerts(1, len(uv_set))
            
            # Add UV coordinates
            for i, uv in enumerate(uv_set):
                uv_vert = MaxPlus.Point3(uv[0], uv[1], 0.0)
                mesh.SetMapVert(1, i, uv_vert)
            
            # Set UV face count
            mesh.SetNumMapFaces(1, qmesh.face_count)
            
            # Map faces to UV vertices (assuming 1:1 mapping)
            for i, face in enumerate(qmesh.faces):
                mesh.SetMapFace(1, i, int(face[0]), int(face[1]), int(face[2]))
        
        # Create node and assign mesh
        node = MaxPlus.Factory.CreateNode(tri_obj)
        node.SetName(name)
        
        # Refresh mesh
        mesh.InvalidateGeomCache()
        mesh.InvalidateTopologyCache()
        
        # Add to scene
        MaxPlus.Core.GetRootNode().AddChild(node, True)
        
        # Select the new node
        MaxPlus.SelectionManager.ClearNodeSelection()
        MaxPlus.SelectionManager.SelectNode(node)
        
        return name
    
    @staticmethod
    def get_scene() -> QScene:
        """
        Export entire 3ds Max scene to QScene.
        
        Returns:
            QScene representing all meshes in current scene
        """
        if not HAS_MAXPLUS:
            raise RuntimeError("MaxPlus not available - must run inside 3ds Max")
        
        scene = QScene()
        
        # Get all nodes in scene
        def traverse_nodes(node, meshes_list):
            """Recursively traverse scene graph"""
            obj = node.GetObject()
            
            # Check if it's a mesh
            if obj and obj.IsSubClassOf(MaxPlus.ClassIds.TriObject):
                # Select this node temporarily to extract mesh
                MaxPlus.SelectionManager.ClearNodeSelection()
                MaxPlus.SelectionManager.SelectNode(node)
                
                try:
                    qmesh = MaxAdapter.get_selected_mesh()
                    meshes_list.append(qmesh)
                except Exception as e:
                    print(f"[MaxAdapter] Failed to export {node.GetName()}: {e}")
            
            # Traverse children
            for i in range(node.GetNumChildren()):
                child = node.GetChild(i)
                traverse_nodes(child, meshes_list)
        
        # Start from root
        root = MaxPlus.Core.GetRootNode()
        traverse_nodes(root, scene.meshes)
        
        # TODO: Export materials, cameras, lights
        
        return scene
    
    @staticmethod
    def import_scene(scene: QScene) -> List[str]:
        """
        Import QScene into 3ds Max.
        
        Args:
            scene: QScene to import
        
        Returns:
            List of created node names
        """
        created_objects = []
        
        for mesh in scene.meshes:
            mesh_name = MaxAdapter.create_mesh_from_qmesh(mesh)
            created_objects.append(mesh_name)
        
        # TODO: Import materials, cameras, lights
        
        return created_objects


# Convenience functions for MaxScript compatibility
def export_selected_mesh():
    """Legacy function - delegates to MaxAdapter"""
    return MaxAdapter.get_selected_mesh()


def import_mesh(qmesh: QMesh, name: str = None):
    """Legacy function - delegates to MaxAdapter"""
    return MaxAdapter.create_mesh_from_qmesh(qmesh, name)
