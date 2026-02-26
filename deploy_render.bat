@echo off
REM One-Click Render Deployment Script for Windows

echo ====================================================
echo    Image Captioning System - Render Deployment
echo ====================================================
echo.

REM Check if git is initialized
if not exist .git (
    echo [92mInitializing Git repository...[0m
    git init
    git add .
    git commit -m "Initial commit for deployment"
    echo [92mGit initialized[0m
) else (
    echo [92mGit already initialized[0m
)

echo.
echo [96mNext Steps:[0m
echo.
echo 1. Push to GitHub:
echo    git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
echo    git push -u origin main
echo.
echo 2. Go to Render.com:
echo    https://render.com
echo.
echo 3. Create New Web Service and use these settings:
echo    - Connect your GitHub repo
echo    - Build Command: pip install -r backend/requirements.txt
echo    - Start Command: cd backend ^&^& uvicorn api.main:app --host 0.0.0.0 --port $PORT
echo.
echo 4. Add Environment Variables:
echo    USE_PRETRAINED=true
echo    DEVICE=cpu
echo    SECRET_KEY=your-random-secret-key-minimum-32-characters
echo    DATABASE_URL=sqlite:///./database/local.db
echo    ALLOWED_ORIGINS=*
echo.
echo 5. Click 'Create Web Service' and wait 5-10 minutes!
echo.
echo [93mFull guide: See EASY_DEPLOY.md[0m
echo.
pause
