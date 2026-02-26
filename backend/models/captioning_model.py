"""
Complete Image Captioning Model
Combines encoder and decoder with training/inference methods.
"""

import torch
import torch.nn as nn
from .encoder import ImageEncoder
from .decoder import TransformerDecoder


class CaptioningModel(nn.Module):
    """
    End-to-end image captioning model with CNN encoder and Transformer decoder.
    """
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        ff_dim: int = 2048,
        dropout: float = 0.1,
        max_seq_len: int = 52,
        pretrained_encoder: bool = True,
        fine_tune_encoder: bool = True,
        fine_tune_layers: int = 2
    ):
        """
        Args:
            vocab_size: Vocabulary size
            embed_dim: Embedding dimension
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
            ff_dim: Feedforward dimension
            dropout: Dropout probability
            max_seq_len: Maximum sequence length
            pretrained_encoder: Use pretrained encoder
            fine_tune_encoder: Fine-tune encoder
            fine_tune_layers: Number of encoder layers to fine-tune
        """
        super(CaptioningModel, self).__init__()
        
        # Encoder
        self.encoder = ImageEncoder(
            embed_dim=embed_dim,
            pretrained=pretrained_encoder,
            fine_tune=fine_tune_encoder,
            fine_tune_layers=fine_tune_layers
        )
        
        # Decoder
        self.decoder = TransformerDecoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            num_heads=num_heads,
            num_layers=num_layers,
            ff_dim=ff_dim,
            dropout=dropout,
            max_seq_len=max_seq_len
        )
        
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
    
    def forward(
        self,
        images: torch.Tensor,
        captions: torch.Tensor,
        caption_mask: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Forward pass for training.
        
        Args:
            images: (batch_size, 3, H, W)
            captions: (batch_size, seq_len)
            caption_mask: Optional causal mask
            
        Returns:
            output: (batch_size, seq_len, vocab_size)
        """
        # Encode images
        image_features = self.encoder.get_feature_maps_flattened(images)
        
        # Decode captions
        output = self.decoder(image_features, captions, caption_mask)
        
        return output
    
    def generate_caption(
        self,
        image: torch.Tensor,
        start_token: int,
        end_token: int,
        max_len: int = 50,
        method: str = 'beam_search',
        beam_width: int = 5,
        temperature: float = 1.0
    ) -> torch.Tensor:
        """
        Generate caption for a single image.
        
        Args:
            image: (1, 3, H, W) or (3, H, W)
            start_token: Start token index
            end_token: End token index
            max_len: Maximum caption length
            method: 'greedy' or 'beam_search'
            beam_width: Beam width for beam search
            temperature: Temperature for sampling
            
        Returns:
            caption: (seq_len,) token indices
        """
        self.eval()
        
        with torch.no_grad():
            # Add batch dimension if needed
            if image.dim() == 3:
                image = image.unsqueeze(0)
            
            # Encode image
            image_features = self.encoder.get_feature_maps_flattened(image)
            
            # Generate caption
            if method == 'greedy':
                captions = self.decoder.greedy_decode(
                    image_features, start_token, end_token, max_len
                )
                return captions[0]  # Return first (and only) caption
            
            elif method == 'beam_search':
                caption = self.decoder.beam_search_decode(
                    image_features, start_token, end_token, max_len, beam_width, temperature
                )
                return caption
            
            else:
                raise ValueError(f"Unknown decoding method: {method}")
    
    def get_trainable_parameters(self):
        """Get trainable parameters with separate encoder/decoder groups."""
        encoder_params = []
        decoder_params = []
        
        for name, param in self.named_parameters():
            if param.requires_grad:
                if 'encoder' in name:
                    encoder_params.append(param)
                else:
                    decoder_params.append(param)
        
        return {
            'encoder': encoder_params,
            'decoder': decoder_params
        }
