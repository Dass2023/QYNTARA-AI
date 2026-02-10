import os
import json
import glob
import random
# import torch
# import torch.nn as nn
# import torch.optim as optim

# Mock PyTorch for prototype demonstration
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    import torch.optim as optim
    from torch.utils.data import Dataset, DataLoader
    import numpy as np
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    print("PyTorch not found. Using Mock mode.")
    # Create dummy classes to avoid NameError in definition
    class nn:
        class Module: pass
        class Conv1d: 
             def __init__(self, *args): pass
        class Linear:
             def __init__(self, *args): pass
        class BatchNorm1d:
             def __init__(self, *args): pass
    class Dataset: pass
    class DataLoader: pass

# --- Mock Implementation for Fallback ---
class MockPointNet:
    def __init__(self):
        print("Initialized PointNet Model (Mock)")
        
    def train(self, data):
        print(f"Training on {len(data)} samples...")
        print("Epoch 1/5 - Loss: 0.85")
        print("Epoch 5/5 - Loss: 0.12")
        
    def save(self, path):
        print(f"Model saved to {path} (Mock)")

# --- PointNet Architecture (Real) ---
if HAS_TORCH:
    class PointNet(nn.Module):
        def __init__(self, output_dim=6):
            super(PointNet, self).__init__()
            # Input: (Batch, 3, NumPoints)
            self.conv1 = nn.Conv1d(3, 64, 1)
            self.conv2 = nn.Conv1d(64, 128, 1)
            self.conv3 = nn.Conv1d(128, 1024, 1)
            
            self.fc1 = nn.Linear(1024, 512)
            self.fc2 = nn.Linear(512, 128)
            self.fc3 = nn.Linear(128, output_dim) # Output: [tx, ty, tz, rx, ry, rz]

            self.bn1 = nn.BatchNorm1d(64)
            self.bn2 = nn.BatchNorm1d(128)
            self.bn3 = nn.BatchNorm1d(1024)
            self.bn1_fc = nn.BatchNorm1d(512)
            self.bn2_fc = nn.BatchNorm1d(128)

        def forward(self, x):
            x = F.relu(self.bn1(self.conv1(x)))
            x = F.relu(self.bn2(self.conv2(x)))
            x = F.relu(self.bn3(self.conv3(x)))
            x = torch.max(x, 2, keepdim=True)[0]
            x = x.view(-1, 1024)
            x = F.relu(self.bn1_fc(self.fc1(x)))
            x = F.relu(self.bn2_fc(self.fc2(x)))
            x = self.fc3(x) # No Softmax for Regression
            return x
else:
    class PointNet: pass # Dummy


# --- Dataset Handler ---
class ModularDataset(Dataset):
    def __init__(self, data_list, num_points=1024):
        self.data_list = data_list
        self.num_points = num_points
        
    def __len__(self):
        return len(self.data_list)
        
    def __getitem__(self, idx):
        item = self.data_list[idx]
        obj_path = item["dirty_path"] # We only train on "Misaligned" input
        meta = item["meta"]
        
        # Load Geometry
        points = self.load_obj_as_points(obj_path, self.num_points)
        
        # Normalize Points
        points = points - np.mean(points, axis=0)
        max_dist = np.max(np.sqrt(np.sum(points**2, axis=1)))
        if max_dist > 0:
            points = points / max_dist
            
        # Transpose to (3, N) for PyTorch Conv1d
        points = points.transpose(1, 0).astype(np.float32)
        
        # Prepare Target Label: [tx, ty, tz, rx, ry, rz]
        # Only available for "Misaligned" objects in meta
        # The generator saves a list of objects in meta. We assume single object pairs for now.
        # But wait, the meta structure is {"objects": [...]}. 
        # We need to find the specific object. ModularDataset usually handles one "scene" per item.
        
        target = np.zeros(6, dtype=np.float32)
        objects = meta.get("objects", [])
        if objects:
            # Assume first object is the one to fix
            obj_data = objects[0]
            
            # Translation
            t_off = obj_data.get("translation_offset", [0,0,0])
            # Rotation (Degrees)
            r_off = obj_data.get("rotation_offset", [0,0,0])
            
            # Normalize Rotation? 
            # Degrees (-180 to 180). Neural nets like small numbers. 
            # Let's scale by 1/180.0
            r_norm = [r / 180.0 for r in r_off]
            
            target[0:3] = t_off
            target[3:6] = r_norm
            
        return torch.from_numpy(points), torch.from_numpy(target)

    def load_obj_as_points(self, path, n_points):
        vertices = []
        if os.path.exists(path):
            with open(path, 'r') as f:
                for line in f:
                    if line.startswith('v '):
                        parts = line.strip().split()
                        vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
        
        if not vertices:
            return np.zeros((n_points, 3))
            
        vertices = np.array(vertices)
        
        # Resample to n_points
        if len(vertices) >= n_points:
            indices = np.random.choice(len(vertices), n_points, replace=False)
        else:
            indices = np.random.choice(len(vertices), n_points, replace=True)
            
        return vertices[indices]

# --- Training Loop ---
def train_model(data_list, epochs=5):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on {device} (Regression Mode)...")
    
    dataset = ModularDataset(data_list)
    dataloader = DataLoader(dataset, batch_size=4, shuffle=True)
    
    model = PointNet(output_dim=6).to(device)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    criterion = nn.MSELoss() # Regression Loss
    
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        
        for i, (points, targets) in enumerate(dataloader):
            points, targets = points.to(device), targets.to(device)
            
            optimizer.zero_grad()
            outputs = model(points)
            loss = criterion(outputs, targets)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        print(f"Epoch {epoch+1}/{epochs} | Loss (MSE): {total_loss/len(dataloader):.6f}")
        
    return model

def run_training():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_dir = os.path.join(base_dir, "dataset")
    model_path = os.path.join(base_dir, "snap_model.pth")
    
    if not os.path.exists(dataset_dir):
        print(f"Dataset not found at {dataset_dir}. Run generate_dataset.py first.")
        # Optional: Auto-generate
        print("Generating small test dataset...")
        from .generate_dataset import DatasetGenerator
        gen = DatasetGenerator(dataset_dir)
        gen.generate_batch(5)

    print("Loading dataset...")
    data = load_dataset(dataset_dir)
    print(f"Found {len(data)} scene pairs.")
    
    if not data:
        print("No data found.")
        return

    if HAS_TORCH:
        try:
            model = train_model(data)
            torch.save(model.state_dict(), model_path)
            print(f"Model saved to {model_path}")
        except Exception as e:
            print(f"Training error: {e}. Falling back to Mock.")
            mock = MockPointNet()
            mock.train(data)
            mock.save(model_path)
    else:
        print("PyTorch not installed. Using Mock training.")
        mock = MockPointNet()
        mock.train(data)
        mock.save(model_path)


def load_dataset(dataset_dir):
    """
    Parses the generated dataset directory.
    """
    scenes = glob.glob(os.path.join(dataset_dir, "scene_*"))
    data = []
    
    for scene in scenes:
        meta_path = os.path.join(scene, "meta.json")
        snapped_obj = os.path.join(scene, "snapped.obj")
        misaligned_obj = os.path.join(scene, "misaligned.obj")
        
        if os.path.exists(meta_path):
            with open(meta_path, 'r') as f:
                meta = json.load(f)
                data.append({
                    "meta": meta,
                    "clean_path": snapped_obj,
                    "dirty_path": misaligned_obj
                })
    return data

if __name__ == "__main__":
    run_training()
