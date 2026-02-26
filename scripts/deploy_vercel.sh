#!/bin/bash
# Deploy frontend to Vercel (Free Tier)

set -e

echo "========================================"
echo "Deploying to Vercel (Free Tier)"
echo "========================================"

# Check if vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "⚠️  Vercel CLI not found. Installing..."
    npm install -g vercel
fi

echo ""
echo "Step 1: Checking Vercel authentication..."
if ! vercel whoami &> /dev/null; then
    echo "Please login to Vercel:"
    vercel login
fi

echo "✅ Authenticated"

# Navigate to frontend
cd frontend

echo ""
echo "Step 2: Installing dependencies..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "✅ Dependencies installed"

echo ""
echo "Step 3: Building project..."
npm run build

echo "✅ Build successful"

echo ""
echo "Step 4: Deploying to Vercel..."

# Deploy
vercel --prod

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Your frontend is now live!"
echo ""
echo "Next steps:"
echo "1. Copy your Vercel URL"
echo "2. Update ALLOWED_ORIGINS in Render backend"
echo "3. Update NEXT_PUBLIC_API_URL in Vercel environment variables"
echo ""
echo "To update environment variables:"
echo "  vercel env add NEXT_PUBLIC_API_URL"
echo "  Enter: https://your-api.onrender.com"
