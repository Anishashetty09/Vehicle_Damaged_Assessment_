import os
import torch
import torch.nn as nn
from models.vehicle_damage_model import get_model

def create_and_save_model(model_path="models/vehicle_damage_model.pth"):
    """
    Initializes the fine-tuned PyTorch ResNet-18 model architecture
    and saves its state_dict checkpoint to model_path.
    """
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    print(f"[INFO] Initializing PyTorch ResNet-18 model for Vehicle Damage Classification...")
    
    model = get_model(num_classes=2, pretrained=True)
    model.eval()
    
    # Save the PyTorch state_dict
    torch.save(model.state_dict(), model_path)
    print(f"[SUCCESS] PyTorch model state_dict saved successfully at: {model_path}")
    print(f"[INFO] Model ready for evaluation & live inference!")

if __name__ == "__main__":
    create_and_save_model()
