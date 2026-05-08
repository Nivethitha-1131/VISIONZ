## VISIONZ BACKEND - QUICK RENDER DEPLOYMENT GUIDE

### ✅ Status: READY TO DEPLOY

---

## 🔧 PRE-DEPLOYMENT (5 minutes)

### 1. Secure Your API Key
```bash
# Remove .env from git tracking
cd backend
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Secure: remove .env from tracking"
git push
```

### 2. Generate Secret Key
```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
```
Copy this value - you'll paste it in Render dashboard

---

## 🚀 RENDER DEPLOYMENT (10 minutes)

### Step 1: Create Service
1. Go to **render.com** → Dashboard
2. Click **+ New** → **Web Service**
3. Click **Connect GitHub** (select your repo)
4. Select the VISIONZ repository

### Step 2: Configure Service
| Setting | Value |
|---------|-------|
| Name | visionz-backend |
| Region | Oregon (default) |
| Branch | main |
| Root Directory | **backend** |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| Python Version | 3.10 |

### Step 3: Set Environment Variables
Click **Advanced** → **Add Environment Variable** for each:

```
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=[from step above]
CORS_ORIGINS=https://your-frontend.vercel.app,https://visionz-backend.onrender.com
ANTHROPIC_API_KEY=[your Claude API key]
LLAMA_BASE_URL=http://localhost:11434
LOG_LEVEL=INFO
RATE_LIMIT_ENABLED=True
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW_SECONDS=60
```

### Step 4: Deploy
Click **Create Web Service** button

**Wait 15-20 minutes** for first deployment (PyTorch download)

---

## ✅ POST-DEPLOYMENT VERIFICATION

### 1. Check Service Status
- Go to Render Dashboard
- Your service should show green "Live" badge
- Check logs for any errors

### 2. Test API
```bash
# Replace URL with your Render domain
curl https://visionz-backend.onrender.com/api/health
# Should return: {"status":"ok"}
```

### 3. View API Docs
```
https://visionz-backend.onrender.com/docs
```

### 4. Update Frontend
In `frontend/js/api.js`, change:
```javascript
// OLD (local)
const API_BASE = 'http://localhost:8000/api';

// NEW (production)
const API_BASE = 'https://visionz-backend.onrender.com/api';
```

---

## 📊 WHAT'S INCLUDED

✅ FastAPI backend with all routes
✅ SQLite database with user seeding
✅ JWT authentication
✅ YOLO defect detection model
✅ Rate limiting & security headers
✅ Claude AI integration
✅ Error handling & logging
✅ CORS configured

---

## ⚠️ IMPORTANT

### Files NOT to Commit to Git
- `backend/.env` - Has API keys!
- Add to `.gitignore`

### First Startup Takes Time
- 1st deployment: 20 minutes (PyTorch download)
- After that: 30-60 second startup

### Database
- Default: SQLite (files lost on redeploy)
- Better: Add Render PostgreSQL addon
- Setup: Just change `DATABASE_URL` env var

### File Upload Directory
- `uploads/` doesn't persist between redeploys
- For prod: Use AWS S3 or Cloudinary

---

## 🎯 YOUR DEPLOYMENT URLs

After deployment:
```
API Base:        https://visionz-backend.onrender.com
Health Check:    https://visionz-backend.onrender.com/api/health
API Docs:        https://visionz-backend.onrender.com/docs
```

---

## ❌ COMMON MISTAKES

Don't do this:
- ❌ Commit .env file to git
- ❌ Use dev SECRET_KEY in production
- ❌ Forget to set CORS_ORIGINS
- ❌ Set DEBUG=True in production
- ❌ Use old API URLs in frontend

---

## 📋 FINAL CHECKLIST

- [ ] Code pushed to GitHub
- [ ] .env removed from git tracking
- [ ] Secret key generated
- [ ] Render service created
- [ ] All environment variables set
- [ ] Root directory = `backend/`
- [ ] Build command = `pip install -r requirements.txt`
- [ ] Start command = `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Health endpoint tested
- [ ] Frontend updated with new API_BASE

---

**Ready to deploy? Go to render.com and create your Web Service!** 🚀
