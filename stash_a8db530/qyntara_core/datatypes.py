"""
Qyntara Core Engine - Universal Data Types
==========================================

DCC-Agnostic 3D asset representation.
All platforms (Maya, Max, Blender, Unity, Unreal) convert to/from these types.

Author: Dass2023
License: MIT (Open-Core)
Version: 5.0.0
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum
import numpy as np


class TopologyType(Enum):
    """Mesh topology types"""
    TRIANGLES = 3
    QUADS = 4
    NGONS = -1  # Mixed or n-sided polygons


@dataclass
class QMesh:
    """
    Universal mesh representation - the core of Qyntara's DCC-agnostic pipeline.
    
    All DCCs (Maya, Max, Blender) convert their native mesh format to QMesh,
    process it with Core Engine, then convert back to their native format.
    
    Example:
        >>> # Create a simple cube
        >>> vertices = np.array([[0,0,0], [1,0,0], [1,1,0], [0,1,0],
        ...                      [0,0,1], [1,0,1], [1,1,1], [0,1,1]], dtype=np.float32)
        >>> faces = np.array([[0,1,2,3], [4,5,6,7], [0,1,5,4],
        ...                   [1,2,6,5], [2,3,7,6], [3,0,4,7]], dtype=np.int32)
        >>> mesh = QMesh(vertices=vertices, faces=faces, name="Cube")
    """
    
    # Required data
    vertices: np.ndarray  # Shape: (N, 3), dtype: float32
    faces: np.ndarray     # Shape: (M, 3|4), dtype: int32 (triangles or quads)
    
    # Optional geometric data
    normals: Optional[np.ndarray] = None          # Shape: (N, 3), vertex normals
    face_normals: Optional[np.ndarray] = None     # Shape: (M, 3), face normals
    uvs: Optional[List[np.ndarray]] = None        # Multiple UV sets, each (N, 2)
    vertex_colors: Optional[np.ndarray] = None    # Shape: (N, 3|4), RGB or RGBA
    
    # Material assignment
    material_ids: Optional[np.ndarray] = None     # Shape: (M,), per-face material ID
    
    # Metadata
    name: str = "mesh"
    transform: Optional[np.ndarray] = None        # 4x4 transformation matrix
    
    # Topology info (auto-computed)
    topology_type: TopologyType = field(default=TopologyType.QUADS, init=False)
    
    def __post_init__(self):
        """Validate and auto-compute topology type"""
        # Validate vertices
        if self.vertices.shape[1] != 3:
            raise ValueError(f"Vertices must be (N, 3), got {self.vertices.shape}")
        
        # Validate faces
        if self.faces.ndim != 2:
            raise ValueError(f"Faces must be 2D array, got shape {self.faces.shape}")
        
        # Determine topology type
        face_sizes = np.array([len([v for v in face if v != -1]) for face in self.faces])
        unique_sizes = np.unique(face_sizes)
        
        if len(unique_sizes) == 1:
            if unique_sizes[0] == 3:
                self.topology_type = TopologyType.TRIANGLES
            elif unique_sizes[0] == 4:
                self.topology_type = TopologyType.QUADS
            else:
                self.topology_type = TopologyType.NGONS
        else:
            self.topology_type = TopologyType.NGONS
    
    @property
    def vertex_count(self) -> int:
        """Number of vertices"""
        return self.vertices.shape[0]
    
    @property
    def face_count(self) -> int:
        """Number of faces"""
        return self.faces.shape[0]
    
    @property
    def is_triangulated(self) -> bool:
        """Check if mesh is fully triangulated"""
        return self.topology_type == TopologyType.TRIANGLES
    
    def triangulate(self) -> 'QMesh':
        """
        Convert quads and n-gons to triangles.
        Simple fan triangulation (not optimal, but deterministic).
        
        Returns:
            New QMesh with triangulated faces
        """
        new_faces = []
        new_material_ids = [] if self.material_ids is not None else None
        
        for i, face in enumerate(self.faces):
            # Remove padding (-1 values for non-quad faces)
            face = face[face != -1]
            
            if len(face) == 3:
                # Already a triangle
                new_faces.append(face)
                if new_material_ids is not None:
                    new_material_ids.append(self.material_ids[i])
            else:
                # Fan triangulation from first vertex
                for j in range(1, len(face) - 1):
                    new_faces.append([face[0], face[j], face[j+1]])
                    if new_material_ids is not None:
                        new_material_ids.append(self.material_ids[i])
        
        return QMesh(
            vertices=self.vertices.copy(),
            faces=np.array(new_faces, dtype=np.int32),
            normals=self.normals.copy() if self.normals is not None else None,
            uvs=[uv.copy() for uv in self.uvs] if self.uvs else None,
            vertex_colors=self.vertex_colors.copy() if self.vertex_colors is not None else None,
            material_ids=np.array(new_material_ids, dtype=np.int32) if new_material_ids else None,
            name=self.name,
            transform=self.transform.copy() if self.transform is not None else None
        )
    
    def compute_normals(self, smooth=True) -> None:
        """
        Compute vertex normals.
        
        Args:
            smooth: If True, compute smooth normals (averaged from adjacent faces).
                   If False, compute hard normals (duplicated from face normals).
        """
        # Compute face normals first
        self.face_normals = np.zeros((self.face_count, 3), dtype=np.float32)
        
        for i, face in enumerate(self.faces):
            # Get face vertices (handle padding)
            face = face[face != -1]
            v0, v1, v2 = self.vertices[face[:3]]
            
            # Compute normal via cross product
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = np.cross(edge1, edge2)
            
            # Normalize
            length = np.linalg.norm(normal)
            if length > 1e-6:
                normal /= length
            
            self.face_normals[i] = normal
        
        if smooth:
            # Smooth normals: average normals from adjacent faces
            self.normals = np.zeros((self.vertex_count, 3), dtype=np.float32)
            
            for i, face in enumerate(self.faces):
                face = face[face != -1]
                for vertex_id in face:
                    self.normals[vertex_id] += self.face_normals[i]
            
            # Normalize
            norms = np.linalg.norm(self.normals, axis=1, keepdims=True)
            norms[norms < 1e-6] = 1.0  # Avoid division by zero
            self.normals /= norms
        else:
            # Hard normals: duplicate vertex per face
            # (more complex, not implemented in basic version)
            raise NotImplementedError("Hard normals require mesh duplication")


@dataclass
class QMaterial:
    """
    Universal PBR material - follows USD MaterialX and glTF 2.0 standards.
    
    Supports both values and texture paths for all parameters.
    
    Example:
        >>> # Procedural material
        >>> mat = QMaterial(
        ...     name="GoldPolished",
        ...     base_color=[1.0, 0.766, 0.336],
        ...     metallic=1.0,
        ...     roughness=0.1
        ... )
        >>> 
        >>> # Textured material
        >>> mat_tex = QMaterial(
        ...     name="RustyMetal",
        ...     base_color="textures/rust_albedo.png",
        ...     metallic="textures/rust_metallic.png",
        ...     roughness="textures/rust_roughness.png",
        ...     normal_map="textures/rust_normal.png"
        ... )
    """
    
    name: str
    
    # PBR parameters (can be value or texture path)
    base_color: Any = field(default_factory=lambda: np.array([0.8, 0.8, 0.8], dtype=np.float32))
    metallic: float = 0.0
    roughness: float = 0.5
    
    # Optional maps
    normal_map: Optional[str] = None
    emission: Optional[Any] = None  # RGB value or texture path
    ao_map: Optional[str] = None  # Ambient occlusion
    
    # Advanced PBR
    specular: float = 0.5
    anisotropy: float = 0.0
    sheen: float = 0.0
    clearcoat: float = 0.0
    
    # Alpha/transparency
    opacity: float = 1.0
    alpha_mode: str = "OPAQUE"  # OPAQUE, MASK, BLEND
    alpha_cutoff: float = 0.5
    
    # Additional properties
    double_sided: bool = False
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def is_textured(self, param: str) -> bool:
        """Check if a parameter uses a texture"""
        value = getattr(self, param)
        return isinstance(value, str)


@dataclass
class QCamera:
    """Universal camera representation"""
    
    name: str = "Camera"
    
    # Transform
    position: np.ndarray = field(default_factory=lambda: np.array([0, 0, 5], dtype=np.float32))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0, 0, 0], dtype=np.float32))
    
    # Projection
    fov: float = 50.0  # Field of view in degrees
    near_clip: float = 0.1
    far_clip: float = 1000.0
    
    # Lens properties
    focal_length: float = 35.0  # mm
    sensor_width: float = 36.0  # mm (35mm film standard)
    
    projection_type: str = "PERSPECTIVE"  # PERSPECTIVE or ORTHOGRAPHIC


@dataclass
class QLight:
    """Universal light representation"""
    
    name: str = "Light"
    
    # Transform
    position: np.ndarray = field(default_factory=lambda: np.array([0, 5, 0], dtype=np.float32))
    rotation: np.ndarray = field(default_factory=lambda: np.array([0, 0, 0], dtype=np.float32))
    
    # Light type
    light_type: str = "POINT"  # POINT, SPOT, DIRECTIONAL, AREA
    
    # Properties
    color: np.ndarray = field(default_factory=lambda: np.array([1, 1, 1], dtype=np.float32))
    intensity: float = 1.0
    
    # Attenuation
    radius: float = 10.0  # For point/spot lights
    
    # Spot properties
    spot_angle: float = 45.0  # degrees
    spot_blend: float = 0.15


@dataclass
class QScene:
    """
    Complete scene graph - represents an entire 3D scene.
    
    This is the top-level container that all DCCs export to/from.
    
    Example:
        >>> scene = QScene(
        ...     meshes=[cube_mesh, sphere_mesh],
        ...     materials=[gold_mat, plastic_mat],
        ...     cameras=[main_camera],
        ...     lights=[key_light, fill_light]
        ... )
        >>> 
        >>> # Export to any format
        >>> from qyntara_core.io import USDExporter, GLTFExporter
        >>> USDExporter.export(scene, "output.usd")
        >>> GLTFExporter.export(scene, "output.glb")
    """
    
    # Scene content
    meshes: List[QMesh] = field(default_factory=list)
    materials: List[QMaterial] = field(default_factory=list)
    cameras: List[QCamera] = field(default_factory=list)
    lights: List[QLight] = field(default_factory=list)
    
    # Scene metadata
    name: str = "Scene"
    up_axis: str = "Y"  # Y or Z
    unit_scale: float = 1.0  # 1.0 = meters
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def total_vertices(self) -> int:
        """Total vertex count across all meshes"""
        return sum(mesh.vertex_count for mesh in self.meshes)
    
    @property
    def total_faces(self) -> int:
        """Total face count across all meshes"""
        return sum(mesh.face_count for mesh in self.meshes)
    
    def get_material_by_name(self, name: str) -> Optional[QMaterial]:
        """Find material by name"""
        for mat in self.materials:
            if mat.name == name:
                return mat
        return None
    
    def validate(self) -> List[str]:
        """
        Validate scene for common issues.
        
        Returns:
            List of warning/error messages
        """
        issues = []
        
        # Check for meshes
        if not self.meshes:
            issues.append("Scene contains no meshes")
        
        # Check for degenerate meshes
        for mesh in self.meshes:
            if mesh.vertex_count == 0:
                issues.append(f"Mesh '{mesh.name}' has no vertices")
            if mesh.face_count == 0:
                issues.append(f"Mesh '{mesh.name}' has no faces")
        
        # Check material references
        for mesh in self.meshes:
            if mesh.material_ids is not None:
                max_id = np.max(mesh.material_ids)
                if max_id >= len(self.materials):
                    issues.append(f"Mesh '{mesh.name}' references material ID {max_id} but only {len(self.materials)} materials exist")
        
        return issues


# Version info
__version__ = "5.0.0"
__author__ = "Dass2023"
__license__ = "MIT"
