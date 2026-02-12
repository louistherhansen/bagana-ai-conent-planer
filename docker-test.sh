#!/bin/bash
# Docker Local Test Script

echo "🐳 BAGANA AI - Docker Local Test"
echo "=================================="
echo ""

# Check Docker
echo "1. Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi
echo "✅ Docker: $(docker --version)"

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed"
    exit 1
fi
echo "✅ Docker Compose: $(docker-compose --version)"
echo ""

# Check .env file
echo "2. Checking .env file..."
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file"
        echo "⚠️  Please edit .env file with your configuration"
    else
        echo "❌ .env.example not found"
        exit 1
    fi
else
    echo "✅ .env file exists"
fi
echo ""

# Check required environment variables
echo "3. Checking required environment variables..."
source .env 2>/dev/null || true

if [ -z "$DB_PASSWORD" ]; then
    echo "⚠️  DB_PASSWORD is not set in .env"
    echo "   Please set DB_PASSWORD in .env file"
fi

if [ -z "$NEXTAUTH_SECRET" ]; then
    echo "⚠️  NEXTAUTH_SECRET is not set in .env"
    echo "   Generating random NEXTAUTH_SECRET..."
    RANDOM_SECRET=$(openssl rand -base64 32 2>/dev/null || echo "change-this-secret-$(date +%s)")
    echo "   Add this to .env: NEXTAUTH_SECRET=$RANDOM_SECRET"
fi
echo ""

# Build images
echo "4. Building Docker images..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi
echo "✅ Build completed"
echo ""

# Start services
echo "5. Starting services..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi
echo "✅ Services started"
echo ""

# Wait for services to be healthy
echo "6. Waiting for services to be ready..."
sleep 10

# Check service status
echo "7. Checking service status..."
docker-compose ps
echo ""

# Check logs
echo "8. Recent logs:"
docker-compose logs --tail=20
echo ""

echo "✅ Docker test setup completed!"
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:3000"
echo "  - Backend:  http://localhost:8000"
echo "  - Database: localhost:5432"
echo ""
echo "Commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop: docker-compose stop"
echo "  - Stop & Remove: docker-compose down"
echo "  - Restart: docker-compose restart"
