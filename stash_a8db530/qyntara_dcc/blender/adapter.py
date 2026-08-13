"""
Qyntara DCC Adapters - Blender Adapter
======================================

Translation layer between Blender's API (bpy) and Qyntara Core Engine.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import bpy
import bmesh
import numpy as np
from typing import Optional, List

from qyntara_core.datatypes import QMesh, QMaterial, QScene


class BlenderAdapter:
    """
    Translate between Blender's bpy/bmesh API and QMesh.
    
    Example:
        >>> from qyntara_dcc.blender.adapter import BlenderAdapter
        >>> qmesh = BlenderAdapter.get_selected_mesh()
    """
    
    @staticmethod
    def get_selected_mesh() -> QMesh:
        """
        Extract active Blender mesh to QMesh.
        """
        obj = bpy.context.active_object
        if not obj or obj.type != 'MESH':
            raise ValueError("No mesh selected in Blender")
        
        mesh_data = obj.data
        
        # Vertices
        vertices = np.array([v.co for v in mesh_data.vertices], dtype=np.float32)
        
        # Faces (padd to 4 for consistency with QMesh logic if requested, 
        # but QMesh supports arbitrary n-gons if backend allows)
        faces = []
        for poly in mesh_data.polygons:
            indices = list(poly.vertices)
            # Pad to 4 for simple array storage if needed, or keep dynamic
            while len(indices) < 4:
                indices.append(-1)
            faces.append(indices[:4])
        
        faces = np.array(faces, dtype=np.int32)
        
        # Normals
        normals = np.array([v.normal for v in mesh_data.vertices], dtype=np.float32)
        
        # UVs (First UV layer)
        uvs = None
        if mesh_data.uv_layers.active:
            uv_layer = mesh_data.uv_layers.active.data
            # Blender stores UVs per loop (face corner)
            # We need to map them back to vertices or store as loop data
            # For simplicity in this scaffold, we extract a basic mapping
            uv_coords = np.zeros((len(mesh_data.vertices), 2), dtype=np.float32)
            for loop in mesh_data.loops:
                uv_coords[loop.vertex_index] = uv_layer[loop.index].uv
            uvs = [uv_coords]
            
        return QMesh(
            vertices=vertices,
            faces=faces,
            normals=normals,
            uvs=uvs,
            name=obj.name,
            transform=np.array(obj.matrix_world, dtype=np.float32)
        )

    @staticmethod
    def create_mesh_from_qmesh(qmesh: QMesh, name: Optional[str] = None) -> str:
        """
        Create Blender mesh from QMesh.
        """
        if name is None:
            name = qmesh.name or "QMesh"
            
        mesh = bpy.data.meshes.new(name)
        obj = bpy.data.objects.new(name, mesh)
        bpy.context.collection.objects.link(obj)
        
        # Build Geometry
        verts = qmesh.vertices.tolist()
        faces = []
        for f in qmesh.faces:
            faces.append([int(i) for i in f if i != -1])
            
        mesh.from_pydata(verts, [], faces)
        mesh.update()
        
        # Apply Transform
        if qmesh.transform is not None:
            obj.matrix_world = qmesh.transform.tolist()
            
        return obj.name

    @staticmethod
    def get_scene() -> QScene:
        """
        Export visible Blender scene objects to QScene.
        """
        scene = QScene()
        for obj in bpy.context.view_layer.objects:
            if obj.type == 'MESH' and not obj.hide_viewport:
                # Set active and extract
                bpy.context.view_layer.objects.active = obj
                try:
                    qmesh = BlenderAdapter.get_selected_mesh()
                    scene.meshes.append(qmesh)
                except: continue
        return scene

    @staticmethod
    def import_scene(scene: QScene) -> List[str]:
        """
        Import QScene into Blender.
        """
        names = []
        for qmesh in scene.meshes:
            name = BlenderAdapter.create_mesh_from_qmesh(qmesh)
            names.append(name)
        return names
