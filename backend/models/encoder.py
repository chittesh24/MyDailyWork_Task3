"""
ResNet50-based Image Encoder
Extracts spatial feature maps from images and projects to embedding dimension.
"""

import torch
import torch.nn as nn
import torchvision.models as models


class ImageEncoder(nn.Module):
    """
    CNN encoder using ResNet50 pretrained on ImageNet.
    Removes classification head and extracts spatial features.
    """
    
    def __init__(
        self,
        embed_dim: int = 512,
        pretrained: bool = True,
        fine_tune: bool = True,
        fine_tune_layers: int = 2
    ):
        """
        Args:
            embed_dim: Dimension of output embeddings
            pretrained: Use ImageNet pretrained weights
            fine_tune: Whether to fine-tune encoder
            fine_tune_layers: Number of final layers to fine-tune (0-4)
        """
        super(ImageEncoder, self).__init__()
        
        # Load ResNet50
        resnet = models.resnet50(pretrained=pretrained)
        
        # Remove avgpool and fc layers to get spatial features
        modules = list(resnet.children())[:-2]  # Keep until layer4
        self.resnet = nn.Sequential(*modules)
        
        # Feature map will be (batch, 2048, H/32, W/32) for ResNet50
        self.feature_dim = 2048
        
        # Project to embedding dimension
        self.projection = nn.Sequential(
            nn.Conv2d(self.feature_dim, embed_dim, kernel_size=1),
            nn.ReLU(),
            nn.Dropout(0.5)
        )
        
        # Freeze layers
        self._freeze_layers(fine_tune, fine_tune_layers)
        
        self.embed_dim = embed_dim
        
    def _freeze_layers(self, fine_tune: bool, fine_tune_layers: int):
        """Freeze early layers, optionally fine-tune final layers."""
        if not fine_tune:
            for param in self.resnet.parameters():
                param.requires_grad = False
        else:
            # Freeze all first
            for param in self.resnet.parameters():
                param.requires_grad = False
                
            # Unfreeze last N layers
            # ResNet structure: conv1, bn1, relu, maxpool, layer1-4
            layers = [self.resnet[-1]]  # layer4
            if fine_tune_layers > 1:
                layers.append(self.resnet[-2])  # layer3
            if fine_tune_layers > 2:
                layers.append(self.resnet[-3])  # layer2
            if fine_tune_layers > 3:
                layers.append(self.resnet[-4])  # layer1
                
            for layer in layers:
                for param in layer.parameters():
                    param.requires_grad = True
    
    def forward(self, images: torch.Tensor) -> torch.Tensor:
        """
        Args:
            images: (batch_size, 3, H, W)
            
        Returns:
            features: (batch_size, embed_dim, grid_h, grid_w)
        """
        # Extract spatial features
        features = self.resnet(images)  # (B, 2048, H/32, W/32)
        
        # Project to embedding dimension
        features = self.projection(features)  # (B, embed_dim, H/32, W/32)
        
        return features
    
    def get_feature_maps_flattened(self, images: torch.Tensor) -> torch.Tensor:
        """
        Get flattened spatial features for attention mechanisms.
        
        Args:
            images: (batch_size, 3, H, W)
            
        Returns:
            features: (batch_size, num_pixels, embed_dim)
        """
        features = self.forward(images)  # (B, embed_dim, H, W)
        batch_size, embed_dim, h, w = features.shape
        
        # Reshape to (B, num_pixels, embed_dim)
        features = features.permute(0, 2, 3, 1)  # (B, H, W, embed_dim)
        features = features.view(batch_size, h * w, embed_dim)
        
        return features
