"""
Qyntara Core Engine - FBX Format Converter
==========================================

Import/export FBX files to/from QMesh format.
Uses FBX SDK or PyFBX for file I/O.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import numpy as np
from typing import Optional, List
from pathlib import Path

try:
    # Try fbx Python SDK (requires Autodesk FBX SDK)
    import fbx
    import FbxCommon
    HAS_FBX_SDK = True
except ImportError:
    HAS_FBX_SDK = False

from qyntara_core.datatypes import QMesh, QMaterial, QScene


class FBXConverter:
    """
    Convert between FBX and QMesh formats.
    
    Note: FBX support requires Autodesk FBX SDK.
    Install: https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2020-3
    
    Alternative: For simple use cases, consider using glTF as intermediate format.
    
    Example:
        >>> from qyntara_core.io import FBXConverter
        >>> 
        >>> # Export to FBX
        >>> scene = QScene(meshes=[my_mesh])
        >>> FBXConverter.export(scene, "output.fbx")
        >>> 
        >>> # Import from FBX
        >>> scene = FBXConverter.import_file("input.fbx")
    """
    
    @staticmethod
    def export(scene: QScene, filepath: str, ascii: bool = False) -> None:
        """
        Export QScene to FBX file.
        
        Args:
            scene: QScene to export
            filepath: Output FBX file path
            ascii: If True, export as ASCII FBX (larger but human-readable)
        
        Raises:
            ImportError: If FBX SDK not installed
            RuntimeError: If export fails
        """
        if not HAS_FBX_SDK:
            # Fallback: Export to glTF and convert externally
            import warnings
            warnings.warn(
                "FBX SDK not installed. "
                "Install from: https://www.autodesk.com/developer-network/platform-technologies/fbx-sdk-2020-3\n"
                "Alternative: Export to glTF and use external converter (e.g., Blender)"
            )
            
            # Try to use glTF as intermediate
            from qyntara_core.io import GLTFConverter
            gltf_path = str(Path(filepath).with_suffix('.glb'))
            GLTFConverter.export(scene, gltf_path, binary=True)
            
            print(f"[FBX] Exported to glTF instead: {gltf_path}")
            print("[FBX] Use Blender CLI to convert: blender --background --python convert_gltf_to_fbx.py")
            return
        
        # Create FBX manager
        manager, fbx_scene = FbxCommon.InitializeSdkObjects()
        
        # Set scene info
        scene_info = fbx.FbxDocumentInfo.Create(manager, "SceneInfo")
        scene_info.mTitle = "Qyntara Export"
        scene_info.mAuthor = "Qyntara Core Engine"
        fbx_scene.SetSceneInfo(scene_info)
        
        # Export each mesh
        for qmesh in scene.meshes:
            _export_mesh_to_fbx(fbx_scene, qmesh)
        
        # Save FBX file
        exporter = fbx.FbxExporter.Create(manager, "")
        
        file_format = manager.GetIOPluginRegistry().GetNativeWriterFormat()
        if ascii:
            # Find ASCII format
            format_count = manager.GetIOPluginRegistry().GetWriterFormatCount()
            for i in range(format_count):
                if manager.GetIOPluginRegistry().WriterIsFBX(i):
                    desc = manager.GetIOPluginRegistry().GetWriterFormatDescription(i)
                    if "ascii" in desc.lower():
                        file_format = i
                        break
        
        if not exporter.Initialize(filepath, file_format):
            raise RuntimeError(f"Failed to initialize FBX exporter: {exporter.GetStatus().GetErrorString()}")
        
        exporter.Export(fbx_scene)
        exporter.Destroy()
        
        # Cleanup
        manager.Destroy()
        
        print(f"[FBX] Exported to: {filepath}")
        print(f"  Format: {'ASCII' if ascii else 'Binary'}")
        print(f"  Meshes: {len(scene.meshes)}")
    
    @staticmethod
    def import_file(filepath: str) -> QScene:
        """
        Import FBX file to QScene.
        
        Args:
            filepath: Input FBX file path
        
        Returns:
            QScene with imported meshes
        
        Raises:
            ImportError: If FBX SDK not installed
            FileNotFoundError: If file doesn't exist
            RuntimeError: If import fails
        """
        if not HAS_FBX_SDK:
            import warnings
            warnings.warn(
                "FBX SDK not installed. "
                "Alternative: Convert FBX to glTF using Blender, then import glTF"
            )
            
            # Try to find corresponding glTF file
            gltf_path = Path(filepath).with_suffix('.glb')
            if gltf_path.exists():
                from qyntara_core.io import GLTFConverter
                return GLTFConverter.import_file(str(gltf_path))
            
            raise ImportError("FBX SDK required for FBX import")
        
        if not Path(filepath).exists():
            raise FileNotFoundError(f"FBX file not found: {filepath}")
        
        # Create FBX manager
        manager, fbx_scene = FbxCommon.InitializeSdkObjects()
        
        # Import FBX file
        importer = fbx.FbxImporter.Create(manager, "")
        
        if not importer.Initialize(filepath, -1):
            raise RuntimeError(f"Failed to initialize FBX importer: {importer.GetStatus().GetErrorString()}")
        
        importer.Import(fbx_scene)
        importer.Destroy()
        
        # Convert to QScene
        scene = QScene()
        
        root_node = fbx_scene.GetRootNode()
        if root_node:
            for i in range(root_node.GetChildCount()):
                node = root_node.GetChild(i)
                _import_node_recursive(node, scene)
        
        # Cleanup
        manager.Destroy()
        
        print(f"[FBX] Imported from: {filepath}")
        print(f"  Meshes: {len(scene.meshes)}")
        
        return scene


def _export_mesh_to_fbx(fbx_scene, qmesh: QMesh):
    """Helper: Export QMesh to FBX scene"""
    manager = fbx_scene.GetFbxManager()
    
    # Create node
    node = fbx.FbxNode.Create(manager, qmesh.name or "Mesh")
    fbx_scene.GetRootNode().AddChild(node)
    
    # Create mesh
    fbx_mesh = fbx.FbxMesh.Create(manager, qmesh.name or "Mesh")
    node.SetNodeAttribute(fbx_mesh)
    
    # Add vertices
    fbx_mesh.InitControlPoints(qmesh.vertex_count)
    control_points = fbx_mesh.GetControlPoints()
    
    for i, vertex in enumerate(qmesh.vertices):
        # Qyntara uses Y-up, FBX uses Y-up (same)
        control_points[i] = fbx.FbxVector4(float(vertex[0]), float(vertex[1]), float(vertex[2]))
    
    # Add faces
    for face in qmesh.faces:
        fbx_mesh.BeginPolygon()
        for vertex_idx in face:
            if vertex_idx != -1:  # Skip padding
                fbx_mesh.AddPolygon(int(vertex_idx))
        fbx_mesh.EndPolygon()
    
    # Add UVs if available
    if qmesh.uvs and len(qmesh.uvs) > 0:
        uv_layer = fbx_mesh.CreateElementUV("UVSet0")
        uv_layer.SetMappingMode(fbx.FbxLayerElement.eByControlPoint)
        uv_layer.SetReferenceMode(fbx.FbxLayerElement.eDirect)
        
        for uv in qmesh.uvs[0]:
            uv_layer.GetDirectArray().Add(fbx.FbxVector2(float(uv[0]), float(uv[1])))


def _import_node_recursive(node, scene: QScene):
    """Helper: Recursively import FBX nodes"""
    # Check if node has a mesh
    mesh_attr = node.GetMesh()
    if mesh_attr:
        qmesh = _import_fbx_mesh(mesh_attr, node.GetName())
        scene.meshes.append(qmesh)
    
    # Process children
    for i in range(node.GetChildCount()):
        child = node.GetChild(i)
        _import_node_recursive(child, scene)


def _import_fbx_mesh(fbx_mesh, name: str) -> QMesh:
    """Helper: Convert FBX mesh to QMesh"""
    # Get vertices
    control_points = fbx_mesh.GetControlPoints()
    vertex_count = fbx_mesh.GetControlPointsCount()
    
    vertices = np.zeros((vertex_count, 3), dtype=np.float32)
    for i in range(vertex_count):
        cp = control_points[i]
        vertices[i] = [cp[0], cp[1], cp[2]]
    
    # Get faces
    faces_list = []
    polygon_count = fbx_mesh.GetPolygonCount()
    
    for i in range(polygon_count):
        polygon_size = fbx_mesh.GetPolygonSize(i)
        face = []
        
        for j in range(polygon_size):
            face.append(fbx_mesh.GetPolygonVertex(i, j))
        
        # Pad to 4 vertices (quad)
        while len(face) < 4:
            face.append(-1)
        
        faces_list.append(face[:4])
    
    faces = np.array(faces_list, dtype=np.int32)
    
    # Get UVs if available
    uvs = None
    uv_element = fbx_mesh.GetElementUV(0)
    if uv_element:
        uv_array = []
        for i in range(vertex_count):
            uv = uv_element.GetDirectArray().GetAt(i)
            uv_array.append([uv[0], uv[1]])
        uvs = [np.array(uv_array, dtype=np.float32)]
    
    return QMesh(
        vertices=vertices,
        faces=faces,
        uvs=uvs,
        name=name
    )
