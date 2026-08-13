"""
Qyntara DCC Adapters - Maya Adapter
===================================

Translation layer between Maya's API and Qyntara Core Engine.

This adapter allows the existing Maya client to use the new Core Engine,
ensuring identical behavior while gaining access to multi-platform features.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import maya.cmds as cmds
import numpy as np
from typing import Optional, List

from qyntara_core.datatypes import QMesh, QMaterial, QScene


class MayaAdapter:
    """
    Translate between Maya's native mesh API and QMesh.
    
    This is the bridge that allows Maya to use the Core Engine.
    All geometry operations in Maya go through this adapter.
    
    Example:
        >>> from qyntara_dcc.maya.adapter import MayaAdapter
        >>> from qyntara_core.geometry import MeshProcessor
        >>> 
        >>> # Get mesh from Maya
        >>> qmesh = MayaAdapter.get_selected_mesh()
        >>> 
        >>> # Process with Core Engine
        >>> optimized = MeshProcessor.center_mesh(qmesh)
        >>> 
        >>> # Send back to Maya
        >>> MayaAdapter.create_mesh_from_qmesh(optimized)
    """
    
    @staticmethod
    def get_selected_mesh() -> QMesh:
        """
        Extract selected Maya mesh to QMesh.
        
        Returns:
            QMesh representation of selected mesh
        
        Raises:
            ValueError: If no mesh is selected
        """
        # Get selection
        selection = cmds.ls(selection=True, dag=True, type='mesh')
        
        if not selection:
            raise ValueError("No mesh selected in Maya")
        
        mesh_shape = selection[0]
        mesh_transform = cmds.listRelatives(mesh_shape, parent=True)[0]
        
        # Get vertices in world space
        vertex_count = cmds.polyEvaluate(mesh_shape, vertex=True)
        vertices = []
        
        for i in range(vertex_count):
            pos = cmds.xform(f"{mesh_shape}.vtx[{i}]", q=True, ws=True, t=True)
            vertices.append(pos)
        
        vertices = np.array(vertices, dtype=np.float32)
        
        # Get faces
        face_count = cmds.polyEvaluate(mesh_shape, face=True)
        faces = []
        
        for i in range(face_count):
            # Get face-vertex connection
            face_info = cmds.polyInfo(f"{mesh_shape}.f[{i}]", faceToVertex=True)[0]
            
            # Parse: "FACE    42:     89     90     91     92\n"
            parts = face_info.split()
            indices = [int(x) for x in parts[2:]]
            
            # Pad to 4 vertices (support quads)
            while len(indices) < 4:
                indices.append(-1)
            
            faces.append(indices[:4])
        
        faces = np.array(faces, dtype=np.int32)
        
        # Get normals
        normal_count = cmds.polyEvaluate(mesh_shape, vertex=True)
        normals = []
        
        for i in range(normal_count):
            normal = cmds.polyNormalPerVertex(f"{mesh_shape}.vtx[{i}]", q=True, xyz=True)
            # Average if multiple normals per vertex
            if len(normal) > 3:
                normal = [
                    sum(normal[j::3]) / (len(normal) // 3) for j in range(3)
                ]
            normals.append(normal[:3])
        
        normals = np.array(normals, dtype=np.float32)
        
        # Get UVs
        uvs = None
        uv_sets = cmds.polyUVSet(mesh_shape, q=True, allUVSets=True)
        
        if uv_sets:
            uvs = []
            for uv_set_name in uv_sets:
                # Get UV coordinates
                u_coords = cmds.polyEditUV(f"{mesh_shape}.map[*]", q=True, u=True, uvSetName=uv_set_name)
                v_coords = cmds.polyEditUV(f"{mesh_shape}.map[*]", q=True, v=True, uvSetName=uv_set_name)
                
                if u_coords and v_coords:
                    uv_array = np.array(list(zip(u_coords, v_coords)), dtype=np.float32)
                    uvs.append(uv_array)
        
        # Get transform matrix
        transform_matrix = None
        xform_matrix = cmds.xform(mesh_transform, q=True, matrix=True, worldSpace=True)
        if xform_matrix:
            transform_matrix = np.array(xform_matrix, dtype=np.float32).reshape(4, 4)
        
        return QMesh(
            vertices=vertices,
            faces=faces,
            normals=normals,
            uvs=uvs if uvs else None,
            name=mesh_transform,
            transform=transform_matrix
        )
    
    @staticmethod
    def create_mesh_from_qmesh(qmesh: QMesh, name: Optional[str] = None) -> str:
        """
        Create Maya mesh from QMesh.
        
        Args:
            qmesh: QMesh to convert
            name: Optional name for new mesh (uses qmesh.name if not provided)
        
        Returns:
            Name of created mesh transform node
        """
        if name is None:
            name = qmesh.name or "QMesh"
        
        # Build vertex list for polyCreateFacet
        points = qmesh.vertices.tolist()
        
        # Maya doesn't support direct n-gon creation easily,
        # so we'll create an empty mesh and add faces
        
        # Create empty poly mesh  
        mesh_transform = cmds.createNode('transform', name=name)
        mesh_shape = cmds.createNode('mesh', name=f"{name}Shape", parent=mesh_transform)
        
        # Build mesh data
        vertex_count = qmesh.vertex_count
        face_count = qmesh.face_count
        
        # Face vertex counts
        face_vertex_counts = []
        for face in qmesh.faces:
            face = face[face != -1]
            face_vertex_counts.append(len(face))
        
        # Flatten face vertex indices
        face_vertex_indices = []
        for face in qmesh.faces:
            face = face[face != -1]
            face_vertex_indices.extend(face.tolist())
        
        # Use OpenMaya to directly set mesh data (more efficient)
        import maya.api.OpenMaya as om
        
        # Get MObject for mesh shape
        sel_list = om.MSelectionList()
        sel_list.add(mesh_shape)
        mesh_obj = sel_list.getDependNode(0)
        
        # Create MFnMesh
        mesh_fn = om.MFnMesh()
        
        # Convert data to Maya types
        m_points = om.MPointArray([om.MPoint(v) for v in points])
        m_face_counts = face_vertex_counts
        m_face_connects = face_vertex_indices
        
        # Create mesh
        mesh_fn.create(m_points, m_face_counts, m_face_connects, parent=mesh_obj)
        
        # Set normals
        if qmesh.normals is not None:
            normal_ids = om.MIntArray(range(vertex_count))
            m_normals = om.MVectorArray([om.MVector(n) for n in qmesh.normals])
            mesh_fn.setNormals(m_normals, om.MSpace.kObject)
        
        # Set UVs
        if qmesh.uvs and len(qmesh.uvs) > 0:
            for uv_idx, uv_set in enumerate(qmesh.uvs):
                uv_set_name = "map1" if uv_idx == 0 else f"map{uv_idx + 1}"
                
                # Create UV set if not first
                if uv_idx > 0:
                    mesh_fn.createUVSet(uv_set_name)
                
                # Set UVs
                u_array = om.MFloatArray([float(uv[0]) for uv in uv_set])
                v_array = om.MFloatArray([float(uv[1]) for uv in uv_set])
                
                # UV indices (one per face-vertex)
                uv_indices = om.MIntArray(face_vertex_indices)
                
                mesh_fn.setUVs(u_array, v_array, uv_set_name)
                mesh_fn.assignUVs(m_face_counts, uv_indices, uv_set_name)
        
        return mesh_transform
    
    @staticmethod
    def get_scene() -> QScene:
        """
        Export entire Maya scene to QScene.
        
        Returns:
            QScene representing all meshes in the current scene
        """
        scene = QScene()
        
        # Get all mesh shapes
        all_meshes = cmds.ls(type='mesh', long=True)
        
        # Filter out intermediate objects
        visible_meshes = [m for m in all_meshes if not cmds.getAttr(f"{m}.intermediateObject")]
        
        for mesh_shape in visible_meshes:
            # Select and convert
            mesh_transform = cmds.listRelatives(mesh_shape, parent=True)[0]
            cmds.select(mesh_transform)
            
            try:
                qmesh = MayaAdapter.get_selected_mesh()
                scene.meshes.append(qmesh)
            except Exception as e:
                cmds.warning(f"Failed to export mesh {mesh_transform}: {e}")
                continue
        
        # TODO: Export materials, cameras, lights
        
        return scene
    
    @staticmethod
    def import_scene(scene: QScene) -> List[str]:
        """
        Import QScene into Maya.
        
        Args:
            scene: QScene to import
        
        Returns:
            List of created mesh transform names
        """
        created_objects = []
        
        for mesh in scene.meshes:
            mesh_name = MayaAdapter.create_mesh_from_qmesh(mesh)
            created_objects.append(mesh_name)
        
        # TODO: Import materials, cameras, lights
        
        return created_objects


# Convenience functions for backward compatibility with existing client
def export_selected_mesh() -> QMesh:
    """Legacy function - delegates to MayaAdapter"""
    return MayaAdapter.get_selected_mesh()


def import_mesh(qmesh: QMesh, name: str = None) -> str:
    """Legacy function - delegates to MayaAdapter"""
    return MayaAdapter.create_mesh_from_qmesh(qmesh, name)
