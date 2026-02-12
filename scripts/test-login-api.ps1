# Test Login API
# Tests the login endpoint with various credentials

$baseUrl = "http://localhost:3000/api/auth/login"
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "[TEST] Testing Login API..." -ForegroundColor Cyan
Write-Host ""

# Test credentials
$testCredentials = @(
    @{ email = "admin@bagana.ai"; password = "admin" },
    @{ email = "admin@bagana.ai"; password = "Admin" },
    @{ email = "admin@bagana.ai"; password = "password" },
    @{ email = "admin@bagana.ai"; password = "Password123" },
    @{ email = "admin"; password = "admin" },
    @{ username = "admin"; password = "admin" }
)

foreach ($cred in $testCredentials) {
    $body = $cred | ConvertTo-Json
    $identifier = if ($cred.email) { $cred.email } else { $cred.username }
    
    Write-Host "Testing: $identifier / $($cred.password)" -ForegroundColor Yellow
    
    try {
        $response = Invoke-RestMethod -Uri $baseUrl -Method Post -Headers $headers -Body $body -ErrorAction Stop
        
        Write-Host "[SUCCESS] Login successful!" -ForegroundColor Green
        Write-Host "Response: $($response | ConvertTo-Json -Depth 3)" -ForegroundColor Green
        Write-Host ""
        break
    } catch {
        $statusCode = if ($_.Exception.Response) { $_.Exception.Response.StatusCode.value__ } else { "N/A" }
        $errorBody = if ($_.ErrorDetails.Message) { $_.ErrorDetails.Message } else { $_.Exception.Message }
        
        Write-Host "[FAILED] Status: $statusCode" -ForegroundColor Red
        Write-Host "Error: $errorBody" -ForegroundColor Red
        Write-Host ""
    }
}

Write-Host "[LOG] Checking frontend logs for errors..." -ForegroundColor Cyan
docker-compose logs frontend --tail 50 2>&1 | Select-String -Pattern "login|password|error|bcrypt|verify" -CaseSensitive:$false | Select-Object -First 20
