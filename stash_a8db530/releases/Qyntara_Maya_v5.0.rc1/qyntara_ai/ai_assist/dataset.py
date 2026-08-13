import torch
from torch.utils.data import Dataset
import os
import glob
import numpy as np

class MeshDataset(Dataset):
    """
    Loads 3D meshes (OBJ) and converts them to Point Clouds for training.
    Assumes directory structure:
    /dataset
        /clean  (Label 0)
        /anomalous (Label 1)
    """
    def __init__(self, root_dir, num_points=1024, partition='train'):
        self.root_dir = root_dir
        self.num_points = num_points
        self.partition = partition
        
        self.clean_files = glob.glob(os.path.join(root_dir, 'clean', '*.obj'))
        self.anomaly_files = glob.glob(os.path.join(root_dir, 'anomalous', '*.obj'))
        
        # Simple split logic (80/20)
        split_idx_clean = int(len(self.clean_files) * 0.8)
        split_idx_anomaly = int(len(self.anomaly_files) * 0.8)
        
        if partition == 'train':
            self.clean_files = self.clean_files[:split_idx_clean]
            self.anomaly_files = self.anomaly_files[:split_idx_anomaly]
        else:
            self.clean_files = self.clean_files[split_idx_clean:]
            self.anomaly_files = self.anomaly_files[split_idx_anomaly:]
            
        self.all_files = self.clean_files + self.anomaly_files
        self.labels = [0]*len(self.clean_files) + [1]*len(self.anomaly_files)
        
        print(f"Loaded {len(self.all_files)} files for {partition} (Clean: {len(self.clean_files)}, Anomaly: {len(self.anomaly_files)})")

    def __len__(self):
        return len(self.all_files)

    def __getitem__(self, idx):
        file_path = self.all_files[idx]
        label = self.labels[idx]
        
        # Load Mesh (Simple OBJ parser for dependency-free operation)
        vertices = []
        try:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.startswith('v '):
                        parts = line.strip().split()
                        vertices.append([float(parts[1]), float(parts[2]), float(parts[3])])
        except Exception as e:
            # Fallback for empty/corrupt files
            vertices = [[0,0,0]]
            
        if not vertices:
             vertices = [[0,0,0]]
             
        # Normalize to Point Cloud
        pc = self._normalize_pc(vertices, self.num_points)
        
        # Transpose for PointNet: (N, 3) -> (3, N)
        pc = pc.transpose(1, 0)
        
        return torch.from_numpy(pc).float(), torch.tensor([label]).float()

    def _normalize_pc(self, points, num_points):
        points = np.array(points)
        
        if len(points) == 0:
             return np.zeros((num_points, 3))
             
        # Center
        centroid = np.mean(points, axis=0)
        points -= centroid
        
        # Scale
        max_dist = np.max(np.sqrt(np.sum(points**2, axis=1)))
        if max_dist > 0:
            points /= max_dist
            
        # Resample
        if len(points) >= num_points:
            choice = np.random.choice(len(points), num_points, replace=False)
        else:
            choice = np.random.choice(len(points), num_points, replace=True)
            
        return points[choice]
