"""
Python training script for MS COCO dataset with automated setup.
More flexible than shell script, works on Windows/Linux/Mac.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))


def download_coco_dataset(data_dir: Path):
    """Download MS COCO dataset."""
    print("\n" + "="*50)
    print("Downloading MS COCO 2017 Dataset")
    print("="*50)
    
    data_dir.mkdir(parents=True, exist_ok=True)
    
    urls = {
        'train_images': 'http://images.cocodataset.org/zips/train2017.zip',
        'val_images': 'http://images.cocodataset.org/zips/val2017.zip',
        'annotations': 'http://images.cocodataset.org/annotations/annotations_trainval2017.zip'
    }
    
    for name, url in urls.items():
        filename = url.split('/')[-1]
        filepath = data_dir / filename
        
        if filepath.exists():
            print(f"✅ {filename} already downloaded")
            continue
        
        print(f"\nDownloading {name} ({filename})...")
        print(f"URL: {url}")
        
        # Use wget or curl
        try:
            subprocess.run(['wget', '-c', url, '-O', str(filepath)], check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            try:
                subprocess.run(['curl', '-C', '-', '-o', str(filepath), url], check=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"❌ Failed to download {filename}")
                print("Please install wget or curl, or download manually from:")
                print(f"  {url}")
                return False
    
    # Extract files
    print("\nExtracting files...")
    import zipfile
    
    for filename in ['train2017.zip', 'val2017.zip', 'annotations_trainval2017.zip']:
        filepath = data_dir / filename
        if filepath.exists():
            print(f"Extracting {filename}...")
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(data_dir)
            print(f"✅ Extracted {filename}")
    
    print("\n✅ Dataset ready!")
    return True


def build_vocabulary(captions_file: Path, vocab_file: Path, freq_threshold: int = 5):
    """Build vocabulary from captions."""
    print("\n" + "="*50)
    print("Building Vocabulary")
    print("="*50)
    
    from training.vocabulary import Vocabulary
    
    # Load captions
    with open(captions_file, 'r') as f:
        data = json.load(f)
    
    captions = [ann['caption'] for ann in data['annotations']]
    print(f"Total captions: {len(captions):,}")
    
    # Build vocabulary
    vocab = Vocabulary(freq_threshold=freq_threshold)
    vocab.build_vocabulary(captions)
    
    # Save
    vocab.save(str(vocab_file))
    print(f"✅ Vocabulary saved: {vocab_file}")
    print(f"   Vocabulary size: {len(vocab):,} tokens")
    
    return vocab


def train_model(args):
    """Run training."""
    print("\n" + "="*50)
    print("Training Image Captioning Model")
    print("="*50)
    
    from training.train import main as train_main
    
    # Override sys.argv for argparse
    sys.argv = [
        'train.py',
        '--train_image_dir', str(args.data_dir / 'train2017'),
        '--train_captions', str(args.data_dir / 'annotations' / 'captions_train2017.json'),
        '--val_image_dir', str(args.data_dir / 'val2017'),
        '--val_captions', str(args.data_dir / 'annotations' / 'captions_val2017.json'),
        '--dataset_type', 'coco',
        '--vocab_path', str(args.checkpoint_dir / 'vocab.json'),
        '--checkpoint_dir', str(args.checkpoint_dir),
        '--batch_size', str(args.batch_size),
        '--num_epochs', str(args.num_epochs),
        '--learning_rate', str(args.learning_rate),
        '--encoder_lr', str(args.encoder_lr),
        '--device', args.device,
        '--num_workers', str(args.num_workers),
        '--seed', str(args.seed),
        '--gradient_clip', '5.0',
        '--scheduler', 'plateau',
        '--early_stopping', '5',
        '--log_interval', '100'
    ]
    
    if args.fine_tune_encoder:
        sys.argv.extend(['--fine_tune_encoder', '--fine_tune_layers', '2'])
    
    if args.use_amp:
        sys.argv.append('--use_amp')
    
    # Run training
    train_main()


def main():
    parser = argparse.ArgumentParser(description='Train MS COCO Image Captioning Model')
    
    # Paths
    parser.add_argument('--data_dir', type=Path, default=Path('./data/coco'),
                       help='Directory for dataset')
    parser.add_argument('--checkpoint_dir', type=Path, default=Path('./checkpoints/coco'),
                       help='Directory for checkpoints')
    
    # Training parameters
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--num_epochs', type=int, default=20)
    parser.add_argument('--learning_rate', type=float, default=3e-4)
    parser.add_argument('--encoder_lr', type=float, default=1e-4)
    parser.add_argument('--device', type=str, default='cuda', choices=['cuda', 'cpu'])
    parser.add_argument('--num_workers', type=int, default=4)
    parser.add_argument('--seed', type=int, default=42)
    
    # Model options
    parser.add_argument('--fine_tune_encoder', action='store_true', default=True)
    parser.add_argument('--use_amp', action='store_true', default=True,
                       help='Use mixed precision training')
    
    # Dataset options
    parser.add_argument('--download', action='store_true',
                       help='Download dataset if not present')
    parser.add_argument('--vocab_threshold', type=int, default=5,
                       help='Minimum word frequency for vocabulary')
    
    args = parser.parse_args()
    
    print("="*50)
    print("MS COCO Image Captioning Training")
    print("="*50)
    print(f"\nConfiguration:")
    print(f"  Data directory: {args.data_dir}")
    print(f"  Checkpoint directory: {args.checkpoint_dir}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Epochs: {args.num_epochs}")
    print(f"  Learning rate: {args.learning_rate}")
    print(f"  Device: {args.device}")
    print(f"  Mixed precision: {args.use_amp}")
    
    # Create directories
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    # Step 1: Check/download dataset
    train_dir = args.data_dir / 'train2017'
    val_dir = args.data_dir / 'val2017'
    annotations_dir = args.data_dir / 'annotations'
    
    if not (train_dir.exists() and val_dir.exists() and annotations_dir.exists()):
        if args.download:
            if not download_coco_dataset(args.data_dir):
                print("\n❌ Failed to download dataset")
                return
        else:
            print("\n❌ Dataset not found!")
            print(f"Expected directories:")
            print(f"  - {train_dir}")
            print(f"  - {val_dir}")
            print(f"  - {annotations_dir}")
            print("\nRun with --download to download automatically, or download manually.")
            return
    else:
        print("\n✅ Dataset found")
    
    # Step 2: Build vocabulary
    vocab_file = args.checkpoint_dir / 'vocab.json'
    if not vocab_file.exists():
        captions_file = annotations_dir / 'captions_train2017.json'
        build_vocabulary(captions_file, vocab_file, args.vocab_threshold)
    else:
        print(f"\n✅ Vocabulary already exists: {vocab_file}")
    
    # Step 3: Train model
    train_model(args)
    
    print("\n" + "="*50)
    print("✅ Training Complete!")
    print("="*50)
    print(f"\nBest model: {args.checkpoint_dir / 'best_model.pth'}")
    print(f"Training history: {args.checkpoint_dir / 'training_history.json'}")
    print("\nTo test inference:")
    print(f"  python backend/inference/inference_script.py \\")
    print(f"    --image path/to/image.jpg \\")
    print(f"    --model {args.checkpoint_dir / 'best_model.pth'} \\")
    print(f"    --vocab {args.checkpoint_dir / 'vocab.json'}")


if __name__ == '__main__':
    main()
