import torch
from diffusers import ShapEPipeline
from diffusers.utils import export_to_ply
import os

class TextTo3DGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[GenAI] Loading Shap-E on {self.device}...")
        try:
            self.pipe = ShapEPipeline.from_pretrained("openai/shap-e", torch_dtype=torch.float16 if self.device == "cuda" else torch.float32)
            self.pipe.to(self.device)
        except Exception as e:
            print(f"[GenAI] Failed to load Shap-E: {e}")
            self.pipe = None

    def generate(self, prompt: str, output_path: str) -> str:
        # Prompt Enhancement: Add quality keywords
        enhanced_prompt = f"{prompt}, high quality, detailed, 3d model, hard surface, clean topology, 4k"
        print(f"[GenAI] Generating 3D for: '{enhanced_prompt}' (Original: '{prompt}')")
        
        if not self.pipe:
            print("[GenAI] Model not loaded, skipping generation.")
            return output_path

        try:
            output = self.pipe(
                enhanced_prompt, 
                guidance_scale=20.0, 
                num_inference_steps=128, 
                frame_size=256,
                output_type="mesh"
            )
            images = output.images
            
            print(f"[GenAI] Output type: {type(images)}")
            if len(images) > 0:
                print(f"[GenAI] First item type: {type(images[0])}")

            mesh_obj = images[0]
            if isinstance(mesh_obj, list):
                print("[GenAI] Unwrapping list...")
                mesh_obj = mesh_obj[0]

            ply_path = output_path.replace(".obj", ".ply")
            export_to_ply(mesh_obj, ply_path)
            
            # For now, we return the PLY path. Ideally we convert PLY to OBJ for broader compatibility if needed,
            # but Three.js can load PLY too. For consistency with the rest of the pipeline expecting OBJ,
            # we might want to convert it, but let's stick to PLY for the raw output first.
            # Or better, let's use Trimesh to convert PLY to OBJ if possible.
            
            import trimesh
            mesh = trimesh.load(ply_path)
            mesh.export(output_path)
            
            return output_path
            
        except Exception as e:
            print(f"[GenAI] Generation failed: {e}")
            return output_path
