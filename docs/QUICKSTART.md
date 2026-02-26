# Quick Start Guide

Get the Image Captioning System running in 5 minutes.

## Prerequisites

- Docker & Docker Compose installed
- 4GB+ RAM
- 10GB free disk space

## 1. Clone Repository

```bash
git clone https://github.com/yourusername/image-captioning-system.git
cd image-captioning-system
```

## 2. Download Pre-trained Model

**Option A: Use pre-trained weights** (recommended for testing)

```bash
# Download from HuggingFace or Google Drive
# Place in backend/checkpoints/
mkdir -p backend/checkpoints
# Download best_model.pth and vocab.json
```

**Option B: Train your own** (requires GPU + dataset)

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md#training-the-model)

## 3. Configure Environment

```bash
# Copy example environment file
cp backend/.env.example backend/.env

# Edit backend/.env
nano backend/.env
```

Minimum required:

```bash
DATABASE_URL=postgresql://postgres:postgres@db:5432/image_captions
SECRET_KEY=change-this-to-a-secure-random-string-min-32-chars
MODEL_CHECKPOINT_PATH=/app/checkpoints/best_model.pth
VOCAB_PATH=/app/checkpoints/vocab.json
DEVICE=cpu  # or 'cuda' if GPU available
```

## 4. Start Services

```bash
# Build and start all services
docker-compose up -d

# Check logs
docker-compose logs -f
```

Wait for services to be ready (~2 minutes).

## 5. Initialize Database

```bash
# Run database migrations
docker exec -it caption_backend python -c "from database.database import init_db; init_db()"
```

## 6. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 7. Create Account

1. Go to http://localhost:3000
2. Click "Register"
3. Enter email and password (min 8 chars)
4. Login with credentials

## 8. Generate API Key

1. Navigate to Dashboard
2. Click "Generate New Key"
3. Copy and save the key (shown once!)

## 9. Generate Caption

1. Click "Upload Image" or drag & drop
2. Wait for processing (~200-500ms on CPU)
3. View generated caption

## Training Your First Model

### Option 1: Quick Training (Flickr8k)

```bash
# Small dataset, good for testing (8,000 images)
bash scripts/train_flickr8k.sh
```

### Option 2: Full Training (MS COCO)

```bash
# Large dataset, best results (118,000 images)
bash scripts/train_coco.sh

# Or with Python script
python scripts/train_coco.py --download --device cuda
```

### Option 3: Download Pre-trained Model

```bash
# Download from HuggingFace or Google Drive
mkdir -p backend/checkpoints
# Place best_model.pth and vocab.json in backend/checkpoints/
```

## Testing with cURL

```bash
# Register user
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Save the access_token from response

# Generate API key
curl -X POST http://localhost:8000/api-keys/generate \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Save the api_key from response

# Generate caption
curl -X POST http://localhost:8000/caption \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -F "file=@path/to/image.jpg"
```

## Troubleshooting

### Services won't start

```bash
# Check Docker status
docker ps

# View logs
docker-compose logs backend
docker-compose logs db

# Restart services
docker-compose restart
```

### Model not loading

```bash
# Check model files exist
ls -la backend/checkpoints/

# Verify paths in .env
cat backend/.env | grep MODEL
```

### Database connection error

```bash
# Check database is running
docker exec -it caption_db psql -U postgres -c "SELECT 1"

# Reinitialize if needed
docker-compose down -v
docker-compose up -d
```

### Frontend can't connect to backend

```bash
# Check CORS settings in backend/.env
ALLOWED_ORIGINS=http://localhost:3000

# Verify API URL in frontend
cat frontend/.env.local
```

## Next Steps

### 1. Train a Model
```bash
# Quick test with Flickr8k
bash scripts/train_flickr8k.sh

# Full training with MS COCO
python scripts/train_coco.py --download
```

### 2. Deploy for Free
```bash
# Automated deployment to Render + Vercel + Supabase
python scripts/setup_free_tier.py
```

### 3. Customize Theme
- Visit http://localhost:3000/settings
- Choose from 6 color themes
- Adjust font size and animations

### 4. Compare Models
```bash
# Benchmark performance
python scripts/benchmark.py \
  --model checkpoints/best_model.pth \
  --vocab checkpoints/vocab.json \
  --image test.jpg
```

### 5. Read Documentation
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete features

## Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f [service]

# Rebuild after code changes
docker-compose up -d --build

# Clean everything
docker-compose down -v
rm -rf backend/uploads/*
```

## Development Mode

For active development without Docker:

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn api.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

## Support

- Documentation: [README.md](README.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)
- Deployment: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- Issues: GitHub Issues
