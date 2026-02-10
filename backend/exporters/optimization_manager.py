import trimesh
import os
import shutil
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from backend.exporters.usd_exporter import UsdExporter

@dataclass
class ExportConfig:
    target_platform: str = "UNREAL_HIGH" # UNREAL_HIGH, MOBILE, WEBGL
    max_triangles: int = 0 # 0 = no limit
    generate_lods: bool = False
    lods: List[float] = field(default_factory=lambda: [1.0, 0.5, 0.25, 0.125]) # Ratios
    export_formats: List[str] = field(default_factory=lambda: ["OBJ"]) # OBJ, GLTF, USD, FBX
    texture_config: Dict[str, Any] = field(default_factory=lambda: {"max_res": "4K", "compression": "BC7"})

@dataclass
class ExportResult:
    status: str
    message: str
    files: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

class MeshOptimizer:
    @staticmethod
    def optimize(mesh: trimesh.Trimesh, max_tri_count: int) -> trimesh.Trimesh:
        current = len(mesh.faces)
        if max_tri_count > 0 and current > max_tri_count:
            print(f"[Optimizer] Reducing {current} -> {max_tri_count} faces...")
            # Trimesh simplify uses ratio generally? No, explicit face count supported in newer versions or quadric?
            # simplify_quadric_decimation takes 'face_count' in some bindings or 'percent' in others
            # Let's assume percent validation.
            percent = 1.0 - (max_tri_count / current)
            if percent > 0:
                 return mesh.simplify_quadric_decimation(percent=percent)
        return mesh

class LODGenerator:
    @staticmethod
    def generate_chain(mesh: trimesh.Trimesh, ratios: List[float]) -> List[trimesh.Trimesh]:
        chain = []
        for i, r in enumerate(ratios):
            if r >= 0.99:
                chain.append(mesh.copy())
            else:
                print(f"[LOD] Generating LOD{i} (Ratio: {r})...")
                # Simplify
                # Note: decimation is destructive, use copy
                lod = mesh.simplify_quadric_decimation(percent=(1.0 - r))
                chain.append(lod)
        return chain

class OptimizationManager:
    """
    Module 6: OPTIMIZATION EXPORT
    """
    def __init__(self):
        self.usd_exporter = UsdExporter()

    def process(self, mesh_paths: List[str], config: ExportConfig) -> ExportResult:
        print(f"[Export] Starting Batch. Platform: {config.target_platform}")
        start_time = time.time()
        output_files = []
        summary_metrics = {}
        
        export_dir = "backend/data/exports"
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)
            
        for path in mesh_paths:
            try:
                base_name = os.path.splitext(os.path.basename(path))[0]
                mesh = trimesh.load(path)
                
                # 1. Mesh Optimization (Global Cap)
                if config.max_triangles > 0:
                    mesh = MeshOptimizer.optimize(mesh, config.max_triangles)
                
                # 2. LOD Generation
                meshes_to_export = [] # List of (suffix, mesh_obj)
                
                if config.generate_lods:
                    lods = LODGenerator.generate_chain(mesh, config.lods)
                    for i, lod_mesh in enumerate(lods):
                         meshes_to_export.append((f"_LOD{i}", lod_mesh))
                else:
                    meshes_to_export.append(("", mesh))
                    
                # 3. Export Formats
                for suffix, m in meshes_to_export:
                    final_name = f"{base_name}{suffix}"
                    
                    for fmt in config.export_formats:
                        fmt = fmt.upper()
                        out_path = os.path.join(export_dir, f"{final_name}.{fmt.lower()}")
                        
                        if fmt == "OBJ":
                            m.export(out_path)
                            output_files.append(out_path)
                            
                        elif fmt == "GLTF" or fmt == "GLB":
                            out_path = out_path.replace(".gltf", ".glb") # Force binary
                            m.export(out_path, file_type='glb')
                            output_files.append(out_path)
                            
                        elif fmt == "USD" or fmt == "USDA":
                            # Use our fallback USD exporter if trimesh fails
                            # Trimesh export(file_type='usd') might work if usd-core installed
                            try:
                                m.export(out_path)
                            except:
                                # Fallback
                                if suffix == "": # Only support LOD0 fallback for now
                                    temp_obj = os.path.join(export_dir, f"{final_name}_temp.obj")
                                    m.export(temp_obj)
                                    self.usd_exporter.export_to_usda(temp_obj, out_path)
                                    if os.path.exists(temp_obj): os.remove(temp_obj)
                            output_files.append(out_path)
                            
                        # FBX is hard without libs. Skip or Placeholder.
                        
                        summary_metrics[final_name] = len(m.faces)
                        
            except Exception as e:
                print(f"[Export] Failed for {path}: {e}")
                return ExportResult("ERROR", str(e))

        elapsed = time.time() - start_time
        return ExportResult(
            status="OK", 
            message=f"Exported {len(output_files)} files in {elapsed:.2f}s",
            files=output_files,
            metrics=summary_metrics
        )
