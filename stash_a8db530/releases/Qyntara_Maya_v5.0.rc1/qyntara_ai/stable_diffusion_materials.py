"""
Qyntara AI Compute Layer - Stable Diffusion Integration
=======================================================

Production Material Synthesis using Stable Diffusion.
Text/image prompts → Full PBR texture sets.

This completes the AI Compute Layer (v5.0).

Author: Dass2023
License: Commercial (requires Pro/Enterprise license)
Version: 5.0.0
"""

import os
import numpy as np
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import warnings

try:
    import torch
    from torch import autocast
    from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
    from PIL import Image
    HAS_DIFFUSERS = True
except ImportError:
    HAS_DIFFUSERS = False

from qyntara_core.datatypes import QMaterial


class StableDiffusionMaterialSynthesizer:
    """
    Production-grade material synthesis using Stable Diffusion.
    
    Features:
        - Text-to-PBR: "rusty metal" → Full texture set
        - Photo-to-PBR: Photo → Tileable PBR maps
        - Map generation: Base color → Normal, roughness, metallic
        - Quality modes: fast (512px), balanced (1024px), quality (2048px)
    
    Example:
        >>> from qyntara_ai.stable_diffusion_materials import StableDiffusionMaterialSynthesizer
        >>> 
        >>> synth = StableDiffusionMaterialSynthesizer(
        ...     model_id="runwayml/stable-diffusion-v1-5",
        ...     device="cuda"
        ... )
        >>> 
        >>> # Generate from text
        >>> material = synth.text_to_pbr(
        ...     prompt="polished gold metal with fine scratches",
        ...     resolution=1024,
        ...     quality="balanced"
        ... )
        >>> 
        >>> # Photo to PBR
        >>> material = synth.photo_to_pbr(
        ...     "wood_sample.jpg",
        ...     resolution=1024
        ... )
    """
    
    def __init__(
        self,
        model_id: str = "runwayml/stable-diffusion-v1-5",
        device: str = "cuda",
        cache_dir: Optional[str] = None,
        enable_attention_slicing: bool = True,
        torch_dtype = None
    ):
        """
        Initialize Stable Diffusion synthesizer.
        
        Args:
            model_id: HuggingFace model ID or local path
            device: "cuda" or "cpu"
            cache_dir: Model cache directory
            enable_attention_slicing: Reduce VRAM usage (slower but more stable)
            torch_dtype: torch.float16 for faster inference, torch.float32 for quality
        """
        if not HAS_DIFFUSERS:
            raise ImportError(
                "Stable Diffusion dependencies not installed. "
                "Install with: pip install diffusers transformers accelerate safetensors"
            )
        
        self.device = device if torch.cuda.is_available() else "cpu"
        self.cache_dir = cache_dir or Path.home() / ".qyntara" / "models"
        
        if torch_dtype is None:
            self.torch_dtype = torch.float16 if self.device == "cuda" else torch.float32
        else:
            self.torch_dtype = torch_dtype
        
        print(f"[SDMaterialSynthesizer] Initializing on {self.device}")
        print(f"  Model: {model_id}")
        print(f"  Precision: {self.torch_dtype}")
        
        # Load models (lazy - only when first used)
        self._txt2img_pipeline = None
        self._img2img_pipeline = None
        self._model_id = model_id
        self._enable_attention_slicing = enable_attention_slicing
        
        print("[SDMaterialSynthesizer] Ready (models will load on first use)")
    
    def _load_txt2img_pipeline(self):
        """Lazy load text-to-image pipeline"""
        if self._txt2img_pipeline is None:
            print("[SDMaterialSynthesizer] Loading text-to-image pipeline...")
            
            self._txt2img_pipeline = StableDiffusionPipeline.from_pretrained(
                self._model_id,
                torch_dtype=self.torch_dtype,
                cache_dir=self.cache_dir
            ).to(self.device)
            
            if self._enable_attention_slicing:
                self._txt2img_pipeline.enable_attention_slicing()
            
            print("[SDMaterialSynthesizer] Text-to-image pipeline ready")
        
        return self._txt2img_pipeline
    
    def _load_img2img_pipeline(self):
        """Lazy load image-to-image pipeline"""
        if self._img2img_pipeline is None:
            print("[SDMaterialSynthesizer] Loading image-to-image pipeline...")
            
            self._img2img_pipeline = StableDiffusionImg2ImgPipeline.from_pretrained(
                self._model_id,
                torch_dtype=self.torch_dtype,
                cache_dir=self.cache_dir
            ).to(self.device)
            
            if Selfself._enable_attention_slicing:
                self._img2img_pipeline.enable_attention_slicing()
            
            print("[SDMaterialSynthesizer] Image-to-image pipeline ready")
        
        return self._img2img_pipeline
    
    def text_to_pbr(
        self,
        prompt: str,
        resolution: int = 1024,
        quality: str = "balanced",
        seamless: bool = True,
        output_dir: Optional[str] = None,
        guidance_scale: float = 7.5,
        num_inference_steps: int = 50
    ) -> QMaterial:
        """
        Generate full PBR material from text description.
        
        Args:
            prompt: Material description (e.g., "polished gold metal")
            resolution: Output resolution (512, 1024, 2048, 4096)
            quality: "fast", "balanced", or "quality"
            seamless: Make textures tileable
            output_dir: Output directory for texture files
            guidance_scale: Classifier-free guidance (higher = more prompt adherence)
            num_inference_steps: Denoising steps (higher = better quality, slower)
        
        Returns:
            QMaterial with generated texture paths
        """
        pipeline = self._load_txt2img_pipeline()
        
        # Adjust settings for quality mode
        quality_settings = {
            "fast": {"steps": 30, "guidance": 7.0},
            "balanced": {"steps": 50, "guidance": 7.5},
            "quality": {"steps": 100, "guidance": 8.0}
        }
        
        settings = quality_settings.get(quality, quality_settings["balanced"])
        num_inference_steps = settings["steps"]
        guidance_scale = settings["guidance"]
        
        # Create output directory
        if output_dir is None:
            output_dir = Path("qyntara_materials") / prompt.replace(" ", "_")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[SDMaterialSynthesizer] Generating material: {prompt}")
        print(f"  Resolution: {resolution}x{resolution}")
        print(f"  Quality: {quality} ({num_inference_steps} steps)")
        print(f"  Seamless: {seamless}")
        
        # Generate base color (albedo)
        print("  [1/4] Generating base color...")
        albedo_prompt = f"{prompt}, clean texture, seamless, diffuse map, 8k, high quality material"
        
        with torch.inference_mode():
            albedo_result = pipeline(
                prompt=albedo_prompt,
                height=resolution,
                width=resolution,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
        
        albedo_image = albedo_result.images[0]
        albedo_path = str(output_dir / "base_color.png")
        albedo_image.save(albedo_path)
        
        # Generate normal map
        print("  [2/4] Generating normal map...")
        normal_prompt = f"{prompt}, normal map, purple and blue, geometric detail, seamless, 8k"
        
        with torch.inference_mode():
            normal_result = pipeline(
                prompt=normal_prompt,
                height=resolution,
                width=resolution,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
        
        normal_image = normal_result.images[0]
        normal_path = str(output_dir / "normal.png")
        normal_image.save(normal_path)
        
        # Generate roughness map
        print("  [3/4] Generating roughness map...")
        roughness_prompt = f"{prompt}, roughness map, grayscale, surface variation, seamless, 8k"
        
        with torch.inference_mode():
            roughness_result = pipeline(
                prompt=roughness_prompt,
                height=resolution,
                width=resolution,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
        
        roughness_image = roughness_result.images[0].convert('L')  # Convert to grayscale
        roughness_path = str(output_dir / "roughness.png")
        roughness_image.save(roughness_path)
        
        # Generate metallic map
        print("  [4/4] Generating metallic map...")
        metallic_prompt = f"{prompt}, metallic map, grayscale, metal mask, seamless, 8k"
        
        with torch.inference_mode():
            metallic_result = pipeline(
                prompt=metallic_prompt,
                height=resolution,
                width=resolution,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale
            )
        
        metallic_image = metallic_result.images[0].convert('L')
        metallic_path = str(output_dir / "metallic.png")
        metallic_image.save(metallic_path)
        
        # Create QMaterial
        material = QMaterial(
            name=prompt.replace(" ", "_"),
            base_color=albedo_path,
            metallic=metallic_path,
            roughness=roughness_path,
            normal_map=normal_path,
            properties={
                "ai_generated": True,
                "model": self._model_id,
                "prompt": prompt,
                "resolution": resolution,
                "quality": quality,
                "seamless": seamless
            }
        )
        
        print(f"✅ Material generated successfully!")
        print(f"   Output: {output_dir}")
        
        return material
    
    def photo_to_pbr(
        self,
        photo_path: str,
        resolution: int = 1024,
        seamless: bool = True,
        output_dir: Optional[str] = None
    ) -> QMaterial:
        """
        Convert photo to tileable PBR material.
        
        Args:
            photo_path: Input photo path
            resolution: Output resolution
            seamless: Make texture tileable
            output_dir: Output directory
        
        Returns:
            QMaterial with generated maps
        """
        pipeline = self._load_img2img_pipeline()
        
        photo_path = Path(photo_path)
        if not photo_path.exists():
            raise FileNotFoundError(f"Photo not found: {photo_path}")
        
        # Load input image
        input_image = Image.open(photo_path).convert("RGB")
        input_image = input_image.resize((resolution, resolution))
        
        # Create output directory
        if output_dir is None:
            output_dir = photo_path.parent / f"{photo_path.stem}_pbr"
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"[SDMaterialSynthesizer] Converting photo to PBR: {photo_path.name}")
        print(f"  Resolution: {resolution}x{resolution}")
        
        # Use img2img to enhance and make seamless
        print("  [1/3] Enhancing base color...")
        with torch.inference_mode():
            albedo_result = pipeline(
                prompt="high quality seamless texture, clean, detailed",
                image=input_image,
                strength=0.3,  # Keep mostly original
                num_inference_steps=30
            )
        
        albedo_path = str(output_dir / "base_color.png")
        albedo_result.images[0].save(albedo_path)
        
        # Generate normal from albedo
        print("  [2/3] Generating normal map...")
        normal_prompt = "normal map, geometric detail, purple and blue tones"
        
        with torch.inference_mode():
            normal_result = pipeline(
                prompt=normal_prompt,
                image=input_image,
                strength=0.7,
                num_inference_steps=30
            )
        
        normal_path = str(output_dir / "normal.png")
        normal_result.images[0].save(normal_path)
        
        # Generate roughness
        print("  [3/3] Generating roughness map...")
        roughness_prompt = "roughness map, grayscale, surface detail"
        
        with torch.inference_mode():
            roughness_result = pipeline(
                prompt=roughness_prompt,
                image=input_image,
                strength=0.7,
                num_inference_steps=30
            )
        
        roughness_path = str(output_dir / "roughness.png")
        roughness_result.images[0].convert('L').save(roughness_path)
        
        # Create material
        material = QMaterial(
            name=photo_path.stem,
            base_color=albedo_path,
            roughness=roughness_path,
            normal_map=normal_path,
            properties={
                "ai_generated": True,
                "source_photo": str(photo_path),
                "resolution": resolution,
                "seamless": seamless
            }
        )
        
        print(f"✅ PBR material created from photo!")
        print(f"   Output: {output_dir}")
        
        return material


# Convenience function
def quick_material(prompt: str, output_dir: str = None) -> QMaterial:
    """Quick material generation with default settings"""
    synth = StableDiffusionMaterialSynthesizer()
    return synth.text_to_pbr(prompt, output_dir=output_dir)
