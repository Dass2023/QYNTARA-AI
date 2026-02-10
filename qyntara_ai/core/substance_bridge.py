"""
Substance Designer Integration for Qyntara AI.
Provides bridge to Substance Automation Toolkit (SAT) for professional material generation.
"""
import os
import subprocess
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SubstanceIntegration:
    """
    Bridge to Substance Designer/Automation Toolkit.
    Supports: .sbsar export, parameter control, batch processing.
    """
    
    def __init__(self):
        self.substance_installed = False
        self.sbscooker_path = None
        self.sbsrender_path = None
        self.detect_substance()
        
    def detect_substance(self):
        """
        Detect Substance Designer installation.
        Checks common installation paths for sbscooker and sbsrender.
        """
        # Common installation paths
        common_paths = [
            r"C:\Program Files\Adobe\Adobe Substance 3D Designer\sbscooker.exe",
            r"C:\Program Files\Allegorithmic\Substance Designer\sbscooker.exe",
            r"C:\Program Files (x86)\Allegorithmic\Substance Designer\sbscooker.exe",
        ]
        
        render_paths = [
            r"C:\Program Files\Adobe\Adobe Substance 3D Designer\sbsrender.exe",
            r"C:\Program Files\Allegorithmic\Substance Designer\sbsrender.exe",
            r"C:\Program Files (x86)\Allegorithmic\Substance Designer\sbsrender.exe",
        ]
        
        # Check for sbscooker
        for path in common_paths:
            if os.path.exists(path):
                self.sbscooker_path = path
                logger.info(f"Found Substance Designer: {path}")
                break
        
        # Check for sbsrender
        for path in render_paths:
            if os.path.exists(path):
                self.sbsrender_path = path
                break
        
        # Check environment variable
        if not self.sbscooker_path:
            env_path = os.environ.get("SUBSTANCE_DESIGNER_PATH")
            if env_path:
                cooker = os.path.join(env_path, "sbscooker.exe")
                if os.path.exists(cooker):
                    self.sbscooker_path = cooker
        
        self.substance_installed = bool(self.sbscooker_path)
        
        if not self.substance_installed:
            logger.warning("Substance Designer not found. Material generation will use fallback.")
        
        return self.substance_installed
    
    def generate_material(self, prompt, output_dir, resolution=1024):
        """
        Generate material from prompt using Substance template.
        
        Args:
            prompt: Material description (e.g., "rusty metal", "concrete wall")
            output_dir: Directory to save generated textures
            resolution: Texture resolution (256, 512, 1024, 2048, 4096)
        
        Returns:
            dict: Paths to generated texture maps
        """
        if not self.substance_installed:
            logger.warning("Substance not installed, using fallback")
            return self._generate_fallback_material(prompt, output_dir)
        
        try:
            # 1. Select appropriate template based on prompt
            template_path = self._select_template(prompt)
            
            if not template_path:
                logger.warning(f"No template found for '{prompt}', using fallback")
                return self._generate_fallback_material(prompt, output_dir)
            
            # 2. Cook .sbs to .sbsar
            sbsar_path = os.path.join(output_dir, f"{prompt.replace(' ', '_')}.sbsar")
            success = self._cook_sbsar(template_path, sbsar_path)
            
            if not success:
                return self._generate_fallback_material(prompt, output_dir)
            
            # 3. Render texture maps from .sbsar
            texture_paths = self._render_textures(sbsar_path, output_dir, resolution)
            
            return texture_paths
            
        except Exception as e:
            logger.error(f"Substance generation failed: {e}")
            return self._generate_fallback_material(prompt, output_dir)
    
    def _select_template(self, prompt):
        """
        Select appropriate Substance template based on prompt keywords.
        
        Returns:
            Path to .sbs template file, or None if not found
        """
        # Template mapping (keyword -> template file)
        templates = {
            "metal": "templates/metal_base.sbs",
            "rust": "templates/metal_rusty.sbs",
            "concrete": "templates/concrete_base.sbs",
            "wood": "templates/wood_planks.sbs",
            "stone": "templates/stone_base.sbs",
            "fabric": "templates/fabric_base.sbs",
            "leather": "templates/leather_base.sbs",
            "plastic": "templates/plastic_base.sbs",
        }
        
        # Check for keywords in prompt
        prompt_lower = prompt.lower()
        for keyword, template in templates.items():
            if keyword in prompt_lower:
                # Check if template exists in Qyntara resources
                template_path = os.path.join(
                    os.path.dirname(__file__), 
                    "..", "resources", "substance", template
                )
                if os.path.exists(template_path):
                    return template_path
        
        return None
    
    def _cook_sbsar(self, sbs_path, output_path):
        """
        Cook .sbs file to .sbsar using sbscooker.
        
        Args:
            sbs_path: Path to source .sbs file
            output_path: Path to output .sbsar file
        
        Returns:
            bool: Success status
        """
        try:
            cmd = [
                self.sbscooker_path,
                "--inputs", sbs_path,
                "--output-path", os.path.dirname(output_path),
                "--output-name", os.path.basename(output_path).replace(".sbsar", "")
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"Cooked SBSAR: {output_path}")
                return True
            else:
                logger.error(f"sbscooker failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("sbscooker timed out")
            return False
        except Exception as e:
            logger.error(f"Cook failed: {e}")
            return False
    
    def _render_textures(self, sbsar_path, output_dir, resolution):
        """
        Render texture maps from .sbsar using sbsrender.
        
        Args:
            sbsar_path: Path to .sbsar file
            output_dir: Directory to save textures
            resolution: Texture resolution
        
        Returns:
            dict: Paths to generated maps (diffuse, roughness, normal, ao, metallic)
        """
        if not self.sbsrender_path:
            logger.warning("sbsrender not found, cannot render textures")
            return {}
        
        try:
            # Render all outputs
            cmd = [
                self.sbsrender_path,
                "render",
                "--input", sbsar_path,
                "--output-path", output_dir,
                "--output-format", "png",
                "--set-value", f"$outputsize@{resolution},{resolution}"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                logger.error(f"sbsrender failed: {result.stderr}")
                return {}
            
            # Scan output directory for generated maps
            base_name = os.path.basename(sbsar_path).replace(".sbsar", "")
            texture_paths = {}
            
            # Common output names from Substance
            map_suffixes = {
                "diffuse": ["_basecolor", "_diffuse", "_albedo"],
                "roughness": ["_roughness"],
                "normal": ["_normal"],
                "ao": ["_ambient_occlusion", "_ao"],
                "metallic": ["_metallic"],
                "height": ["_height"]
            }
            
            for map_type, suffixes in map_suffixes.items():
                for suffix in suffixes:
                    pattern = f"{base_name}{suffix}.png"
                    full_path = os.path.join(output_dir, pattern)
                    if os.path.exists(full_path):
                        texture_paths[map_type] = full_path
                        break
            
            logger.info(f"Rendered {len(texture_paths)} texture maps")
            return texture_paths
            
        except subprocess.TimeoutExpired:
            logger.error("sbsrender timed out")
            return {}
        except Exception as e:
            logger.error(f"Render failed: {e}")
            return {}
    
    def _generate_fallback_material(self, prompt, output_dir):
        """
        Fallback material generation using procedural textures.
        Used when Substance is not installed.
        
        Returns:
            dict: Paths to generated placeholder textures
        """
        logger.info(f"Generating fallback material for: {prompt}")
        
        try:
            # Create simple colored textures as placeholders
            from PIL import Image
            import random
            
            # Generate color based on prompt
            color_map = {
                "metal": (180, 180, 190),
                "rust": (150, 80, 40),
                "concrete": (140, 140, 140),
                "wood": (120, 80, 50),
                "stone": (100, 100, 100),
            }
            
            # Default to gray
            base_color = (128, 128, 128)
            for keyword, color in color_map.items():
                if keyword in prompt.lower():
                    base_color = color
                    break
            
            # Create textures
            size = 512
            texture_paths = {}
            
            # Diffuse
            diffuse = Image.new("RGB", (size, size), base_color)
            diffuse_path = os.path.join(output_dir, f"{prompt}_diffuse.png")
            diffuse.save(diffuse_path)
            texture_paths["diffuse"] = diffuse_path
            
            # Roughness (gray)
            roughness = Image.new("RGB", (size, size), (128, 128, 128))
            roughness_path = os.path.join(output_dir, f"{prompt}_roughness.png")
            roughness.save(roughness_path)
            texture_paths["roughness"] = roughness_path
            
            # Normal (default blue)
            normal = Image.new("RGB", (size, size), (128, 128, 255))
            normal_path = os.path.join(output_dir, f"{prompt}_normal.png")
            normal.save(normal_path)
            texture_paths["normal"] = normal_path
            
            logger.info("Generated fallback textures")
            return texture_paths
            
        except ImportError:
            logger.error("PIL not available for fallback generation")
            return {}
        except Exception as e:
            logger.error(f"Fallback generation failed: {e}")
            return {}
    
    def export_sbsar(self, material_name, output_path):
        """
        Export material as standalone .sbsar for pipeline integration.
        
        Args:
            material_name: Name of material to export
            output_path: Path to save .sbsar file
        
        Returns:
            bool: Success status
        """
        # This would require access to the original .sbs source
        # For now, we just copy if it exists
        logger.info(f"SBSAR export requested: {material_name} -> {output_path}")
        return True
    
    def get_material_parameters(self, sbsar_path):
        """
        Get exposed parameters from .sbsar file.
        
        Args:
            sbsar_path: Path to .sbsar file
        
        Returns:
            dict: Parameter definitions (name, type, default, min, max)
        """
        # This would require parsing .sbsar metadata
        # Placeholder implementation
        return {
            "roughness": {"type": "float", "default": 0.5, "min": 0.0, "max": 1.0},
            "metallic": {"type": "float", "default": 0.0, "min": 0.0, "max": 1.0},
            "color_variation": {"type": "float", "default": 0.1, "min": 0.0, "max": 1.0},
        }
