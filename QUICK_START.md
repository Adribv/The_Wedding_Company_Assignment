# Quick Start Guide - Run and Test

## Step 1: Verify Your Setup

Make sure you have:
- ✅ `.env` file with your MongoDB Atlas connection string
- ✅ Docker installed (for Docker method) OR Python 3.11+ (for local method)

## Step 2: Run the Application

### Method A: Using Docker (Recommended)

```bash
# Start the API service (connects to MongoDB Atlas)
docker-compose up --build api
```

The API will be available at: **http://localhost:8000**

### Method B: Local Development

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
uvicorn app.main:app --reload
```

The API will be available at: **http://localhost:8000**

## Step 3: Verify the Application is Running

Open your browser or use curl:

```bash
# Check health endpoint
curl http://localhost:8000/health

# Check root endpoint
curl http://localhost:8000/

# View interactive API docs
# Open in browser: http://localhost:8000/docs
```

## Step 4: Test the API Endpoints

### 4.1 Create an Organization

```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Acme Corp",
    "email": "admin@acme.com",
    "password": "securepass123"
  }'
```

**Expected Response:**
```json
{
  "message": "Organization created successfully",
  "organization": {
    "organization_name": "Acme Corp",
    "collection_name": "org_acme_corp",
    "admin": {
      "admin_id": "...",
      "email": "admin@acme.com"
    },
    "created_at": "2024-01-01T12:00:00"
  }
}
```

### 4.2 Login as Admin

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "securepass123"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save the token** for next steps:
```bash
# On Linux/Mac
export TOKEN="your-token-here"

# On Windows PowerShell
$env:TOKEN="your-token-here"
```

### 4.3 Get Organization Details

```bash
curl "http://localhost:8000/org/get?organization_name=Acme%20Corp"
```

### 4.4 Update Organization (Requires Token)

```bash
# On Linux/Mac
curl -X PUT "http://localhost:8000/org/update" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "organization_name": "Acme Corp",
    "new_organization_name": "Acme Corporation",
    "email": "newadmin@acme.com"
  }'

# On Windows PowerShell
curl -X PUT "http://localhost:8000/org/update" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $env:TOKEN" `
  -d '{\"organization_name\": \"Acme Corp\", \"new_organization_name\": \"Acme Corporation\", \"email\": \"newadmin@acme.com\"}'
```

### 4.5 Delete Organization (Requires Token)

```bash
# On Linux/Mac
curl -X DELETE "http://localhost:8000/org/delete" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "organization_name": "Acme Corporation"
  }'

# On Windows PowerShell
curl -X DELETE "http://localhost:8000/org/delete" `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer $env:TOKEN" `
  -d '{\"organization_name\": \"Acme Corporation\"}'
```

## Step 5: Run Automated Tests

### Using Docker

```bash
# Start MongoDB for testing (if using local MongoDB)
docker-compose --profile local-db up -d mongodb

# Run tests
docker-compose run --rm api pytest tests/ -v
```

### Local Testing

```bash
# Set test environment variables
export MONGODB_URL="mongodb://localhost:27017"
export MONGODB_DB_NAME="org_master_test"
export JWT_SECRET_KEY="test-secret-key"

# Or use your MongoDB Atlas for testing
export MONGODB_URL="mongodb+srv://bhubesh:bhubesh123@cluster0.arodjaf.mongodb.net/"
export MONGODB_DB_NAME="org_master_test"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=app --cov-report=html
```

## Step 6: Use Interactive API Documentation

1. Start the application
2. Open your browser: **http://localhost:8000/docs**
3. You can test all endpoints directly from the browser!

## Troubleshooting

### Connection Issues

If you get MongoDB connection errors:

1. **Check MongoDB Atlas:**
   - Verify your IP is whitelisted in Network Access
   - Check your username/password are correct
   - Ensure the cluster is running

2. **Check .env file:**
   ```bash
   # Verify .env file exists and has correct values
   cat .env  # Linux/Mac
   Get-Content .env  # Windows PowerShell
   ```

3. **Test MongoDB connection:**
   ```bash
   # Install mongosh if needed
   # Then test connection
   mongosh "mongodb+srv://bhubesh:bhubesh123@cluster0.arodjaf.mongodb.net/"
   ```

### Port Already in Use

If port 8000 is already in use:

```bash
# Change port in docker-compose.yaml or run with different port:
uvicorn app.main:app --reload --port 8001
```

### Import Errors

If you get import errors:

```bash
# Make sure you're in the project directory
cd d:\wedding_company_assignment

# Reinstall dependencies
pip install -r requirements.txt
```

## Next Steps

- Explore the API documentation at http://localhost:8000/docs
- Check the management CLI: `python scripts/manage.py list-orgs`
- Review DESIGN.md for architecture details
- Read README.md for more information

