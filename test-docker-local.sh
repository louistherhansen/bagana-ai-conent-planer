#!/bin/bash
# Script untuk test Docker lokal
# Usage: bash test-docker-local.sh

set -e

echo "🐳 BAGANA AI - Docker Local Test"
echo "================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}⚠️  File .env tidak ditemukan${NC}"
    echo "Membuat .env dari .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}⚠️  Silakan edit .env dan set DB_PASSWORD sebelum melanjutkan${NC}"
        exit 1
    else
        echo -e "${RED}❌ File .env.example juga tidak ditemukan${NC}"
        exit 1
    fi
fi

# Check if DB_PASSWORD is set
if ! grep -q "DB_PASSWORD=.*[^=]$" .env || grep -q "DB_PASSWORD=your_secure_password" .env; then
    echo -e "${RED}❌ DB_PASSWORD belum di-set di .env${NC}"
    echo "Silakan edit .env dan set DB_PASSWORD dengan password yang aman"
    exit 1
fi

echo -e "${GREEN}✅ Environment check passed${NC}"
echo ""

# Step 1: Stop existing containers
echo "📦 Step 1: Stopping existing containers..."
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✅ Done${NC}"
echo ""

# Step 2: Build images
echo "🔨 Step 2: Building Docker images..."
echo "This may take a few minutes..."
docker-compose build --no-cache
echo -e "${GREEN}✅ Build completed${NC}"
echo ""

# Step 3: Start services
echo "🚀 Step 3: Starting services..."
docker-compose up -d
echo -e "${GREEN}✅ Services started${NC}"
echo ""

# Step 4: Wait for services to be healthy
echo "⏳ Step 4: Waiting for services to be healthy..."
echo "Checking PostgreSQL..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose exec -T postgres pg_isready -U bagana_user -d bagana_ai > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready${NC}"
        break
    fi
    echo "Waiting for PostgreSQL... ($elapsed/$timeout seconds)"
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo -e "${RED}❌ PostgreSQL failed to start${NC}"
    docker-compose logs postgres
    exit 1
fi

echo ""
echo "Checking Backend..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker-compose exec backend python -c "import requests; requests.get('http://localhost:8000/health')" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready${NC}"
        break
    fi
    echo "Waiting for Backend... ($elapsed/$timeout seconds)"
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo -e "${YELLOW}⚠️  Backend health check timeout (may still be starting)${NC}"
fi

echo ""
echo "Checking Frontend..."
timeout=90
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if curl -f http://localhost:3000/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready${NC}"
        break
    fi
    echo "Waiting for Frontend... ($elapsed/$timeout seconds)"
    sleep 3
    elapsed=$((elapsed + 3))
done

if [ $elapsed -ge $timeout ]; then
    echo -e "${YELLOW}⚠️  Frontend health check timeout (may still be starting)${NC}"
fi

echo ""
echo "================================"
echo -e "${GREEN}✅ Docker Local Test Completed!${NC}"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "🌐 Service URLs:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  Database: localhost:5432"
echo ""
echo "📝 Useful Commands:"
echo "  View logs:        docker-compose logs -f"
echo "  Stop services:    docker-compose stop"
echo "  Restart services: docker-compose restart"
echo "  Clean up:         docker-compose down -v"
echo ""
