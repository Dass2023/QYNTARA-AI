import numpy as np
import trimesh
import os
import shutil
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

# --- Configuration ---

@dataclass
class UniversalMaterialConfig:
    """Config for Material AI operations."""
    scope: str = "SCENE" # SELECTED, SCENE
    source_profile: str = "AUTO" # STANDARD, ARNOLD, VRAY, USD
    target_profile: str = "UNREAL" # UNREAL, UNITY_URP, UNITY_HDRP, GLTF
    swap_prompt: Optional[str] = None
    texture_intel: Dict[str, Any] = field(default_factory=lambda: {
        "generate_missing": True,
        "upscale": "2K", # 1K, 2K, 4K
        "seamless": True,
        "pack_channels": True # ORM (Occlusion, Roughness, Metallic)
    })

@dataclass
class MaterialConversionResult:
    status: str
    message: str
    processed_materials: List[Dict[str, Any]] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)

# --- Core Classes ---

class UniversalPBRMaterial:
    """
    Intermediate representation of a PBR material.
    Normalized 0-1 values.
    """
    def __init__(self, name: str):
        self.name = name
        self.base_color = [1.0, 1.0, 1.0, 1.0] # float rgba
        self.roughness = 0.5
        self.metallic = 0.0
        self.normal_strength = 1.0
        self.emissive = [0.0, 0.0, 0.0]
        self.ao = 1.0
        self.opacity = 1.0
        
        # Texture Paths
        self.textures = {
            "base_color": None,
            "roughness": None,
            "metallic": None,
            "normal": None,
            "height": None,
            "emissive": None,
            "ao": None
        }

class ShaderConverter:
    """
    Converts Universal PBR to Engine-Specific Shader Param sets.
    """
    @staticmethod
    def convert(material: UniversalPBRMaterial, target_profile: str) -> Dict[str, Any]:
        profile = target_profile.upper()
        
        # Default PBR
        result = {
            "name": material.name,
            "type": "PBR",
            "params": {}
        }

        if "UNREAL" in profile:
            # Unreal Engine 5 Standard
            # Packing: ORM (Linear) -> R=AO, G=Rough, B=Metal
            result["type"] = "Unreal_M_Standard"
            result["params"] = {
                "BaseColor": material.base_color,
                "Roughness": material.roughness,
                "Metallic": material.metallic,
                "Normal": material.normal_strength,
                "Specular": 0.5 # Default UE
            }
            # Note: In a real implementation, we would generate a Python script or USD snippet
            # to import this into Unreal.
            
        elif "UNITY" in profile:
            # Unity URP/HDRP
            # Packing: MaskMap (Linear) -> R=Metal, G=AO, B=Detail, A=Smoothness
            result["type"] = "Unity_HDRP_Lit"
            result["params"] = {
                "_BaseColor": material.base_color,
                "_Smoothness": 1.0 - material.roughness, # Invert Roughness
                "_Metallic": material.metallic,
                "_NormalScale": material.normal_strength
            }
        
        elif "GLTF" in profile:
            # glTF 2.0
            # Packing: ORM -> R=Occ, G=Rough, B=Metal
            result["type"] = "glTF_PBR"
            result["params"] = {
                "baseColorFactor": material.base_color,
                "roughnessFactor": material.roughness,
                "metallicFactor": material.metallic
            }

        return result

class TextureProcessor:
    """
    Texture Intelligence: Packing, Scaling, Seaming.
    Uses PIL/cv2 if available.
    """
    @staticmethod
    def pack_channels(mat: UniversalPBRMaterial, target: str):
        # Placeholder for actual image processing logic.
        # Would load mat.textures['roughness'], mat.textures['metallic']...
        # and merge channels.
        
        print(f"[Texture] Packing channels for {mat.name} -> {target}")
        if target == "UNREAL":
            return "ORM_packed.png" # Mock return
        elif target == "UNITY":
            return "MaskMap_packed.png"
        return None

class MaterialManager:
    """
    The Material AI Module.
    """
    def __init__(self):
        # Mock library for swapping
        self.library = {
            "gold": UniversalPBRMaterial("Gold"),
            "concrete": UniversalPBRMaterial("Concrete")
        }
        self._init_library()

    def _init_library(self):
        m = self.library["gold"]
        m.base_color = [1.0, 0.8, 0.0, 1.0]
        m.metallic = 1.0
        m.roughness = 0.1
        
        m = self.library["concrete"]
        m.base_color = [0.5, 0.5, 0.5, 1.0]
        m.metallic = 0.0
        m.roughness = 0.9

    def process(self, mesh_paths: List[str], config: UniversalMaterialConfig) -> MaterialConversionResult:
        """
        Main entry point for Material AI pipeline.
        """
        print(f"[MaterialAI] Starting Processing. Target: {config.target_profile}")
        
        processed = []
        
        # 1. Analyze / Load Materials from Meshes
        # Trimesh loads materials from .mtl if OBJ.
        # We will iterate and upgrade them.
        
        for p in mesh_paths:
            # Simulation: assume we found a material "DefaultMat"
            # In production, parse .mtl or .usd
            
            # Create a Universal Material from the asset
            # (Mocking ingestion)
            mat = UniversalPBRMaterial("SourceMat_01")
            mat.roughness = 0.8 # Standard guess
            
            # 2. Swap Logic (AI Intent)
            if config.swap_prompt:
                print(f"[MaterialAI] Analyzing intent: '{config.swap_prompt}'...")
                # Simple keyword matching
                if "gold" in config.swap_prompt.lower():
                    print("[MaterialAI] Swap Match: Gold")
                    mat = self.library["gold"] # Swap
                elif "concrete" in config.swap_prompt.lower():
                     mat = self.library["concrete"]

            # 3. Texture Intelligence
            if config.texture_intel.get("pack_channels"):
                packed_map = TextureProcessor.pack_channels(mat, "UNREAL" if "UNREAL" in config.target_profile else "UNITY")
            
            # 4. Conversion
            converted = ShaderConverter.convert(mat, config.target_profile)
            processed.append(converted)
            
            print(f"[MaterialAI] Processed {mat.name} -> {converted['type']}")

        return MaterialConversionResult(
            status="OK",
            message="Material Conversion & Optimization Complete.",
            processed_materials=processed
        )

    def assign_material(self, mesh: trimesh.Trimesh, material_name: str) -> trimesh.Trimesh:
        # Legacy support
        # Simply change vertex colors for preview
        return mesh

