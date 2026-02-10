from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

class SegmentationArtifacts(BaseModel):
    object_masks: List[str] = Field(default_factory=list)
    mesh_region_masks: List[str] = Field(default_factory=list)
    curvature_boundaries: List[str] = Field(default_factory=list)
    material_clusters: List[Dict[str, Any]] = Field(default_factory=list)
    uv_region_clusters: List[Dict[str, Any]] = Field(default_factory=list)
    surface_semantic_zones: List[str] = Field(default_factory=list)

class GeometryValidation(BaseModel):
    watertight: bool = True
    issues: List[str] = Field(default_factory=list)
    non_manifold_edges: int = 0
    open_boundaries: int = 0
    lamina_faces: int = 0
    self_intersections: int = 0
    inverted_normals: int = 0
    degenerate_tris: int = 0

class UVValidation(BaseModel):
    overlaps: int = 0
    distortion: float = 0.0
    missing_uv_sets: int = 0
    udim_issues: int = 0

class MaterialValidation(BaseModel):
    missing_maps: List[str] = Field(default_factory=list)
    incorrect_pbr_channels: List[str] = Field(default_factory=list)
    texture_mismatch: bool = False
    shader_inconsistencies: List[str] = Field(default_factory=list)

class TopologyValidation(BaseModel):
    triangulated: bool = True
    manifold: bool = True
    issues: List[str] = Field(default_factory=list)
    valence_issues: int = 0
    bad_edge_flow: int = 0
    tri_noise: int = 0
    hard_edge_errors: int = 0

class ValidationReport(BaseModel):
    geometry: GeometryValidation
    uv: UVValidation
    material: MaterialValidation
    topology: TopologyValidation
    topology: TopologyValidation
    passed: bool = True

class RemeshMetrics(BaseModel):
    poly_count: int = 0
    topology_score: float = 0.0

class RemeshOutput(BaseModel):
    status: str = "pending"
    mesh_path: Optional[str] = None
    metrics: Optional[RemeshMetrics] = None

class MaterialProfile(BaseModel):
    clusters: List[Dict[str, Any]] = []

class UVOutput(BaseModel):
    seam_field_path: str = ""
    unwrap_status: str = "pending"
    packing_efficiency: float = 0.0
    texel_density: float = 0.0
    udim_count: int = 1
    sam_guided_zones: List[str] = Field(default_factory=list)

class LightmapQualityMetrics(BaseModel):
    texel_density: float = 0.0
    padding_distribution: float = 0.0
    chart_score: float = 0.0
    distortion_score: float = 0.0

class LightmapUVOutput(BaseModel):
    texture_verification: str = "pass"
    auto_fix_recommendations: List[str] = Field(default_factory=list)
    shader_mapping: Dict[str, str] = Field(default_factory=dict)
    neural_enhancement_applied: bool = False

class Generative3DOutput(BaseModel):
    generated_mesh_path: Optional[str] = None
    reconstructed_mesh_path: Optional[str] = None
    partial_regeneration_regions: List[str] = Field(default_factory=list)
    style_transfer_applied: bool = False
    neural_enhancement_applied: bool = False

class ExportComplianceReport(BaseModel):
    target_engine: str
    compliant: bool = False
    issues: List[str] = Field(default_factory=list)
    fixed_items: List[str] = Field(default_factory=list)

class AutodeskValidation(BaseModel):
    status: str
    checks: Dict[str, Dict[str, Any]]
    maya_compatible: bool

class LightmapValidationReport(BaseModel):
    health_score: float = 100.0
    overlaps_detected: bool = False
    padding_issues: int = 0
    coverage_percent: float = 0.0
    issues: List[str] = []

class DualUVOutput(BaseModel):
    status: str = "pending"
    texture_mesh_path: Optional[str] = None
    lightmap_mesh_path: Optional[str] = None
    texture_metrics: Optional[UVOutput] = None
    lightmap_metrics: Optional[LightmapQualityMetrics] = None
    lightmap_diagnostics: Optional[LightmapValidationReport] = None

class QyntaraArtifacts(BaseModel):
    status: str
    segmentation: SegmentationArtifacts
    validationReport: ValidationReport
    autodeskValidation: AutodeskValidation
    uvOutput: UVOutput
    lightmapUVOutput: LightmapUVOutput
    dualUVOutput: Optional[DualUVOutput] = None
    lightmapDiagnostics: Optional[LightmapValidationReport] = None
    remeshOutput: RemeshOutput
    materialProfile: MaterialProfile
    generative3DOutput: Generative3DOutput
    exportCompliance: ExportComplianceReport
    optimization_export: Dict[str, Any] = Field(default_factory=dict)

class PipelineRequest(BaseModel):
    scene: Dict[str, Any] = Field(default_factory=dict)
    meshes: List[str]
    materials: List[str]
    tasks: List[str] = ["segment", "validate", "uv", "lightmapuv", "remesh", "material", "generative", "export"]
    engineTarget: str = "unity"
    remesh_settings: Dict[str, Any] = Field(default_factory=dict)
    generative_settings: Dict[str, Any] = Field(default_factory=dict)
    uv_settings: Dict[str, Any] = Field(default_factory=dict)
    material_settings: Dict[str, Any] = Field(default_factory=dict)
    export_settings: Dict[str, Any] = Field(default_factory=dict)
    validation_profile: str = "GENERIC"

class ExportRequest(BaseModel):
    source_path: str
    target_path: str
    format: str
    engine: str
