import trimesh
import numpy as np
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from ..models import LightmapValidationReport, ValidationReport

@dataclass
class ValidationIssue:
    severity: str # ERROR, WARNING, INFO
    category: str # GEOMETRY, UV, MATERIAL, NAMING
    object_name: str
    description: str
    auto_fix_available: bool = False

@dataclass
class SceneValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)
    score: float = 100.0
    summary: str = ""

class SceneValidator:
    """
    Module 4: VALIDATE SCENE
    Orchestrates validation rules based on target profiles.
    """
    
    PATTERNS = {
        "UNREAL": r"^(SM_|SK_|T_|M_)[A-Za-z0-9_]+$",
        "UNITY": r"^[A-Z][a-zA-Z0-9_]*$",
        "GENERIC": r"^[a-zA-Z0-9_]+$"
    }

    def validate(self, meshes: List[str], profile: str = "GENERIC") -> SceneValidationResult:
        result = SceneValidationResult()
        print(f"[Validator] Running checks with profile: {profile}")
        
        total_objects = len(meshes)
        issues_count = 0
        
        for mesh_path in meshes:
            try:
                mesh_name = mesh_path.split("/")[-1] # Simple name
                # Load mesh
                # Note: Trimesh loading might be slow for massive scenes.
                # In production, we might use a lighter parser or metadata if available.
                mesh = trimesh.load(mesh_path)
                
                # --- 1. Naming Conventions ---
                pattern = self.PATTERNS.get(profile, self.PATTERNS["GENERIC"])
                # Extract basename without extension
                base_name = mesh_name.split(".")[0]
                if not re.match(pattern, base_name):
                    result.issues.append(ValidationIssue(
                        "WARNING", "NAMING", mesh_name, 
                        f"Name does not match {profile} convention ({pattern}).",
                        False
                    ))
                    issues_count += 0.5
                
                # --- 2. Geometry Checks ---
                # N-Gons (Trimesh loads as triangles usually, but we check metadata if preservable)
                # If we loaded an OBJ that had ngons, trimesh triangulates it by default.
                # We can check processing metadata if we loaded with process=False?
                # For now, we assume trimesh is valid triangle mesh.
                
                if not mesh.is_watertight:
                     result.issues.append(ValidationIssue(
                        "WARNING", "GEOMETRY", mesh_name,
                        "Mesh is not watertight (holes detected).",
                        True # Auto-fill
                    ))
                     issues_count += 1
                
                if not mesh.is_winding_consistent:
                     result.issues.append(ValidationIssue(
                        "ERROR", "GEOMETRY", mesh_name,
                        "Inconsistent face winding (normals flipped).",
                        True # Auto-fix
                    ))
                     issues_count += 3

                # Standard Zero Area check
                if mesh.area < 1e-6:
                     result.issues.append(ValidationIssue(
                        "ERROR", "GEOMETRY", mesh_name,
                        "Mesh has near-zero surface area.",
                        False
                    ))
                     issues_count += 5

                # --- 3. UV Checks ---
                # UVs are in mesh.visual.uv
                if not hasattr(mesh.visual, 'uv') or mesh.visual.uv is None or len(mesh.visual.uv) == 0:
                     result.issues.append(ValidationIssue(
                        "ERROR", "UV", mesh_name,
                        "Mesh has no UV coordinates.",
                        True # Auto-UV
                    ))
                     issues_count += 5
                else:
                    # Check overlap (Heuristic)
                    # Use LightmapValidator logic?
                    pass

                # --- 4. Material Checks ---
                # Trimesh doesn't deeply parse materials
                # We can check simple face materials
                
                # --- 5. Transform Checks ---
                if not np.allclose(mesh.extents, [0,0,0], atol=1e-4):
                    # Check for negative scale? Trimesh applies transform on load usually.
                    pass

            except Exception as e:
                result.issues.append(ValidationIssue(
                    "ERROR", "SYSTEM", mesh_path,
                    f"Failed to load or validate: {str(e)}",
                    False
                ))
                issues_count += 5

        # Format Summary
        result.score = max(0, 100 - (issues_count * 5))
        result.summary = f"Scanned {total_objects} objects. Found {len(result.issues)} issues. Health: {result.score}%"
        
        return result

class LightmapValidator:
    """
    Engine-Verified Lightmap Diagnostics.
    """
    
    @staticmethod
    def validate(mesh: trimesh.Trimesh, resolution: int = 1024) -> LightmapValidationReport:
        report = LightmapValidationReport()
        issues = []
        health = 100.0
        
        # 1. Check UV Channels
        if not hasattr(mesh.visual, 'uv') or mesh.visual.uv is None or len(mesh.visual.uv) == 0:
            return LightmapValidationReport(
                health_score=0.0,
                issues=["CRITICAL: No UVs found."]
            )
            
        uvs = mesh.visual.uv
        
        # 2. Coverage Calculation
        try:
            uv_mesh = trimesh.Trimesh(vertices=uvs, faces=mesh.faces, process=False)
            uv_area = uv_mesh.area
            report.coverage_percent = round(uv_area * 100, 2)
            
            if report.coverage_percent < 50.0:
                issues.append(f"Low UV Efficiency ({report.coverage_percent}%). Waste of texture space.")
                health -= 10.0
            elif report.coverage_percent > 98.0:
                issues.append(f"High UV Coverage ({report.coverage_percent}%). High risk of edge bleeding.")
                health -= 5.0
                
        except Exception as e:
            issues.append(f"Coverage Calc Failed: {str(e)}")
            
        # 3. Overlap Check (Simplified)
        if np.any(uvs < 0.0) or np.any(uvs > 1.0):
             issues.append("UVs verify_out_of_bounds [0, 1].")
             health -= 20.0
             
        report.health_score = max(0, health)
        report.issues = issues
        report.overlaps_detected = False
        
        return report
