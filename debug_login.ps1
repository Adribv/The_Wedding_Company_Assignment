# Simple script to debug login issues
$baseUrl = "http://localhost:8000"

Write-Host "=== Debug Login Test ===" -ForegroundColor Green
Write-Host ""

# First, create an organization
Write-Host "1. Creating test organization..." -ForegroundColor Yellow
$orgName = "DebugTest_$(Get-Date -Format 'yyyyMMddHHmmss')"
$email = "debug@test.com"
$password = "testpass123"

$createData = @{
    organization_name = $orgName
    email = $email
    password = $password
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$baseUrl/org/create" -Method Post -Body $createData -ContentType "application/json"
    Write-Host "   [OK] Organization created: $($createResponse.organization.organization_name)" -ForegroundColor Green
    Write-Host "   Admin email: $($createResponse.organization.admin.email)" -ForegroundColor Cyan
} catch {
    Write-Host "   [ERROR] Failed to create: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Status Code: $statusCode" -ForegroundColor Yellow
        Write-Host "   Response: $responseBody" -ForegroundColor Yellow
    }
    exit
}

Write-Host ""

# Wait a moment for database to sync
Write-Host "   Waiting 2 seconds for database sync..." -ForegroundColor Gray
Start-Sleep -Seconds 2

# Now try to login
Write-Host ""
Write-Host "2. Attempting login..." -ForegroundColor Yellow
Write-Host "   Email: $email" -ForegroundColor Gray
Write-Host "   Password: $password" -ForegroundColor Gray

$loginData = @{
    email = $email
    password = $password
} | ConvertTo-Json

Write-Host "   Request body: $loginData" -ForegroundColor Gray
Write-Host ""

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/admin/login" -Method Post -Body $loginData -ContentType "application/json"
    
    # Check if we got a response
    if ($loginResponse) {
        Write-Host "   [OK] Login successful!" -ForegroundColor Green
        
        # Safely get the token
        if ($loginResponse.access_token) {
            $token = $loginResponse.access_token
            $tokenPreview = if ($token.Length -gt 30) { $token.Substring(0, 30) + "..." } else { $token }
            Write-Host "   Token received: $tokenPreview" -ForegroundColor Cyan
            Write-Host "   Token type: $($loginResponse.token_type)" -ForegroundColor Cyan
        } else {
            Write-Host "   [WARNING] No access_token in response" -ForegroundColor Yellow
            Write-Host "   Full response:" -ForegroundColor Gray
            $loginResponse | ConvertTo-Json -Depth 10 | Write-Host
        }
    } else {
        Write-Host "   [ERROR] Empty response from server" -ForegroundColor Red
    }
} catch {
    Write-Host "   [ERROR] Login failed!" -ForegroundColor Red
    Write-Host "   Error Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode
        Write-Host "   Status Code: $statusCode" -ForegroundColor Yellow
        
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $responseBody = $reader.ReadToEnd()
            $reader.Close()
            $stream.Close()
            Write-Host "   Response Body: $responseBody" -ForegroundColor Yellow
        } catch {
            Write-Host "   Could not read response body: $($_.Exception.Message)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   No HTTP response available" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Troubleshooting:" -ForegroundColor Cyan
    Write-Host "  1. Check if the API is running: curl http://localhost:8000/health" -ForegroundColor White
    Write-Host "  2. Verify MongoDB connection in .env file" -ForegroundColor White
    Write-Host "  3. Check API logs for errors" -ForegroundColor White
    Write-Host "  4. Verify the organization was created in MongoDB Atlas" -ForegroundColor White
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Green
