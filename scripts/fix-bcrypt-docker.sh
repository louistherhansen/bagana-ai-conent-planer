#!/bin/bash
# Script to fix bcrypt in running Docker container
# This is a temporary fix - rebuild the image for permanent solution

echo "🔧 Fixing bcrypt in frontend container..."

# Install build dependencies and rebuild bcrypt as root
docker-compose exec -u root frontend sh -c "
apk add --no-cache python3 make g++ 2>/dev/null || true
cd /app
npm rebuild bcrypt --build-from-source
"

if [ $? -eq 0 ]; then
    echo "✅ bcrypt has been rebuilt successfully!"
    echo ""
    echo "Testing bcrypt..."
    docker-compose exec frontend node -e "try { require('bcrypt'); console.log('✅ bcrypt is available'); } catch(e) { console.log('❌ bcrypt is NOT available:', e.message); }"
else
    echo "❌ Failed to rebuild bcrypt. Please rebuild the Docker image:"
    echo "   docker-compose build frontend"
    echo "   docker-compose up -d frontend"
fi
