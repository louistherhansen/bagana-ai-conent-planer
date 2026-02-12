# Debug Login Test Script
# Tests login API with detailed logging

$baseUrl = "http://localhost:3000/api/auth/login"
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "[DEBUG] Testing Login API with detailed logging..." -ForegroundColor Cyan
Write-Host ""

# Get hash from database first
Write-Host "[STEP 1] Checking database..." -ForegroundColor Yellow
$dbHash = docker-compose exec -T postgres psql -U postgres -d bagana-ai-cp -t -c "SELECT password_hash FROM users WHERE email = 'admin@bagana.ai' LIMIT 1;" 2>&1 | Select-String -Pattern "^[a-f0-9]{64}$"
if ($dbHash) {
    $dbHash = $dbHash.ToString().Trim()
    Write-Host "Found hash: $($dbHash.Substring(0, 20))..." -ForegroundColor Green
    Write-Host "Hash length: $($dbHash.Length)" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[WARNING] Could not retrieve hash from database" -ForegroundColor Yellow
    Write-Host ""
}

# Test common passwords
$testPasswords = @(
    "admin",
    "Admin", 
    "password",
    "Password123",
    "bagana123",
    "Bagana123",
    "admin123",
    "Admin123",
    "bagana",
    "Bagana"
)

Write-Host "[STEP 2] Testing passwords..." -ForegroundColor Yellow
foreach ($pwd in $testPasswords) {
    $body = @{
        email = "admin@bagana.ai"
        password = $pwd
    } | ConvertTo-Json
    
    Write-Host "Testing password: '$pwd'" -ForegroundColor Gray
    
    try {
        $response = Invoke-RestMethod -Uri $baseUrl -Method Post -Headers $headers -Body $body -ErrorAction Stop
        
        Write-Host "[SUCCESS] Login successful with password: '$pwd'" -ForegroundColor Green
        Write-Host "Response: $($response | ConvertTo-Json -Depth 2)" -ForegroundColor Green
        Write-Host ""
        break
    } catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
        $errorBody = if ($_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { $_.Exception.Message }
        
        if ($statusCode -eq 401) {
            Write-Host "  [FAILED] 401 Unauthorized" -ForegroundColor Red
        } else {
            Write-Host "  [ERROR] Status: $statusCode" -ForegroundColor Red
            Write-Host "  Error: $errorBody" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "[STEP 3] Checking frontend logs..." -ForegroundColor Yellow
docker-compose logs frontend --tail 50 2>&1 | Select-String -Pattern "login|password|verify|error|bcrypt|sha256" -CaseSensitive:$false | Select-Object -Last 15
