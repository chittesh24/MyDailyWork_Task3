#!/bin/bash
# Training script for MS COCO dataset
# This script automates the complete training pipeline

set -e  # Exit on error

echo "========================================="
echo "MS COCO Image Captioning Training Script"
echo "========================================="

# Configuration
DATASET_DIR="${DATASET_DIR:-./data/coco}"
CHECKPOINT_DIR="${CHECKPOINT_DIR:-./checkpoints/coco}"
BATCH_SIZE="${BATCH_SIZE:-32}"
NUM_EPOCHS="${NUM_EPOCHS:-20}"
LEARNING_RATE="${LEARNING_RATE:-3e-4}"
ENCODER_LR="${ENCODER_LR:-1e-4}"
DEVICE="${DEVICE:-cuda}"
NUM_WORKERS="${NUM_WORKERS:-4}"

# Step 1: Check if dataset exists
echo ""
echo "Step 1: Checking dataset..."
if [ ! -d "$DATASET_DIR/train2017" ] || [ ! -d "$DATASET_DIR/val2017" ]; then
    echo "⚠️  MS COCO dataset not found!"
    echo "Downloading MS COCO 2017 dataset..."
    
    mkdir -p $DATASET_DIR
    cd $DATASET_DIR
    
    # Download images
    echo "Downloading train images (18GB)..."
    wget -c http://images.cocodataset.org/zips/train2017.zip
    
    echo "Downloading val images (1GB)..."
    wget -c http://images.cocodataset.org/zips/val2017.zip
    
    echo "Downloading annotations..."
    wget -c http://images.cocodataset.org/annotations/annotations_trainval2017.zip
    
    # Extract
    echo "Extracting files..."
    unzip -q train2017.zip
    unzip -q val2017.zip
    unzip -q annotations_trainval2017.zip
    
    # Clean up
    rm train2017.zip val2017.zip annotations_trainval2017.zip
    
    cd - > /dev/null
    echo "✅ Dataset downloaded and extracted"
else
    echo "✅ Dataset found at $DATASET_DIR"
fi

# Step 2: Create checkpoint directory
echo ""
echo "Step 2: Setting up checkpoint directory..."
mkdir -p $CHECKPOINT_DIR
echo "✅ Checkpoint directory: $CHECKPOINT_DIR"

# Step 3: Build vocabulary (if not exists)
echo ""
echo "Step 3: Building vocabulary..."
if [ ! -f "$CHECKPOINT_DIR/vocab.json" ]; then
    echo "Building vocabulary from training captions..."
    python -c "
from training.vocabulary import Vocabulary
import json

# Load captions
with open('$DATASET_DIR/annotations/captions_train2017.json', 'r') as f:
    data = json.load(f)

captions = [ann['caption'] for ann in data['annotations']]

# Build vocabulary
vocab = Vocabulary(freq_threshold=5)
vocab.build_vocabulary(captions)
vocab.save('$CHECKPOINT_DIR/vocab.json')

print(f'✅ Vocabulary built: {len(vocab)} tokens')
"
else
    echo "✅ Vocabulary already exists"
fi

# Step 4: Train model
echo ""
echo "Step 4: Training model..."
echo "Configuration:"
echo "  - Batch size: $BATCH_SIZE"
echo "  - Epochs: $NUM_EPOCHS"
echo "  - Learning rate: $LEARNING_RATE"
echo "  - Encoder LR: $ENCODER_LR"
echo "  - Device: $DEVICE"
echo ""

python backend/training/train.py \
    --train_image_dir $DATASET_DIR/train2017 \
    --train_captions $DATASET_DIR/annotations/captions_train2017.json \
    --val_image_dir $DATASET_DIR/val2017 \
    --val_captions $DATASET_DIR/annotations/captions_val2017.json \
    --dataset_type coco \
    --vocab_path $CHECKPOINT_DIR/vocab.json \
    --checkpoint_dir $CHECKPOINT_DIR \
    --batch_size $BATCH_SIZE \
    --num_epochs $NUM_EPOCHS \
    --learning_rate $LEARNING_RATE \
    --encoder_lr $ENCODER_LR \
    --fine_tune_encoder \
    --fine_tune_layers 2 \
    --use_amp \
    --gradient_clip 5.0 \
    --scheduler plateau \
    --early_stopping 5 \
    --log_interval 100 \
    --device $DEVICE \
    --num_workers $NUM_WORKERS \
    --seed 42

echo ""
echo "========================================="
echo "✅ Training completed!"
echo "========================================="
echo ""
echo "Best model saved to: $CHECKPOINT_DIR/best_model.pth"
echo "Training history: $CHECKPOINT_DIR/training_history.json"
echo ""
echo "To test inference:"
echo "  python backend/inference/inference_script.py \\"
echo "    --image path/to/test/image.jpg \\"
echo "    --model $CHECKPOINT_DIR/best_model.pth \\"
echo "    --vocab $CHECKPOINT_DIR/vocab.json \\"
echo "    --device $DEVICE"
