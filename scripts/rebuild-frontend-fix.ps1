# Script to rebuild frontend with bcrypt fix
Write-Host "🔧 Rebuilding frontend Docker image with bcrypt fix..." -ForegroundColor Yellow
Write-Host ""

# Stop frontend container
Write-Host "Stopping frontend container..." -ForegroundColor Cyan
docker-compose stop frontend

# Rebuild frontend image
Write-Host "Building frontend image (this may take a few minutes)..." -ForegroundColor Cyan
docker-compose build frontend

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Build successful! Starting frontend..." -ForegroundColor Green
    
    # Start frontend
    docker-compose up -d frontend
    
    # Wait a bit for container to start
    Start-Sleep -Seconds 5
    
    # Test bcrypt
    Write-Host ""
    Write-Host "Testing bcrypt..." -ForegroundColor Cyan
    docker-compose exec frontend node -e "try { require('bcrypt'); console.log('✅ bcrypt is available'); } catch(e) { console.log('❌ bcrypt is NOT available:', e.message); }"
    
    Write-Host ""
    Write-Host "✅ Frontend rebuilt and started successfully!" -ForegroundColor Green
    Write-Host "You can now try logging in again." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Build failed. Please check the error messages above." -ForegroundColor Red
}
