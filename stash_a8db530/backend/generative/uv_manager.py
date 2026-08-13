import trimesh
import numpy as np
import xatlas
from typing import Dict, Any, List, Optional
import os

class DualChannelUVManager:
    """
    Qyntara Production Multi-UV Controller.
    Preserves UV1 (Textures) while generating UV2 (Lightmaps).
    """
    
    @staticmethod
    def process_mesh(mesh: trimesh.Trimesh, lightmap_res: int = 512) -> trimesh.Trimesh:
        """
        Takes a mesh with existing UVs and adds a second channel.
        """
        print(f"[DualUV] Processing mesh with {len(mesh.vertices)} verts...")
        
        # 1. Capture Original UVs (UV1)
        original_uvs = None
        if hasattr(mesh.visual, 'uv'):
            original_uvs = mesh.visual.uv
            print(f"[DualUV] Detected UV1: {len(original_uvs)} coords")
        else:
            print("[DualUV] No UV1 detected. Generating default UV1...")
            # Fallback if mesh has no UVs
            mesh.visual = trimesh.visual.TextureVisuals(uv=trimesh.visual.uv.simple_unwrap(mesh))
            original_uvs = mesh.visual.uv

        # 2. Generate Lightmap UVs (UV2) using xatlas
        atlas = xatlas.Atlas()
        verts = np.ascontiguousarray(mesh.vertices, dtype=np.float32)
        indices = np.ascontiguousarray(mesh.faces, dtype=np.int32)
        
        atlas.add_mesh(verts, indices)
        
        # Lightmap optimization: Higher padding, brute force packing
        chart_options = xatlas.ChartOptions()
        pack_options = xatlas.PackOptions()
        pack_options.resolution = lightmap_res
        pack_options.padding = 4
        pack_options.bruteForce = True
        
        atlas.generate(chart_options=chart_options, pack_options=pack_options)
        
        v_mapping, new_indices, uv2 = atlas[0]
        
        # 3. Synchronize Channels (New Mesh Reconstruction)
        # xatlas changes vertex count/indexing to handle seams.
        # We must map original UV1 to the new vertex layout.
        new_uv1 = original_uvs[v_mapping]
        
        # 4. Construct Multi-Channel Mesh
        new_vertices = mesh.vertices[v_mapping]
        new_normals = mesh.normals[v_mapping] if hasattr(mesh, 'normals') else None
        
        final_mesh = trimesh.Trimesh(
            vertices=new_vertices,
            faces=new_indices,
            vertex_normals=new_normals,
            process=False
        )
        
        # Store both sets in metadata/custom attributes
        # Trimesh only supports ONE uv set in .visual.uv
        # We will use .visual.uv for Texture (UV1)
        # and Store UV2 in metadata for the exporter to pick up.
        final_mesh.visual = trimesh.visual.TextureVisuals(uv=new_uv1)
        final_mesh.metadata['uv2'] = uv2
        
        print(f"[DualUV] Reconstruction Complete. UV1 and UV2 synchronized.")
        return final_mesh

    @staticmethod
    def export_multi_uv(mesh: trimesh.Trimesh, output_path: str):
        """
        Export mesh with multiple UV sets.
        Format must be one that supports multi-UV (e.g. GLB, OBJ with custom tags, or USD).
        We will use USD for production.
        """
        # Note: USD implementation would happen in UsdExporter.
        # For this logic, we just ensure metadata carries the payload.
        mesh.export(output_path)
        print(f"[DualUV] Mesh exported to {output_path} (Metadata contains UV2 payload)")
