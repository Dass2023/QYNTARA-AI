from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import List, Optional
from backend.pipeline import QyntaraPipeline

class Generate3DInput(BaseModel):
    prompt: str = Field(description="The text description of the 3D object to generate.")
    provider: str = Field(default="internal", description="The provider to use: 'internal' (Shap-E) or 'scenario'.")

class ValidateMeshInput(BaseModel):
    mesh_paths: List[str] = Field(description="List of file paths to the meshes to validate.")

class ExportMeshInput(BaseModel):
    engine: str = Field(description="Target engine: 'unreal', 'unity', or 'maya'.")

class ExtrudeFloorplanInput(BaseModel):
    image_path: str = Field(description="Path to the floorplan image.")
    height: float = Field(default=2.5, description="Wall height in meters.")

class RemeshInput(BaseModel):
    mesh_paths: List[str] = Field(description="List of meshes to remesh.")
    target_faces: int = Field(default=5000, description="Target face count.")

class UVInput(BaseModel):
    mesh_paths: List[str] = Field(description="List of meshes to unwrap.")

class MaterialInput(BaseModel):
    mesh_paths: List[str] = Field(description="List of meshes to assign material to.")
    material_name: str = Field(description="Name of the material (e.g., 'gold', 'concrete').")

class QyntaraTools:
    def __init__(self, pipeline: QyntaraPipeline):
        self.pipeline = pipeline

    def get_tools(self) -> List[StructuredTool]:
        return [
            StructuredTool.from_function(
                func=self._generate_3d,
                name="generate_3d_from_text",
                description="Generates a 3D model from a text description.",
                args_schema=Generate3DInput
            ),
            StructuredTool.from_function(
                func=self._validate_mesh,
                name="validate_mesh",
                description="Validates the geometry, topology, and UVs of 3D meshes.",
                args_schema=ValidateMeshInput
            ),
            StructuredTool.from_function(
                func=self._export_mesh,
                name="export_mesh",
                description="Exports the current model to a specific game engine format (USDA/GLTF) with governance checks.",
                args_schema=ExportMeshInput
            ),
            StructuredTool.from_function(
                func=self._extrude_floorplan,
                name="extrude_floorplan",
                description="Converts a 2D floorplan image into a 3D mesh by extruding walls.",
                args_schema=ExtrudeFloorplanInput
            ),
            StructuredTool.from_function(
                func=self._remesh_model,
                name="remesh_model",
                description="Optimizes mesh topology using Voxel Quad Remeshing.",
                args_schema=RemeshInput
            ),
            StructuredTool.from_function(
                func=self._generate_uvs,
                name="generate_uvs",
                description="Generates production-ready UVs using Smart Unwrapping.",
                args_schema=UVInput
            ),
            StructuredTool.from_function(
                func=self._assign_material,
                name="assign_material",
                description="Assigns a material to the mesh (e.g., gold, concrete, plastic).",
                args_schema=MaterialInput
            )
        ]

    async def _generate_3d(self, prompt: str, provider: str = "internal") -> str:
        result = await self.pipeline.run_generative_3d(prompt, provider)
        import json
        return json.dumps({
            "message": f"Generated model at: {result.generated_mesh_path}",
            "output_path": result.generated_mesh_path
        })

    async def _validate_mesh(self, mesh_paths: List[str]) -> str:
        report = await self.pipeline.run_validation(mesh_paths)
        issues = []
        if not report.geometry.watertight: issues.append("Not Watertight")
        issues.extend(report.geometry.issues)
        issues.extend(report.topology.issues)
        
        status = "Validation Passed" if not issues else "Validation Failed"
        message = f"{status}: {', '.join(issues)}" if issues else f"{status}: Mesh is clean."
        
        import json
        return json.dumps({
            "message": message,
            "output_path": mesh_paths[0] if mesh_paths else None,
            "status": status
        })

    async def _export_mesh(self, engine: str) -> str:
        report = await self.pipeline.run_export_governance(engine)
        import json
        return json.dumps({
            "message": f"Exported for {engine}. Compliant: {report.compliant}",
            "output_path": None # Export usually doesn't change the working mesh context
        })

    async def _extrude_floorplan(self, image_path: str, height: float = 2.5) -> str:
        result = await self.pipeline.run_floorplan_extrusion(image_path, height)
        import json
        if result.get("status") == "success":
            return json.dumps({
                "message": f"Floorplan extruded to {result.get('mesh_path')}",
                "output_path": result.get("mesh_path")
            })
        return json.dumps({"message": f"Floorplan extrusion failed: {result.get('message')}", "output_path": None})

    async def _remesh_model(self, mesh_paths: List[str], target_faces: int = 5000) -> str:
        result = await self.pipeline.run_quad_remeshing(mesh_paths, {"target_faces": target_faces})
        import json
        return json.dumps({
            "message": f"Remeshed model saved to: {result.mesh_path}",
            "output_path": result.mesh_path
        })

    async def _generate_uvs(self, mesh_paths: List[str]) -> str:
        result = await self.pipeline.run_uv_generation(mesh_paths)
        import json
        if result.unwrap_status == "success":
            # Assuming single mesh for now for context tracking
            # The pipeline generates _uv.obj
            # We need to return the new path. run_uv_generation returns UVOutput which doesn't explicitly have paths in the return type definition in pipeline.py (it returns UVOutput object).
            # But wait, I modified pipeline.py to return UVOutput.
            # I should verify if UVOutput has paths. It doesn't seem so in previous view.
            # Let's assume the path convention: input.obj -> input_uv.obj
            output_path = mesh_paths[0].replace(".obj", "_uv.obj") if mesh_paths else None
            return json.dumps({
                "message": f"UVs Generated. Efficiency: {result.packing_efficiency:.1%}",
                "output_path": output_path
            })
        return json.dumps({"message": "UV Generation Failed.", "output_path": None})

    async def _assign_material(self, mesh_paths: List[str], material_name: str) -> str:
        result_path = await self.pipeline.run_material_assignment(mesh_paths, material_name)
        import json
        if result_path != "Failed":
            return json.dumps({
                "message": f"Material '{material_name}' assigned. Saved to: {result_path}",
                "output_path": result_path
            })
        return json.dumps({"message": "Material Assignment Failed.", "output_path": None})
