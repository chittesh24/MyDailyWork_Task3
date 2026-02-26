"""
Image transformations and augmentations.
"""

import torchvision.transforms as transforms


def get_transforms(mode: str = 'train', image_size: int = 224):
    """
    Get image transformations for training or validation.
    
    Args:
        mode: 'train' or 'val'
        image_size: Target image size
        
    Returns:
        transform: Composed transformations
    """
    # ImageNet normalization statistics
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
    
    if mode == 'train':
        transform = transforms.Compose([
            transforms.Resize((image_size + 32, image_size + 32)),
            transforms.RandomCrop(image_size),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            normalize
        ])
    else:  # val or test
        transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.ToTensor(),
            normalize
        ])
    
    return transform


def denormalize_image(tensor, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]):
    """
    Denormalize image tensor for visualization.
    
    Args:
        tensor: Normalized image tensor (C, H, W)
        mean: Normalization mean
        std: Normalization std
        
    Returns:
        denormalized: Denormalized tensor
    """
    import torch
    
    mean = torch.tensor(mean).view(3, 1, 1)
    std = torch.tensor(std).view(3, 1, 1)
    
    denormalized = tensor * std + mean
    denormalized = torch.clamp(denormalized, 0, 1)
    
    return denormalized
