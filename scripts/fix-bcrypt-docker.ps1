# Script to fix bcrypt in running Docker container
# This is a temporary fix - rebuild the image for permanent solution

Write-Host "🔧 Fixing bcrypt in frontend container..." -ForegroundColor Yellow

# Install build dependencies and rebuild bcrypt as root
docker-compose exec -u root frontend sh -c @"
apk add --no-cache python3 make g++ 2>/dev/null || true
cd /app
npm rebuild bcrypt --build-from-source
"@

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ bcrypt has been rebuilt successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Testing bcrypt..." -ForegroundColor Yellow
    docker-compose exec frontend node -e "try { require('bcrypt'); console.log('✅ bcrypt is available'); } catch(e) { console.log('❌ bcrypt is NOT available:', e.message); }"
} else {
    Write-Host "❌ Failed to rebuild bcrypt. Please rebuild the Docker image:" -ForegroundColor Red
    Write-Host "   docker-compose build frontend" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d frontend" -ForegroundColor Cyan
}
