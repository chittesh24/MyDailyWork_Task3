# 🚀 Installation Guide - Zero to Deployed in 5 Minutes

This guide gets you from zero to a fully deployed image captioning system in the fastest way possible.

---

## ⚡ Quick Install (Recommended)

### Prerequisites
- Docker Desktop installed ([download here](https://www.docker.com/get-started))
- 4GB+ RAM
- 10GB free disk space

### One-Command Install

```bash
# Clone repository
git clone https://github.com/yourusername/image-captioning-system.git
cd image_captioning_system

# Run quick setup
python3 scripts/quick_setup.py

# Deploy everything
bash scripts/one_click_deploy.sh
```

**That's it!** 🎉

Access your application at:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 📋 Step-by-Step Install

If you prefer manual control:

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/image-captioning-system.git
cd image_captioning_system
```

### Step 2: Validate Project

```bash
python3 scripts/validate_project.py
```

This checks:
- ✅ All required files exist
- ✅ Dependencies listed
- ✅ Configuration files valid

### Step 3: Setup Environment

```bash
# Backend environment
cp backend/.env.example backend/.env

# Generate secret key and update .env
python3 -c "import secrets; print(f'SECRET_KEY={secrets.token_hex(32)}')"

# Frontend environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > frontend/.env.local
```

### Step 4: Start Services

```bash
docker-compose up -d
```

### Step 5: Initialize Database

```bash
docker-compose exec backend python -c "from database.database import init_db; init_db()"
```

### Step 6: Verify Health

```bash
bash scripts/health_check.sh
```

---

## 🐳 Docker Installation Details

### What Gets Installed

The Docker setup includes:
- PostgreSQL 15 (database)
- Python 3.11 backend (FastAPI)
- Node.js 18 frontend (Next.js)
- All dependencies automatically

### Container Management

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart backend

# Rebuild after code changes
docker-compose up -d --build

# Remove everything (including data)
docker-compose down -v
```

---

## 💻 Local Development Install (Without Docker)

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database URL

# Run development server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Setup environment
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

### Database Setup

You'll need PostgreSQL installed locally:

```bash
# Install PostgreSQL 15
# Then create database
createdb image_captions

# Run schema
psql -d image_captions -f backend/database/schema.sql

# Update DATABASE_URL in backend/.env
DATABASE_URL=postgresql://user:password@localhost:5432/image_captions
```

---

## ☁️ Cloud Deployment (Free Tier)

### Automated Cloud Deploy

```bash
python3 scripts/setup_free_tier.py
```

This interactive wizard deploys to:
- **Supabase** (Database) - 500MB free
- **Render** (Backend) - 750 hrs/month free
- **Vercel** (Frontend) - Unlimited free
- **Total: $0/month**

### Manual Cloud Deploy

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # Backend
lsof -i :3000  # Frontend

# Kill process
kill -9 <PID>

# Or change port in docker-compose.yml
```

### Docker Not Starting

```bash
# Check Docker is running
docker ps

# Restart Docker Desktop
# OR
sudo systemctl restart docker  # Linux
```

### Database Connection Error

```bash
# Check database is ready
docker-compose exec db pg_isready -U postgres

# Restart database
docker-compose restart db

# View database logs
docker-compose logs db
```

### Frontend Build Error

```bash
# Clear Next.js cache
cd frontend
rm -rf .next
npm install
npm run build
```

### Backend Import Errors

```bash
# Test imports
python3 scripts/test_imports.py

# Reinstall dependencies
cd backend
pip install -r requirements.txt --force-reinstall
```

---

## ✅ Verification Checklist

After installation, verify everything works:

- [ ] Backend responds: `curl http://localhost:8000/`
- [ ] Frontend loads: Open http://localhost:3000
- [ ] Can register user
- [ ] Can login
- [ ] Can access dashboard
- [ ] Can generate API key
- [ ] Database connected: `docker-compose exec db psql -U postgres`

---

## 📦 What's Included

After installation, you have:

✅ **Backend API**
- FastAPI server
- JWT authentication
- PostgreSQL database
- Rate limiting
- File upload handling

✅ **Frontend UI**
- Next.js 14 application
- Dark/Light mode
- 6 color themes
- Responsive design
- Image upload interface

✅ **ML Components**
- CNN + Transformer model architecture
- Training scripts
- Inference pipeline
- Model comparison tools

✅ **Deployment**
- Docker configuration
- Free tier deployment scripts
- Production configs

---

## 🎯 Next Steps

1. **Train a Model:**
   ```bash
   bash scripts/train_flickr8k.sh
   ```

2. **Customize Theme:**
   - Visit http://localhost:3000/settings
   - Choose your preferred theme

3. **Generate Captions:**
   - Upload an image on the homepage
   - Get instant captions!

4. **Deploy to Production:**
   ```bash
   python3 scripts/setup_free_tier.py
   ```

---

## 📚 Additional Resources

- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) - Detailed deployment
- [DEPLOYMENT_READY.md](DEPLOYMENT_READY.md) - Pre-deployment checklist
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md) - Complete features

---

## 🆘 Getting Help

1. **Run Diagnostics:**
   ```bash
   python3 scripts/validate_project.py
   bash scripts/health_check.sh
   ```

2. **Check Logs:**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

3. **Common Issues:**
   See troubleshooting section above

---

## ✨ Success!

If all checks pass, you now have:
- ✅ Fully functional image captioning system
- ✅ Production-ready deployment
- ✅ Free hosting option available
- ✅ Complete documentation

**Enjoy your image captioning system!** 🎉
