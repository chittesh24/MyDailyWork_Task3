# 🐳 Docker-Only Testing Guide

**Easiest way to test - no Python/Node.js installation needed!**

## What You Need

- ✅ Docker Desktop installed
- ✅ 4GB+ RAM
- ✅ 10GB free disk space

## 3-Step Quick Start

### Step 1: Start Docker Desktop

Windows: Start Menu → Docker Desktop  
Mac: Applications → Docker Desktop

Wait for "Docker is running" 🐋

### Step 2: Start Application

```bash
cd image_captioning_system
docker-compose up -d --build
```

⏳ **First run takes 5-10 minutes** (downloads ~2GB)

### Step 3: Open Browser

http://localhost:3000

**Done!** 🎉

---

## Test It

### Sample Images

We've created 4 test images in `test_images/`:

```
test_images/
├── beach.jpg      (beach scene with sun)
├── mountain.jpg   (mountain landscape)
├── city.jpg       (city buildings)
└── tree.jpg       (nature with tree)
```

### How to Test

1. Open http://localhost:3000
2. Click **"Register"** or **"Get Started"**
3. Create account (email: test@test.com, password: test123)
4. Login
5. **Drag & drop** `test_images/beach.jpg`
6. See caption appear! ✨

---

## What's Running?

```bash
docker-compose ps
```

You should see:

| Service | Port | Status |
|---------|------|--------|
| caption_db | 5432 | Up |
| caption_backend | 8000 | Up |
| caption_frontend | 3000 | Up |

---

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| **Web App** | http://localhost:3000 | Upload images |
| **API Docs** | http://localhost:8000/docs | API documentation |
| **Backend** | http://localhost:8000 | REST API |
| **Database** | localhost:5432 | PostgreSQL |

---

## Useful Commands

### View Logs

```bash
# All services
docker-compose logs

# Just backend
docker-compose logs backend

# Follow live logs
docker-compose logs -f backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart one service
docker-compose restart backend
```

### Stop Services

```bash
# Stop (keeps data)
docker-compose stop

# Stop and remove containers
docker-compose down

# Remove everything (including database data)
docker-compose down -v
```

### Check Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Check database health
docker-compose exec db pg_isready -U postgres
```

---

## Demo Mode Explained

⚠️ **Currently running in DEMO mode**

This means:
- No trained AI model loaded
- Captions are **placeholder/generic**
- Everything else works normally (upload, API, database, auth)

### Example Demo Captions:
- "A scenic view with sky and landscape"
- "An image showing various objects"
- "A photograph with interesting elements"

### To Get Real AI Captions:

**Option 1: Train a model (requires GPU)**
```bash
docker-compose exec backend bash
python scripts/train_flickr8k.sh
```

**Option 2: Download pre-trained model**
- Download from HuggingFace/Google Drive
- Place in `backend/checkpoints/`:
  - `best_model.pth` (model weights)
  - `vocab.json` (vocabulary)

**Option 3: Use the demo for testing architecture only**
- Test API endpoints
- Test file uploads
- Test authentication
- Test database integration

---

## Troubleshooting

### Containers Won't Start

```bash
# Clean slate
docker-compose down -v
docker system prune -f
docker-compose up -d --build
```

### Port Conflicts

```bash
# Windows: Check what's using port 3000
netstat -ano | findstr :3000

# Mac/Linux: Check port usage
lsof -i :3000

# Change ports in docker-compose.yml if needed
```

### Out of Memory

```bash
# Docker Desktop → Settings → Resources
# Increase Memory to 4GB+
# Increase Swap to 2GB
# Click "Apply & Restart"
```

### Slow Performance

```bash
# Check resource usage
docker stats

# If CPU/Memory is maxed:
# - Close other applications
# - Increase Docker resources
# - Use smaller model (when training)
```

### Can't Access Localhost

```bash
# Try 127.0.0.1 instead of localhost
http://127.0.0.1:3000

# Or check Docker network
docker network ls
docker network inspect image_captioning_system_caption-network
```

---

## Testing the API

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click **"Authorize"**
3. Register/Login to get token
4. Try endpoints:
   - POST `/auth/register`
   - POST `/auth/login`
   - POST `/caption/generate`
   - GET `/caption/history`

### Using cURL

```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Login
curl -X POST http://localhost:8000/auth/login \
  -F "username=test@example.com" \
  -F "password=test123"

# Generate caption (replace TOKEN)
curl -X POST http://localhost:8000/caption/generate \
  -H "Authorization: Bearer TOKEN" \
  -F "file=@test_images/beach.jpg"
```

---

## What's Next?

✅ **Everything Working?**

1. Explore the dashboard: http://localhost:3000/dashboard
2. Try all sample images
3. Check API documentation
4. View logs to understand the flow
5. Train a real model (see training scripts)

📚 **Read More:**
- [QUICKSTART.md](QUICKSTART.md) - Feature overview
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Production deployment
- [README.md](README.md) - Full documentation

🚀 **Deploy for Free:**
```bash
python scripts/setup_free_tier.py
```

Deploys to Render + Vercel + Supabase for **$0/month**!

---

## Stop When Done

```bash
# Stop services (keeps data)
docker-compose stop

# Or remove everything
docker-compose down -v
```

**Enjoy testing!** 🎉
