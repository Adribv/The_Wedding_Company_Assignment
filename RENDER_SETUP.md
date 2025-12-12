# Render Deployment Setup Guide

## Important: Change Language from Docker to Python

**⚠️ CRITICAL:** Your application is a Python/FastAPI app, NOT Docker. 

In the Render dashboard:
- **Language**: Select **"Python 3"** (NOT Docker)
- The Docker option is for Dockerfile-based deployments, but you're using a standard Python app

## Render Configuration

### Basic Settings

- **Name**: `The_Wedding_Company_Assignment` (or your preferred name)
- **Language**: **Python 3** ⚠️ (NOT Docker)
- **Branch**: `main`
- **Region**: `Oregon (US West)` (or your preferred region)
- **Root Directory**: Leave empty (unless using monorepo)
- **Instance Type**: `Free` (for testing) or `Starter` ($7/month) for production

### Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Environment Variables

Add these environment variables in the Render dashboard:

### Required Variables

1. **MONGODB_URL**
   - **Value**: `mongodb+srv://bhubesh:bhubesh123@cluster0.arodjaf.mongodb.net/`
   - **Description**: Your MongoDB Atlas connection string
   - **Required**: Yes

2. **JWT_SECRET_KEY**
   - **Value**: `8eacb2adee54e921c332fa5b494bde4f` (or generate a new one)
   - **Description**: Secret key for JWT token signing
   - **Required**: Yes
   - **Note**: For production, use a longer, more secure random string

### Optional Variables (with defaults)

3. **MONGODB_DB_NAME**
   - **Value**: `org_master`
   - **Description**: MongoDB database name
   - **Required**: No (defaults to `org_master`)

4. **JWT_ALGORITHM**
   - **Value**: `HS256`
   - **Description**: JWT signing algorithm
   - **Required**: No (defaults to `HS256`)

5. **JWT_EXPIRATION_HOURS**
   - **Value**: `24`
   - **Description**: JWT token expiration time in hours
   - **Required**: No (defaults to `24`)

6. **DEBUG**
   - **Value**: `false`
   - **Description**: Enable debug mode
   - **Required**: No (defaults to `false`)

7. **APP_NAME**
   - **Value**: `Organization Management Service`
   - **Description**: Application name
   - **Required**: No

8. **APP_VERSION**
   - **Value**: `1.0.0`
   - **Description**: Application version
   - **Required**: No

## Step-by-Step Setup in Render Dashboard

### Step 1: Basic Configuration

1. **Name**: `The_Wedding_Company_Assignment`
2. **Language**: Select **"Python 3"** ⚠️ (NOT Docker)
3. **Branch**: `main`
4. **Region**: `Oregon (US West)`
5. **Instance Type**: `Free` (for testing)

### Step 2: Build & Start Commands

Scroll down to "Build & Deploy" section:

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Step 3: Environment Variables

Click "Advanced" → "Add Environment Variable" and add:

| Key | Value |
|-----|-------|
| `MONGODB_URL` | `mongodb+srv://bhubesh:bhubesh123@cluster0.arodjaf.mongodb.net/` |
| `JWT_SECRET_KEY` | `8eacb2adee54e921c332fa5b494bde4f` |
| `MONGODB_DB_NAME` | `org_master` |
| `JWT_ALGORITHM` | `HS256` |
| `JWT_EXPIRATION_HOURS` | `24` |
| `DEBUG` | `false` |

### Step 4: Deploy

Click **"Create Web Service"** and Render will:
1. Clone your repository
2. Install dependencies
3. Start your application
4. Provide a URL like: `https://the-wedding-company-assignment.onrender.com`

## Verification After Deployment

1. **Check Health:**
   ```bash
   curl https://your-app-name.onrender.com/health
   ```
   Should return: `{"status":"healthy"}`

2. **Check API Docs:**
   Open: `https://your-app-name.onrender.com/docs`

3. **Test Create Organization:**
   ```bash
   curl -X POST "https://your-app-name.onrender.com/org/create" \
     -H "Content-Type: application/json" \
     -d '{
       "organization_name": "TestOrg",
       "email": "admin@test.com",
       "password": "securepass123"
     }'
   ```

## Troubleshooting

### Build Fails
- Check that `requirements.txt` exists
- Verify Python version (should be 3.11+)
- Check build logs in Render dashboard

### Application Crashes
- Check application logs
- Verify all environment variables are set
- Ensure MongoDB connection string is correct

### MongoDB Connection Issues
- Verify MongoDB Atlas IP whitelist includes Render IPs
- Check connection string format
- Verify database user permissions

## Security Recommendations

1. **JWT_SECRET_KEY**: Generate a strong random string:
   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

2. **MongoDB Atlas**: 
   - Whitelist Render IPs (or use 0.0.0.0/0 for testing)
   - Use strong database passwords
   - Enable MongoDB Atlas authentication

3. **Environment Variables**: 
   - Never commit secrets to Git
   - Use Render's environment variable encryption
   - Rotate secrets regularly

## Quick Reference

**Minimum Required Variables:**
- `MONGODB_URL`
- `JWT_SECRET_KEY`

**Recommended for Production:**
- All variables listed above
- Strong `JWT_SECRET_KEY` (32+ characters)
- `DEBUG=false`
- Paid instance type for better performance

