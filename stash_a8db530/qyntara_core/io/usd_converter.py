"""
Qyntara Core Engine - USD Converter
===================================

Export/import OpenUSD format.
Based on Pixar's USD (Universal Scene Description).

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

from typing import Optional
import numpy as np
from pathlib import Path

try:
    from pxr import Usd, UsdGeom, UsdShade, Gf
    HAS_USD = True
except ImportError:
    HAS_USD = False

from ..datatypes import QMesh, QMaterial, QCamera, QLight, QScene


class USDConverter:
    """
    QScene ↔ OpenUSD converter
    
    Supports USD/USDA/USDC/USDZ formats
    
    Example:
        >>> from qyntara_core.io import USDConverter
        >>> scene = QScene(meshes=[my_mesh], materials=[my_mat])
        >>> USDConverter.export(scene, "output.usd")
        >>> loaded = USDConverter.import_file("output.usd")
    """
    
    @staticmethod
    def export(scene: QScene, filepath: str, binary: bool = True) -> bool:
        """
        Export QScene to USD file.
        
        Args:
            scene: QScene to export
            filepath: Output file path (.usd, .usda, .usdc, .usdz)
            binary: If True, write binary .usdc (faster). If False, ASCII .usda (human-readable)
        
        Returns:
            True if successful
        """
        if not HAS_USD:
            raise ImportError("USD (pxr) required. Install with: pip install usd-core")
        
        filepath = Path(filepath)
        
        # Create USD stage
        stage = Usd.Stage.CreateNew(str(filepath))
        
        # Set metadata
        UsdGeom.SetStageUpAxis(stage, UsdGeom.Tokens.y if scene.up_axis == "Y" else UsdGeom.Tokens.z)
        UsdGeom.SetStageMetersPerUnit(stage, scene.unit_scale)
        
        # Export materials first
        material_paths = {}
        if scene.materials:
            looks_scope = UsdGeom.Scope.Define(stage, "/Looks")
            
            for mat in scene.materials:
                mat_path = f"/Looks/{mat.name}"
                usd_mat = UsdShade.Material.Define(stage, mat_path)
                material_paths[mat.name] = mat_path
                
                # Create PBR shader
                shader = UsdShade.Shader.Define(stage, f"{mat_path}/Shader")
                shader.CreateIdAttr("UsdPreviewSurface")
                
                # Base color
                if isinstance(mat.base_color, np.ndarray):
                    shader.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(
                        Gf.Vec3f(*mat.base_color[:3])
                    )
                
                # Metallic/Roughness
                shader.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(float(mat.metallic))
                shader.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(float(mat.roughness))
                
                # Connect shader to material
                usd_mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(), "surface")
        
        # Export meshes
        for i, mesh in enumerate(scene.meshes):
            mesh_path = f"/{mesh.name or f'Mesh_{i}'}"
            usd_mesh = UsdGeom.Mesh.Define(stage, mesh_path)
            
            # Vertices
            usd_mesh.CreatePointsAttr(Gf.Vec3fArray.FromNumpy(mesh.vertices))
            
            # Faces
            face_vertex_counts = []
            face_vertex_indices = []
            for face in mesh.faces:
                face = face[face != -1]
                face_vertex_counts.append(len(face))
                face_vertex_indices.extend(face.tolist())
            
            usd_mesh.CreateFaceVertexCountsAttr(face_vertex_counts)
            usd_mesh.CreateFaceVertexIndicesAttr(face_vertex_indices)
            
            # Normals
            if mesh.normals is not None:
                usd_mesh.CreateNormalsAttr(Gf.Vec3fArray.FromNumpy(mesh.normals))
                usd_mesh.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
            
            # UVs
            if mesh.uvs and len(mesh.uvs) > 0:
                primvars = usd_mesh.GetPrimvarsAPI()
                for uv_idx, uv_set in enumerate(mesh.uvs):
                    uv_name = "st" if uv_idx == 0 else f"st{uv_idx}"
                    uv_primvar = primvars.CreatePrimvar(
                        uv_name,
                        Sdf.ValueTypeNames.TexCoord2fArray
                    )
                    uv_primvar.Set(Gf.Vec2fArray.FromNumpy(uv_set))
                    uv_primvar.SetInterpolation(UsdGeom.Tokens.vertex)
            
            # Material binding
            if mesh.material_ids is not None and len(scene.materials) > 0:
                # Use first material for now (single material per mesh)
                mat_id = int(mesh.material_ids[0])
                if mat_id < len(scene.materials):
                    mat_name = scene.materials[mat_id].name
                    if mat_name in material_paths:
                        binding = UsdShade.MaterialBindingAPI(usd_mesh.GetPrim())
                        binding.Bind(UsdShade.Material(stage.GetPrimAtPath(material_paths[mat_name])))
            
            # Transform
            if mesh.transform is not None:
                xform = UsdGeom.Xformable(usd_mesh)
                matrix = Gf.Matrix4d(*mesh.transform.flatten().tolist())
                xform.AddTransformOp().Set(matrix)
        
        # Export cameras
        for cam in scene.cameras:
            cam_path = f"/{cam.name}"
            usd_cam = UsdGeom.Camera.Define(stage, cam_path)
            
            usd_cam.CreateFocalLengthAttr(cam.focal_length)
            usd_cam.CreateHorizontalApertureAttr(cam.sensor_width)
            
            # Position/rotation
            xform = UsdGeom.Xformable(usd_cam)
            translate_op = xform.AddTranslateOp()
            translate_op.Set(Gf.Vec3d(*cam.position))
            
            rotate_op = xform.AddRotateXYZOp()
            rotate_op.Set(Gf.Vec3f(*cam.rotation))
        
        # Export lights
        for light in scene.lights:
            light_path = f"/{light.name}"
            
            if light.light_type == "POINT":
                usd_light = UsdLux.SphereLight.Define(stage, light_path)
                usd_light.CreateRadiusAttr(light.radius)
            elif light.light_type == "DIRECTIONAL":
                usd_light = UsdLux.DistantLight.Define(stage, light_path)
            elif light.light_type == "SPOT":
                usd_light = UsdLux.DiskLight.Define(stage, light_path)
            else:
                usd_light = UsdLux.SphereLight.Define(stage, light_path)
            
            usd_light.CreateColorAttr(Gf.Vec3f(*light.color))
            usd_light.CreateIntensityAttr(light.intensity)
            
            # Position
            xform = UsdGeom.Xformable(usd_light)
            translate_op = xform.AddTranslateOp()
            translate_op.Set(Gf.Vec3d(*light.position))
        
        # Save
        stage.Save()
        return True
    
    @staticmethod
    def import_file(filepath: str) -> QScene:
        """
        Import USD file to QScene.
        
        Args:
            filepath: Path to USD file
        
        Returns:
            QScene loaded from file
        """
        if not HAS_USD:
            raise ImportError("USD (pxr) required. Install with: pip install usd-core")
        
        stage = Usd.Stage.Open(str(filepath))
        
        # Get scene metadata
        up_axis = UsdGeom.GetStageUpAxis(stage)
        unit_scale = UsdGeom.GetStageMetersPerUnit(stage)
        
        scene = QScene(
            up_axis="Y" if up_axis == UsdGeom.Tokens.y else "Z",
            unit_scale=unit_scale
        )
        
        # Import meshes
        for prim in stage.Traverse():
            if prim.IsA(UsdGeom.Mesh):
                usd_mesh = UsdGeom.Mesh(prim)
                
                # Get vertices
                points = usd_mesh.GetPointsAttr().Get()
                vertices = np.array([[p[0], p[1], p[2]] for p in points], dtype=np.float32)
                
                # Get faces
                face_counts = usd_mesh.GetFaceVertexCountsAttr().Get()
                face_indices = usd_mesh.GetFaceVertexIndicesAttr().Get()
                
                faces = []
                idx = 0
                for count in face_counts:
                    face = list(face_indices[idx:idx+count])
                    # Pad to 4 vertices (quads)
                    while len(face) < 4:
                        face.append(-1)
                    faces.append(face[:4])
                    idx += count
                
                # Get normals
                normals_attr = usd_mesh.GetNormalsAttr()
                normals = None
                if normals_attr.HasValue():
                    normals_data = normals_attr.Get()
                    normals = np.array([[n[0], n[1], n[2]] for n in normals_data], dtype=np.float32)
                
                # Get UVs
                uvs = []
                primvars = usd_mesh.GetPrimvarsAPI()
                st_primvar = primvars.GetPrimvar("st")
                if st_primvar.HasValue():
                    uv_data = st_primvar.Get()
                    uv_array = np.array([[uv[0], uv[1]] for uv in uv_data], dtype=np.float32)
                    uvs.append(uv_array)
                
                mesh = QMesh(
                    vertices=vertices,
                    faces=np.array(faces, dtype=np.int32),
                    normals=normals,
                    uvs=uvs if uvs else None,
                    name=prim.GetName()
                )
                
                scene.meshes.append(mesh)
        
        return scene
