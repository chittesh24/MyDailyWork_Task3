"""
Dataset classes for image captioning.
Supports MS COCO and Flickr8k datasets.
"""

import os
import json
from typing import List, Tuple, Dict, Optional
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence

from .vocabulary import Vocabulary
from .transforms import get_transforms


class CaptionDataset(Dataset):
    """Dataset for image captioning."""
    
    def __init__(
        self,
        image_dir: str,
        captions_file: str,
        vocabulary: Vocabulary,
        transform=None,
        max_length: int = 50,
        dataset_type: str = 'coco'  # 'coco' or 'flickr8k'
    ):
        """
        Args:
            image_dir: Directory containing images
            captions_file: Path to captions JSON or CSV file
            vocabulary: Vocabulary instance
            transform: Image transformations
            max_length: Maximum caption length
            dataset_type: Type of dataset ('coco' or 'flickr8k')
        """
        self.image_dir = image_dir
        self.vocabulary = vocabulary
        self.transform = transform
        self.max_length = max_length
        self.dataset_type = dataset_type
        
        # Load captions
        self.data = self._load_captions(captions_file)
        
    def _load_captions(self, captions_file: str) -> List[Dict]:
        """
        Load captions from file.
        
        Returns:
            data: List of {'image_id': str, 'caption': str, 'image_path': str}
        """
        data = []
        
        if self.dataset_type == 'coco':
            # MS COCO format
            with open(captions_file, 'r') as f:
                coco_data = json.load(f)
            
            # Create image_id to filename mapping
            image_map = {img['id']: img['file_name'] for img in coco_data['images']}
            
            # Extract captions
            for ann in coco_data['annotations']:
                image_id = ann['image_id']
                caption = ann['caption']
                image_path = os.path.join(self.image_dir, image_map[image_id])
                
                data.append({
                    'image_id': str(image_id),
                    'caption': caption,
                    'image_path': image_path
                })
        
        elif self.dataset_type == 'flickr8k':
            # Flickr8k format (CSV or text file)
            if captions_file.endswith('.csv'):
                df = pd.read_csv(captions_file)
                for _, row in df.iterrows():
                    image_name = row['image']
                    caption = row['caption']
                    image_path = os.path.join(self.image_dir, image_name)
                    
                    data.append({
                        'image_id': image_name,
                        'caption': caption,
                        'image_path': image_path
                    })
            else:
                # Text file format: image_name.jpg#caption_num\tcaption
                with open(captions_file, 'r') as f:
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) == 2:
                            image_caption_id, caption = parts
                            image_name = image_caption_id.split('#')[0]
                            image_path = os.path.join(self.image_dir, image_name)
                            
                            data.append({
                                'image_id': image_name,
                                'caption': caption,
                                'image_path': image_path
                            })
        
        print(f"Loaded {len(data)} image-caption pairs")
        return data
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor, int]:
        """
        Returns:
            image: Transformed image tensor
            caption: Encoded caption tensor
            caption_length: Length of caption (including special tokens)
        """
        item = self.data[idx]
        
        # Load and transform image
        try:
            image = Image.open(item['image_path']).convert('RGB')
        except Exception as e:
            print(f"Error loading image {item['image_path']}: {e}")
            # Return a black image as fallback
            image = Image.new('RGB', (224, 224), (0, 0, 0))
        
        if self.transform:
            image = self.transform(image)
        
        # Encode caption
        caption_indices = self.vocabulary.encode(item['caption'], add_special_tokens=True)
        
        # Truncate if too long
        if len(caption_indices) > self.max_length:
            caption_indices = caption_indices[:self.max_length-1] + [self.vocabulary.end_idx]
        
        caption = torch.tensor(caption_indices, dtype=torch.long)
        caption_length = len(caption)
        
        return image, caption, caption_length


def collate_fn(batch: List[Tuple], pad_idx: int = 0):
    """
    Custom collate function to pad captions to same length.
    
    Args:
        batch: List of (image, caption, length) tuples
        pad_idx: Padding index
        
    Returns:
        images: (batch_size, 3, H, W)
        captions: (batch_size, max_len) - padded
        lengths: (batch_size,)
    """
    # Sort batch by caption length (descending) for packed sequences
    batch.sort(key=lambda x: x[2], reverse=True)
    
    images, captions, lengths = zip(*batch)
    
    # Stack images
    images = torch.stack(images, dim=0)
    
    # Pad captions
    captions_padded = pad_sequence(
        captions,
        batch_first=True,
        padding_value=pad_idx
    )
    
    # Lengths as tensor
    lengths = torch.tensor(lengths, dtype=torch.long)
    
    return images, captions_padded, lengths


def get_data_loaders(
    train_image_dir: str,
    train_captions_file: str,
    val_image_dir: str,
    val_captions_file: str,
    vocabulary: Vocabulary,
    batch_size: int = 32,
    num_workers: int = 4,
    dataset_type: str = 'coco',
    image_size: int = 224,
    max_length: int = 50
) -> Tuple[DataLoader, DataLoader]:
    """
    Create train and validation data loaders.
    
    Returns:
        train_loader: Training DataLoader
        val_loader: Validation DataLoader
    """
    # Get transforms
    train_transform = get_transforms('train', image_size)
    val_transform = get_transforms('val', image_size)
    
    # Create datasets
    train_dataset = CaptionDataset(
        train_image_dir,
        train_captions_file,
        vocabulary,
        train_transform,
        max_length,
        dataset_type
    )
    
    val_dataset = CaptionDataset(
        val_image_dir,
        val_captions_file,
        vocabulary,
        val_transform,
        max_length,
        dataset_type
    )
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        collate_fn=lambda x: collate_fn(x, vocabulary.pad_idx),
        pin_memory=True
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        collate_fn=lambda x: collate_fn(x, vocabulary.pad_idx),
        pin_memory=True
    )
    
    return train_loader, val_loader
