#!/bin/bash
# Script untuk test Docker deployment secara lokal

set -e

echo "🐳 BAGANA AI - Docker Local Testing"
echo "===================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker tidak terinstall!${NC}"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo -e "${RED}❌ Docker Compose tidak terinstall!${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker dan Docker Compose terdeteksi${NC}"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  File .env tidak ditemukan${NC}"
    if [ -f .env.production.example ]; then
        echo "Copying .env.production.example to .env..."
        cp .env.production.example .env
        echo -e "${YELLOW}⚠️  Silakan edit .env dengan nilai lokal Anda${NC}"
    else
        echo -e "${RED}❌ File .env.production.example tidak ditemukan!${NC}"
        exit 1
    fi
fi

echo "📋 Step 1: Building Docker images..."
echo "-----------------------------------"
docker-compose build --no-cache

echo ""
echo "📋 Step 2: Starting services..."
echo "-----------------------------------"
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 10

echo ""
echo "📋 Step 3: Checking service status..."
echo "-----------------------------------"
docker-compose ps

echo ""
echo "📋 Step 4: Checking service health..."
echo "-----------------------------------"

# Check PostgreSQL
echo -n "PostgreSQL: "
if docker-compose exec -T postgres pg_isready -U bagana_user &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${RED}❌ Not ready${NC}"
fi

# Check Backend
echo -n "Backend API: "
if curl -s http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Not ready (might need more time)${NC}"
fi

# Check Frontend
echo -n "Frontend: "
if curl -s http://localhost:3000 &> /dev/null; then
    echo -e "${GREEN}✅ Healthy${NC}"
else
    echo -e "${YELLOW}⚠️  Not ready (might need more time)${NC}"
fi

echo ""
echo "📋 Step 5: Service URLs"
echo "-----------------------------------"
echo "Frontend:  http://localhost:3000"
echo "Backend:   http://localhost:8000"
echo "Database:  localhost:5432"
echo ""

echo "📋 Step 6: View logs"
echo "-----------------------------------"
echo "View all logs:    docker-compose logs -f"
echo "View frontend:    docker-compose logs -f frontend"
echo "View backend:     docker-compose logs -f backend"
echo "View database:    docker-compose logs -f postgres"
echo ""

echo "📋 Step 7: Stop services"
echo "-----------------------------------"
echo "Stop all:         docker-compose stop"
echo "Stop & remove:    docker-compose down"
echo "Stop & cleanup:   docker-compose down -v"
echo ""

echo -e "${GREEN}✅ Docker local testing setup complete!${NC}"
echo ""
echo "Next steps:"
echo "1. Initialize database: docker-compose exec backend python scripts/init-auth-db.py"
echo "2. Access frontend: http://localhost:3000"
echo "3. Check logs if any issues: docker-compose logs -f"
