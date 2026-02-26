# 🚀 Quick Test Guide - Image Captioning System

## Prerequisites

- **Docker Desktop** installed and running
- At least 4GB RAM available
- Internet connection (for first-time image pull)

## Option 1: Quick Docker Test (Recommended)

This is the **easiest way** to test without installing Python dependencies locally.

### Step 1: Start Services

```bash
cd image_captioning_system
docker-compose up -d --build
```

**First run takes 5-10 minutes** (downloads images and builds containers)

### Step 2: Wait for Services

```bash
# Check status
docker-compose ps

# Watch logs (optional)
docker-compose logs -f
```

Wait until you see:
- ✅ Database: "database system is ready"
- ✅ Backend: "Application startup complete"
- ✅ Frontend: "compiled successfully"

### Step 3: Access the App

Open your browser:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

### Step 4: Test with Sample Images

Sample images are in `test_images/`:
- `beach.jpg` - Beach scene
- `mountain.jpg` - Mountain landscape
- `city.jpg` - City buildings
- `tree.jpg` - Nature scene

**Upload any image** and get a caption!

⚠️ **Note**: Currently runs in DEMO mode with placeholder captions.
For real AI captions, you need to train or download a model.

---

## Option 2: Without Docker (Python Required)

### Prerequisites
```bash
# Python 3.11+
python --version

# PostgreSQL 15
psql --version
```

### Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend (in new terminal)
cd frontend
npm install
```

### Setup Database

```bash
# Start PostgreSQL
# Create database
psql -U postgres -c "CREATE DATABASE image_captions;"

# Run schema
psql -U postgres -d image_captions -f backend/database/schema.sql
```

### Configure Environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your database credentials
```

### Start Services

```bash
# Terminal 1: Backend
cd backend
python run.py

# Terminal 2: Frontend
cd frontend
npm run dev
```

Access at http://localhost:3000

---

## Troubleshooting

### Docker Issues

**Containers won't start:**
```bash
# Clean up and retry
docker-compose down
docker system prune -f
docker-compose up -d --build
```

**Port already in use:**
```bash
# Stop conflicting services
# Windows: netstat -ano | findstr :3000
# Linux/Mac: lsof -i :3000

# Or change ports in docker-compose.yml
```

**Out of memory:**
```bash
# Increase Docker memory limit
# Docker Desktop → Settings → Resources → Memory (set to 4GB+)
```

### Check Logs

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f backend
```

### Verify Health

```bash
# Check all containers
docker-compose ps

# Test database
docker-compose exec db pg_isready -U postgres

# Test backend API
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000
```

---

## Stop Services

```bash
# Stop (keeps data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove everything including volumes
docker-compose down -v
```

---

## Next Steps

Once it's working:

1. **Register an account** at http://localhost:3000/register
2. **Login** and get your API key
3. **Upload test images** from `test_images/`
4. **View API docs** at http://localhost:8000/docs
5. **Check dashboard** for usage stats

### To Get Real AI Captions:

```bash
# Option 1: Train your own model (2-3 hours on GPU)
bash scripts/train_flickr8k.sh

# Option 2: Download pre-trained model
# Place in backend/checkpoints/
#   - best_model.pth
#   - vocab.json
```

---

## Sample API Usage

### cURL
```bash
# Get token
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Generate caption
curl -X POST http://localhost:8000/caption/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test_images/beach.jpg"
```

### Python
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    data={"username": "test@example.com", "password": "password123"}
)
token = response.json()["access_token"]

# Generate caption
files = {"file": open("test_images/beach.jpg", "rb")}
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    "http://localhost:8000/caption/generate",
    files=files,
    headers=headers
)
print(response.json()["caption"])
```

---

## Questions?

Check the detailed documentation:
- [INSTALL.md](INSTALL.md) - Complete installation guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [START_HERE.md](START_HERE.md) - Overview and features
- [README.md](README.md) - Project documentation

**Need help?** Open an issue on GitHub!
