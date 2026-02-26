"""
Training loop with mixed precision, gradient clipping, and checkpointing.
"""

import os
import time
import json
from typing import Dict, Optional
import torch
import torch.nn as nn
from torch.cuda.amp import autocast, GradScaler
from torch.utils.data import DataLoader
from loguru import logger

from .metrics import CaptionMetrics


class Trainer:
    """Trainer for image captioning models."""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        optimizer: torch.optim.Optimizer,
        criterion: nn.Module,
        vocabulary,
        device: torch.device,
        checkpoint_dir: str = 'checkpoints',
        log_interval: int = 100,
        use_amp: bool = True,
        gradient_clip: float = 5.0,
        scheduler: Optional[torch.optim.lr_scheduler._LRScheduler] = None
    ):
        """
        Args:
            model: Captioning model
            train_loader: Training data loader
            val_loader: Validation data loader
            optimizer: Optimizer
            criterion: Loss function
            vocabulary: Vocabulary instance
            device: Device to train on
            checkpoint_dir: Directory to save checkpoints
            log_interval: Logging frequency (batches)
            use_amp: Use automatic mixed precision
            gradient_clip: Gradient clipping threshold
            scheduler: Learning rate scheduler
        """
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.optimizer = optimizer
        self.criterion = criterion
        self.vocabulary = vocabulary
        self.device = device
        self.checkpoint_dir = checkpoint_dir
        self.log_interval = log_interval
        self.use_amp = use_amp
        self.gradient_clip = gradient_clip
        self.scheduler = scheduler
        
        # Mixed precision scaler
        self.scaler = GradScaler() if use_amp else None
        
        # Create checkpoint directory
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'val_metrics': [],
            'learning_rates': []
        }
        
        # Best model tracking
        self.best_val_loss = float('inf')
        self.best_bleu4 = 0.0
        self.epochs_without_improvement = 0
    
    def train_epoch(self, epoch: int) -> float:
        """
        Train for one epoch.
        
        Args:
            epoch: Current epoch number
            
        Returns:
            avg_loss: Average training loss
        """
        self.model.train()
        total_loss = 0
        start_time = time.time()
        
        for batch_idx, (images, captions, lengths) in enumerate(self.train_loader):
            # Move to device
            images = images.to(self.device)
            captions = captions.to(self.device)
            lengths = lengths.to(self.device)
            
            # Forward pass with mixed precision
            self.optimizer.zero_grad()
            
            if self.use_amp:
                with autocast():
                    # Model forward
                    outputs = self.model(images, captions[:, :-1])  # Teacher forcing
                    
                    # Compute loss
                    targets = captions[:, 1:]  # Shift targets
                    loss = self._compute_loss(outputs, targets, lengths - 1)
                
                # Backward pass with gradient scaling
                self.scaler.scale(loss).backward()
                
                # Gradient clipping
                if self.gradient_clip > 0:
                    self.scaler.unscale_(self.optimizer)
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(),
                        self.gradient_clip
                    )
                
                # Optimizer step
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                # Standard training
                outputs = self.model(images, captions[:, :-1])
                targets = captions[:, 1:]
                loss = self._compute_loss(outputs, targets, lengths - 1)
                
                loss.backward()
                
                if self.gradient_clip > 0:
                    torch.nn.utils.clip_grad_norm_(
                        self.model.parameters(),
                        self.gradient_clip
                    )
                
                self.optimizer.step()
            
            total_loss += loss.item()
            
            # Logging
            if (batch_idx + 1) % self.log_interval == 0:
                avg_loss = total_loss / (batch_idx + 1)
                elapsed = time.time() - start_time
                logger.info(
                    f"Epoch [{epoch}] Batch [{batch_idx + 1}/{len(self.train_loader)}] "
                    f"Loss: {loss.item():.4f} | Avg Loss: {avg_loss:.4f} | "
                    f"Time: {elapsed:.2f}s"
                )
        
        avg_loss = total_loss / len(self.train_loader)
        return avg_loss
    
    def validate(self, epoch: int) -> tuple[float, Dict[str, float]]:
        """
        Validate the model.
        
        Args:
            epoch: Current epoch number
            
        Returns:
            avg_loss: Average validation loss
            metrics: Evaluation metrics
        """
        self.model.eval()
        total_loss = 0
        
        # Metrics
        metrics_evaluator = CaptionMetrics()
        
        with torch.no_grad():
            for images, captions, lengths in self.val_loader:
                images = images.to(self.device)
                captions = captions.to(self.device)
                lengths = lengths.to(self.device)
                
                # Forward pass
                outputs = self.model(images, captions[:, :-1])
                targets = captions[:, 1:]
                loss = self._compute_loss(outputs, targets, lengths - 1)
                
                total_loss += loss.item()
                
                # Generate captions for metrics (sample a few)
                if len(metrics_evaluator.predictions) < 500:  # Limit for speed
                    for i in range(min(4, images.size(0))):
                        # Generate caption
                        pred_caption = self.model.generate_caption(
                            images[i:i+1],
                            self.vocabulary.start_idx,
                            self.vocabulary.end_idx,
                            max_len=50,
                            method='greedy'
                        )
                        
                        # Decode
                        pred_text = self.vocabulary.decode(pred_caption.tolist())
                        ref_text = self.vocabulary.decode(captions[i].tolist())
                        
                        # Update metrics
                        metrics_evaluator.update([pred_text], [[ref_text]])
        
        avg_loss = total_loss / len(self.val_loader)
        
        # Compute metrics
        metrics = metrics_evaluator.compute_all() if len(metrics_evaluator.predictions) > 0 else {}
        
        logger.info(f"Validation - Epoch [{epoch}] Loss: {avg_loss:.4f}")
        if metrics:
            logger.info(f"Metrics: {json.dumps(metrics, indent=2)}")
        
        return avg_loss, metrics
    
    def _compute_loss(
        self,
        outputs: torch.Tensor,
        targets: torch.Tensor,
        lengths: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute loss with padding mask.
        
        Args:
            outputs: (batch_size, seq_len, vocab_size)
            targets: (batch_size, seq_len)
            lengths: (batch_size,)
            
        Returns:
            loss: Scalar loss
        """
        batch_size, seq_len, vocab_size = outputs.shape
        
        # Reshape for cross entropy
        outputs = outputs.reshape(-1, vocab_size)
        targets = targets.reshape(-1)
        
        # Compute loss (ignore padding)
        loss = self.criterion(outputs, targets)
        
        return loss
    
    def train(
        self,
        num_epochs: int,
        early_stopping_patience: int = 5,
        save_best_only: bool = False
    ):
        """
        Full training loop.
        
        Args:
            num_epochs: Number of epochs to train
            early_stopping_patience: Epochs to wait before early stopping
            save_best_only: Only save best model
        """
        logger.info(f"Starting training for {num_epochs} epochs")
        logger.info(f"Device: {self.device}")
        logger.info(f"Mixed Precision: {self.use_amp}")
        
        for epoch in range(1, num_epochs + 1):
            epoch_start = time.time()
            
            # Train
            train_loss = self.train_epoch(epoch)
            
            # Validate
            val_loss, val_metrics = self.validate(epoch)
            
            # Update history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_loss)
            self.history['val_metrics'].append(val_metrics)
            
            if self.scheduler:
                current_lr = self.optimizer.param_groups[0]['lr']
                self.history['learning_rates'].append(current_lr)
                self.scheduler.step(val_loss)
            
            # Save checkpoint
            bleu4 = val_metrics.get('BLEU-4', 0.0)
            
            is_best_loss = val_loss < self.best_val_loss
            is_best_bleu = bleu4 > self.best_bleu4
            
            if is_best_loss:
                self.best_val_loss = val_loss
                self.epochs_without_improvement = 0
            else:
                self.epochs_without_improvement += 1
            
            if is_best_bleu:
                self.best_bleu4 = bleu4
            
            # Save model
            if not save_best_only or is_best_loss or is_best_bleu:
                self.save_checkpoint(epoch, val_loss, val_metrics, is_best_loss or is_best_bleu)
            
            epoch_time = time.time() - epoch_start
            logger.info(f"Epoch [{epoch}] completed in {epoch_time:.2f}s")
            logger.info(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f}")
            
            # Early stopping
            if self.epochs_without_improvement >= early_stopping_patience:
                logger.info(f"Early stopping triggered after {epoch} epochs")
                break
        
        logger.info("Training completed!")
        self.save_training_history()
    
    def save_checkpoint(
        self,
        epoch: int,
        val_loss: float,
        metrics: Dict,
        is_best: bool = False
    ):
        """Save model checkpoint."""
        checkpoint = {
            'epoch': epoch,
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'val_loss': val_loss,
            'metrics': metrics,
            'history': self.history,
            'vocabulary_size': len(self.vocabulary),
            'model_config': {
                'vocab_size': self.model.vocab_size,
                'embed_dim': self.model.embed_dim
            }
        }
        
        if self.scheduler:
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
        
        # Save regular checkpoint
        checkpoint_path = os.path.join(
            self.checkpoint_dir,
            f'checkpoint_epoch_{epoch}.pth'
        )
        torch.save(checkpoint, checkpoint_path)
        logger.info(f"Saved checkpoint: {checkpoint_path}")
        
        # Save best model
        if is_best:
            best_path = os.path.join(self.checkpoint_dir, 'best_model.pth')
            torch.save(checkpoint, best_path)
            logger.info(f"Saved best model: {best_path}")
    
    def save_training_history(self):
        """Save training history to JSON."""
        history_path = os.path.join(self.checkpoint_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        logger.info(f"Saved training history: {history_path}")
    
    @staticmethod
    def load_checkpoint(checkpoint_path: str, model: nn.Module, optimizer: Optional[torch.optim.Optimizer] = None):
        """Load model from checkpoint."""
        checkpoint = torch.load(checkpoint_path, map_location='cpu')
        model.load_state_dict(checkpoint['model_state_dict'])
        
        if optimizer and 'optimizer_state_dict' in checkpoint:
            optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        
        logger.info(f"Loaded checkpoint from epoch {checkpoint['epoch']}")
        return checkpoint
