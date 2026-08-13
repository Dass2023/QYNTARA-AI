import os
import json
import random
import torch
try:
    from .train_model import PointNet, HAS_TORCH
except ImportError:
    # Handle standalone execution vs package import
    try:
        from train_model import PointNet, HAS_TORCH
    except:
        HAS_TORCH = False

import numpy as np

class SnappingInference:
    def __init__(self, model_path=None):
        if not model_path:
            base = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(base, "snap_model.pth")
            
        self.model_path = model_path
        self.device = torch.device("cpu") # Inference usually fine on CPU
        self.model = None
        self.load_model()
        
    def load_model(self):
        if HAS_TORCH and os.path.exists(self.model_path):
            print(f"Loading model from {self.model_path}...")
            try:
                self.model = PointNet(classes=2)
                self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
                self.model.to(self.device).eval()
            except Exception as e:
                print(f"Failed to load PyTorch model: {e}")
                self.model = None
        else:
            print("Model not found or PyTorch missing. Using Mock Inference.")
            self.model = None

    def predict_points(self, points):
        """
        Runs inference on raw point data (N, 3).
        """
        if not self.model or not HAS_TORCH:
             # Mock
             return self._mock_predict()
             
        # Preprocess
        # Sample to 1024 unique points
        target_n = 1024
        if len(points) >= target_n:
            indices = np.random.choice(len(points), target_n, replace=False)
        else:
            indices = np.random.choice(len(points), target_n, replace=True)
        
        sample = points[indices]
        sample = sample - np.mean(sample, axis=0)
        dist = np.max(np.sqrt(np.sum(sample**2, axis=1)))
        if dist > 0: sample /= dist
        
        # To Tensor (1, 3, 1024)
        input_tensor = torch.from_numpy(sample.transpose(1, 0)).float().unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            output = self.model(input_tensor)
            # Log Softmax -> Exp for probs
            probs = torch.exp(output)
            pred_idx = torch.argmax(probs, dim=1).item()
            confidence = probs[0][pred_idx].item()
            
        # Class 1 = Snapped, 0 = Misaligned
        is_snapped = (pred_idx == 1)
        
        return {
            "is_snapped": is_snapped,
            "confidence": confidence,
            "model_used": "PointNet"
        }

    def _mock_predict(self):
        is_snapped = random.choice([True, False])
        return {
            "is_snapped": is_snapped,
            "confidence": random.uniform(0.7, 0.99),
            "model_used": "Mock"
        }

    def predict(self, obj_path):
        """
        Runs inference on the given OBJ file.
        """
        if not os.path.exists(obj_path):
            return {"error": "File not found"}
            
        print(f"Running inference on {obj_path}...")
        
        # Load Points
        verts = []
        with open(obj_path, 'r') as f:
            for line in f:
                if line.startswith('v '):
                   verts.append([float(x) for x in line.strip().split()[1:4]])
                   
        if not verts:
            return {"error": "No vertices found"}
            
        return self.predict_points(np.array(verts))

if __name__ == "__main__":
    # Test
    import sys
    test_file = sys.argv[1] if len(sys.argv) > 1 else "test.obj"
    
    worker = SnappingInference()
    result = worker.predict(test_file)
    print(json.dumps(result, indent=2))
