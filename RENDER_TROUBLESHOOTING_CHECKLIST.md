# VISIONZ Render Deployment - Troubleshooting Checklist

Based on the error: `Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'`

---

## Step 1: Check Current render.yaml

**Current Configuration:**
```yaml
buildCommand: pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt
startCommand: sh -c 'cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT'
```

**Status:** ✅ Uses absolute path `backend/requirements.txt` from project root

---

## Step 2: Verify File Existence

**On Local Machine:**
- ✅ File exists: `D:\VISIONZ_FIXED_VIDEO\backend\requirements.txt`
- ✅ File size: 370 bytes
- ✅ Contains: 20 Python packages
- ✅ Last modified: 4/6/2026

**In Git Repository:**
- ✅ File is tracked in GitHub
- ✅ File is NOT in .gitignore
- ✅ File will be available during Render build

---

## Step 3: Common Build Errors & Fixes

### Error: "No such file or directory: 'requirements.txt'"

**Possible Causes:**

| Cause | Fix |
|-------|-----|
| Build running from wrong directory | ✅ FIXED: Using `backend/requirements.txt` absolute path |
| requirements.txt not committed to Git | ✅ VERIFIED: File is in repo |
| File path has spaces or special chars | ✅ NO SPACES: Path is clean |
| Render not detecting render.yaml | See Step 4 |
| Case sensitivity issue (Windows vs Linux) | ✅ CHECKED: Path is correct |

---

## Step 4: Render Dashboard Verification

**Before Redeploying, Confirm:**

✅ Service is connected to: `Nivethitha-1131/VISIONZ`
✅ Branch selected: `main`
✅ Runtime selected: Python
✅ Build command is set (should auto-detect from render.yaml)
✅ Start command is set (should auto-detect from render.yaml)

**Do NOT manually enter commands if using render.yaml!** Render should auto-detect them.

---

## Step 5: Environment Variables Check

**Required Variables Set in Render Dashboard:**

- [ ] `PYTHON_VERSION` = `3.10.14`
- [ ] `PYTHONUNBUFFERED` = `1`
- [ ] `ENVIRONMENT` = `production`
- [ ] `DEBUG` = `false`
- [ ] `LOG_LEVEL` = `INFO`
- [ ] `CORS_ORIGINS` = `https://visionz.vercel.app`
- [ ] `PORT` = `10000`

**Note:** These are already in `render.yaml`, but verify they appear in Render Dashboard

---

## Step 6: Deployment Steps

### Option A: Fresh Deploy (Recommended)

1. **Delete current service** (if needed)
2. **Create NEW Web Service:**
   - Connect to GitHub repo: `Nivethitha-1131/VISIONZ`
   - Select branch: `main`
   - Select runtime: **Python**
   - **DO NOT enter build/start commands manually**
   - Render will auto-detect from `render.yaml`
3. **Set Environment Variables** in dashboard
4. **Click "Create Web Service"**
5. **Wait 5-10 minutes**

### Option B: Redeploy Existing Service

1. **Clear build cache:** Dashboard → Service → Settings → "Clear build cache"
2. **Click "Redeploy"**
3. **Wait 5-10 minutes**
4. **Check logs** in Render Dashboard

---

## Step 7: How to Check Logs on Render

1. Go to: https://dashboard.render.com
2. Select your service: `visionz-backend`
3. Click **"Logs"** tab
4. Search for "error" or "ERROR"
5. Look for specific error messages
6. Share error message for further troubleshooting

---

## Step 8: If Build Still Fails

**Common Issues & Fixes:**

### Issue: "ModuleNotFoundError"
- **Cause:** Dependency not in requirements.txt
- **Fix:** Add package to `requirements.txt`, commit, redeploy

### Issue: "SyntaxError" 
- **Cause:** Python file has syntax error
- **Fix:** Run `python -m py_compile filename.py` locally to find it

### Issue: "502 Bad Gateway"
- **Cause:** App crashes on startup
- **Fix:** Check startCommand logs, look for import errors

### Issue: "Connection refused"
- **Cause:** App not binding to correct host/port
- **Fix:** Verify startCommand includes `--host 0.0.0.0 --port $PORT`

---

## Step 9: Runtime Configuration Checklist

✅ **Python Version:** 3.10.14 (specified in runtime.txt)
✅ **Dependencies:** All 20 packages in requirements.txt
✅ **Host:** 0.0.0.0 (in startCommand)
✅ **Port:** $PORT (uses Render's PORT variable = 10000)
✅ **App:** FastAPI with Uvicorn
✅ **Working Directory:** backend (handled by cd command)

---

## Step 10: Git Repository Status

**Latest Commit:**
```
9faa0bb Fix: Use absolute paths in buildCommand, use sh -c wrapper for startCommand
```

**Files in Repository:**
- ✅ render.yaml (correct configuration)
- ✅ backend/requirements.txt (all dependencies)
- ✅ backend/Procfile
- ✅ backend/runtime.txt
- ✅ backend/app/ (all source code)
- ✅ frontend/ (frontend code)

---

## Action Plan for Next Deploy

1. **Go to Render Dashboard:** https://dashboard.render.com
2. **Review Configuration:**
   - Build Command should be: `pip install --upgrade pip setuptools wheel && pip install -r backend/requirements.txt`
   - Start Command should be: `sh -c 'cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT'`
3. **Redeploy:**
   - Click "Clear build cache"
   - Click "Redeploy"
4. **Monitor Build:**
   - Go to Logs tab
   - Watch for build progress
   - Look for errors
5. **If Success:**
   - App will show "Live"
   - You'll get a URL like: `https://visionz-backend.onrender.com`
6. **If Error:**
   - Copy full error message
   - Use this checklist to identify cause
   - Make fixes in code/config
   - Recommit to GitHub
   - Redeploy

---

## Expected Build Output (Success)

```
Collect packages>24.0
Downloading packaging-26.2-py3-none-any.whl (100 kB)
Installing collected packages: setuptools, pip, packaging, wheel
Successfully installed packaging-26.2 pip-26.1.1 setuptools-82.0.1 wheel-0.47.0
Collecting fastapi==0.110.1
Downloading fastapi-0.110.1-py3-none-any.whl (92 kB)
...
Successfully installed [all packages]
==> Build successful ✅
```

---

## Expected Start Output (Success)

```
INFO:     Uvicorn running on http://0.0.0.0:10000
```

Then service shows: **Live** ✅

---

## Critical Notes

⚠️ **DO NOT** manually upload requirements.txt to Render  
⚠️ **DO NOT** use `rootDir` - use absolute paths instead  
⚠️ **DO NOT** override build/start commands unless troubleshooting  
⚠️ **DO** keep render.yaml in git repository root  
⚠️ **DO** commit changes before redeploying  

---

## Still Having Issues?

If deployment still fails after these steps:

1. Run locally to confirm it works: `cd backend && uvicorn app.main:app --reload`
2. Check Render logs for exact error message
3. Match error to the "Common Errors" section above
4. Apply the fix
5. Commit and redeploy

**Questions?** Check the full Render troubleshooting guide in the logs.
