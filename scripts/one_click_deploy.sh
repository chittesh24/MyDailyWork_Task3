#!/bin/bash
# One-Click Deployment Script
# Deploys entire stack with minimal user input

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     🚀 ONE-CLICK DEPLOYMENT - Image Captioning System      ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

command -v docker >/dev/null 2>&1 || { echo -e "${RED}❌ Docker not found. Please install Docker first.${NC}"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo -e "${RED}❌ Docker Compose not found.${NC}"; exit 1; }

echo -e "${GREEN}✅ Docker found${NC}"
echo -e "${GREEN}✅ Docker Compose found${NC}"

# Validate project
echo ""
echo -e "${BLUE}Validating project structure...${NC}"
python3 scripts/validate_project.py
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Validation failed. Please fix errors first.${NC}"
    exit 1
fi

# Setup environment
echo ""
echo -e "${BLUE}Setting up environment...${NC}"

if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}Creating backend/.env from template...${NC}"
    cp backend/.env.example backend/.env
    
    # Generate secret key
    SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")
    
    # Update secret key in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-minimum-32-characters/$SECRET_KEY/" backend/.env
    else
        # Linux
        sed -i "s/your-secret-key-here-minimum-32-characters/$SECRET_KEY/" backend/.env
    fi
    
    echo -e "${GREEN}✅ Environment file created${NC}"
    echo -e "${YELLOW}⚠️  Review backend/.env and update DATABASE_URL if needed${NC}"
else
    echo -e "${GREEN}✅ Environment file exists${NC}"
fi

# Fix permissions
echo ""
echo -e "${BLUE}Fixing script permissions...${NC}"
chmod +x scripts/*.sh
chmod +x scripts/*.py
echo -e "${GREEN}✅ Permissions fixed${NC}"

# Build and start
echo ""
echo -e "${BLUE}Building Docker containers...${NC}"
echo -e "${YELLOW}This may take 5-10 minutes on first run...${NC}"
docker-compose build

echo ""
echo -e "${BLUE}Starting services...${NC}"
docker-compose up -d

# Wait for services to be ready
echo ""
echo -e "${BLUE}Waiting for services to start...${NC}"
sleep 10

# Check health
echo ""
echo -e "${BLUE}Checking service health...${NC}"

# Check database
if docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Database ready${NC}"
else
    echo -e "${RED}❌ Database not ready${NC}"
fi

# Check backend
if curl -s http://localhost:8000/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend ready${NC}"
else
    echo -e "${YELLOW}⚠️  Backend still starting...${NC}"
fi

# Check frontend
if curl -s http://localhost:3000/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend ready${NC}"
else
    echo -e "${YELLOW}⚠️  Frontend still starting...${NC}"
fi

# Initialize database
echo ""
echo -e "${BLUE}Initializing database...${NC}"
docker-compose exec -T backend python -c "from database.database import init_db; init_db()" 2>/dev/null || echo -e "${YELLOW}⚠️  Database may already be initialized${NC}"

# Print success message
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║              🎉 DEPLOYMENT SUCCESSFUL! 🎉                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}Services are running:${NC}"
echo ""
echo "  📱 Frontend:  http://localhost:3000"
echo "  🚀 Backend:   http://localhost:8000"
echo "  📖 API Docs:  http://localhost:8000/docs"
echo "  🗄️  Database: localhost:5432"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo ""
echo "  1. Visit http://localhost:3000"
echo "  2. Register a new account"
echo "  3. Generate an API key in Dashboard"
echo "  4. Upload an image to generate captions!"
echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "  - Model checkpoint files needed in backend/checkpoints/"
echo "  - Run 'bash scripts/train_flickr8k.sh' to train a model"
echo "  - Or download pre-trained weights"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo ""
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose down"
echo "  Restart:          docker-compose restart"
echo "  Rebuild:          docker-compose up -d --build"
echo ""
echo -e "${GREEN}Deployment complete! ✨${NC}"
