"""
Vocabulary builder for caption tokenization.
"""

import json
from collections import Counter
from typing import List, Dict
import pickle


class Vocabulary:
    """Build and manage vocabulary for captions."""
    
    # Special tokens
    PAD_TOKEN = '<pad>'
    START_TOKEN = '<start>'
    END_TOKEN = '<end>'
    UNK_TOKEN = '<unk>'
    
    def __init__(self, freq_threshold: int = 5):
        """
        Args:
            freq_threshold: Minimum word frequency to include in vocabulary
        """
        self.freq_threshold = freq_threshold
        
        # Token to index mapping
        self.word2idx = {}
        self.idx2word = {}
        
        # Special token indices
        self.pad_idx = 0
        self.start_idx = 1
        self.end_idx = 2
        self.unk_idx = 3
        
        # Initialize with special tokens
        self._init_special_tokens()
        
    def _init_special_tokens(self):
        """Initialize special tokens."""
        self.word2idx = {
            self.PAD_TOKEN: self.pad_idx,
            self.START_TOKEN: self.start_idx,
            self.END_TOKEN: self.end_idx,
            self.UNK_TOKEN: self.unk_idx
        }
        self.idx2word = {idx: word for word, idx in self.word2idx.items()}
    
    def build_vocabulary(self, captions: List[str]):
        """
        Build vocabulary from list of captions.
        
        Args:
            captions: List of caption strings
        """
        # Count word frequencies
        word_counts = Counter()
        for caption in captions:
            tokens = self.tokenize(caption)
            word_counts.update(tokens)
        
        # Add words above threshold
        idx = len(self.word2idx)
        for word, count in word_counts.items():
            if count >= self.freq_threshold and word not in self.word2idx:
                self.word2idx[word] = idx
                self.idx2word[idx] = word
                idx += 1
        
        print(f"Vocabulary built: {len(self.word2idx)} tokens")
        print(f"Words filtered (freq < {self.freq_threshold}): {len(word_counts) - len(self.word2idx) + 4}")
    
    @staticmethod
    def tokenize(text: str) -> List[str]:
        """
        Tokenize text into words.
        
        Args:
            text: Input text
            
        Returns:
            tokens: List of tokens
        """
        # Lowercase and split
        text = text.lower().strip()
        
        # Remove punctuation and split
        import string
        translator = str.maketrans('', '', string.punctuation)
        text = text.translate(translator)
        
        tokens = text.split()
        return tokens
    
    def encode(self, text: str, add_special_tokens: bool = True) -> List[int]:
        """
        Convert text to token indices.
        
        Args:
            text: Input text
            add_special_tokens: Add <start> and <end> tokens
            
        Returns:
            indices: List of token indices
        """
        tokens = self.tokenize(text)
        
        # Convert to indices
        indices = [self.word2idx.get(token, self.unk_idx) for token in tokens]
        
        # Add special tokens
        if add_special_tokens:
            indices = [self.start_idx] + indices + [self.end_idx]
        
        return indices
    
    def decode(self, indices: List[int], skip_special_tokens: bool = True) -> str:
        """
        Convert token indices to text.
        
        Args:
            indices: List of token indices
            skip_special_tokens: Skip special tokens in output
            
        Returns:
            text: Decoded text
        """
        special_indices = {self.pad_idx, self.start_idx, self.end_idx}
        
        tokens = []
        for idx in indices:
            if skip_special_tokens and idx in special_indices:
                continue
            
            # Stop at end token
            if idx == self.end_idx:
                break
                
            tokens.append(self.idx2word.get(idx, self.UNK_TOKEN))
        
        return ' '.join(tokens)
    
    def __len__(self) -> int:
        """Return vocabulary size."""
        return len(self.word2idx)
    
    def save(self, filepath: str):
        """Save vocabulary to file."""
        vocab_dict = {
            'word2idx': self.word2idx,
            'idx2word': self.idx2word,
            'freq_threshold': self.freq_threshold
        }
        
        if filepath.endswith('.json'):
            with open(filepath, 'w') as f:
                json.dump(vocab_dict, f, indent=2)
        else:
            with open(filepath, 'wb') as f:
                pickle.dump(vocab_dict, f)
        
        print(f"Vocabulary saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'Vocabulary':
        """Load vocabulary from file."""
        if filepath.endswith('.json'):
            with open(filepath, 'r') as f:
                vocab_dict = json.load(f)
        else:
            with open(filepath, 'rb') as f:
                vocab_dict = pickle.load(f)
        
        # Create vocabulary instance
        vocab = cls(freq_threshold=vocab_dict['freq_threshold'])
        vocab.word2idx = vocab_dict['word2idx']
        
        # Convert string keys to int for idx2word
        if filepath.endswith('.json'):
            vocab.idx2word = {int(k): v for k, v in vocab_dict['idx2word'].items()}
        else:
            vocab.idx2word = vocab_dict['idx2word']
        
        print(f"Vocabulary loaded from {filepath}: {len(vocab)} tokens")
        return vocab
