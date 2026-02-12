# PowerShell script untuk test Docker deployment secara lokal

Write-Host "🐳 BAGANA AI - Docker Local Testing" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker terdeteksi" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker tidak terinstall!" -ForegroundColor Red
    Write-Host "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose terdeteksi" -ForegroundColor Green
} catch {
    try {
        docker compose version | Out-Null
        Write-Host "✅ Docker Compose terdeteksi" -ForegroundColor Green
    } catch {
        Write-Host "❌ Docker Compose tidak terinstall!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Host "⚠️  File .env tidak ditemukan" -ForegroundColor Yellow
    if (Test-Path .env.production.example) {
        Copy-Item .env.production.example .env
        Write-Host "✅ File .env dibuat dari .env.production.example" -ForegroundColor Green
        Write-Host "⚠️  Silakan edit .env dengan nilai lokal Anda" -ForegroundColor Yellow
    } else {
        Write-Host "❌ File .env.production.example tidak ditemukan!" -ForegroundColor Red
        exit 1
    }
}

Write-Host ""
Write-Host "📋 Step 1: Building Docker images..." -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
docker-compose build --no-cache

Write-Host ""
Write-Host "📋 Step 2: Starting services..." -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
docker-compose up -d

Write-Host ""
Write-Host "⏳ Waiting for services to be ready..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host ""
Write-Host "📋 Step 3: Checking service status..." -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "📋 Step 4: Checking service health..." -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan

# Check PostgreSQL
Write-Host -NoNewline "PostgreSQL: "
try {
    docker-compose exec -T postgres pg_isready -U bagana_user | Out-Null
    Write-Host "✅ Healthy" -ForegroundColor Green
} catch {
    Write-Host "❌ Not ready" -ForegroundColor Red
}

# Check Backend
Write-Host -NoNewline "Backend API: "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Healthy" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Not ready (might need more time)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Not ready (might need more time)" -ForegroundColor Yellow
}

# Check Frontend
Write-Host -NoNewline "Frontend: "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Healthy" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Not ready (might need more time)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Not ready (might need more time)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Step 5: Service URLs" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "Frontend:  http://localhost:3000"
Write-Host "Backend:   http://localhost:8000"
Write-Host "Database:  localhost:5432"
Write-Host ""

Write-Host "📋 Step 6: View logs" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "View all logs:    docker-compose logs -f"
Write-Host "View frontend:    docker-compose logs -f frontend"
Write-Host "View backend:     docker-compose logs -f backend"
Write-Host "View database:    docker-compose logs -f postgres"
Write-Host ""

Write-Host "📋 Step 7: Stop services" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "Stop all:         docker-compose stop"
Write-Host "Stop & remove:    docker-compose down"
Write-Host "Stop & cleanup:   docker-compose down -v"
Write-Host ""

Write-Host "✅ Docker local testing setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Initialize database: docker-compose exec backend python scripts/init-auth-db.py"
Write-Host "2. Access frontend: http://localhost:3000"
Write-Host "3. Check logs if any issues: docker-compose logs -f"
