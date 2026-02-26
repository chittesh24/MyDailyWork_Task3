# Deployment Guide

Production deployment for Image Captioning System.

## Table of Contents

1. [Local Development](#local-development)
2. [Training the Model](#training-the-model)
3. [Docker Deployment](#docker-deployment)
4. [Production Deployment](#production-deployment)
5. [Environment Variables](#environment-variables)
6. [Monitoring](#monitoring)

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- CUDA (optional, for GPU training)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python -c "from database.database import init_db; init_db()"

# Run development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local

# Run development server
npm run dev
```

Access application at `http://localhost:3000`

---

## Training the Model

### 1. Download Dataset

**MS COCO (Recommended)**

```bash
# Download images and annotations
wget http://images.cocodataset.org/zips/train2017.zip
wget http://images.cocodataset.org/zips/val2017.zip
wget http://images.cocodataset.org/annotations/annotations_trainval2017.zip

# Extract
unzip train2017.zip -d data/coco/
unzip val2017.zip -d data/coco/
unzip annotations_trainval2017.zip -d data/coco/
```

**Flickr8k (Smaller, for testing)**

```bash
# Download from Kaggle or official source
# Place images in data/flickr8k/images/
# Place captions in data/flickr8k/captions.txt
```

### 2. Build Vocabulary

```bash
cd backend

python training/train.py \
  --train_image_dir ../data/coco/train2017 \
  --train_captions ../data/coco/annotations/captions_train2017.json \
  --val_image_dir ../data/coco/val2017 \
  --val_captions ../data/coco/annotations/captions_val2017.json \
  --dataset_type coco \
  --checkpoint_dir checkpoints \
  --num_epochs 0  # Just build vocab
```

### 3. Train Model

**Full Training (GPU Recommended)**

```bash
python training/train.py \
  --train_image_dir ../data/coco/train2017 \
  --train_captions ../data/coco/annotations/captions_train2017.json \
  --val_image_dir ../data/coco/val2017 \
  --val_captions ../data/coco/annotations/captions_val2017.json \
  --dataset_type coco \
  --batch_size 32 \
  --num_epochs 20 \
  --learning_rate 3e-4 \
  --encoder_lr 1e-4 \
  --fine_tune_encoder \
  --use_amp \
  --checkpoint_dir checkpoints \
  --device cuda
```

**Quick Test (CPU)**

```bash
python training/train.py \
  --train_image_dir ../data/flickr8k/images \
  --train_captions ../data/flickr8k/captions.txt \
  --val_image_dir ../data/flickr8k/images \
  --val_captions ../data/flickr8k/captions.txt \
  --dataset_type flickr8k \
  --batch_size 8 \
  --num_epochs 5 \
  --checkpoint_dir checkpoints \
  --device cpu
```

### 4. Test Inference

```bash
cd backend/inference

python inference_script.py \
  --image path/to/test/image.jpg \
  --model ../checkpoints/best_model.pth \
  --vocab ../checkpoints/vocab.json \
  --method beam_search \
  --beam_width 5 \
  --device cuda
```

---

## Docker Deployment

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Access Services

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Database: `localhost:5432`

### Add Model Checkpoint

```bash
# Place trained model in backend/checkpoints/
cp path/to/best_model.pth backend/checkpoints/
cp path/to/vocab.json backend/checkpoints/

# Restart backend
docker-compose restart backend
```

---

## Production Deployment

### Option 1: Render + Vercel + Supabase (Free Tier - $0/month)

**Automated Deployment**

```bash
# Interactive deployment wizard
python scripts/setup_free_tier.py
```

This script guides you through:
1. Supabase database setup (500MB free)
2. Render backend deployment (750 hrs/month free)
3. Vercel frontend deployment (unlimited free)
4. CORS configuration
5. Environment variables setup

**Manual Deployment**

**Step 1: Database (Supabase)**

```bash
bash scripts/deploy_supabase.sh
```

Follow the interactive guide to:
- Create Supabase account
- Set up PostgreSQL database
- Run SQL schema
- Get connection string

**Step 2: Backend (Render)**

```bash
bash scripts/deploy_render.sh
```

Or manually:

1. Create new Web Service on Render
2. Connect GitHub repository
3. Configure:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
   - Root Directory: `backend`
4. Add Environment Variables (see below)
5. Add PostgreSQL database (free tier)

**Frontend Deployment (Vercel)**

```bash
cd frontend
vercel deploy --prod
```

Update `NEXT_PUBLIC_API_URL` in Vercel environment variables.

### Option 2: AWS EC2 + RDS

**1. Launch EC2 Instance**

```bash
# t2.medium or larger recommended
# Ubuntu 22.04 LTS

# SSH into instance
ssh -i key.pem ubuntu@your-ec2-ip

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/yourusername/image-captioning-system.git
cd image-captioning-system

# Set environment variables
nano .env

# Start services
docker-compose up -d
```

**2. Setup RDS PostgreSQL**

- Create RDS PostgreSQL instance
- Update `DATABASE_URL` in .env
- Run migrations

**3. Setup Load Balancer**

- Create Application Load Balancer
- Configure target groups
- Setup SSL certificate (AWS Certificate Manager)

**4. Setup S3 for Image Storage**

```python
# Update backend/api/utils.py to use S3
import boto3

s3_client = boto3.client('s3')

def save_to_s3(file, bucket, key):
    s3_client.upload_fileobj(file, bucket, key)
    return f"https://{bucket}.s3.amazonaws.com/{key}"
```

### Option 3: Google Cloud Run

**Backend**

```bash
# Build container
gcloud builds submit --tag gcr.io/PROJECT_ID/caption-backend

# Deploy
gcloud run deploy caption-backend \
  --image gcr.io/PROJECT_ID/caption-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

**Frontend**

Deploy to Vercel or Cloud Run.

---

## Environment Variables

### Backend (.env)

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Security
SECRET_KEY=your-secret-key-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Model
MODEL_CHECKPOINT_PATH=checkpoints/best_model.pth
VOCAB_PATH=checkpoints/vocab.json
DEVICE=cuda  # or 'cpu'

# API Settings
MAX_FILE_SIZE_MB=5
ALLOWED_MIME_TYPES=image/jpeg,image/png
RATE_LIMIT_PER_MINUTE=10

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000

# Optional: Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-key
```

### Frontend (.env.local)

```bash
NEXT_PUBLIC_API_URL=https://your-backend-api.com
```

---

## Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/

# Database connection
docker exec -it caption_db psql -U postgres -d image_captions -c "SELECT COUNT(*) FROM users;"
```

### Logs

```bash
# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Production logs (systemd)
journalctl -u caption-backend -f
```

### Metrics

Add Prometheus + Grafana:

```yaml
# docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    depends_on:
      - prometheus
```

---

## Performance Optimization

### 1. Model Optimization

```python
# Export to TorchScript
from inference.predictor import CaptionPredictor

predictor = CaptionPredictor(model_path, vocab_path)
predictor.export_torchscript('model_scripted.pt')

# Export to ONNX
predictor.export_onnx('model.onnx')

# Quantization (CPU)
predictor.quantize_model()
```

### 2. Caching

```python
# Add Redis caching
import redis
from functools import lru_cache

redis_client = redis.Redis(host='localhost', port=6379)

@lru_cache(maxsize=100)
def cached_predict(image_hash):
    return predictor.predict(image)
```

### 3. Batch Processing

```python
# Process multiple images
captions = predictor.predict_batch(image_list)
```

### 4. CDN

- Use CloudFront (AWS) or Cloudflare
- Cache static assets
- Enable compression

---

## Security Checklist

- ✅ HTTPS enabled
- ✅ API keys hashed (SHA-256)
- ✅ Passwords hashed (bcrypt)
- ✅ JWT tokens with expiration
- ✅ Rate limiting enabled
- ✅ File validation (size + MIME)
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ XSS prevention (input sanitization)
- ✅ CORS properly configured
- ✅ Environment secrets not in code
- ✅ Database backups enabled

---

## Troubleshooting

### Model Loading Error

```bash
# Check model path
ls -la backend/checkpoints/

# Verify vocabulary
python -c "from training.vocabulary import Vocabulary; v = Vocabulary.load('checkpoints/vocab.json'); print(len(v))"
```

### Database Connection Error

```bash
# Test connection
psql postgresql://user:password@host:5432/dbname

# Check migrations
docker exec -it caption_db psql -U postgres -d image_captions -c "\dt"
```

### CORS Error

Update `ALLOWED_ORIGINS` in backend .env:

```bash
ALLOWED_ORIGINS=https://yourdomain.com,http://localhost:3000
```

### Out of Memory

Reduce batch size or use CPU:

```bash
--batch_size 8 --device cpu
```

---

## Scaling

### Horizontal Scaling

```bash
# Increase backend replicas
docker-compose up -d --scale backend=3

# Use load balancer
# nginx/traefik configuration
```

### Vertical Scaling

- Use GPU instances (AWS p3, GCP A100)
- Increase memory for larger models
- SSD for faster I/O

---

## Cost Optimization (Free Tier)

| Service | Provider | Free Tier |
|---------|----------|-----------|
| Backend | Render | 750 hrs/month |
| Frontend | Vercel | Unlimited |
| Database | Supabase | 500MB |
| Storage | Cloudflare R2 | 10GB |

**Total Cost: $0/month**

For production: ~$20-50/month (RDS + EC2 + S3)

---

## Support

- Documentation: `/docs`
- API Reference: `http://localhost:8000/docs`
- Issues: GitHub Issues
