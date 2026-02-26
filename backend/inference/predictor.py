"""
Inference pipeline for generating captions.
Supports TorchScript export and ONNX optimization.
"""

import torch
import torch.nn as nn
from PIL import Image
from typing import Union, List, Dict
import numpy as np

from models.captioning_model import CaptioningModel
from training.vocabulary import Vocabulary
from training.transforms import get_transforms


class CaptionPredictor:
    """Production-ready caption predictor with optimization support."""
    
    def __init__(
        self,
        model_path: str,
        vocab_path: str,
        device: str = 'cuda' if torch.cuda.is_available() else 'cpu',
        use_torchscript: bool = False
    ):
        """
        Args:
            model_path: Path to model checkpoint
            vocab_path: Path to vocabulary file
            device: Device to run inference on
            use_torchscript: Use TorchScript for faster inference
        """
        self.device = torch.device(device)
        
        # Load vocabulary
        self.vocabulary = Vocabulary.load(vocab_path)
        
        # Load model
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Extract model config
        config = checkpoint.get('model_config', {})
        vocab_size = config.get('vocab_size', len(self.vocabulary))
        embed_dim = config.get('embed_dim', 512)
        
        # Initialize model
        self.model = CaptioningModel(
            vocab_size=vocab_size,
            embed_dim=embed_dim
        )
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model = self.model.to(self.device)
        self.model.eval()
        
        # Optionally convert to TorchScript
        if use_torchscript:
            self.model = torch.jit.script(self.model)
        
        # Image preprocessing
        self.transform = get_transforms('val', image_size=224)
        
    def preprocess_image(self, image: Union[str, Image.Image, np.ndarray]) -> torch.Tensor:
        """
        Preprocess image for model input.
        
        Args:
            image: Image path, PIL Image, or numpy array
            
        Returns:
            tensor: Preprocessed image tensor (1, 3, H, W)
        """
        # Load image if path
        if isinstance(image, str):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image).convert('RGB')
        
        # Apply transforms
        tensor = self.transform(image)
        tensor = tensor.unsqueeze(0)  # Add batch dimension
        
        return tensor
    
    def predict(
        self,
        image: Union[str, Image.Image, np.ndarray],
        method: str = 'beam_search',
        beam_width: int = 5,
        max_length: int = 50,
        temperature: float = 1.0,
        return_probs: bool = False
    ) -> Union[str, Dict]:
        """
        Generate caption for image.
        
        Args:
            image: Input image
            method: 'greedy' or 'beam_search'
            beam_width: Beam width for beam search
            max_length: Maximum caption length
            temperature: Sampling temperature
            return_probs: Return token probabilities
            
        Returns:
            caption: Generated caption string (or dict with probs if return_probs=True)
        """
        # Preprocess
        image_tensor = self.preprocess_image(image).to(self.device)
        
        # Generate
        with torch.no_grad():
            caption_indices = self.model.generate_caption(
                image_tensor,
                start_token=self.vocabulary.start_idx,
                end_token=self.vocabulary.end_idx,
                max_len=max_length,
                method=method,
                beam_width=beam_width,
                temperature=temperature
            )
        
        # Decode
        caption = self.vocabulary.decode(caption_indices.tolist(), skip_special_tokens=True)
        
        if return_probs:
            return {
                'caption': caption,
                'tokens': caption_indices.tolist()
            }
        
        return caption
    
    def predict_batch(
        self,
        images: List[Union[str, Image.Image, np.ndarray]],
        method: str = 'beam_search',
        beam_width: int = 5,
        max_length: int = 50,
        temperature: float = 1.0
    ) -> List[str]:
        """
        Generate captions for multiple images.
        
        Args:
            images: List of images
            method: Decoding method
            beam_width: Beam width
            max_length: Max caption length
            temperature: Sampling temperature
            
        Returns:
            captions: List of caption strings
        """
        captions = []
        
        # Batch processing
        for image in images:
            caption = self.predict(
                image,
                method=method,
                beam_width=beam_width,
                max_length=max_length,
                temperature=temperature
            )
            captions.append(caption)
        
        return captions
    
    def export_torchscript(self, output_path: str):
        """Export model to TorchScript format."""
        scripted_model = torch.jit.script(self.model)
        torch.jit.save(scripted_model, output_path)
        print(f"TorchScript model saved to {output_path}")
    
    def export_onnx(
        self,
        output_path: str,
        image_size: int = 224,
        dynamic_axes: bool = True
    ):
        """
        Export model to ONNX format.
        
        Args:
            output_path: Path to save ONNX model
            image_size: Input image size
            dynamic_axes: Use dynamic batch size
        """
        # Dummy input
        dummy_image = torch.randn(1, 3, image_size, image_size).to(self.device)
        dummy_caption = torch.zeros(1, 10, dtype=torch.long).to(self.device)
        
        # Export
        input_names = ['image', 'caption']
        output_names = ['output']
        
        dynamic_axes_dict = None
        if dynamic_axes:
            dynamic_axes_dict = {
                'image': {0: 'batch_size'},
                'caption': {0: 'batch_size', 1: 'seq_len'},
                'output': {0: 'batch_size', 1: 'seq_len'}
            }
        
        torch.onnx.export(
            self.model,
            (dummy_image, dummy_caption),
            output_path,
            input_names=input_names,
            output_names=output_names,
            dynamic_axes=dynamic_axes_dict,
            opset_version=14
        )
        print(f"ONNX model saved to {output_path}")
    
    def quantize_model(self):
        """Apply dynamic quantization for faster CPU inference."""
        self.model = torch.quantization.quantize_dynamic(
            self.model,
            {nn.Linear},
            dtype=torch.qint8
        )
        print("Model quantized for CPU inference")
