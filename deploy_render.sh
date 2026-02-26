#!/bin/bash

# One-Click Render Deployment Script

echo "🚀 Image Captioning System - Render Deployment"
echo "=============================================="
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit for deployment"
    echo "✅ Git initialized"
else
    echo "✅ Git already initialized"
fi

echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Push to GitHub:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git"
echo "   git push -u origin main"
echo ""
echo "2. Go to Render.com:"
echo "   https://render.com"
echo ""
echo "3. Create New Web Service and use these settings:"
echo "   • Connect your GitHub repo"
echo "   • Build Command: pip install -r backend/requirements.txt"
echo "   • Start Command: cd backend && uvicorn api.main:app --host 0.0.0.0 --port \$PORT"
echo ""
echo "4. Add Environment Variables:"
echo "   USE_PRETRAINED=true"
echo "   DEVICE=cpu"
echo "   SECRET_KEY=$(openssl rand -base64 32)"
echo "   DATABASE_URL=sqlite:///./database/local.db"
echo "   ALLOWED_ORIGINS=*"
echo ""
echo "5. Click 'Create Web Service' and wait 5-10 minutes!"
echo ""
echo "📖 Full guide: See EASY_DEPLOY.md"
echo ""
