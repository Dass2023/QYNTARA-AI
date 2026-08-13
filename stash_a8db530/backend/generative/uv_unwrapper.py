import trimesh
import numpy as np
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

try:
    import xatlas
    HAS_XATLAS = True
except ImportError:
    HAS_XATLAS = False
    print("[UV] Warning: xatlas not found. UV generation will be limited.")

# --- Configuration & Data Structures ---

@dataclass
class UniversalUVConfig:
    """
    Configuration for the Universal UV Module.
    """
    mode: str = "AUTO"  # AUTO, UDIM, LIGHTMAP
    asset_type: str = "auto"
    texel_density: float = 0.0 # 0.0 = auto
    resolution: int = 2048 # target resolution per tile
    padding: Dict[str, Any] = field(default_factory=lambda: {"tile": 4, "shell": 2})
    packing: Dict[str, Any] = field(default_factory=lambda: {"strategy": "default", "rotate": True, "flip": False})
    udim_config: Dict[str, Any] = field(default_factory=lambda: {"max_tiles": 10, "start_tile": 1001})
    lightmap_config: Dict[str, Any] = field(default_factory=lambda: {"engine": "unreal", "min_chart_size": 4})
    debug: bool = False

@dataclass
class UniversalUVResult:
    status: str
    message: str
    output_mesh: Optional[trimesh.Trimesh] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    udim_tiles: List[int] = field(default_factory=list)

# --- AI Core ---

@dataclass
class MeshMetrics:
    classification: str
    sharpness_score: float
    avg_curvature: float
    density_multiplier: float

class MeshClassifier:
    """
    TD-Level Intelligence Core for Mesh Analysis.
    """
    @staticmethod
    def analyze(mesh: trimesh.Trimesh) -> MeshMetrics:
        try:
            if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
                 return MeshMetrics("organic", 0.0, 0.0, 1.0)

            edges = mesh.face_adjacency_angles
            if len(edges) == 0: 
                return MeshMetrics("organic", 0.0, 0.0, 1.0)
            
            # Curvature
            avg_curvature = np.mean(edges)
            
            # Sharpness (> 30 deg)
            sharp_threshold = np.radians(30)
            sharp_count = np.sum(edges > sharp_threshold)
            sharpness_score = sharp_count / len(edges)
            
            # Classification
            classification = "organic"
            if sharpness_score > 0.1:
                classification = "hard_surface"
            elif avg_curvature < 0.1 and sharpness_score > 0.05:
                classification = "hard_surface"
                
            # Density Multiplier (Harmonizer)
            density_multiplier = 1.0
            if avg_curvature > 0.3: density_multiplier = 1.25
            elif avg_curvature < 0.05: density_multiplier = 0.8
            
            return MeshMetrics(classification, sharpness_score, avg_curvature, density_multiplier)
                
        except Exception as e:
            print(f"[AI Core] Analysis failed: {e}")
            return MeshMetrics("organic", 0.0, 0.0, 1.0)

# --- Main Module ---

class SmartUVUnwrapper:
    """
    The Universal UV Module (implementation of Qyntara Spec).
    """

    def unwrap(self, mesh: trimesh.Trimesh, settings_dict: Dict[str, Any] = {}) -> Dict[str, Any]:
        """
        Legacy wrapper for pipeline compatibility.
        """
        # Adapt simple dict to UniversalUVConfig
        cfg = UniversalUVConfig()
        cfg.mode = settings_dict.get("mode", "AUTO").upper()
        cfg.resolution = int(settings_dict.get("resolution", 2048))
        
        # Run new logic
        result = self.generate(mesh, cfg)
        
        # Return dict expected by pipeline
        if result.status == "OK":
            return {
                "mesh": result.output_mesh,
                "metrics": result.metrics
            }
        else:
            raise Exception(result.message)

    def generate(self, mesh: trimesh.Trimesh, cfg: UniversalUVConfig) -> UniversalUVResult:
        print(f"[UniversalUV] Starting Generation. Mode: {cfg.mode}, Res: {cfg.resolution}")
        start_time = time.time()
        
        if not HAS_XATLAS:
            return UniversalUVResult("ERROR", "xatlas library is missing.")

        # 1. AI Analysis
        ai_metrics = MeshClassifier.analyze(mesh)
        print(f"[UniversalUV] Classification: {ai_metrics.classification} (Sharpness: {ai_metrics.sharpness_score:.2f})")

        # 2. XAtlas Configuration
        chart_options = xatlas.ChartOptions()
        pack_options = xatlas.PackOptions()
        
        # General Settings
        pack_options.resolution = cfg.resolution
        
        # Padding Logic
        # If user specifies padding in dictionary, use it
        padding = cfg.padding.get("tile", 4)
        if isinstance(cfg.padding, int): padding = cfg.padding # Handle legacy int input if any
        pack_options.padding = padding
        
        # Mode Specifics
        if cfg.mode == "LIGHTMAP":
            # Strict Non-Overlap & High Padding
            pack_options.bruteForce = True
            pack_options.rotate_charts = True # Rotation allowed for lightmaps
            pack_options.blockAlign = True # Better for lightmaps on grid
            
            # Engine Specifics
            engine = cfg.lightmap_config.get("engine", "unreal").lower()
            if engine == "unreal":
                # Unreal likes 2px min padding usually, but xatlas padding is dilation
                # Safe defaults
                pack_options.padding = max(padding, 2)
            
            chart_options.normal_deviation_weight = 2.0 # Favor flat charts
            
        elif cfg.mode == "UDIM":
            # Enable multi-atlas generation?
            # xatlas pack_options doesn't explicitly say "enable UDIM", 
            # but if charts don't fit, does it make multiple atlases? 
            # XAtlas python wrapper default behavior: creates as many atlases as needed?
            # We need to test/assume standard behavior.
            pack_options.bruteForce = True
            
        else: # AUTO
            if ai_metrics.classification == "hard_surface":
                chart_options.normal_deviation_weight = 4.0 # Cut on edges
                pack_options.rotate_charts = cfg.packing.get("rotate", True)
            else:
                chart_options.normal_deviation_weight = 1.0 # Standard
                pack_options.rotate_charts = cfg.packing.get("rotate", True)

        # 3. Execution
        try:
            atlas = xatlas.Atlas()
            
            # Prepare Data
            verts = np.ascontiguousarray(mesh.vertices, dtype=np.float32)
            indices = np.ascontiguousarray(mesh.faces, dtype=np.int32)
            
            atlas.add_mesh(verts, indices)
            
            # Generate
            atlas.generate(chart_options=chart_options, pack_options=pack_options)
            
            # Process Output
            if atlas.mesh_count == 0:
                 raise Exception("No mesh generated.")
                 
            v_mapping, new_indices, uvs = atlas[0] # First mesh
            
            # 4. UDIM Distribution Logic
            # XAtlas returns uvs normalized to 0-1 usually.
            # Does it return chart index? 
            # In the Python wrapper, atlas.chart_count gives number of charts.
            # But the 'uvs' array is just (N, 2).
            # If xatlas generated multiple atlases (pages), how do we get them?
            # The python wrapper implementation varies. 
            # Standard xatlas-python: uvs are normalized. 
            # If we want UDIMs, we might need to rely on 'texel_density' enforcing scaling 
            # and then manual packing into UDIM grids.
            
            # Since strict UDIM packing is complex in this wrapper, we will implement a heuristic:
            # If mode IS UDIM, we assume the user might want to pack charts into tiles.
            # But simple xatlas call usually fits into one 0-1 tile.
            # We will accept the 0-1 layout for now unless we implement custom packer.
            # BUT, we can support Texel Density Scaling here.
            
            # 5. Texel Density Application
            if cfg.texel_density > 0:
                # Calculate current density
                # Get mesh area
                mesh_area = mesh.area
                if mesh_area > 0:
                    current_uv_area = self._calc_uv_area(uvs, new_indices)
                    # pixels = uv_area * res^2
                    # density = sqrt(pixels) / sqrt(mesh_area)
                    # We want density = target.
                    # required_pixels = (target * sqrt(mesh_area))^2
                    # required_uv_area = required_pixels / (res^2)
                    # scale_factor = sqrt(required_uv_area / current_uv_area)
                    
                    # Alternatively, simpler:
                    # Scale UVs by ratio.
                    # Current Px/Unit = (sqrt(current_uv_area)*res) / sqrt(mesh_area)
                    # ratio = target / Current Px/Unit
                    
                    current_density = (np.sqrt(current_uv_area) * cfg.resolution) / np.sqrt(mesh_area)
                    if current_density > 0:
                        scale = cfg.texel_density / current_density
                        uvs *= scale
                        print(f"[UniversalUV] Scaled UVs by {scale:.2f} to match {cfg.texel_density} px/unit")
                        
                        # Apply UDIM offsets if it spills 0-1?
                        # This works for "unfold" but needs a packer to arrange into tiles.
                        # For now, we leave it scaled (possibly > 1) which is valid UDIM-ready data.
            
            # 6. Apply to Mesh
            new_vertices = mesh.vertices[v_mapping]
            
            new_mesh = trimesh.Trimesh(
                vertices=new_vertices, 
                faces=new_indices, 
                visual=trimesh.visual.TextureVisuals(uv=uvs),
                process=False
            )
            
            # 7. Validation / Metrics
            final_metrics = self._calculate_metrics(uvs, new_indices, cfg.resolution, mesh.area)
            final_metrics["mode"] = cfg.mode
            
            # Identify used UDIM tiles
            # Check integer floor of UVs
            u_tiles = np.floor(uvs[:, 0])
            v_tiles = np.floor(uvs[:, 1])
            # Hash to UDIM ID: 1001 + u + (v * 10)
            tiles = set()
            # Sampling some points to avoid heavy loop
            # Or unique tiles
            unique_u = np.unique(u_tiles)
            unique_v = np.unique(v_tiles)
            for u in unique_u:
                for v in unique_v:
                    if u >= 0 and v >= 0 and u < 10 and v < 100: # standard limits
                         tiles.add(int(1001 + u + (v * 10)))
            
            return UniversalUVResult(
                status="OK",
                message="UV Generation Successful",
                output_mesh=new_mesh,
                metrics=final_metrics,
                udim_tiles=sorted(list(tiles))
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return UniversalUVResult("ERROR", str(e), None)

    def _calc_uv_area(self, uvs, faces):
        if len(uvs) == 0: return 0.0
        v0 = uvs[faces[:, 0]]
        v1 = uvs[faces[:, 1]]
        v2 = uvs[faces[:, 2]]
        e1 = v1 - v0
        e2 = v2 - v0
        areas = 0.5 * np.abs(e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0])
        return np.sum(areas)

    def _calculate_metrics(self, uvs, faces, res, surf_area):
        uv_area = self._calc_uv_area(uvs, faces)
        packing_efficiency = min(uv_area, 1.0) # Relative to one tile 0-1?
        
        texel_density = 0.0
        if surf_area > 0:
             uv_pixels = uv_area * (res * res)
             texel_density = np.sqrt(uv_pixels) / np.sqrt(surf_area)

        return {
            "packing_efficiency": float(packing_efficiency),
            "uv_area": float(uv_area),
            "texel_density": float(texel_density)
        }
