#!/bin/bash
# Health check script for deployment validation

echo "🏥 Running Health Checks..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

ERRORS=0

# Check database
echo -n "Database (Port 5432): "
if nc -z localhost 5432 2>/dev/null || docker-compose exec -T db pg_isready -U postgres >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not responding${NC}"
    ((ERRORS++))
fi

# Check backend
echo -n "Backend (Port 8000): "
if curl -s http://localhost:8000/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not responding${NC}"
    ((ERRORS++))
fi

# Check frontend
echo -n "Frontend (Port 3000): "
if curl -s http://localhost:3000/ >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not responding${NC}"
    ((ERRORS++))
fi

# Check backend API endpoints
echo -n "Backend API Health: "
HEALTH=$(curl -s http://localhost:8000/ | grep -o '"status":"running"')
if [ ! -z "$HEALTH" ]; then
    echo -e "${GREEN}✅ Running${NC}"
else
    echo -e "${YELLOW}⚠️  Unknown status${NC}"
fi

# Summary
echo ""
if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✅ All services healthy!${NC}"
    exit 0
else
    echo -e "${RED}❌ $ERRORS service(s) unhealthy${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  docker-compose logs -f      # View all logs"
    echo "  docker-compose ps           # Check container status"
    echo "  docker-compose restart      # Restart services"
    exit 1
fi
