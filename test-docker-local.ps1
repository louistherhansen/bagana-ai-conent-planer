# Docker Local Test Script
# Script untuk test Docker setup lokal sebelum deploy ke production

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  BAGANA AI - Docker Local Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker installation
Write-Host "[1/8] Checking Docker installation..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version
    Write-Host "  ✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Docker not found. Please install Docker Desktop." -ForegroundColor Red
    exit 1
}

try {
    $composeVersion = docker-compose --version
    Write-Host "  ✅ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ❌ Docker Compose not found." -ForegroundColor Red
    exit 1
}

# Check .env file
Write-Host ""
Write-Host "[2/8] Checking environment configuration..." -ForegroundColor Yellow
if (Test-Path .env) {
    Write-Host "  ✅ .env file exists" -ForegroundColor Green
    
    # Check critical variables
    $envContent = Get-Content .env -Raw
    $requiredVars = @("DB_PASSWORD", "OPENROUTER_API_KEY")
    $missingVars = @()
    
    foreach ($var in $requiredVars) {
        if ($envContent -notmatch "$var\s*=") {
            $missingVars += $var
        }
    }
    
    if ($missingVars.Count -gt 0) {
        Write-Host "  ⚠️  Missing required variables: $($missingVars -join ', ')" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ Required environment variables found" -ForegroundColor Green
    }
} else {
    Write-Host "  ❌ .env file not found!" -ForegroundColor Red
    Write-Host "  💡 Copy .env.production.example to .env and configure it" -ForegroundColor Yellow
    exit 1
}

# Check Dockerfile existence
Write-Host ""
Write-Host "[3/8] Checking Dockerfile files..." -ForegroundColor Yellow
$dockerfiles = @("Dockerfile.frontend", "Dockerfile.backend", "docker-compose.yml")
$allExist = $true

foreach ($file in $dockerfiles) {
    if (Test-Path $file) {
        Write-Host "  ✅ $file exists" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $file not found!" -ForegroundColor Red
        $allExist = $false
    }
}

if (-not $allExist) {
    Write-Host "  ❌ Missing Docker configuration files!" -ForegroundColor Red
    exit 1
}

# Validate docker-compose.yml
Write-Host ""
Write-Host "[4/8] Validating docker-compose.yml..." -ForegroundColor Yellow
try {
    docker-compose config > $null 2>&1
    Write-Host "  ✅ docker-compose.yml is valid" -ForegroundColor Green
} catch {
    Write-Host "  ❌ docker-compose.yml has errors!" -ForegroundColor Red
    docker-compose config
    exit 1
}

# Check if containers are running
Write-Host ""
Write-Host "[5/8] Checking existing containers..." -ForegroundColor Yellow
$runningContainers = docker ps --filter "name=bagana-ai" --format "{{.Names}}"
if ($runningContainers) {
    Write-Host "  ⚠️  Found running containers:" -ForegroundColor Yellow
    $runningContainers | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
    Write-Host "  💡 Consider stopping them first: docker-compose down" -ForegroundColor Yellow
} else {
    Write-Host "  ✅ No existing containers found" -ForegroundColor Green
}

# Build images
Write-Host ""
Write-Host "[6/8] Building Docker images..." -ForegroundColor Yellow
Write-Host "  This may take several minutes..." -ForegroundColor Gray

$buildResult = docker-compose build 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✅ Images built successfully" -ForegroundColor Green
} else {
    Write-Host "  ❌ Build failed!" -ForegroundColor Red
    Write-Host $buildResult
    exit 1
}

# Start services
Write-Host ""
Write-Host "[7/8] Starting services..." -ForegroundColor Yellow
try {
    docker-compose up -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✅ Services started" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Failed to start services!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  ❌ Error starting services: $_" -ForegroundColor Red
    exit 1
}

# Wait for services to be healthy
Write-Host ""
Write-Host "[8/8] Waiting for services to be healthy..." -ForegroundColor Yellow
$maxWait = 60
$waited = 0
$allHealthy = $false

while ($waited -lt $maxWait -and -not $allHealthy) {
    Start-Sleep -Seconds 5
    $waited += 5
    
    $postgresStatus = docker inspect bagana-ai-db --format='{{.State.Health.Status}}' 2>$null
    $backendStatus = docker inspect bagana-ai-backend --format='{{.State.Health.Status}}' 2>$null
    $frontendStatus = docker inspect bagana-ai-frontend --format='{{.State.Health.Status}}' 2>$null
    
    Write-Host "  Waiting... ($waited/$maxWait seconds)" -ForegroundColor Gray
    
    if ($postgresStatus -eq "healthy" -and $backendStatus -eq "healthy" -and $frontendStatus -eq "healthy") {
        $allHealthy = $true
    }
}

if ($allHealthy) {
    Write-Host "  ✅ All services are healthy!" -ForegroundColor Green
} else {
    Write-Host "  ⚠️  Some services may still be starting..." -ForegroundColor Yellow
    Write-Host "  💡 Check logs: docker-compose logs" -ForegroundColor Yellow
}

# Display service status
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Service Status" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
docker-compose ps

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Service URLs" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "  Database: localhost:5432" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Useful Commands" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  View logs:     docker-compose logs -f" -ForegroundColor Gray
Write-Host "  Stop services: docker-compose stop" -ForegroundColor Gray
Write-Host "  Remove all:    docker-compose down" -ForegroundColor Gray
Write-Host "  Restart:       docker-compose restart" -ForegroundColor Gray
Write-Host ""

Write-Host "✅ Docker local test completed!" -ForegroundColor Green
Write-Host ""
