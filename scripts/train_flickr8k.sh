#!/bin/bash
# Training script for Flickr8k dataset (smaller, faster for testing)

set -e

echo "========================================="
echo "Flickr8k Image Captioning Training Script"
echo "========================================="

# Configuration
DATASET_DIR="${DATASET_DIR:-./data/flickr8k}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-./checkpoints/flickr8k}"
BATCH_SIZE="${BATCH_SIZE:-16}"
NUM_EPOCHS="${NUM_EPOCHS:-10}"
LEARNING_RATE="${LEARNING_RATE:-3e-4}"
ENCODER_LR="${ENCODER_LR:-1e-4}"
DEVICE="${DEVICE:-cuda}"

# Step 1: Check dataset
echo ""
echo "Step 1: Checking Flickr8k dataset..."
if [ ! -d "$DATASET_DIR/images" ] || [ ! -f "$DATASET_DIR/captions.txt" ]; then
    echo "⚠️  Flickr8k dataset not found!"
    echo ""
    echo "Please download Flickr8k dataset manually:"
    echo "1. Visit: https://www.kaggle.com/datasets/adityajn105/flickr8k"
    echo "2. Download and extract to: $DATASET_DIR"
    echo "3. Structure should be:"
    echo "   $DATASET_DIR/"
    echo "   ├── images/        # 8,000 images"
    echo "   └── captions.txt   # Image captions"
    echo ""
    exit 1
else
    echo "✅ Flickr8k dataset found"
    
    # Count images
    num_images=$(ls -1 $DATASET_DIR/images | wc -l)
    echo "   Images: $num_images"
fi

# Step 2: Prepare train/val split
echo ""
echo "Step 2: Creating train/val split..."
if [ ! -f "$DATASET_DIR/train_captions.txt" ]; then
    python -c "
import os
import random

# Read all captions
with open('$DATASET_DIR/captions.txt', 'r') as f:
    lines = f.readlines()

# Group by image
from collections import defaultdict
image_captions = defaultdict(list)

for line in lines[1:]:  # Skip header
    parts = line.strip().split(',', 1)
    if len(parts) == 2:
        image, caption = parts
        image_captions[image].append(caption)

# Split 80/20
images = list(image_captions.keys())
random.seed(42)
random.shuffle(images)

split_idx = int(len(images) * 0.8)
train_images = set(images[:split_idx])
val_images = set(images[split_idx:])

# Write train captions
with open('$DATASET_DIR/train_captions.txt', 'w') as f:
    f.write('image,caption\n')
    for img in train_images:
        for caption in image_captions[img]:
            f.write(f'{img},{caption}\n')

# Write val captions
with open('$DATASET_DIR/val_captions.txt', 'w') as f:
    f.write('image,caption\n')
    for img in val_images:
        for caption in image_captions[img]:
            f.write(f'{img},{caption}\n')

print(f'✅ Train: {len(train_images)} images')
print(f'✅ Val: {len(val_images)} images')
"
else
    echo "✅ Train/val split already exists"
fi

# Step 3: Create checkpoint directory
echo ""
echo "Step 3: Setting up checkpoint directory..."
mkdir -p $CHECKPOINT_DIR
echo "✅ Checkpoint directory: $CHECKPOINT_DIR"

# Step 4: Build vocabulary
echo ""
echo "Step 4: Building vocabulary..."
if [ ! -f "$CHECKPOINT_DIR/vocab.json" ]; then
    python -c "
from training.vocabulary import Vocabulary
import pandas as pd

# Load captions
df = pd.read_csv('$DATASET_DIR/train_captions.txt')
captions = df['caption'].tolist()

# Build vocabulary
vocab = Vocabulary(freq_threshold=3)  # Lower threshold for smaller dataset
vocab.build_vocabulary(captions)
vocab.save('$CHECKPOINT_DIR/vocab.json')

print(f'✅ Vocabulary built: {len(vocab)} tokens')
"
else
    echo "✅ Vocabulary already exists"
fi

# Step 5: Train model
echo ""
echo "Step 5: Training model..."
echo "Configuration:"
echo "  - Batch size: $BATCH_SIZE"
echo "  - Epochs: $NUM_EPOCHS"
echo "  - Learning rate: $LEARNING_RATE"
echo "  - Device: $DEVICE"
echo ""

python backend/training/train.py \
    --train_image_dir $DATASET_DIR/images \
    --train_captions $DATASET_DIR/train_captions.txt \
    --val_image_dir $DATASET_DIR/images \
    --val_captions $DATASET_DIR/val_captions.txt \
    --dataset_type flickr8k \
    --vocab_path $CHECKPOINT_DIR/vocab.json \
    --checkpoint_dir $CHECKPOINT_DIR \
    --batch_size $BATCH_SIZE \
    --num_epochs $NUM_EPOCHS \
    --learning_rate $LEARNING_RATE \
    --encoder_lr $ENCODER_LR \
    --fine_tune_encoder \
    --use_amp \
    --gradient_clip 5.0 \
    --scheduler plateau \
    --early_stopping 3 \
    --device $DEVICE \
    --seed 42

echo ""
echo "========================================="
echo "✅ Training completed!"
echo "========================================="
echo ""
echo "Model saved to: $CHECKPOINT_DIR/best_model.pth"
echo ""
echo "Quick test:"
echo "  python backend/inference/inference_script.py \\"
echo "    --image $DATASET_DIR/images/\$(ls $DATASET_DIR/images | head -1) \\"
echo "    --model $CHECKPOINT_DIR/best_model.pth \\"
echo "    --vocab $CHECKPOINT_DIR/vocab.json"
