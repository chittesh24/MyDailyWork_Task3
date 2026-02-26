"""
Main training script.
"""

import os
import argparse
import json
import torch
import torch.nn as nn
from loguru import logger

from models.captioning_model import CaptioningModel
from training.vocabulary import Vocabulary
from training.dataset import get_data_loaders
from training.trainer import Trainer


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Train Image Captioning Model')
    
    # Data
    parser.add_argument('--train_image_dir', type=str, required=True, help='Training images directory')
    parser.add_argument('--train_captions', type=str, required=True, help='Training captions file')
    parser.add_argument('--val_image_dir', type=str, required=True, help='Validation images directory')
    parser.add_argument('--val_captions', type=str, required=True, help='Validation captions file')
    parser.add_argument('--dataset_type', type=str, default='coco', choices=['coco', 'flickr8k'])
    
    # Model
    parser.add_argument('--embed_dim', type=int, default=512)
    parser.add_argument('--num_heads', type=int, default=8)
    parser.add_argument('--num_layers', type=int, default=6)
    parser.add_argument('--ff_dim', type=int, default=2048)
    parser.add_argument('--dropout', type=float, default=0.1)
    parser.add_argument('--max_seq_len', type=int, default=52)
    parser.add_argument('--fine_tune_encoder', action='store_true')
    parser.add_argument('--fine_tune_layers', type=int, default=2)
    
    # Vocabulary
    parser.add_argument('--vocab_threshold', type=int, default=5)
    parser.add_argument('--vocab_path', type=str, default=None, help='Path to existing vocabulary')
    
    # Training
    parser.add_argument('--batch_size', type=int, default=32)
    parser.add_argument('--num_epochs', type=int, default=20)
    parser.add_argument('--learning_rate', type=float, default=3e-4)
    parser.add_argument('--encoder_lr', type=float, default=1e-4)
    parser.add_argument('--weight_decay', type=float, default=0.0)
    parser.add_argument('--gradient_clip', type=float, default=5.0)
    parser.add_argument('--num_workers', type=int, default=4)
    
    # Optimization
    parser.add_argument('--use_amp', action='store_true', help='Use mixed precision training')
    parser.add_argument('--scheduler', type=str, default='plateau', choices=['plateau', 'cosine', 'none'])
    parser.add_argument('--early_stopping', type=int, default=5)
    
    # Checkpointing
    parser.add_argument('--checkpoint_dir', type=str, default='checkpoints')
    parser.add_argument('--log_interval', type=int, default=100)
    parser.add_argument('--save_best_only', action='store_true')
    
    # Resume
    parser.add_argument('--resume', type=str, default=None, help='Path to checkpoint to resume from')
    
    # Device
    parser.add_argument('--device', type=str, default='cuda' if torch.cuda.is_available() else 'cpu')
    
    # Random seed
    parser.add_argument('--seed', type=int, default=42)
    
    return parser.parse_args()


def set_seed(seed: int):
    """Set random seeds for reproducibility."""
    import random
    import numpy as np
    
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def build_vocabulary(args):
    """Build or load vocabulary."""
    if args.vocab_path and os.path.exists(args.vocab_path):
        logger.info(f"Loading vocabulary from {args.vocab_path}")
        vocabulary = Vocabulary.load(args.vocab_path)
    else:
        logger.info("Building vocabulary from training data")
        vocabulary = Vocabulary(freq_threshold=args.vocab_threshold)
        
        # Load all training captions
        if args.dataset_type == 'coco':
            with open(args.train_captions, 'r') as f:
                coco_data = json.load(f)
            captions = [ann['caption'] for ann in coco_data['annotations']]
        elif args.dataset_type == 'flickr8k':
            import pandas as pd
            if args.train_captions.endswith('.csv'):
                df = pd.read_csv(args.train_captions)
                captions = df['caption'].tolist()
            else:
                captions = []
                with open(args.train_captions, 'r') as f:
                    for line in f:
                        parts = line.strip().split('\t')
                        if len(parts) == 2:
                            captions.append(parts[1])
        
        vocabulary.build_vocabulary(captions)
        
        # Save vocabulary
        vocab_save_path = os.path.join(args.checkpoint_dir, 'vocab.json')
        os.makedirs(args.checkpoint_dir, exist_ok=True)
        vocabulary.save(vocab_save_path)
    
    return vocabulary


def main():
    """Main training function."""
    args = parse_args()
    
    # Set seed
    set_seed(args.seed)
    
    # Setup logging
    logger.add(os.path.join(args.checkpoint_dir, 'training.log'))
    logger.info(f"Arguments: {vars(args)}")
    
    # Build vocabulary
    vocabulary = build_vocabulary(args)
    logger.info(f"Vocabulary size: {len(vocabulary)}")
    
    # Create data loaders
    logger.info("Creating data loaders")
    train_loader, val_loader = get_data_loaders(
        args.train_image_dir,
        args.train_captions,
        args.val_image_dir,
        args.val_captions,
        vocabulary,
        args.batch_size,
        args.num_workers,
        args.dataset_type,
        max_length=args.max_seq_len
    )
    
    # Create model
    logger.info("Creating model")
    model = CaptioningModel(
        vocab_size=len(vocabulary),
        embed_dim=args.embed_dim,
        num_heads=args.num_heads,
        num_layers=args.num_layers,
        ff_dim=args.ff_dim,
        dropout=args.dropout,
        max_seq_len=args.max_seq_len,
        pretrained_encoder=True,
        fine_tune_encoder=args.fine_tune_encoder,
        fine_tune_layers=args.fine_tune_layers
    )
    
    device = torch.device(args.device)
    model = model.to(device)
    
    logger.info(f"Model parameters: {sum(p.numel() for p in model.parameters()) / 1e6:.2f}M")
    
    # Create optimizer with different learning rates for encoder and decoder
    trainable_params = model.get_trainable_parameters()
    
    if args.fine_tune_encoder and len(trainable_params['encoder']) > 0:
        optimizer = torch.optim.AdamW([
            {'params': trainable_params['encoder'], 'lr': args.encoder_lr},
            {'params': trainable_params['decoder'], 'lr': args.learning_rate}
        ], weight_decay=args.weight_decay)
    else:
        optimizer = torch.optim.AdamW(
            trainable_params['decoder'],
            lr=args.learning_rate,
            weight_decay=args.weight_decay
        )
    
    # Create loss function
    criterion = nn.CrossEntropyLoss(ignore_index=vocabulary.pad_idx)
    
    # Create scheduler
    scheduler = None
    if args.scheduler == 'plateau':
        scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode='min', factor=0.5, patience=2, verbose=True
        )
    elif args.scheduler == 'cosine':
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer, T_max=args.num_epochs
        )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        train_loader=train_loader,
        val_loader=val_loader,
        optimizer=optimizer,
        criterion=criterion,
        vocabulary=vocabulary,
        device=device,
        checkpoint_dir=args.checkpoint_dir,
        log_interval=args.log_interval,
        use_amp=args.use_amp,
        gradient_clip=args.gradient_clip,
        scheduler=scheduler
    )
    
    # Resume from checkpoint if specified
    if args.resume:
        logger.info(f"Resuming from checkpoint: {args.resume}")
        trainer.load_checkpoint(args.resume, model, optimizer)
    
    # Train
    trainer.train(
        num_epochs=args.num_epochs,
        early_stopping_patience=args.early_stopping,
        save_best_only=args.save_best_only
    )
    
    logger.info("Training finished!")


if __name__ == '__main__':
    main()
