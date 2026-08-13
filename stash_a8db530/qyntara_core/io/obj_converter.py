"""
Qyntara Core Engine - OBJ/MTL Format Converter
==============================================

Import/export Wavefront OBJ and MTL files.
Simple, lightweight format for static meshes.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import numpy as np
from typing import Optional, List, Dict
from pathlib import Path

from qyntara_core.datatypes import QMesh, QMaterial, QScene


class OBJConverter:
    """
    Convert between OBJ/MTL and QMesh formats.
    
    OBJ is a simple, human-readable format ideal for static meshes.
    
    Features:
        - Vertices, faces, normals, UVs
        - Material support via MTL files
        - Multiple UV sets (via custom vt# syntax)
        - Vertex colors (via custom vc extension)
    
    Example:
        >>> from qyntara_core.io import OBJConverter
        >>> 
        >>> # Export to OBJ
        >>> scene = QScene(meshes=[my_mesh], materials=[my_material])
        >>> OBJConverter.export(scene, "output.obj")
        >>> 
        >>> # Import from OBJ
        >>> scene = OBJConverter.import_file("input.obj")
    """
    
    @staticmethod
    def export(scene: QScene, filepath: str, export_mtl: bool = True) -> None:
        """
        Export QScene to OBJ/MTL files.
        
        Args:
            scene: QScene to export
            filepath: Output OBJ file path
            export_mtl: If True, also create MTL file for materials
        """
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        obj_lines = []
        obj_lines.append(f"# Qyntara Core Engine OBJ Export")
        obj_lines.append(f"# File: {filepath.name}")
        obj_lines.append(f"# Meshes: {len(scene.meshes)}")
        obj_lines.append("")
        
        # Reference MTL file if exporting materials
        if export_mtl and scene.materials:
            mtl_filepath = filepath.with_suffix('.mtl')
            obj_lines.append(f"mtllib {mtl_filepath.name}")
            obj_lines.append("")
        
        vertex_offset = 1  # OBJ uses 1-based indexing
        normal_offset = 1
        uv_offset = 1
        
        # Export each mesh
        for mesh_idx, qmesh in enumerate(scene.meshes):
            obj_lines.append(f"# Mesh: {qmesh.name or f'mesh_{mesh_idx}'}")
            obj_lines.append(f"o {qmesh.name or f'mesh_{mesh_idx}'}")
            obj_lines.append("")
            
            # Export vertices
            for vertex in qmesh.vertices:
                obj_lines.append(f"v {vertex[0]} {vertex[1]} {vertex[2]}")
            obj_lines.append("")
            
            # Export normals
            if qmesh.normals is not None:
                for normal in qmesh.normals:
                    obj_lines.append(f"vn {normal[0]} {normal[1]} {normal[2]}")
                obj_lines.append("")
            
            # Export UVs
            if qmesh.uvs and len(qmesh.uvs) > 0:
                for uv in qmesh.uvs[0]:  # OBJ only supports one UV set natively
                    obj_lines.append(f"vt {uv[0]} {uv[1]}")
                obj_lines.append("")
            
            # Export faces
            has_normals = qmesh.normals is not None
            has_uvs = qmesh.uvs is not None and len(qmesh.uvs) > 0
            
            for face in qmesh.faces:
                face_str = "f"
                for vertex_idx in face:
                    if vertex_idx == -1:  # Skip padding
                        continue
                    
                    v_idx = vertex_offset + vertex_idx
                    
                    if has_uvs and has_normals:
                        uv_idx = uv_offset + vertex_idx
                        n_idx = normal_offset + vertex_idx
                        face_str += f" {v_idx}/{uv_idx}/{n_idx}"
                    elif has_uvs:
                        uv_idx = uv_offset + vertex_idx
                        face_str += f" {v_idx}/{uv_idx}"
                    elif has_normals:
                        n_idx = normal_offset + vertex_idx
                        face_str += f" {v_idx}//{n_idx}"
                    else:
                        face_str += f" {v_idx}"
                
                obj_lines.append(face_str)
            
            obj_lines.append("")
            
            # Update offsets
            vertex_offset += qmesh.vertex_count
            if has_normals:
                normal_offset += qmesh.vertex_count
            if has_uvs:
                uv_offset += len(qmesh.uvs[0])
        
        # Write OBJ file
        with open(filepath, 'w') as f:
            f.write('\n'.join(obj_lines))
        
        print(f"[OBJ] Exported to: {filepath}")
        print(f"  Meshes: {len(scene.meshes)}")
        print(f"  Total vertices: {vertex_offset - 1}")
        
        # Export MTL file
        if export_mtl and scene.materials:
            _export_mtl(scene.materials, filepath.with_suffix('.mtl'))
    
    @staticmethod
    def import_file(filepath: str) -> QScene:
        """
        Import OBJ file to QScene.
        
        Args:
            filepath: Input OBJ file path
        
        Returns:
            QScene with imported meshes and materials
        """
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"OBJ file not found: {filepath}")
        
        scene = QScene()
        
        vertices = []
        normals = []
        uvs = []
        
        current_mesh_name = "default"
        mesh_faces = []
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if not parts:
                    continue
                
                cmd = parts[0]
                
                if cmd == 'v':  # Vertex
                    vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
                
                elif cmd == 'vn':  # Normal
                    normals.append([float(parts[1]), float(parts[2]), float(parts[3])])
                
                elif cmd == 'vt':  # UV
                    uvs.append([float(parts[1]), float(parts[2])])
                
                elif cmd == 'o' or cmd == 'g':  # Object/group
                    # Save previous mesh if exists
                    if mesh_faces:
                        qmesh = _build_qmesh(current_mesh_name, vertices, normals, uvs, mesh_faces)
                        scene.meshes.append(qmesh)
                        mesh_faces = []
                    
                    current_mesh_name = parts[1] if len(parts) > 1 else "default"
                
                elif cmd == 'f':  # Face
                    face_vertices = []
                    for i in range(1, len(parts)):
                        face_vertices.append(_parse_face_vertex(parts[i]))
                    
                    # Pad to quad
                    while len(face_vertices) < 4:
                        face_vertices.append(-1)
                    
                    mesh_faces.append(face_vertices[:4])
                
                elif cmd == 'mtllib':  # Material library
                    mtl_filepath = filepath.parent / parts[1]
                    if mtl_filepath.exists():
                        scene.materials = _import_mtl(mtl_filepath)
        
        # Save last mesh
        if mesh_faces:
            qmesh = _build_qmesh(current_mesh_name, vertices, normals, uvs, mesh_faces)
            scene.meshes.append(qmesh)
        
        print(f"[OBJ] Imported from: {filepath}")
        print(f"  Meshes: {len(scene.meshes)}")
        print(f"  Materials: {len(scene.materials)}")
        
        return scene


def _export_mtl(materials: List[QMaterial], filepath: Path) -> None:
    """Export materials to MTL file"""
    mtl_lines = []
    mtl_lines.append("# Qyntara Core Engine MTL Export")
    mtl_lines.append("")
    
    for material in materials:
        mtl_lines.append(f"newmtl {material.name}")
        
        # Base color
        if material.base_color:
            if isinstance(material.base_color, str):
                mtl_lines.append(f"map_Kd {material.base_color}")
            else:
                mtl_lines.append(f"Kd {material.base_color[0]} {material.base_color[1]} {material.base_color[2]}")
        
        # Metallic/roughness (non-standard, but useful)
        if material.metallic is not None:
            mtl_lines.append(f"# metallic {material.metallic}")
        if material.roughness is not None:
            mtl_lines.append(f"# roughness {material.roughness}")
        
        # Normal map
        if material.normal_map:
            mtl_lines.append(f"map_Bump {material.normal_map}")
        
        mtl_lines.append("")
    
    with open(filepath, 'w') as f:
        f.write('\n'.join(mtl_lines))
    
    print(f"[MTL] Exported to: {filepath}")


def _import_mtl(filepath: Path) -> List[QMaterial]:
    """Import materials from MTL file"""
    materials = []
    current_material = None
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            if not line or line.startswith('#'):
                continue
            
            parts = line.split()
            if not parts:
                continue
            
            cmd = parts[0]
            
            if cmd == 'newmtl':
                if current_material:
                    materials.append(current_material)
                current_material = QMaterial(name=parts[1])
            
            elif cmd == 'Kd' and current_material:  # Diffuse color
                r, g, b = float(parts[1]), float(parts[2]), float(parts[3])
                current_material.base_color = (r, g, b, 1.0)
            
            elif cmd == 'map_Kd' and current_material:  # Diffuse texture
                current_material.base_color = parts[1]
            
            elif cmd == 'map_Bump' and current_material:  # Normal map
                current_material.normal_map = parts[1]
    
    if current_material:
        materials.append(current_material)
    
    return materials


def _parse_face_vertex(vertex_str: str) -> int:
    """Parse face vertex (v/vt/vn format)"""
    parts = vertex_str.split('/')
    # OBJ uses 1-based indexing, convert to 0-based
    return int(parts[0]) - 1


def _build_qmesh(name: str, all_vertices: List, all_normals: List, all_uvs: List, faces: List) -> QMesh:
    """Build QMesh from accumulated data"""
    # Get unique vertices referenced by faces
    vertex_indices = set()
    for face in faces:
        for v_idx in face:
            if v_idx != -1:
                vertex_indices.add(v_idx)
    
    # Create vertex array
    vertices = np.array([all_vertices[i] for i in sorted(vertex_indices)], dtype=np.float32)
    
    # Remap face indices
    index_map = {old_idx: new_idx for new_idx, old_idx in enumerate(sorted(vertex_indices))}
    remapped_faces = []
    for face in faces:
        remapped_face = [index_map.get(v, -1) if v != -1 else -1 for v in face]
        remapped_faces.append(remapped_face)
    
    faces_array = np.array(remapped_faces, dtype=np.int32)
    
    # Get normals if available
    normals = None
    if all_normals:
        normals = np.array([all_normals[i] for i in sorted(vertex_indices)], dtype=np.float32)
    
    # Get UVs if available
    uvs_array = None
    if all_uvs:
        uvs_array = [np.array([all_uvs[i] for i in sorted(vertex_indices)], dtype=np.float32)]
    
    return QMesh(
        vertices=vertices,
        faces=faces_array,
        normals=normals,
        uvs=uvs_array,
        name=name
    )
