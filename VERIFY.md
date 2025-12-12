# How to Verify the Application

## Quick Verification Steps

### 1. Check Application Starts

**Using Docker:**
```bash
docker-compose up --build api
```

**Or locally:**
```bash
uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Test Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status":"healthy"}
```

### 3. Check API Documentation

Open in browser: **http://localhost:8000/docs**

You should see Swagger UI with all endpoints listed.

### 4. Run Automated Tests

```bash
# Set test environment
export MONGODB_URL="mongodb+srv://bhubesh:bhubesh123@cluster0.arodjaf.mongodb.net/"
export MONGODB_DB_NAME="org_master_test"
export JWT_SECRET_KEY="test-secret-key"

# Run tests
pytest tests/ -v
```

All tests should pass ✅

### 5. Manual Endpoint Testing

Use the test scripts or test manually:

**Option A: Use PowerShell test script**
```powershell
.\test_api.ps1
```

**Option B: Use debug script**
```powershell
.\debug_login.ps1
```

**Option C: Test manually with curl**

#### Step 1: Create Organization
```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "TestCompany",
    "email": "admin@testcompany.com",
    "password": "securepass123"
  }'
```

Expected: 201 Created with organization details

#### Step 2: Get Organization
```bash
curl "http://localhost:8000/org/get?organization_name=TestCompany"
```

Expected: 200 OK with organization details

#### Step 3: Login
```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@testcompany.com",
    "password": "securepass123"
  }'
```

Expected: 200 OK with JWT token

Save the token for next steps:
```bash
export TOKEN="your-token-here"
```

#### Step 4: Update Organization (requires token)
```bash
curl -X PUT "http://localhost:8000/org/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "organization_name": "TestCompany",
    "email": "newadmin@testcompany.com"
  }'
```

Expected: 200 OK with updated organization

#### Step 5: Delete Organization (requires token)
```bash
curl -X DELETE "http://localhost:8000/org/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "organization_name": "TestCompany"
  }'
```

Expected: 200 OK with success message

## Verification Checklist

### ✅ Code Quality
- [ ] No syntax errors
- [ ] No linter errors
- [ ] All imports work
- [ ] Code follows structure

### ✅ Endpoints
- [ ] POST /org/create works
- [ ] GET /org/get works
- [ ] PUT /org/update works (with auth)
- [ ] DELETE /org/delete works (with auth)
- [ ] POST /admin/login works

### ✅ Authentication
- [ ] JWT tokens are generated
- [ ] Tokens contain admin_id and organization_name
- [ ] Protected endpoints require valid token
- [ ] Invalid tokens are rejected

### ✅ Database
- [ ] Connects to MongoDB
- [ ] Creates collections dynamically
- [ ] Stores data in master database
- [ ] Migrates collections on rename

### ✅ Security
- [ ] Passwords are hashed
- [ ] JWT tokens expire
- [ ] Admin can only access their org
- [ ] Input validation works

## Common Issues and Solutions

### Issue: MongoDB Connection Failed
**Solution:**
- Check `.env` file has correct `MONGODB_URL`
- Verify MongoDB Atlas IP whitelist
- Check network connectivity

### Issue: 401 Unauthorized
**Solution:**
- Verify JWT token is valid
- Check token hasn't expired
- Ensure Authorization header format: `Bearer <token>`

### Issue: Organization Already Exists
**Solution:**
- Use a unique organization name
- Or delete existing organization first

### Issue: Collection Creation Failed
**Solution:**
- Check MongoDB permissions
- Verify database connection
- Check collection name is valid

## Pre-Deployment Checklist

Before deploying to Render:

- [ ] All tests pass locally
- [ ] Health endpoint works
- [ ] All endpoints tested manually
- [ ] Environment variables documented
- [ ] `.env` file has correct values
- [ ] No hardcoded secrets
- [ ] Code is clean (no debug code)
- [ ] Documentation is complete

## Post-Deployment Verification

After deploying to Render:

1. **Check Health:**
   ```bash
   curl https://your-app.onrender.com/health
   ```

2. **Test Create:**
   ```bash
   curl -X POST "https://your-app.onrender.com/org/create" \
     -H "Content-Type: application/json" \
     -d '{"organization_name":"Test","email":"test@test.com","password":"pass123"}'
   ```

3. **Check Logs:**
   - Go to Render dashboard
   - Check application logs for errors

4. **Test All Endpoints:**
   - Use Swagger UI: `https://your-app.onrender.com/docs`
   - Or use curl commands with your Render URL

