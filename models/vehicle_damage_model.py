import torch
import torch.nn as nn
from torchvision.models import resnet18, ResNet18_Weights

class VehicleDamageCNN(nn.Module):
    """
    PyTorch ResNet-18 Transfer Learning Architecture for Vehicle Damage Classification.
    Classifies vehicle images into 2 classes:
      0: 00-damage (Damaged)
      1: 01-whole  (Whole)
    """
    def __init__(self, num_classes=2, pretrained=True):
        super(VehicleDamageCNN, self).__init__()
        # Load ResNet-18 with default ImageNet pretrained weights if requested
        weights = ResNet18_Weights.DEFAULT if pretrained else None
        self.model = resnet18(weights=weights)
        
        # Replace the final fully-connected (fc) layer with 2 output logits
        in_features = self.model.fc.in_features
        self.model.fc = nn.Linear(in_features, num_classes)

    def forward(self, x):
        return self.model(x)

def get_model(num_classes=2, pretrained=True):
    """
    Factory function to instantiate and return the model.
    """
    model = VehicleDamageCNN(num_classes=num_classes, pretrained=pretrained)
    return model
