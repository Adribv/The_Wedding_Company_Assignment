# PowerShell script to test the API endpoints
# Make sure the API is running first!

$baseUrl = "http://localhost:8000"

Write-Host "=== Testing Organization Management API ===" -ForegroundColor Green
Write-Host ""

# Test 1: Health Check
Write-Host "1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/health" -Method Get
    Write-Host "   ✓ Health check passed: $($response.status)" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Health check failed. Is the API running?" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Create Organization
Write-Host "2. Creating Organization..." -ForegroundColor Yellow
$orgName = "TestOrg_$(Get-Date -Format 'yyyyMMddHHmmss')"
$adminEmail = "admin@testorg.com"
$adminPassword = "securepass123"

$orgData = @{
    organization_name = $orgName
    email = $adminEmail
    password = $adminPassword
} | ConvertTo-Json

try {
    $createResponse = Invoke-RestMethod -Uri "$baseUrl/org/create" -Method Post -Body $orgData -ContentType "application/json"
    $createdOrgName = $createResponse.organization.organization_name
    Write-Host "   ✓ Organization created: $createdOrgName" -ForegroundColor Green
    Write-Host "   Collection: $($createResponse.organization.collection_name)" -ForegroundColor Cyan
    Write-Host "   Admin Email: $($createResponse.organization.admin.email)" -ForegroundColor Cyan
    
    # Verify we can retrieve it
    $verifyResponse = Invoke-RestMethod -Uri "$baseUrl/org/get?organization_name=$([System.Web.HttpUtility]::UrlEncode($createdOrgName))" -Method Get
    Write-Host "   ✓ Verified organization exists in database" -ForegroundColor Green
} catch {
    Write-Host "   ✗ Failed to create organization: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Status: $statusCode" -ForegroundColor Yellow
        Write-Host "   Response: $responseBody" -ForegroundColor Yellow
    }
    exit 1
}

Write-Host ""

# Test 3: Login
Write-Host "3. Logging in as Admin..." -ForegroundColor Yellow
Write-Host "   Using email: $adminEmail" -ForegroundColor Gray

$loginData = @{
    email = $adminEmail
    password = $adminPassword
} | ConvertTo-Json

Write-Host "   Request: $loginData" -ForegroundColor Gray

try {
    $loginResponse = Invoke-RestMethod -Uri "$baseUrl/admin/login" -Method Post -Body $loginData -ContentType "application/json"
    
    Write-Host "   Response: $($loginResponse | ConvertTo-Json)" -ForegroundColor Gray
    
    $token = $loginResponse.access_token
    
    if ([string]::IsNullOrEmpty($token)) {
        Write-Host "   ✗ Login failed: No token received" -ForegroundColor Red
        Write-Host "   Full response: $($loginResponse | ConvertTo-Json -Depth 10)" -ForegroundColor Yellow
        exit 1
    }
    
    Write-Host "   ✓ Login successful" -ForegroundColor Green
    Write-Host "   Token: $($token.Substring(0, [Math]::Min(20, $token.Length)))..." -ForegroundColor Cyan
} catch {
    Write-Host "   ✗ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Status Code: $statusCode" -ForegroundColor Yellow
        Write-Host "   Response Body: $responseBody" -ForegroundColor Yellow
    }
    Write-Host "   Tip: Make sure the organization was created successfully in step 2" -ForegroundColor Cyan
    exit 1
}

Write-Host ""

# Test 4: Get Organization
Write-Host "4. Getting Organization Details..." -ForegroundColor Yellow
try {
    $encodedOrgName = [System.Web.HttpUtility]::UrlEncode($createdOrgName)
    $getUri = "$baseUrl/org/get?organization_name=$encodedOrgName"
    $getResponse = Invoke-RestMethod -Uri $getUri -Method Get
    Write-Host "   ✓ Organization retrieved: $($getResponse.organization.organization_name)" -ForegroundColor Green
} catch {
    $errorMsg = $_.Exception.Message
    if ($_.Exception.Response) {
        $statusCode = [int]$_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   ✗ Failed to get organization (Status: $statusCode)" -ForegroundColor Red
        Write-Host "   Response: $responseBody" -ForegroundColor Yellow
    } else {
        Write-Host "   ✗ Failed to get organization: $errorMsg" -ForegroundColor Red
    }
}

Write-Host ""

# Test 5: Update Organization
Write-Host "5. Updating Organization..." -ForegroundColor Yellow

if ([string]::IsNullOrEmpty($token)) {
    Write-Host "   ✗ Cannot update: No authentication token available" -ForegroundColor Red
    Write-Host "   (Login must succeed first)" -ForegroundColor Gray
} else {
    $updateData = @{
        organization_name = $createdOrgName
        email = "newadmin@testorg.com"
    } | ConvertTo-Json

    try {
        # Use Invoke-WebRequest for better header control, then convert response
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-WebRequest -Uri "$baseUrl/org/update" -Method Put -Body $updateData -Headers $headers -UseBasicParsing
        $updateResponse = $response.Content | ConvertFrom-Json
        Write-Host "   ✓ Organization updated" -ForegroundColor Green
        Write-Host "   New email: $($updateResponse.organization.admin.email)" -ForegroundColor Cyan
    } catch {
        $errorMsg = $_.Exception.Message
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "   ✗ Failed to update organization (Status: $statusCode)" -ForegroundColor Red
            Write-Host "   Response: $responseBody" -ForegroundColor Yellow
        } else {
            Write-Host "   ✗ Failed to update organization: $errorMsg" -ForegroundColor Red
        }
    }
}

Write-Host ""

# Test 6: Delete Organization
Write-Host "6. Deleting Organization..." -ForegroundColor Yellow

if ([string]::IsNullOrEmpty($token)) {
    Write-Host "   ✗ Cannot delete: No authentication token available" -ForegroundColor Red
    Write-Host "   (Login must succeed first)" -ForegroundColor Gray
} else {
    $deleteData = @{
        organization_name = $createdOrgName
    } | ConvertTo-Json

    try {
        # Use Invoke-WebRequest for better header control, then convert response
        $headers = @{
            "Authorization" = "Bearer $token"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-WebRequest -Uri "$baseUrl/org/delete" -Method Delete -Body $deleteData -Headers $headers -UseBasicParsing
        $deleteResponse = $response.Content | ConvertFrom-Json
        Write-Host "   ✓ Organization deleted: $($deleteResponse.message)" -ForegroundColor Green
    } catch {
        $errorMsg = $_.Exception.Message
        if ($_.Exception.Response) {
            $statusCode = [int]$_.Exception.Response.StatusCode
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "   ✗ Failed to delete organization (Status: $statusCode)" -ForegroundColor Red
            Write-Host "   Response: $responseBody" -ForegroundColor Yellow
        } else {
            Write-Host "   ✗ Failed to delete organization: $errorMsg" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=== All Tests Completed ===" -ForegroundColor Green

