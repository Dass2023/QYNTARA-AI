"""
Qyntara DCC Adapters - Blender Adapter
======================================

Translation layer between Blender's API (bpy) and Qyntara Core Engine.

Uses Blender's Python API (bpy) for seamless integration.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import numpy as np
from typing import Optional, List

try:
    import bpy
    import bmesh
    HAS_BPY = True
except ImportError:
    HAS_BPY = False
    print("[Blender Adapter] bpy not available - running outside Blender")

from qyntara_core.datatypes import QMesh, QMaterial, QScene


class BlenderAdapter:
    """
    Translate between Blender's bpy API and QMesh.
    
    This adapter allows Blender to use the Core Engine with identical
    behavior to Maya, 3ds Max, and game engines.
    
    Example (run in Blender Text Editor):
        >>> from qyntara_dcc.blender import BlenderAdapter
        >>> from qyntara_core.geometry import MeshProcessor
        >>> 
        >>> # Get selected mesh
        >>> qmesh = BlenderAdapter.get_selected_mesh()
        >>> 
        >>> # Process with Core Engine
        >>> centered = MeshProcessor.center_mesh(qmesh)
        >>> 
        >>> # Create in Blender
        >>> BlenderAdapter.create_mesh_from_qmesh(centered)
    """
    
    @staticmethod
    def get_selected_mesh() -> QMesh:
        """
        Extract selected Blender mesh to QMesh.
        
        Returns:
            QMesh representation of selected mesh
        
        Raises:
            ValueError: If no mesh is selected
            RuntimeError: If not running in Blender
        """
        if not HAS_BPY:
            raise RuntimeError("bpy not available - must run inside Blender")
        
        # Get active object
        obj = bpy.context.active_object
        
        if obj is None or obj.type != 'MESH':
            raise ValueError("No mesh object selected in Blender")
        
        # Get mesh data
        mesh = obj.data
        
        # Apply modifiers and get evaluated mesh
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        eval_mesh = eval_obj.to_mesh()
        
        # Extract vertices (Blender uses Z-up, same as Qyntara convention)
        vertices = np.zeros((len(eval_mesh.vertices), 3), dtype=np.float32)
        eval_mesh.vertices.foreach_get('co', vertices.ravel())
        
        # Extract faces
        faces_list = []
        for poly in eval_mesh.polygons:
            face = list(poly.vertices)
            
            # Pad to 4 vertices (support quads)
            while len(face) < 4:
                face.append(-1)
            
            faces_list.append(face[:4])
        
        faces = np.array(faces_list, dtype=np.int32)
        
        # Extract normals
        normals = None
        if eval_mesh.has_custom_normals or len(eval_mesh.vertices) > 0:
            normals = np.zeros((len(eval_mesh.vertices), 3), dtype=np.float32)
            eval_mesh.vertices.foreach_get('normal', normals.ravel())
        
        # Extract UVs
        uvs = None
        if eval_mesh.uv_layers:
            uvs = []
            
            for uv_layer in eval_mesh.uv_layers:
                # Get UV coordinates per vertex
                uv_dict = {}
                
                for poly in eval_mesh.polygons:
                    for loop_idx in poly.loop_indices:
                        loop = eval_mesh.loops[loop_idx]
                        vert_idx = loop.vertex_index
                        uv_coord = uv_layer.data[loop_idx].uv
                        
                        # Store UV for this vertex (last one wins if duplicates)
                        uv_dict[vert_idx] = [uv_coord[0], uv_coord[1]]
                
                # Create UV array in vertex order
                uv_array = np.zeros((len(eval_mesh.vertices), 2), dtype=np.float32)
                for vert_idx, uv_coord in uv_dict.items():
                    uv_array[vert_idx] = uv_coord
                
                uvs.append(uv_array)
        
        # Clean up evaluated mesh
        eval_obj.to_mesh_clear()
        
        return QMesh(
            vertices=vertices,
            faces=faces,
            normals=normals,
            uvs=uvs if uvs else None,
            name=obj.name
        )
    
    @staticmethod
    def create_mesh_from_qmesh(qmesh: QMesh, name: Optional[str] = None) -> str:
        """
        Create Blender mesh from QMesh.
        
        Args:
            qmesh: QMesh to convert
            name: Optional name for new mesh
        
        Returns:
            Name of created mesh object
        """
        if not HAS_BPY:
            raise RuntimeError("bpy not available - must run inside Blender")
        
        if name is None:
            name = qmesh.name or "QMesh"
        
        # Create new mesh data
        mesh_data = bpy.data.meshes.new(name + "_mesh")
        
        # Extract face vertex counts and indices
        face_vertices = []
        for face in qmesh.faces:
            # Remove padding
            face_clean = [int(v) for v in face if v != -1]
            face_vertices.append(face_clean)
        
        # Create mesh from vertices and faces
        # Blender uses: vertices, edges, faces
        # We only have vertices and faces, so edges will be auto-generated
        mesh_data.from_pydata(
            vertices=qmesh.vertices.tolist(),
            edges=[],
            faces=face_vertices
        )
        
        # Update mesh
        mesh_data.update()
        
        # Set normals if available
        if qmesh.normals is not None:
            # Custom normals require split normals
            mesh_data.use_auto_smooth = True
            mesh_data.normals_split_custom_set_from_vertices(qmesh.normals.tolist())
        
        # Set UVs if available
        if qmesh.uvs and len(qmesh.uvs) > 0:
            for uv_idx, uv_set in enumerate(qmesh.uvs):
                # Create UV layer
                uv_layer_name = "UVMap" if uv_idx == 0 else f"UVMap_{uv_idx}"
                uv_layer = mesh_data.uv_layers.new(name=uv_layer_name)
                
                # Set UV coordinates
                for poly in mesh_data.polygons:
                    for loop_idx in poly.loop_indices:
                        loop = mesh_data.loops[loop_idx]
                        vert_idx = loop.vertex_index
                        
                        # Get UV from vertex
                        if vert_idx < len(uv_set):
                            uv_layer.data[loop_idx].uv = tuple(uv_set[vert_idx])
        
        # Create object and link to scene
        obj = bpy.data.objects.new(name, mesh_data)
        bpy.context.collection.objects.link(obj)
        
        # Select and make active
        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj
        
        return obj.name
    
    @staticmethod
    def get_scene() -> QScene:
        """
        Export entire Blender scene to QScene.
        
        Returns:
            QScene representing all meshes in current scene
        """
        if not HAS_BPY:
            raise RuntimeError("bpy not available - must run inside Blender")
        
        scene = QScene()
        
        # Get all mesh objects in scene
        for obj in bpy.context.scene.objects:
            if obj.type == 'MESH':
                # Temporarily select this object
                bpy.ops.object.select_all(action='DESELECT')
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj
                
                try:
                    qmesh = BlenderAdapter.get_selected_mesh()
                    scene.meshes.append(qmesh)
                except Exception as e:
                    print(f"[BlenderAdapter] Failed to export {obj.name}: {e}")
        
        # TODO: Export materials, cameras, lights
        
        return scene
    
    @staticmethod
    def import_scene(scene: QScene) -> List[str]:
        """
        Import QScene into Blender.
        
        Args:
            scene: QScene to import
        
        Returns:
            List of created object names
        """
        created_objects = []
        
        for mesh in scene.meshes:
            obj_name = BlenderAdapter.create_mesh_from_qmesh(mesh)
            created_objects.append(obj_name)
        
        # TODO: Import materials, cameras, lights
        
        return created_objects


# Convenience functions for Blender script compatibility
def export_selected_mesh():
    """Legacy function - delegates to BlenderAdapter"""
    return BlenderAdapter.get_selected_mesh()


def import_mesh(qmesh: QMesh, name: str = None):
    """Legacy function - delegates to BlenderAdapter"""
    return BlenderAdapter.create_mesh_from_qmesh(qmesh, name)
