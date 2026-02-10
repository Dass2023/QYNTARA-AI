import torch
from diffusers import StableDiffusionPipeline
import os

class TextToImageGenerator:
    def __init__(self, device="cuda"):
        self.device = device if torch.cuda.is_available() else "cpu"
        self.pipe = None
        print(f"[GenAI] Initializing TextToImageGenerator on {self.device}...")

    def load_model(self):
        if self.pipe is None:
            try:
                print("[GenAI] Loading Stable Diffusion v1-5...")
                # Use v1-5 for better compatibility/speed on typical consumer GPUs
                self.pipe = StableDiffusionPipeline.from_pretrained(
                    "runwayml/stable-diffusion-v1-5", 
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32
                )
                self.pipe.to(self.device)
                # Enable memory efficient attention if available
                try:
                    self.pipe.enable_xformers_memory_efficient_attention()
                except:
                    pass
                print("[GenAI] Stable Diffusion loaded.")
            except Exception as e:
                print(f"[GenAI] Failed to load Stable Diffusion: {e}")
                self.pipe = None

    def generate(self, prompt: str, output_path: str, negative_prompt: str = "") -> str:
        if self.pipe is None:
            self.load_model()
        
        if self.pipe is None:
            print("[GenAI] Model not loaded, skipping image generation.")
            return None

        print(f"[GenAI] Generating Image for: '{prompt}'")
        try:
            image = self.pipe(
                prompt, 
                negative_prompt=negative_prompt,
                num_inference_steps=30,
                guidance_scale=7.5
            ).images[0]
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            image.save(output_path)
            print(f"[GenAI] Image saved to {output_path}")
            return output_path
        except Exception as e:
            print(f"[GenAI] Image generation failed: {e}")
            return None
