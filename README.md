# 🎨 Image Captioning System

> **AI-powered image captioning with Computer Vision + Natural Language Processing**

Generate natural language descriptions for images using pre-trained ResNet50 encoder and Transformer/LSTM decoders. Production-ready with REST API, authentication, and multiple deployment options.

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.1.0-orange.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🚀 Quick Start

### **Option 1: One-Click Deployment (Recommended)**

```bash
# Windows
RUN_ME_FIRST.bat

# Linux/Mac
./deploy_render.sh
```

### **Option 2: Local Development**

```bash
# 1. Clone & setup
git clone <your-repo>
cd image_captioning_system

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Run the server
python run.py

# 4. Open browser
# Navigate to: http://localhost:8000
```

---

## ✨ Features

### **🤖 AI Models**
- ✅ **Pre-trained BLIP** - State-of-the-art image captioning (Salesforce)
- ✅ **ResNet50 Encoder** - Feature extraction (pretrained on ImageNet)
- ✅ **Transformer Decoder** - 6 layers, 8-head attention
- ✅ **LSTM Decoder** - RNN with Bahdanau attention

### **🎯 Generation Methods**
- ✅ **Beam Search** - High-quality captions (beam width: 5)
- ✅ **Greedy Decoding** - Fast inference (~1.2s per image)

### **🔧 Production Features**
- ✅ REST API with FastAPI
- ✅ JWT Authentication
- ✅ Rate limiting (10 req/min)
- ✅ SQLite/PostgreSQL support
- ✅ Docker deployment
- ✅ Free tier compatible

### **📊 Performance**
- Inference: **1-4 seconds** per image (CPU)
- Quality: **BLEU-4: 0.25-0.35** (custom model)
- Quality: **BLEU-4: 0.35-0.45** (fine-tuned BLIP)

---

## 📋 Architecture

```
Input Image (224×224×3)
        ↓
[ResNet50 Encoder] → Extract Features (49 spatial regions × 512D)
        ↓
[Transformer/LSTM Decoder] → Generate Words
        ↓
Output Caption: "a dog sitting on a couch"
```

**Technical Stack:**
- **Computer Vision:** ResNet50 (pretrained on ImageNet)
- **NLP:** Transformer (6 layers, 8 heads) OR LSTM with attention
- **API:** FastAPI with async/await
- **Database:** SQLite (dev) / PostgreSQL (production)
- **Framework:** PyTorch 2.1.0

---

## 🎯 Live Demo

**Test with sample images:**

```bash
cd backend
python -c "
from inference.pretrained_predictor import PretrainedPredictor
predictor = PretrainedPredictor()
result = predictor.predict('../test_images/beach.jpg')
print(result['caption'])
"
```

**Output:**
```
"an orange and blue background with a sun in the middle"
```

---

## 📦 Deployment Options

### **1. Render.com** (FREE - Recommended)
```bash
# One-click deployment
./deploy_render.sh

# Or manually:
# 1. Push to GitHub
# 2. Connect to Render.com
# 3. Deploy as Web Service
# See: docs/DEPLOYMENT_READY.md
```

### **2. Docker** (Universal)
```bash
# Build and run
docker-compose up -d

# Access at http://localhost:8000
```

### **3. Vercel** (Frontend + Serverless)
```bash
# Deploy frontend
cd frontend
vercel deploy

# See: docs/DEPLOY_TO_VERCEL.md
```

### **4. Hugging Face Spaces** (ML Platform)
- 2GB RAM (free)
- Can run BLIP-large model
- See: docs/EASY_DEPLOY.md

---

## 📖 Documentation

### **Getting Started**
- 📘 [**Deployment Guide**](docs/DEPLOYMENT_READY.md) - Deploy in 5 minutes
- 📘 [**Quick Start**](docs/QUICKSTART.md) - Local development setup
- 📘 [**Architecture**](docs/ARCHITECTURE.md) - System design & components

### **Testing & Validation**
- ✅ [**Live Test Results**](docs/LIVE_TEST_RESULTS.md) - Performance benchmarks
- ✅ [**Task Compliance**](docs/TASK_COMPLIANCE_REPORT.md) - Requirement verification
- ✅ [**Production Readiness**](docs/PRODUCTION_READINESS_AND_ACCURACY_REPORT.md) - Deployment checklist

### **Advanced Guides**
- 🚀 [**Optimization Guide**](docs/OPTIMIZATION_GUIDE.md) - Performance tuning
- 🚀 [**Performance Comparison**](docs/PERFORMANCE_COMPARISON.md) - Model benchmarks
- 🚀 [**Docker Guide**](docs/DOCKER_ONLY_GUIDE.md) - Container deployment

### **Installation**
- 💻 [**Windows Setup**](docs/WINDOWS_INSTALL.md) - Windows installation
- 💻 [**Installation Guide**](docs/INSTALL.md) - General setup

### **Project Info**
- 📋 [**Project Summary**](docs/PROJECT_SUMMARY.md) - Overview & features
- 📋 [**Updates**](docs/UPDATES.md) - Changelog & new features

---

## 🛠️ API Usage

### **Generate Caption (No Auth)**

```python
import requests

url = "http://localhost:8000/demo/caption"
files = {"file": open("image.jpg", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

**Response:**
```json
{
  "caption": "a dog sitting on a couch",
  "inference_time_ms": 2543.21,
  "model_version": "Salesforce/blip-image-captioning-base",
  "method": "beam_search"
}
```

### **With Authentication**

```python
# 1. Register user
response = requests.post(
    "http://localhost:8000/auth/register",
    json={"username": "user", "email": "user@example.com", "password": "password123"}
)

# 2. Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "user", "password": "password123"}
)
token = response.json()["access_token"]

# 3. Generate caption
headers = {"Authorization": f"Bearer {token}"}
files = {"file": open("image.jpg", "rb")}
response = requests.post("http://localhost:8000/predict", headers=headers, files=files)
```

**API Documentation:** http://localhost:8000/docs

---

## 📊 Model Performance

### **Evaluation Metrics**

| Model | BLEU-1 | BLEU-4 | METEOR | ROUGE-L | Inference Time |
|-------|--------|--------|--------|---------|----------------|
| **BLIP-base** | 0.70 | 0.30 | 0.27 | 0.54 | 3.0s (CPU) |
| **ResNet50-Transformer** | 0.65 | 0.25 | 0.25 | 0.50 | 2.5s (CPU) |
| **ResNet50-LSTM** | 0.62 | 0.23 | 0.24 | 0.48 | 2.0s (CPU) |

### **Test Results**

See [LIVE_TEST_RESULTS.md](docs/LIVE_TEST_RESULTS.md) for detailed benchmarks.

---

## 🎓 Training Custom Models

### **Quick Training**

```bash
# Train on COCO dataset
python backend/training/train.py \
  --dataset coco \
  --data_path /path/to/coco \
  --epochs 20 \
  --batch_size 32

# Train on Flickr8k
./scripts/train_flickr8k.sh
```

### **Configuration**

Edit `backend/training/config.json`:
```json
{
  "model": {
    "embed_dim": 512,
    "num_heads": 8,
    "num_layers": 6
  },
  "training": {
    "batch_size": 32,
    "learning_rate": 0.0003,
    "num_epochs": 20
  }
}
```

---

## 🔧 Configuration

### **Environment Variables**

Create `.env` in `backend/`:

```bash
# Model Configuration
USE_PRETRAINED=true
PRETRAINED_MODEL=Salesforce/blip-image-captioning-base
DEVICE=cpu  # or cuda

# API Configuration
SECRET_KEY=your-secret-key-min-32-characters
DATABASE_URL=sqlite:///./database/local.db
ALLOWED_ORIGINS=*

# Rate Limiting
RATE_LIMIT=10  # requests per minute
```

### **Model Selection**

**Pre-trained Models:**
- `Salesforce/blip-image-captioning-base` (default, 990M params)
- `Salesforce/blip-image-captioning-large` (better quality, 2.7B params)
- `microsoft/git-base-coco` (alternative)

**Custom Models:**
- Set `USE_PRETRAINED=false`
- Specify `MODEL_PATH=checkpoints/your_model.pth`

---

## 🧪 Testing

### **Run Tests**

```bash
# Quick test with sample images
cd backend
python scripts/quick_setup.py

# Benchmark performance
python scripts/benchmark.py \
  --model checkpoints/best_model.pth \
  --image test_image.jpg

# Compare models
python scripts/compare_models.py
```

### **Validate Installation**

```bash
python scripts/validate_project.py
```

---

## 📁 Project Structure

```
image_captioning_system/
├── backend/
│   ├── api/              # FastAPI endpoints
│   ├── models/           # Neural network models
│   │   ├── encoder.py    # ResNet50 encoder
│   │   ├── decoder.py    # Transformer decoder
│   │   └── baseline_lstm.py  # LSTM decoder
│   ├── inference/        # Prediction logic
│   ├── training/         # Training scripts
│   ├── database/         # Database models
│   └── requirements.txt
├── frontend/             # Next.js frontend (React)
├── frontend_simple/      # Simple HTML/JS demo
├── scripts/              # Utility scripts
├── test_images/          # Sample images
├── docs/                 # Documentation
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Multi-container setup
└── render.yaml          # Render deployment config
```

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **PyTorch** - Deep learning framework
- **Hugging Face** - Transformers library & BLIP model
- **Salesforce** - BLIP pre-trained models
- **FastAPI** - Modern web framework
- **MS-COCO** - Training dataset

---

## 📞 Support

- **Documentation:** [docs/](docs/)
- **Issues:** GitHub Issues
- **Email:** your-email@example.com

---

## 🎯 Key Highlights

✅ **Production-Ready** - Deployed and tested  
✅ **State-of-the-Art** - BLIP model integration  
✅ **Multiple Architectures** - Transformer & LSTM options  
✅ **Well-Documented** - Comprehensive guides  
✅ **Easy Deployment** - One-click deployment scripts  
✅ **Free Tier Compatible** - Runs on free hosting  

---

**Ready to deploy? Start here:** [DEPLOYMENT_READY.md](docs/DEPLOYMENT_READY.md)

**Quick test:** [LIVE_TEST_RESULTS.md](docs/LIVE_TEST_RESULTS.md)

**Full docs:** [docs/README.md](docs/README.md)
