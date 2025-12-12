# Deployment Guide - Render

## Prerequisites
- GitHub repository with your code
- MongoDB Atlas account (or MongoDB connection string)
- Render account

## Step 1: Prepare Your Repository

1. Ensure all files are committed and pushed to GitHub
2. Verify `.env.example` exists (for reference)
3. Make sure `requirements.txt` is up to date

## Step 2: Deploy on Render

### Option A: Using Render Dashboard

1. **Create New Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository

2. **Configure Service**
   - **Name**: `org-management-api` (or your preferred name)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

3. **Set Environment Variables**
   Click "Advanced" → "Add Environment Variable" and add:
   ```
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
   MONGODB_DB_NAME=org_master
   JWT_SECRET_KEY=your-secret-key-here
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   DEBUG=false
   ```

4. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### Option B: Using render.yaml (Infrastructure as Code)

1. **Push render.yaml to your repository** (already included)

2. **Create Blueprint**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Connect your GitHub repository
   - Render will detect `render.yaml` automatically

3. **Set Environment Variables**
   - In the Blueprint, set:
     - `MONGODB_URL` (your MongoDB Atlas connection string)
     - `JWT_SECRET_KEY` (generate a secure random string)

4. **Deploy**
   - Click "Apply" to deploy

## Step 3: Verify Deployment

1. **Check Health Endpoint**
   ```bash
   curl https://your-app-name.onrender.com/health
   ```
   Should return: `{"status":"healthy"}`

2. **Access API Documentation**
   - Open: `https://your-app-name.onrender.com/docs`
   - Test endpoints directly from Swagger UI

3. **Test Create Organization**
   ```bash
   curl -X POST "https://your-app-name.onrender.com/org/create" \
     -H "Content-Type: application/json" \
     -d '{
       "organization_name": "TestOrg",
       "email": "admin@test.com",
       "password": "securepass123"
     }'
   ```

## Environment Variables Reference

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `MONGODB_URL` | Yes | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net/` |
| `MONGODB_DB_NAME` | No | Database name (default: `org_master`) | `org_master` |
| `JWT_SECRET_KEY` | Yes | Secret key for JWT signing | Random 32+ character string |
| `JWT_ALGORITHM` | No | JWT algorithm (default: `HS256`) | `HS256` |
| `JWT_EXPIRATION_HOURS` | No | Token expiration (default: `24`) | `24` |
| `DEBUG` | No | Debug mode (default: `false`) | `false` |

## Troubleshooting

### Build Fails
- Check `requirements.txt` is correct
- Verify Python version compatibility
- Check build logs in Render dashboard

### Application Crashes
- Check application logs in Render dashboard
- Verify MongoDB connection string is correct
- Ensure all environment variables are set

### Database Connection Issues
- Verify MongoDB Atlas IP whitelist includes Render IPs (0.0.0.0/0 for testing)
- Check MongoDB Atlas connection string format
- Verify database user has correct permissions

### 401 Unauthorized Errors
- Verify JWT_SECRET_KEY is set correctly
- Check token expiration settings
- Ensure Authorization header format: `Bearer <token>`

## Production Recommendations

1. **Security**
   - Use strong `JWT_SECRET_KEY` (32+ random characters)
   - Restrict CORS origins in production
   - Enable MongoDB Atlas IP whitelisting
   - Use environment-specific secrets

2. **Performance**
   - Enable MongoDB connection pooling
   - Monitor application logs
   - Set up health check monitoring

3. **Monitoring**
   - Set up Render alerts
   - Monitor MongoDB Atlas metrics
   - Track API response times

## Custom Domain (Optional)

1. In Render dashboard, go to your service
2. Click "Settings" → "Custom Domains"
3. Add your domain and follow DNS configuration instructions

