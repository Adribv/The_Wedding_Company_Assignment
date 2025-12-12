# Comprehensive verification script
$baseUrl = "http://localhost:8000"
$errors = @()

Write-Host "=== Application Verification ===" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get -ErrorAction Stop
    if ($response.status -eq "healthy") {
        Write-Host "   [OK] Health check passed" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] Unexpected response: $($response | ConvertTo-Json)" -ForegroundColor Red
        $errors += "Health check returned unexpected response"
    }
} catch {
    Write-Host "   [FAIL] Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Make sure the API is running!" -ForegroundColor Yellow
    $errors += "Health check failed"
    exit 1
}

Write-Host ""

# Test 2: API Documentation
Write-Host "2. Checking API Documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/docs" -Method Get -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Host "   [OK] API docs accessible at $baseUrl/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "   [WARN] Could not access docs: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""

# Test 3: Create Organization
Write-Host "3. Testing Create Organization..." -ForegroundColor Yellow
$orgName = "VerifyTest_$(Get-Date -Format 'yyyyMMddHHmmss')"
$email = "verify@test.com"
$password = "testpass123"

$createData = @{
    organization_name = $orgName
    email = $email
    password = $password
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$baseUrl/org/create" -Method Post -Body $createData -ContentType "application/json" -ErrorAction Stop
    if ($createResponse.organization.organization_name -eq $orgName) {
        Write-Host "   [OK] Organization created successfully" -ForegroundColor Green
        Write-Host "   Collection: $($createResponse.organization.collection_name)" -ForegroundColor Cyan
    } else {
        Write-Host "   [FAIL] Organization name mismatch" -ForegroundColor Red
        $errors += "Create organization returned wrong name"
    }
} catch {
    Write-Host "   [FAIL] Create organization failed: $($_.Exception.Message)" -ForegroundColor Red
    $errors += "Create organization failed"
}

Write-Host ""

# Test 4: Get Organization
Write-Host "4. Testing Get Organization..." -ForegroundColor Yellow
Start-Sleep -Seconds 1

try {
    $encodedName = [System.Web.HttpUtility]::UrlEncode($orgName)
    $getResponse = Invoke-RestMethod -Uri "$baseUrl/org/get?organization_name=$encodedName" -Method Get -ErrorAction Stop
    if ($getResponse.organization.organization_name -eq $orgName) {
        Write-Host "   [OK] Organization retrieved successfully" -ForegroundColor Green
    } else {
        Write-Host "   [FAIL] Retrieved wrong organization" -ForegroundColor Red
        $errors += "Get organization returned wrong data"
    }
} catch {
    Write-Host "   [FAIL] Get organization failed: $($_.Exception.Message)" -ForegroundColor Red
    $errors += "Get organization failed"
}

Write-Host ""

# Test 5: Login
Write-Host "5. Testing Admin Login..." -ForegroundColor Yellow
$loginData = @{
    email = $email
    password = $password
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/admin/login" -Method Post -Body $loginData -ContentType "application/json" -ErrorAction Stop
    if ($loginResponse.access_token) {
        $token = $loginResponse.access_token
        Write-Host "   [OK] Login successful, token received" -ForegroundColor Green
        
        # Verify token structure
        $tokenParts = $token.Split('.')
        if ($tokenParts.Length -eq 3) {
            Write-Host "   [OK] Token structure valid (JWT)" -ForegroundColor Green
        } else {
            Write-Host "   [WARN] Token structure unexpected" -ForegroundColor Yellow
        }
    } else {
        Write-Host "   [FAIL] No token in response" -ForegroundColor Red
        $errors += "Login did not return token"
    }
} catch {
    Write-Host "   [FAIL] Login failed: $($_.Exception.Message)" -ForegroundColor Red
    $errors += "Login failed"
    $token = $null
}

Write-Host ""

# Test 6: Update Organization (if login succeeded)
if ($token) {
    Write-Host "6. Testing Update Organization..." -ForegroundColor Yellow
    $updateData = @{
        organization_name = $orgName
        email = "updated@test.com"
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/org/update" -Method Put -Body $updateData -Headers $headers -UseBasicParsing -ErrorAction Stop
        $updateResponse = $response.Content | ConvertFrom-Json
        if ($updateResponse.organization.admin.email -eq "updated@test.com") {
            Write-Host "   [OK] Organization updated successfully" -ForegroundColor Green
        } else {
            Write-Host "   [FAIL] Update did not work correctly" -ForegroundColor Red
            $errors += "Update organization failed"
        }
    } catch {
        Write-Host "   [FAIL] Update failed: $($_.Exception.Message)" -ForegroundColor Red
        $errors += "Update organization failed"
    }
} else {
    Write-Host "6. Skipping Update (login failed)" -ForegroundColor Yellow
}

Write-Host ""

# Test 7: Delete Organization (if login succeeded)
if ($token) {
    Write-Host "7. Testing Delete Organization..." -ForegroundColor Yellow
    $deleteData = @{
        organization_name = $orgName
    } | ConvertTo-Json
    
    $headers = @{
        "Authorization" = "Bearer $token"
        "Content-Type" = "application/json"
    }
    
    try {
        $response = Invoke-WebRequest -Uri "$baseUrl/org/delete" -Method Delete -Body $deleteData -Headers $headers -UseBasicParsing -ErrorAction Stop
        $deleteResponse = $response.Content | ConvertFrom-Json
        if ($deleteResponse.message -like "*deleted successfully*") {
            Write-Host "   [OK] Organization deleted successfully" -ForegroundColor Green
        } else {
            Write-Host "   [FAIL] Delete did not work correctly" -ForegroundColor Red
            $errors += "Delete organization failed"
        }
    } catch {
        Write-Host "   [FAIL] Delete failed: $($_.Exception.Message)" -ForegroundColor Red
        $errors += "Delete organization failed"
    }
} else {
    Write-Host "7. Skipping Delete (login failed)" -ForegroundColor Yellow
}

Write-Host ""

# Test 8: Verify Delete (should fail)
Write-Host "8. Verifying Organization Deleted..." -ForegroundColor Yellow
try {
    $encodedName = [System.Web.HttpUtility]::UrlEncode($orgName)
    $getResponse = Invoke-RestMethod -Uri "$baseUrl/org/get?organization_name=$encodedName" -Method Get -ErrorAction Stop
    Write-Host "   [FAIL] Organization still exists after delete" -ForegroundColor Red
    $errors += "Organization not deleted"
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host "   [OK] Organization correctly deleted (404 as expected)" -ForegroundColor Green
    } else {
        Write-Host "   [WARN] Unexpected error: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== Verification Summary ===" -ForegroundColor Green

if ($errors.Count -eq 0) {
    Write-Host "All tests passed! Application is working correctly." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "  1. Review API documentation: $baseUrl/docs" -ForegroundColor White
    Write-Host "  2. Run automated tests: pytest tests/ -v" -ForegroundColor White
    Write-Host "  3. Deploy to Render (see DEPLOYMENT.md)" -ForegroundColor White
} else {
    Write-Host "Found $($errors.Count) error(s):" -ForegroundColor Red
    foreach ($error in $errors) {
        Write-Host "  - $error" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Please fix the errors before deploying." -ForegroundColor Yellow
}

