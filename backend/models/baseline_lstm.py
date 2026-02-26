"""
Baseline LSTM Model with Bahdanau Attention
CNN encoder + LSTM decoder with attention mechanism.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from .encoder import ImageEncoder


class BahdanauAttention(nn.Module):
    """Bahdanau (additive) attention mechanism."""
    
    def __init__(self, encoder_dim: int, decoder_dim: int, attention_dim: int):
        super(BahdanauAttention, self).__init__()
        
        self.encoder_att = nn.Linear(encoder_dim, attention_dim)
        self.decoder_att = nn.Linear(decoder_dim, attention_dim)
        self.full_att = nn.Linear(attention_dim, 1)
        
    def forward(
        self,
        encoder_out: torch.Tensor,
        decoder_hidden: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            encoder_out: (batch_size, num_pixels, encoder_dim)
            decoder_hidden: (batch_size, decoder_dim)
            
        Returns:
            context: (batch_size, encoder_dim)
            attention_weights: (batch_size, num_pixels)
        """
        # Compute attention scores
        att1 = self.encoder_att(encoder_out)  # (B, num_pixels, attention_dim)
        att2 = self.decoder_att(decoder_hidden).unsqueeze(1)  # (B, 1, attention_dim)
        
        att = self.full_att(torch.tanh(att1 + att2))  # (B, num_pixels, 1)
        att = att.squeeze(2)  # (B, num_pixels)
        
        # Softmax to get attention weights
        alpha = F.softmax(att, dim=1)  # (B, num_pixels)
        
        # Compute context vector
        context = (encoder_out * alpha.unsqueeze(2)).sum(dim=1)  # (B, encoder_dim)
        
        return context, alpha


class LSTMDecoder(nn.Module):
    """LSTM decoder with attention."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        decoder_dim: int = 512,
        attention_dim: int = 512,
        encoder_dim: int = 512,
        dropout: float = 0.5
    ):
        super(LSTMDecoder, self).__init__()
        
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.decoder_dim = decoder_dim
        
        # Embedding layer
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        
        # Attention
        self.attention = BahdanauAttention(encoder_dim, decoder_dim, attention_dim)
        
        # LSTM cell
        self.lstm_cell = nn.LSTMCell(embed_dim + encoder_dim, decoder_dim)
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # Output layers
        self.fc = nn.Linear(decoder_dim, vocab_size)
        
        # Initialize hidden state
        self.init_h = nn.Linear(encoder_dim, decoder_dim)
        self.init_c = nn.Linear(encoder_dim, decoder_dim)
        
    def init_hidden_state(self, encoder_out: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Initialize LSTM hidden state from encoder output.
        
        Args:
            encoder_out: (batch_size, num_pixels, encoder_dim)
            
        Returns:
            h: (batch_size, decoder_dim)
            c: (batch_size, decoder_dim)
        """
        mean_encoder_out = encoder_out.mean(dim=1)  # (B, encoder_dim)
        h = self.init_h(mean_encoder_out)
        c = self.init_c(mean_encoder_out)
        return h, c
    
    def forward(
        self,
        encoder_out: torch.Tensor,
        captions: torch.Tensor,
        caption_lengths: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            encoder_out: (batch_size, num_pixels, encoder_dim)
            captions: (batch_size, max_len)
            caption_lengths: (batch_size,)
            
        Returns:
            predictions: (batch_size, max_len, vocab_size)
            alphas: (batch_size, max_len, num_pixels)
        """
        batch_size = encoder_out.size(0)
        num_pixels = encoder_out.size(1)
        
        # Sort by caption length (descending) for packed sequences
        caption_lengths, sort_idx = caption_lengths.sort(dim=0, descending=True)
        encoder_out = encoder_out[sort_idx]
        captions = captions[sort_idx]
        
        # Embedding
        embeddings = self.embedding(captions)  # (B, max_len, embed_dim)
        
        # Initialize hidden state
        h, c = self.init_hidden_state(encoder_out)
        
        # We won't decode at the <end> position
        decode_lengths = (caption_lengths - 1).tolist()
        max_len = max(decode_lengths)
        
        # Storage
        predictions = torch.zeros(batch_size, max_len, self.vocab_size).to(encoder_out.device)
        alphas = torch.zeros(batch_size, max_len, num_pixels).to(encoder_out.device)
        
        # Teacher forcing
        for t in range(max_len):
            # Determine batch size at this timestep (sequences may have ended)
            batch_size_t = sum([l > t for l in decode_lengths])
            
            # Attention
            context, alpha = self.attention(encoder_out[:batch_size_t], h[:batch_size_t])
            
            # LSTM
            lstm_input = torch.cat([embeddings[:batch_size_t, t, :], context], dim=1)
            h_t, c_t = self.lstm_cell(lstm_input, (h[:batch_size_t], c[:batch_size_t]))
            
            # Output
            preds = self.fc(self.dropout(h_t))
            
            # Store
            predictions[:batch_size_t, t, :] = preds
            alphas[:batch_size_t, t, :] = alpha
            
            # Update hidden state
            h[:batch_size_t] = h_t
            c[:batch_size_t] = c_t
        
        return predictions, alphas


class LSTMCaptioningModel(nn.Module):
    """Baseline CNN + LSTM + Attention model."""
    
    def __init__(
        self,
        vocab_size: int,
        embed_dim: int = 512,
        decoder_dim: int = 512,
        attention_dim: int = 512,
        dropout: float = 0.5,
        pretrained_encoder: bool = True,
        fine_tune_encoder: bool = True,
        fine_tune_layers: int = 2
    ):
        super(LSTMCaptioningModel, self).__init__()
        
        # Encoder
        self.encoder = ImageEncoder(
            embed_dim=embed_dim,
            pretrained=pretrained_encoder,
            fine_tune=fine_tune_encoder,
            fine_tune_layers=fine_tune_layers
        )
        
        # Decoder
        self.decoder = LSTMDecoder(
            vocab_size=vocab_size,
            embed_dim=embed_dim,
            decoder_dim=decoder_dim,
            attention_dim=attention_dim,
            encoder_dim=embed_dim,
            dropout=dropout
        )
        
        self.vocab_size = vocab_size
    
    def forward(
        self,
        images: torch.Tensor,
        captions: torch.Tensor,
        caption_lengths: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            images: (batch_size, 3, H, W)
            captions: (batch_size, max_len)
            caption_lengths: (batch_size,)
            
        Returns:
            predictions: (batch_size, max_len, vocab_size)
            alphas: (batch_size, max_len, num_pixels)
        """
        # Encode
        encoder_out = self.encoder.get_feature_maps_flattened(images)
        
        # Decode
        predictions, alphas = self.decoder(encoder_out, captions, caption_lengths)
        
        return predictions, alphas
