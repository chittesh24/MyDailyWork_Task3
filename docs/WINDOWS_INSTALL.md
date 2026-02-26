# 🪟 Windows Installation Guide

## Quick Docker Setup (Easiest)

### 1. Install Docker Desktop

Download and install: https://www.docker.com/products/docker-desktop

**After installation:**
- Restart your computer
- Open Docker Desktop
- Wait for "Docker is running" status

### 2. Clone or Download Project

```powershell
# If you have Git
git clone https://github.com/yourusername/image-captioning-system.git
cd image-captioning_system

# Or download ZIP and extract
```

### 3. Start Application

```powershell
# Navigate to project
cd image_captioning_system

# Start services (takes 5-10 min first time)
docker-compose up -d --build
```

### 4. Check Status

```powershell
# View running containers
docker-compose ps

# Should see 3 services running:
# - caption_db (database)
# - caption_backend (API)
# - caption_frontend (web app)
```

### 5. Access Application

Open browser: http://localhost:3000

**Test images** are in `test_images\` folder!

---

## Without Docker (Manual Setup)

### Prerequisites

1. **Python 3.11**
   - Download: https://www.python.org/downloads/
   - ✅ Check "Add Python to PATH"
   - Verify: `python --version`

2. **Node.js 18+**
   - Download: https://nodejs.org/
   - Verify: `node --version`

3. **PostgreSQL 15**
   - Download: https://www.postgresql.org/download/windows/
   - Remember your password!
   - Verify: `psql --version`

### Backend Setup

```powershell
# Navigate to backend
cd image_captioning_system\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If you get execution policy error:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Install dependencies
pip install -r requirements.txt
```

### Database Setup

```powershell
# Start PostgreSQL service
# Windows Services → PostgreSQL → Start

# Create database
psql -U postgres
# Enter password when prompted

# In psql terminal:
CREATE DATABASE image_captions;
\q

# Load schema
psql -U postgres -d image_captions -f database\schema.sql
```

### Environment Configuration

```powershell
# Copy example config
copy .env.example .env

# Edit .env in Notepad
notepad .env

# Update DATABASE_URL with your password:
# DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/image_captions
```

### Start Backend

```powershell
# Make sure venv is activated (you should see (venv) in prompt)
.\venv\Scripts\Activate.ps1

# Start server
python run.py

# Should see: "Application startup complete at http://0.0.0.0:8000"
```

### Frontend Setup (New PowerShell Window)

```powershell
# Navigate to frontend
cd image_captioning_system\frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Should see: "ready - started server on 0.0.0.0:3000"
```

### Access Application

Open browser: http://localhost:3000

---

## Common Windows Issues

### 1. Docker Won't Start

**Issue:** "Docker Desktop starting..." forever

**Fix:**
```powershell
# Enable Windows features
# Control Panel → Programs → Turn Windows features on/off
# Enable:
#  - Hyper-V
#  - Windows Subsystem for Linux
#  - Virtual Machine Platform

# Restart computer
```

### 2. Port Already in Use

**Issue:** "Port 3000 is already in use"

**Fix:**
```powershell
# Find process using port
netstat -ano | findstr :3000

# Kill process (use PID from above)
taskkill /PID <PID> /F

# Or use different port in docker-compose.yml:
# ports:
#   - "3001:3000"  # Use 3001 instead
```

### 3. PostgreSQL Connection Failed

**Issue:** "Could not connect to database"

**Fix:**
```powershell
# Check PostgreSQL is running
# Windows Services → PostgreSQL 15 → Status should be "Running"

# If not, start it:
net start postgresql-x64-15

# Check connection:
psql -U postgres -d image_captions

# If password error, reset .env DATABASE_URL
```

### 4. Python Module Not Found

**Issue:** "ModuleNotFoundError: No module named 'fastapi'"

**Fix:**
```powershell
# Make sure venv is activated
.\venv\Scripts\Activate.ps1

# Reinstall requirements
pip install -r requirements.txt

# If still failing, update pip:
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. npm install Fails

**Issue:** "npm ERR! code ENOENT"

**Fix:**
```powershell
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
Remove-Item -Recurse -Force node_modules
Remove-Item package-lock.json

# Reinstall
npm install

# If still failing, try:
npm install --legacy-peer-deps
```

### 6. PowerShell Script Execution Error

**Issue:** "cannot be loaded because running scripts is disabled"

**Fix:**
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Or bypass for one session:
powershell -ExecutionPolicy Bypass
```

---

## Verify Installation

### Check All Services

```powershell
# In project root
.\scripts\health_check.sh

# Or manually:

# 1. Database
docker-compose exec db pg_isready -U postgres

# 2. Backend
curl http://localhost:8000/docs

# 3. Frontend
curl http://localhost:3000
```

### Test Image Upload

1. Open http://localhost:3000
2. Register account
3. Login
4. Upload `test_images\beach.jpg`
5. See caption generated!

---

## Useful Commands

```powershell
# Docker commands
docker-compose ps                    # Check status
docker-compose logs backend          # View backend logs
docker-compose logs -f               # Follow all logs
docker-compose restart               # Restart all
docker-compose down                  # Stop all
docker-compose up -d --build         # Rebuild and start

# Stop services
docker-compose stop                  # Stop (keep data)
docker-compose down                  # Stop and remove
docker-compose down -v               # Remove everything

# Database access
docker-compose exec db psql -U postgres -d image_captions

# Backend shell
docker-compose exec backend bash

# View container stats
docker stats
```

---

## Next Steps

✅ Application running? Great!

Now:
1. **Register** at http://localhost:3000/register
2. **Test upload** with sample images
3. **View API docs** at http://localhost:8000/docs
4. **Train model** (optional): `bash scripts/train_flickr8k.sh`

---

## Getting Help

- **Logs not helping?** Run with verbose output:
  ```powershell
  docker-compose up --build  # Without -d flag
  ```

- **Still stuck?**
  - Check [QUICK_TEST.md](QUICK_TEST.md)
  - Check [INSTALL.md](INSTALL.md)
  - Review Docker Desktop logs
  - Check Windows Event Viewer

**Happy coding!** 🚀
