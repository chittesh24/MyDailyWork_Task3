#!/bin/bash
# Deploy backend to Render.com (Free Tier)

set -e

echo "========================================"
echo "Deploying to Render.com (Free Tier)"
echo "========================================"

# Check if render CLI is installed
if ! command -v render &> /dev/null; then
    echo "⚠️  Render CLI not found. Installing..."
    npm install -g @render/cli
fi

# Check if logged in
echo ""
echo "Step 1: Checking Render authentication..."
if ! render whoami &> /dev/null; then
    echo "Please login to Render:"
    render login
fi

echo "✅ Authenticated"

# Create render.yaml if not exists
if [ ! -f "render.yaml" ]; then
    echo ""
    echo "Creating render.yaml configuration..."
    
    cat > render.yaml << 'EOF'
services:
  - type: web
    name: image-caption-api
    env: python
    region: oregon
    plan: free
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && uvicorn api.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: image-caption-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: DEVICE
        value: cpu
      - key: MODEL_CHECKPOINT_PATH
        value: /opt/render/project/src/backend/checkpoints/best_model.pth
      - key: VOCAB_PATH
        value: /opt/render/project/src/backend/checkpoints/vocab.json
      - key: ALLOWED_ORIGINS
        value: https://your-frontend.vercel.app

databases:
  - name: image-caption-db
    plan: free
    databaseName: image_captions
    user: postgres
EOF

    echo "✅ Created render.yaml"
fi

echo ""
echo "Step 2: Preparing deployment..."

# Check for model files
if [ ! -f "backend/checkpoints/best_model.pth" ]; then
    echo "⚠️  Model checkpoint not found!"
    echo "Please ensure you have:"
    echo "  - backend/checkpoints/best_model.pth"
    echo "  - backend/checkpoints/vocab.json"
    echo ""
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "Step 3: Deploying to Render..."
echo ""
echo "Visit: https://dashboard.render.com"
echo ""
echo "Manual steps:"
echo "1. Create New > Web Service"
echo "2. Connect your GitHub repository"
echo "3. Select branch: main"
echo "4. Root directory: backend"
echo "5. Build command: pip install -r requirements.txt"
echo "6. Start command: uvicorn api.main:app --host 0.0.0.0 --port \$PORT"
echo "7. Add environment variables from .env.example"
echo "8. Create PostgreSQL database (free tier)"
echo "9. Deploy!"
echo ""
echo "Your API will be available at: https://your-service.onrender.com"
echo ""
echo "⚠️  Important:"
echo "- Upload model files via Render dashboard or use external storage"
echo "- Free tier sleeps after 15min inactivity (cold start: 30s)"
echo "- 750 hours/month free (enough for testing)"
