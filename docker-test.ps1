# Docker Local Test Script for Windows PowerShell

Write-Host "🐳 BAGANA AI - Docker Local Test" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "1. Checking Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

try {
    $composeVersion = docker-compose --version
    Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed or not in PATH" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check .env file
Write-Host "2. Checking .env file..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "✅ .env file exists" -ForegroundColor Green
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
    if (Test-Path .env.example) {
        Write-Host "Creating .env from .env.example..." -ForegroundColor Yellow
        Copy-Item .env.example .env
        Write-Host "✅ Created .env file" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env file with your configuration" -ForegroundColor Yellow
    } else {
        Write-Host "❌ .env.example not found" -ForegroundColor Red
        exit 1
    }
}
Write-Host ""

# Check Docker daemon
Write-Host "3. Checking Docker daemon..." -ForegroundColor Yellow
try {
    docker info | Out-Null
    Write-Host "✅ Docker daemon is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker daemon is not running" -ForegroundColor Red
    Write-Host "   Please start Docker Desktop" -ForegroundColor Yellow
    exit 1
}
Write-Host ""

# Build images
Write-Host "4. Building Docker images..." -ForegroundColor Yellow
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Build failed" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Build completed" -ForegroundColor Green
Write-Host ""

# Start services
Write-Host "5. Starting services..." -ForegroundColor Yellow
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Services started" -ForegroundColor Green
Write-Host ""

# Wait for services
Write-Host "6. Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10
Write-Host ""

# Check service status
Write-Host "7. Checking service status..." -ForegroundColor Yellow
docker-compose ps
Write-Host ""

# Check logs
Write-Host "8. Recent logs:" -ForegroundColor Yellow
docker-compose logs --tail=20
Write-Host ""

Write-Host "✅ Docker test setup completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Services:" -ForegroundColor Cyan
Write-Host "  - Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  - Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "  - Database: localhost:5432" -ForegroundColor White
Write-Host ""
Write-Host "Commands:" -ForegroundColor Cyan
Write-Host "  - View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  - Stop: docker-compose stop" -ForegroundColor White
Write-Host "  - Stop & Remove: docker-compose down" -ForegroundColor White
Write-Host "  - Restart: docker-compose restart" -ForegroundColor White
