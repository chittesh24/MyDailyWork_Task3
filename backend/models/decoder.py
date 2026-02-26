"""
Transformer Decoder for Caption Generation
Implements masked self-attention and cross-attention with image features.
"""

import torch
import torch.nn as nn
import math


class PositionalEncoding(nn.Module):
    """Sinusoidal positional encoding for transformer."""
    
    def __init__(self, embed_dim: int, max_len: int = 5000, dropout: float = 0.1):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        # Create positional encoding matrix
        pe = torch.zeros(max_len, embed_dim)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(
            torch.arange(0, embed_dim, 2).float() * (-math.log(10000.0) / embed_dim)
        )
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)  # (1, max_len, embed_dim)
        
        self.register_buffer('pe', pe)
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: (batch_size, seq_len, embed_dim)
        """
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class TransformerDecoder(nn.Module):
    """
    Transformer decoder with cross-attention to image features.
    """
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        num_heads: int = 8,
        num_layers: int = 6,
        ff_dim: int = 2048,
        dropout: float = 0.1,
        max_seq_len: int = 52
    ):
        """
        Args:
            vocab_size: Size of vocabulary
            embed_dim: Embedding dimension
            num_heads: Number of attention heads
            num_layers: Number of transformer layers
            ff_dim: Feedforward dimension
            dropout: Dropout probability
            max_seq_len: Maximum sequence length
        """
        super(TransformerDecoder, self).__init__()
        
        self.embed_dim = embed_dim
        self.vocab_size = vocab_size
        
        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        
        # Positional encoding
        self.pos_encoding = PositionalEncoding(embed_dim, max_seq_len, dropout)
        
        # Transformer decoder layers
        decoder_layer = nn.TransformerDecoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=ff_dim,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_decoder = nn.TransformerDecoder(
            decoder_layer,
            num_layers=num_layers
        )
        
        # Output projection
        self.fc_out = nn.Linear(embed_dim, vocab_size)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Initialize weights
        self._init_weights()
    
    def _init_weights(self):
        """Initialize weights using Xavier initialization."""
        nn.init.xavier_uniform_(self.token_embedding.weight)
        nn.init.xavier_uniform_(self.fc_out.weight)
        nn.init.constant_(self.fc_out.bias, 0)
    
    def forward(
        self,
        image_features: torch.Tensor,
        captions: torch.Tensor,
        caption_mask: torch.Tensor = None
    ) -> torch.Tensor:
        """
        Args:
            image_features: (batch_size, num_pixels, embed_dim)
            captions: (batch_size, seq_len) - token indices
            caption_mask: (seq_len, seq_len) - causal mask
            
        Returns:
            outputs: (batch_size, seq_len, vocab_size)
        """
        batch_size, seq_len = captions.shape
        
        # Embed tokens
        embedded = self.token_embedding(captions)  # (B, seq_len, embed_dim)
        embedded = self.pos_encoding(embedded)
        
        # Create causal mask if not provided
        if caption_mask is None:
            caption_mask = self._generate_square_subsequent_mask(seq_len).to(captions.device)
        
        # Transformer decoder with cross-attention
        # memory = image_features, tgt = embedded captions
        output = self.transformer_decoder(
            tgt=embedded,
            memory=image_features,
            tgt_mask=caption_mask
        )  # (B, seq_len, embed_dim)
        
        # Project to vocabulary
        output = self.fc_out(output)  # (B, seq_len, vocab_size)
        
        return output
    
    def _generate_square_subsequent_mask(self, sz: int) -> torch.Tensor:
        """
        Generate causal mask to prevent attending to future tokens.
        
        Args:
            sz: Sequence length
            
        Returns:
            mask: (sz, sz)
        """
        mask = torch.triu(torch.ones(sz, sz), diagonal=1).bool()
        return mask
    
    def greedy_decode(
        self,
        image_features: torch.Tensor,
        start_token: int,
        end_token: int,
        max_len: int = 50
    ) -> torch.Tensor:
        """
        Greedy decoding for inference.
        
        Args:
            image_features: (batch_size, num_pixels, embed_dim)
            start_token: Start token index
            end_token: End token index
            max_len: Maximum generation length
            
        Returns:
            captions: (batch_size, seq_len)
        """
        batch_size = image_features.size(0)
        device = image_features.device
        
        # Initialize with start token
        captions = torch.full((batch_size, 1), start_token, dtype=torch.long, device=device)
        
        for _ in range(max_len):
            # Forward pass
            output = self.forward(image_features, captions)  # (B, seq_len, vocab_size)
            
            # Get next token (greedy)
            next_token = output[:, -1, :].argmax(dim=-1, keepdim=True)  # (B, 1)
            
            # Append to captions
            captions = torch.cat([captions, next_token], dim=1)
            
            # Check if all sequences have ended
            if (next_token == end_token).all():
                break
        
        return captions
    
    def beam_search_decode(
        self,
        image_features: torch.Tensor,
        start_token: int,
        end_token: int,
        max_len: int = 50,
        beam_width: int = 5,
        temperature: float = 1.0
    ) -> torch.Tensor:
        """
        Beam search decoding for better quality captions.
        
        Args:
            image_features: (1, num_pixels, embed_dim) - single image
            start_token: Start token index
            end_token: End token index
            max_len: Maximum generation length
            beam_width: Beam width
            temperature: Sampling temperature
            
        Returns:
            best_caption: (seq_len,)
        """
        device = image_features.device
        
        # Initialize beams
        # Each beam: (sequence, score)
        beams = [(torch.tensor([start_token], device=device), 0.0)]
        completed_beams = []
        
        for step in range(max_len):
            candidates = []
            
            for seq, score in beams:
                # Skip if sequence already ended
                if seq[-1].item() == end_token:
                    completed_beams.append((seq, score))
                    continue
                
                # Forward pass
                seq_input = seq.unsqueeze(0)  # (1, seq_len)
                output = self.forward(image_features, seq_input)  # (1, seq_len, vocab_size)
                
                # Get probabilities for next token
                logits = output[0, -1, :] / temperature  # (vocab_size,)
                log_probs = torch.log_softmax(logits, dim=-1)
                
                # Get top-k candidates
                top_log_probs, top_indices = torch.topk(log_probs, beam_width)
                
                for log_prob, token_idx in zip(top_log_probs, top_indices):
                    new_seq = torch.cat([seq, token_idx.unsqueeze(0)])
                    new_score = score + log_prob.item()
                    candidates.append((new_seq, new_score))
            
            # Select top beam_width candidates
            beams = sorted(candidates, key=lambda x: x[1], reverse=True)[:beam_width]
            
            # Early stopping if all beams completed
            if len(beams) == 0:
                break
        
        # Add remaining beams to completed
        completed_beams.extend(beams)
        
        # Select best beam
        if completed_beams:
            best_seq, _ = max(completed_beams, key=lambda x: x[1])
            return best_seq
        else:
            return beams[0][0]
