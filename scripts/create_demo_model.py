#!/usr/bin/env python3
"""
Create demo model and vocabulary for testing without training.
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
backend_dir = project_root / "backend"
sys.path.insert(0, str(backend_dir))

def create_demo_model():
    """Create demo model checkpoint and vocabulary."""
    
    checkpoints_dir = backend_dir / "checkpoints"
    checkpoints_dir.mkdir(exist_ok=True)
    
    print("\n" + "="*60)
    print("  🤖 CREATING DEMO MODEL")
    print("="*60 + "\n")
    
    # Create vocabulary
    vocab = {
        "<pad>": 0,
        "<start>": 1,
        "<end>": 2,
        "<unk>": 3,
        "a": 4, "the": 5, "in": 6, "on": 7, "of": 8,
        "person": 9, "people": 10, "man": 11, "woman": 12,
        "cat": 13, "dog": 14, "bird": 15,
        "beach": 16, "mountain": 17, "city": 18, "forest": 19,
        "tree": 20, "building": 21, "sky": 22, "water": 23,
        "standing": 24, "sitting": 25, "walking": 26,
        "with": 27, "and": 28, "is": 29, "are": 30,
        "blue": 31, "green": 32, "red": 33, "white": 34,
        "large": 35, "small": 36, "beautiful": 37, "sunny": 38
    }
    
    # Save vocabulary
    vocab_path = checkpoints_dir / "demo_vocab.json"
    with open(vocab_path, 'w') as f:
        json.dump(vocab, f, indent=2)
    print(f"✅ Vocabulary saved: {vocab_path}")
    print(f"   Vocabulary size: {len(vocab)} words")
    
    # Create model config
    model_config = {
        "vocab_size": len(vocab),
        "embed_dim": 512,
        "num_heads": 8,
        "num_layers": 6,
        "ff_dim": 2048,
        "max_seq_len": 50,
        "dropout": 0.1,
        "model_type": "demo",
        "version": "1.0.0"
    }
    
    config_path = checkpoints_dir / "model_config.json"
    with open(config_path, 'w') as f:
        json.dump(model_config, f, indent=2)
    print(f"✅ Model config saved: {config_path}")
    
    # Create a dummy model file (just metadata for demo)
    try:
        import torch
        
        # Create minimal model state
        model_state = {
            'vocab_size': len(vocab),
            'embed_dim': 512,
            'model_type': 'demo',
            'version': '1.0.0'
        }
        
        model_path = checkpoints_dir / "demo_model.pth"
        torch.save(model_state, model_path)
        print(f"✅ Demo model saved: {model_path}")
        
    except ImportError:
        # If torch not available, create a simple JSON file
        model_path = checkpoints_dir / "demo_model.json"
        with open(model_path, 'w') as f:
            json.dump(model_config, f, indent=2)
        print(f"✅ Demo model config saved: {model_path}")
        print("   (PyTorch not installed - using demo predictor)")
    
    print("\n" + "="*60)
    print("  ✅ DEMO MODEL READY")
    print("="*60 + "\n")
    
    return vocab_path, model_path

if __name__ == "__main__":
    try:
        create_demo_model()
    except Exception as e:
        print(f"\n❌ Error creating demo model: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
