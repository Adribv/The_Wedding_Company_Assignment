# Fix for Render Build Error

## Problem
The build is failing because Rust-based packages (like `cryptography`) are trying to build from source, which requires write access to system directories that are read-only on Render.

## Solution

### Option 1: Updated requirements.txt (Recommended)

I've updated `requirements.txt` to:
1. Pin `cryptography` to a version with pre-built wheels
2. Remove test dependencies (not needed for production)
3. Ensure all packages have pre-built wheels available

### Option 2: Add Build Configuration

If the issue persists, you can also:

1. **Set Python Version Explicitly**
   - Create `runtime.txt` with: `python-3.11.9`
   - This ensures consistent Python version

2. **Update Build Command in Render**
   ```
   pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
   ```

3. **Use Pre-built Wheels Only**
   Add to build command:
   ```
   pip install --only-binary :all: -r requirements.txt
   ```

## Updated Build Command for Render

In Render dashboard, set:

**Build Command:**
```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

**Start Command:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Alternative: Use Docker (If Python build still fails)

If the Python build continues to fail, you can use Docker instead:

1. **Create Dockerfile** (already exists)
2. **Change Language to Docker** in Render
3. **Set Dockerfile Path**: `Dockerfile`
4. **No build/start commands needed** (Docker handles it)

## Verification

After updating, the build should:
- ✅ Install all dependencies successfully
- ✅ Use pre-built wheels (no Rust compilation)
- ✅ Complete in reasonable time

## If Issues Persist

1. Check Render build logs for specific package causing issues
2. Try pinning that specific package to an older version
3. Consider using Docker deployment instead

