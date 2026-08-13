import torch
import torch.optim as optim
import torch.nn as nn
import os
import argparse
from .models import MeshAnomalyNet
from .dataset import MeshDataset

def train(args):
    # 1. Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on: {device}")
    
    # 2. Data
    train_dataset = MeshDataset(args.dataset_dir, partition='train')
    test_dataset = MeshDataset(args.dataset_dir, partition='test')
    
    if len(train_dataset) == 0:
        print("Error: No training data found. Please run 'create_dataset_*.py' scripts first.")
        return

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=args.batch_size, shuffle=False)
    
    # 3. Model
    model = MeshAnomalyNet().to(device)
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    criterion = nn.BCELoss() # Binary Cross Entropy
    
    # 4. Loop
    model.train()
    best_acc = 0.0
    
    for epoch in range(args.epochs):
        total_loss = 0
        correct = 0
        total = 0
        
        for i, (points, labels) in enumerate(train_loader):
            points, labels = points.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(points)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
            # Calc Accuracy
            predicted = (outputs > 0.5).float()
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
            
        acc = 100 * correct / total
        print(f"Epoch {epoch+1}/{args.epochs} | Loss: {total_loss/len(train_loader):.4f} | Acc: {acc:.2f}%")
        
        # Save Checkpoint
        if acc > best_acc:
            best_acc = acc
            os.makedirs(args.save_dir, exist_ok=True)
            save_path = os.path.join(args.save_dir, 'anomaly_net.pth')
            torch.save(model.state_dict(), save_path)
            print(f"  -> Model saved to {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Default to a 'dataset' folder in root
    base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dataset_path = os.path.join(base_path, 'dataset')
    
    parser.add_argument('--dataset_dir', type=str, default=dataset_path)
    parser.add_argument('--save_dir', type=str, default='weights')
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--epochs', type=int, default=20)
    parser.add_argument('--lr', type=float, default=0.001)
    
    args = parser.parse_args()
    train(args)
