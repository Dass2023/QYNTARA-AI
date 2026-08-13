import torch
from diffusers import ShapEImg2ImgPipeline
from diffusers.utils import export_to_ply
from PIL import Image
import os

class ImageTo3DGenerator:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[GenAI] Loading Shap-E Image-to-3D on {self.device}...")
        try:
            self.pipe = ShapEImg2ImgPipeline.from_pretrained("openai/shap-e-img2img", torch_dtype=torch.float16 if self.device == "cuda" else torch.float32)
            self.pipe.to(self.device)
        except Exception as e:
            print(f"[GenAI] Failed to load Shap-E Img2Img: {e}")
            self.pipe = None

    def generate(self, image_path: str, output_path: str) -> dict:
        print(f"[GenAI] Generating 3D from image: {image_path}")
        
        if not self.pipe:
            print("[GenAI] Model not loaded, skipping generation.")
            return {"status": "failed", "error": "Model not loaded"}

        try:
            image = Image.open(image_path)
            
            # Handle RGBA (transparency) by compositing on white background
            if image.mode == 'RGBA':
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[3])
                image = background
            else:
                image = image.convert("RGB")
                
            # Resize to 256x256 as expected by Shap-E
            image = image.resize((256, 256))

            images = self.pipe(
                image, 
                guidance_scale=3.0, 
                num_inference_steps=64, 
                frame_size=256,
            ).images

            ply_path = output_path.replace(".obj", ".ply")
            export_to_ply(images[0], ply_path)
            
            # Convert PLY to OBJ using Trimesh
            import trimesh
            mesh = trimesh.load(ply_path)
            mesh.export(output_path)
            
            return {"status": "success", "output_path": output_path}
            
        except Exception as e:
            print(f"[GenAI] Generation failed: {e}")
            return {"status": "failed", "error": str(e)}
