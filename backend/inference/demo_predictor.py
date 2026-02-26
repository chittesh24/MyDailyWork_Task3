"""
Demo predictor that generates captions without a trained model.
Uses random captions from a template for testing.
"""

import random
from typing import Union
from PIL import Image
import numpy as np


class DemoPredictor:
    """Simple demo predictor for testing without a trained model."""
    
    def __init__(self, model_path: str = None, vocab_path: str = None, device: str = 'cpu'):
        """
        Initialize demo predictor.
        
        Args:
            model_path: Not used (for compatibility)
            vocab_path: Not used (for compatibility)
            device: Not used (for compatibility)
        """
        # Pre-defined caption templates
        self.templates = [
            "a {} {} {} {}",
            "a {} is {} in the {}",
            "a {} {} with {} {}",
            "{} {} standing on a {}",
            "a beautiful {} with {} {}",
            "a {} {} near a {}",
        ]
        
        self.subjects = ["person", "man", "woman", "dog", "cat", "bird", "group of people"]
        self.actions = ["standing", "sitting", "walking", "running", "playing"]
        self.locations = ["beach", "park", "street", "forest", "mountain", "field", "city"]
        self.objects = ["tree", "building", "water", "sky", "grass", "road"]
        self.adjectives = ["large", "small", "blue", "green", "sunny", "beautiful", "colorful"]
        
        print("Demo predictor initialized (no model required)")
    
    def predict(
        self,
        image: Union[str, Image.Image, np.ndarray],
        method: str = 'beam_search',
        beam_width: int = 5,
        max_length: int = 50,
        temperature: float = 1.0,
        return_probs: bool = False
    ) -> str:
        """
        Generate a random caption for the image.
        
        Args:
            image: Input image (not used, returns random caption)
            method: Not used (for compatibility)
            beam_width: Not used (for compatibility)
            max_length: Not used (for compatibility)
            temperature: Not used (for compatibility)
            return_probs: Not used (for compatibility)
            
        Returns:
            caption: Generated caption string
        """
        # Validate image exists (if path)
        if isinstance(image, str):
            img = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            img = Image.fromarray(image).convert('RGB')
        else:
            img = image
        
        # For demo purposes, analyze basic image properties
        # This is a very simple heuristic
        img_array = np.array(img)
        avg_color = img_array.mean(axis=(0, 1))
        
        # Generate caption based on dominant color
        if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:  # Blue dominant
            caption = random.choice([
                "a beautiful blue sky over a landscape",
                "a scenic view with clear blue sky",
                "a person standing near water under blue sky",
            ])
        elif avg_color[1] > avg_color[0] and avg_color[1] > avg_color[2]:  # Green dominant
            caption = random.choice([
                "a lush green forest with trees",
                "a person walking in a green park",
                "a beautiful green landscape",
            ])
        elif avg_color[0] > 150 and avg_color[1] > 150 and avg_color[2] > 150:  # Bright/White
            caption = random.choice([
                "a bright sunny day at the beach",
                "a white building in a sunny location",
                "people enjoying a bright sunny day",
            ])
        else:
            # Generate random caption
            template = random.choice(self.templates)
            caption = template.format(
                random.choice(self.subjects),
                random.choice(self.adjectives),
                random.choice(self.actions),
                random.choice(self.locations)
            )
        
        return caption
    
    def predict_batch(self, images, **kwargs):
        """Generate captions for multiple images."""
        return [self.predict(img, **kwargs) for img in images]
