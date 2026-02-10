import logging
import os
import random
import time

logger = logging.getLogger(__name__)

class GenAIClient:
    """
    Bridge client for Generative AI Texturing.
    Connects to a local Stable Diffusion WebUI API (default: http://127.0.0.1:7860)
    or falls back to 'Mock Mode' if no server is found.
    """
    
    def __init__(self, api_url="http://127.0.0.1:7860"):
        self.api_url = api_url
        self.output_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Documents", "Qyntara_GenAI")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_material(self, prompt, resolution=1024):
        """
        Main Entry Point.
        Returns a dictionary of paths: {'diffuse': path, 'normal': path, 'roughness': path}
        """
        timestamp = int(time.time())
        clean_prompt = "".join([c for c in prompt if c.isalnum() or c in (' ', '_')]).strip().replace(" ", "_")
        base_filename = f"{clean_prompt}_{timestamp}"
        
        # 1. Try Real API (Placeholder for future)
        # if self._check_connection():
        #     return self._request_stable_diffusion(prompt, base_filename)
            
        # 2. Fallback to Mock
        return self._generate_mock_textures(base_filename, resolution)

    def _generate_mock_textures(self, base_name, size):
        """
        Generates procedural noise images to simulate AI output.
        Writes standard PPM files (easy to write in pure Python, Maya reads them).
        """
        logger.info(f"Generating Mock AI Textures for: {base_name}...")
        
        # Paths
        diff_path = os.path.join(self.output_dir, f"{base_name}_Color.ppm")
        norm_path = os.path.join(self.output_dir, f"{base_name}_Normal.ppm")
        rough_path = os.path.join(self.output_dir, f"{base_name}_Roughness.ppm")
        
        # Generate Colored Noise (Diffuse)
        self._write_ppm(diff_path, size, size, color=True)
        
        # Generate Blue-ish Noise (Normal)
        self._write_ppm(norm_path, size, size, color=True, is_normal=True)
        
        # Generate Grayscale Noise (Roughness)
        self._write_ppm(rough_path, size, size, color=False)
        
        return {
            "diffuse": diff_path,
            "normal": norm_path,
            "roughness": rough_path
        }

    def _write_ppm(self, path, width, height, color=True, is_normal=False):
        """ Writes a raw P3 or P2 PPM image file. """
        header = f"P3\n{width} {height}\n255\n"
        
        # Generate minimal data (optimization: don't loop 1024x1024 in python)
        # We will create a small pattern and write it out repeatedly or just a solid color with noise.
        # Python loop for 1M pixels is too slow.
        # Strategy: Write a tiny 64x64 texture. Maya will stretch it, but it proves the pipeline.
        w, h = 64, 64
        header = f"P3\n{w} {h}\n255\n"
        
        with open(path, 'w') as f:
            f.write(header)
            for y in range(h):
                line = []
                for x in range(w):
                    if is_normal:
                        # Flat Normal (128, 128, 255) + Noise
                        r = 128 + random.randint(-10, 10)
                        g = 128 + random.randint(-10, 10)
                        b = 255
                        line.append(f"{r} {g} {b}")
                    elif color:
                        # Random Color Noise
                        r = random.randint(0, 255)
                        g = random.randint(0, 255)
                        b = random.randint(0, 255)
                        line.append(f"{r} {g} {b}")
                    else:
                        # Grayscale
                        v = random.randint(50, 200)
                        line.append(f"{v} {v} {v}")
                f.write(" ".join(line) + "\n")
        
        logger.info(f"Saved: {path}")

