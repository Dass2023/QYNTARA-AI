"""
Qyntara Core Engine - glTF/GLB Converter
========================================

Export/import glTF 2.0 format (the "JPEG of 3D").
Optimized for web, game engines, and AR/VR.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

import numpy as np
import json
import struct
import base64
from pathlib import Path
from typing import Optional, List, Dict, Any

from ..datatypes import QMesh, QMaterial, QScene


class GLTFConverter:
    """
    QScene ↔ glTF 2.0 converter
    
    Supports both .gltf (JSON + separate .bin) and .glb (binary container)
    
    Example:
        >>> from qyntara_core.io import GLTFConverter
        >>> scene = QScene(meshes=[my_mesh])
        >>> GLTF Converter.export(scene, "output.glb", binary=True)
        >>> loaded = GLTFConverter.import_file("input.glb")
    """
    
    @staticmethod
    def export(scene: QScene, filepath: str, binary: bool = True) -> bool:
        """
        Export QScene to glTF/GLB file.
        
        Args:
            scene: QScene to export
            filepath: Output file path
            binary: If True, write .glb. If False, write .gltf + .bin
        
        Returns:
            True if successful
        """
        filepath = Path(filepath)
        
        # Build glTF JSON structure
        gltf = {
            "asset": {
                "version": "2.0",
                "generator": "Qyntara Core Engine 5.0"
            },
            "scene": 0,
            "scenes": [{"nodes": []}],
            "nodes": [],
            "meshes": [],
            "materials": [],
            "buffers": [],
            "bufferViews": [],
            "accessors": []
        }
        
        # Binary buffer data
        buffer_data = bytearray()
        
        def add_buffer_data(data: np.ndarray) -> int:
            """Add numpy array to buffer, return byte offset"""
            offset = len(buffer_data)
            buffer_data.extend(data.tobytes())
            # Align to 4-byte boundary
            while len(buffer_data) % 4 != 0:
                buffer_data.append(0)
            return offset
        
        def create_accessor(buffer_view_idx: int, component_type: int,
                           count: int, accessor_type: str, min_vals=None, max_vals=None) -> int:
            """Create accessor, return index"""
            accessor = {
                "bufferView": buffer_view_idx,
                "componentType": component_type,
                "count": count,
                "type": accessor_type
            }
            if min_vals is not None:
                accessor["min"] = min_vals
            if max_vals is not None:
                accessor["max"] = max_vals
            
            gltf["accessors"].append(accessor)
            return len(gltf["accessors"]) - 1
        
        # Export materials
        for mat in scene.materials:
            gltf_mat = {
                "name": mat.name,
                "pbrMetallicRoughness": {
                    "baseColorFactor": mat.base_color.tolist() if isinstance(mat.base_color, np.ndarray) else [0.8, 0.8, 0.8, 1.0],
                    "metallicFactor": float(mat.metallic),
                    "roughnessFactor": float(mat.roughness)
                },
                "doubleSided": mat.double_sided
            }
            
            if mat.alpha_mode != "OPAQUE":
                gltf_mat["alphaMode"] = mat.alpha_mode
                gltf_mat["alphaCutoff"] = mat.alpha_cutoff
            
            gltf["materials"].append(gltf_mat)
        
        # Export meshes
        for mesh in scene.meshes:
            # Ensure triangulated
            if not mesh.is_triangulated:
                mesh = mesh.triangulate()
            
            # Vertices
            vertices_offset = add_buffer_data(mesh.vertices.astype(np.float32))
            vertices_view = {
                "buffer": 0,
                "byteOffset": vertices_offset,
               "byteLength": mesh.vertices.nbytes,
                "target": 34962  # ARRAY_BUFFER
            }
            gltf["bufferViews"].append(vertices_view)
            vertices_view_idx = len(gltf["bufferViews"]) - 1
            
            vertices_accessor_idx = create_accessor(
                vertices_view_idx,
                5126,  # FLOAT
                mesh.vertex_count,
                "VEC3",
                mesh.vertices.min(axis=0).tolist(),
                mesh.vertices.max(axis=0).tolist()
            )
            
            # Indices
            indices = mesh.faces.flatten().astype(np.uint32)
            indices_offset = add_buffer_data(indices)
            indices_view = {
                "buffer": 0,
                "byteOffset": indices_offset,
                "byteLength": indices.nbytes,
                "target": 34963  # ELEMENT_ARRAY_BUFFER
            }
            gltf["bufferViews"].append(indices_view)
            indices_view_idx = len(gltf["bufferViews"]) - 1
            
            indices_accessor_idx = create_accessor(
                indices_view_idx,
                5125,  # UNSIGNED_INT
                len(indices),
                "SCALAR",
                [int(indices.min())],
                [int(indices.max())]
            )
            
            # Build mesh primitive
            primitive = {
                "attributes": {
                    "POSITION": vertices_accessor_idx
                },
                "indices": indices_accessor_idx,
                "mode": 4  # TRIANGLES
            }
            
            # Normals
            if mesh.normals is not None:
                normals_offset = add_buffer_data(mesh.normals.astype(np.float32))
                normals_view = {
                    "buffer": 0,
                    "byteOffset": normals_offset,
                    "byteLength": mesh.normals.nbytes,
                    "target": 34962
                }
                gltf["bufferViews"].append(normals_view)
                normals_view_idx = len(gltf["bufferViews"]) - 1
                
                normals_accessor_idx = create_accessor(
                    normals_view_idx,
                    5126,  # FLOAT
                    mesh.vertex_count,
                    "VEC3"
                )
                primitive["attributes"]["NORMAL"] = normals_accessor_idx
            
            # UVs
            if mesh.uvs and len(mesh.uvs) > 0:
                uv_set = mesh.uvs[0].astype(np.float32)
                uvs_offset = add_buffer_data(uv_set)
                uvs_view = {
                    "buffer": 0,
                    "byteOffset": uvs_offset,
                    "byteLength": uv_set.nbytes,
                    "target": 34962
                }
                gltf["bufferViews"].append(uvs_view)
                uvs_view_idx = len(gltf["bufferViews"]) - 1
                
                uvs_accessor_idx = create_accessor(
                    uvs_view_idx,
                    5126,  # FLOAT
                    mesh.vertex_count,
                    "VEC2"
                )
                primitive["attributes"]["TEXCOORD_0"] = uvs_accessor_idx
            
            # Material
            if mesh.material_ids is not None and len(scene.materials) > 0:
                mat_id = int(mesh.material_ids[0])
                if mat_id < len(scene.materials):
                    primitive["material"] = mat_id
            
            # Add mesh
            gltf_mesh = {
                "name": mesh.name,
                "primitives": [primitive]
            }
            gltf["meshes"].append(gltf_mesh)
            
            # Add node
            node = {
                "name": mesh.name,
                "mesh": len(gltf["meshes"]) - 1
            }
            gltf["nodes"].append(node)
            gltf["scenes"][0]["nodes"].append(len(gltf["nodes"]) - 1)
        
        # Define buffer
        gltf["buffers"].append({
            "byteLength": len(buffer_data)
        })
        
        # Write output
        if binary:
            # GLB format
            GLTFConverter._write_glb(filepath, gltf, buffer_data)
        else:
            # glTF + .bin format
            bin_filepath = filepath.with_suffix('.bin')
            gltf["buffers"][0]["uri"] = bin_filepath.name
            
            # Write JSON
            with open(filepath, 'w') as f:
                json.dump(gltf, f, indent=2)
            
            # Write binary
            with open(bin_filepath, 'wb') as f:
                f.write(buffer_data)
        
        return True
    
    @staticmethod
    def _write_glb(filepath: Path, gltf_json: dict, buffer_data: bytearray):
        """Write binary GLB file"""
        # JSON chunk
        json_str = json.dumps(gltf_json, separators=(',', ':'))
        json_bytes = json_str.encode('utf-8')
        
        # Pad JSON to 4-byte boundary
        while len(json_bytes) % 4 != 0:
            json_bytes += b' '
        
        # Pad buffer to 4-byte boundary
        while len(buffer_data) % 4 != 0:
            buffer_data.append(0)
        
        # GLB header
        magic = 0x46546C67  # "glTF"
        version = 2
        total_length = 12 + 8 + len(json_bytes) + 8 + len(buffer_data)
        
        with open(filepath, 'wb') as f:
            # Header
            f.write(struct.pack('<III', magic, version, total_length))
            
            # JSON chunk
            f.write(struct.pack('<II', len(json_bytes), 0x4E4F534A))  # "JSON"
            f.write(json_bytes)
            
            # Binary chunk
            f.write(struct.pack('<II', len(buffer_data), 0x004E4942))  # "BIN\0"
            f.write(buffer_data)
    
    @staticmethod
    def import_file(filepath: str) -> QScene:
        """
        Import glTF/GLB file to QScene.
        
        Args:
            filepath: Path to glTF or GLB file
        
        Returns:
            QScene loaded from file
        """
        filepath = Path(filepath)
        
        # Determine format and load
        if filepath.suffix.lower() == '.glb':
            gltf_json, buffer_data = GLTFConverter._read_glb(filepath)
        else:
            with open(filepath, 'r') as f:
                gltf_json = json.load(f)
            
            # Load binary buffer
            buffer_uri = gltf_json["buffers"][0].get("uri")
            if buffer_uri:
                bin_path = filepath.parent / buffer_uri
                with open(bin_path, 'rb') as f:
                    buffer_data = f.read()
            else:
                buffer_data = b''
        
        scene = QScene()
        
        # Parse materials
        for gltf_mat in gltf_json.get("materials", []):
            pbr = gltf_mat.get("pbrMetallicRoughness", {})
            
            base_color = pbr.get("baseColorFactor", [1, 1, 1, 1])
            
            mat = QMaterial(
                name=gltf_mat.get("name", "Material"),
                base_color=np.array(base_color[:3], dtype=np.float32),
                metallic=pbr.get("metallicFactor", 0.0),
                roughness=pbr.get("roughnessFactor", 0.5),
                alpha_mode=gltf_mat.get("alphaMode", "OPAQUE"),
                double_sided=gltf_mat.get("doubleSided", False)
            )
            scene.materials.append(mat)
        
        # Parse meshes
        for gltf_mesh in gltf_json.get("meshes", []):
            for primitive in gltf_mesh.get("primitives", []):
                # Get accessors
                pos_accessor_idx = primitive["attributes"]["POSITION"]
                indices_accessor_idx = primitive.get("indices")
                
                # Parse vertices
                vertices = GLTFConverter._parse_accessor(
                    gltf_json, buffer_data, pos_accessor_idx
                )
                
                # Parse indices
                if indices_accessor_idx is not None:
                    indices = GLTFConverter._parse_accessor(
                        gltf_json, buffer_data, indices_accessor_idx
                    ).astype(np.int32)
                    # Reshape to triangles
                    faces = indices.reshape(-1, 3)
                else:
                    # Non-indexed mesh
                    faces = np.arange(len(vertices), dtype=np.int32).reshape(-1, 3)
                
                # Parse normals
                normals = None
                if "NORMAL" in primitive["attributes"]:
                    normals = GLTFConverter._parse_accessor(
                        gltf_json, buffer_data, primitive["attributes"]["NORMAL"]
                    )
                
                # Parse UVs
                uvs = None
                if "TEXCOORD_0" in primitive["attributes"]:
                    uv_data = GLTFConverter._parse_accessor(
                        gltf_json, buffer_data, primitive["attributes"]["TEXCOORD_0"]
                    )
                    uvs = [uv_data]
                
                # Material
                material_ids = None
                if "material" in primitive:
                    mat_id = primitive["material"]
                    material_ids = np.full(len(faces), mat_id, dtype=np.int32)
                
                mesh = QMesh(
                    vertices=vertices.astype(np.float32),
                    faces=faces,
                    normals=normals,
                    uvs=uvs,
                    material_ids=material_ids,
                    name=gltf_mesh.get("name", "Mesh")
                )
                scene.meshes.append(mesh)
        
        return scene
    
    @staticmethod
    def _read_glb(filepath: Path):
        """Read binary GLB file, return (json_dict, buffer_bytes)"""
        with open(filepath, 'rb') as f:
            # Read header
            magic, version, length = struct.unpack('<III', f.read(12))
            
            if magic != 0x46546C67:
                raise ValueError("Not a valid GLB file")
            
            # Read JSON chunk
            json_length, json_type = struct.unpack('<II', f.read(8))
            json_bytes = f.read(json_length)
            gltf_json = json.loads(json_bytes.decode('utf-8'))
            
            # Read binary chunk
            bin_length, bin_type = struct.unpack('<II', f.read(8))
            buffer_data = f.read(bin_length)
            
            return gltf_json, buffer_data
    
    @staticmethod
    def _parse_accessor(gltf_json: dict, buffer_data: bytes, accessor_idx: int) -> np.ndarray:
        """Parse accessor to numpy array"""
        accessor = gltf_json["accessors"][accessor_idx]
        buffer_view = gltf_json["bufferViews"][accessor["bufferView"]]
        
        # Component types
        component_types = {
            5120: (np.int8, 1),
            5121: (np.uint8, 1),
            5122: (np.int16, 2),
            5123: (np.uint16, 2),
            5125: (np.uint32, 4),
            5126: (np.float32, 4)
        }
        
        dtype, byte_size = component_types[accessor["componentType"]]
        
        # Accessor types
        type_sizes = {
            "SCALAR": 1,
            "VEC2": 2,
            "VEC3": 3,
            "VEC4": 4,
            "MAT4": 16
        }
        
        component_count = type_sizes[accessor["type"]]
        count = accessor["count"]
        
        # Extract data
        offset = buffer_view.get("byteOffset", 0)
        data = np.frombuffer(
            buffer_data,
            dtype=dtype,
            count=count * component_count,
            offset=offset
        )
        
        if component_count > 1:
            data = data.reshape(count, component_count)
        
        return data
