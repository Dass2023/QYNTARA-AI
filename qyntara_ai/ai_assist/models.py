import torch
import torch.nn as nn
import torch.nn.functional as F

class MeshAnomalyNet(nn.Module):
    """
    A simplified PointNet-like architecture for detecting geometric anomalies 
    in 3D mesh vertex data.
    
    Input: (Batch, 3, Num_Points)
    Output: (Batch, 1) - Anomaly Score (0=Good, 1=Bad)
    """
    def __init__(self, num_points=1024):
        super(MeshAnomalyNet, self).__init__()
        
        # Encoder (Point features)
        self.conv1 = nn.Conv1d(3, 64, 1)
        self.conv2 = nn.Conv1d(64, 128, 1)
        self.conv3 = nn.Conv1d(128, 1024, 1)
        
        self.bn1 = nn.BatchNorm1d(64)
        self.bn2 = nn.BatchNorm1d(128)
        self.bn3 = nn.BatchNorm1d(1024)
        
        # Decoder / Classifier
        self.fc1 = nn.Linear(1024, 512)
        self.fc2 = nn.Linear(512, 256)
        self.fc3 = nn.Linear(256, 1) # Probability of anomaly
        
        self.dropout = nn.Dropout(p=0.3)
        self.bn_fc1 = nn.BatchNorm1d(512)
        self.bn_fc2 = nn.BatchNorm1d(256)

    def forward(self, x):
        # x shape: [Batch, 3, N]
        
        # Local Feature Extraction
        x = F.relu(self.bn1(self.conv1(x)))
        x = F.relu(self.bn2(self.conv2(x)))
        x = F.relu(self.bn3(self.conv3(x)))
        
        # Global Feature Aggregation (Max Pooling)
        x = torch.max(x, 2, keepdim=True)[0]
        x = x.view(-1, 1024)
        
        # Classification
        x = F.relu(self.bn_fc1(self.fc1(x)))
        x = self.dropout(x)
        x = F.relu(self.bn_fc2(self.fc2(x)))
        x = self.dropout(x)
        x = torch.sigmoid(self.fc3(x))
        
        return x

def get_model():
    return MeshAnomalyNet()
