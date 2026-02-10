import numpy as np
try:
    import cv2
except ImportError:
    cv2 = None

class TextureGenerator:
    def generate(self, prompt: str, output_path: str, width=512, height=512) -> str:
        print(f"[GenAI] Texture for: '{prompt}'")
        if not cv2: return output_path
        img = np.zeros((height, width, 3), dtype=np.uint8)
        np.random.seed(sum([ord(c) for c in prompt]))
        noise = np.random.randint(0, 256, (height, width, 3), dtype=np.uint8)
        blur = cv2.GaussianBlur(noise, (0, 0), sigmaX=15, sigmaY=15)
        tint = np.array([0, 0, 255] if "fire" in prompt else [0, 255, 0] if "grass" in prompt else [200, 200, 200], dtype=np.uint8)
        cv2.imwrite(output_path, cv2.addWeighted(blur, 0.7, np.full_like(blur, tint), 0.3, 0))
        return output_path
