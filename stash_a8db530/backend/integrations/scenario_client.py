import os, time, numpy as np
try:
    import cv2
except ImportError:
    cv2 = None

class ScenarioClient:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
    def generate_pbr_maps(self, prompt: str) -> dict:
        print(f"[Scenario] PBR for: '{prompt}'"); time.sleep(1)
        base = f"scenario_{int(time.time())}"
        for t in ["albedo", "normal", "roughness"]:
            self._dummy(f"backend/data/{base}_{t}.png", t)
        return {k: f"{base}_{k}.png" for k in ["albedo", "normal", "roughness"]}
    def _dummy(self, path, t):
        if not cv2: return
        img = np.zeros((512, 512, 3), dtype=np.uint8)
        if t == "albedo": img[:] = (100, 100, 200)
        elif t == "normal": img[:] = (255, 128, 128)
        else: img[:] = (128, 128, 128)
        cv2.imwrite(path, img)
