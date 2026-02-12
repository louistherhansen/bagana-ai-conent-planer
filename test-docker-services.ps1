# Script untuk Review dan Test Docker Services (Frontend, Backend, Database)
# Bagana AI Content Planner

Write-Host "BAGANA AI - Docker Services Review & Test" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Function untuk menampilkan status
function Show-Status {
    param(
        [string]$Service,
        [string]$Status,
        [string]$Color = "White"
    )
    $icon = if ($Status -eq "OK" -or $Status -match "Healthy|Running|Ready") { "[OK]" } 
            elseif ($Status -match "Warning|Not ready") { "[WARN]" } 
            else { "[FAIL]" }
    Write-Host "$icon $Service`: $Status" -ForegroundColor $Color
}

# 1. Check Docker Installation
Write-Host "Step 1: Checking Docker Installation" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    Show-Status "Docker" "Installed - $dockerVersion" "Green"
} catch {
    Show-Status "Docker" "Not installed" "Red"
    exit 1
}

try {
    $composeVersion = docker-compose --version 2>&1
    Show-Status "Docker Compose" "Installed - $composeVersion" "Green"
} catch {
    Show-Status "Docker Compose" "Not installed" "Red"
    exit 1
}

Write-Host ""

# 2. Check Configuration Files
Write-Host "Step 2: Checking Configuration Files" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

if (Test-Path "docker-compose.yml") {
    Show-Status "docker-compose.yml" "Found" "Green"
} else {
    Show-Status "docker-compose.yml" "Not found" "Red"
    exit 1
}

if (Test-Path "Dockerfile.backend") {
    Show-Status "Dockerfile.backend" "Found" "Green"
} else {
    Show-Status "Dockerfile.backend" "Not found" "Red"
}

if (Test-Path "Dockerfile.frontend") {
    Show-Status "Dockerfile.frontend" "Found" "Green"
} else {
    Show-Status "Dockerfile.frontend" "Not found" "Red"
}

if (Test-Path ".env") {
    Show-Status ".env file" "Found" "Green"
} else {
    Show-Status ".env file" "Not found - Required!" "Red"
    Write-Host "   [WARN] Please create .env file from .env.example" -ForegroundColor Yellow
}

Write-Host ""

# 3. Check Current Container Status
Write-Host "Step 3: Current Container Status" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$containers = docker ps -a --filter "name=bagana" --format '{{.Names}}|{{.Status}}|{{.Ports}}'
if ($containers) {
    $containers | ForEach-Object {
        $parts = $_ -split '\|'
        $name = $parts[0]
        $status = $parts[1]
        $ports = $parts[2]
        Write-Host "  Container: $name" -ForegroundColor Cyan
        Write-Host "    Status: $status" -ForegroundColor $(if ($status -match "Up|running") { "Green" } else { "Yellow" })
        Write-Host "    Ports: $ports" -ForegroundColor Gray
    }
} else {
    Write-Host "  No containers found" -ForegroundColor Gray
}

Write-Host ""

# 4. Check Docker Compose Services
Write-Host "Step 4: Docker Compose Services Configuration" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

try {
    $services = docker-compose config --services 2>&1 | Where-Object { $_ -notmatch "warning|level" }
    Write-Host "  Services defined:" -ForegroundColor Cyan
    $services | ForEach-Object {
        Write-Host "    - $_" -ForegroundColor Gray
    }
} catch {
    Write-Host "  [WARN] Error reading docker-compose config" -ForegroundColor Yellow
}

Write-Host ""

# 5. Test Building Images (if not already built)
Write-Host "Step 5: Testing Image Builds" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow
Write-Host "  Checking if images exist..." -ForegroundColor Gray

$images = docker images --format '{{.Repository}}:{{.Tag}}' | Select-String "bagana"
if ($images) {
    Write-Host "  Existing images:" -ForegroundColor Cyan
    $images | ForEach-Object {
        Write-Host "    [OK] $_" -ForegroundColor Green
    }
} else {
    Write-Host "  [WARN] No images found. Run: docker-compose build" -ForegroundColor Yellow
}

Write-Host ""

# 6. Test Service Health (if running)
Write-Host "Step 6: Testing Service Health" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

# Check PostgreSQL
Write-Host -NoNewline "  PostgreSQL (Database): "
try {
    $dbStatus = docker-compose exec -T postgres pg_isready -U bagana_user 2>&1
    if ($LASTEXITCODE -eq 0) {
        Show-Status "" "Healthy" "Green"
    } else {
        Show-Status "" "Not ready" "Yellow"
    }
} catch {
    Show-Status "" "Not running" "Gray"
}

# Check Backend
Write-Host -NoNewline "  Backend API (Port 8000): "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue 2>&1
    if ($response.StatusCode -eq 200) {
        Show-Status "" "Healthy" "Green"
    } else {
        Show-Status "" "Not ready" "Yellow"
    }
} catch {
    Show-Status "" "Not running" "Gray"
}

# Check Frontend
Write-Host -NoNewline "  Frontend (Port 3000): "
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue 2>&1
    if ($response.StatusCode -eq 200) {
        Show-Status "" "Healthy" "Green"
    } else {
        Show-Status "" "Not ready" "Yellow"
    }
} catch {
    Show-Status "" "Not running" "Gray"
}

Write-Host ""

# 7. Summary and Recommendations
Write-Host "Step 7: Summary and Recommendations" -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Yellow

$runningContainers = docker ps --filter "name=bagana" --format '{{.Names}}'
if ($runningContainers) {
    Write-Host "  [OK] Services are running!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Service URLs:" -ForegroundColor Cyan
    Write-Host "    Frontend:  http://localhost:3000" -ForegroundColor Gray
    Write-Host "    Backend:   http://localhost:8000" -ForegroundColor Gray
    Write-Host "    Database:  localhost:5432" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Useful commands:" -ForegroundColor Cyan
    Write-Host "    View logs:      docker-compose logs -f" -ForegroundColor Gray
    Write-Host "    Stop services:  docker-compose stop" -ForegroundColor Gray
    Write-Host "    Restart:        docker-compose restart" -ForegroundColor Gray
} else {
    Write-Host "  [WARN] Services are not running" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  To start services:" -ForegroundColor Cyan
    Write-Host "    1. Build images:  docker-compose build" -ForegroundColor Gray
    Write-Host "    2. Start services: docker-compose up -d" -ForegroundColor Gray
    Write-Host "    3. Check status:   docker-compose ps" -ForegroundColor Gray
    Write-Host "    4. View logs:      docker-compose logs -f" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Review Complete!" -ForegroundColor Green
Write-Host ""
