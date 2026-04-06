# Render Backend Deployment Guide

## Critical Files for Render

```
backend/
├── runtime.txt          ✅ Forces Python 3.10.14
├── Procfile             ✅ Startup command
├── requirements.txt     ✅ All dependencies (prebuilt wheels only)
├── .renderignore        ✅ Exclude unnecessary files
├── app/
│   ├── main.py          ✅ FastAPI entry point
│   └── ...
└── ...
```

## Setup Instructions

### 1. Connect to Render
1. Go to Render Dashboard
2. Create new **Web Service**
3. Connect your GitHub repository (`Nivethitha-1131/VISIONZ`)
4. Select `main` branch

### 2. Configure Service Settings
- **Name:** visionz-backend
- **Runtime:** Python 3
- **Build Command:** `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Root Directory:** `backend/` (CRITICAL!)

### 3. Add Environment Variables
Add these in Render Dashboard under "Environment":

```
PORT=8000
PYTHONUNBUFFERED=1
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=postgresql://user:pass@host:5432/visionz
SECRET_KEY=<generate-strong-key>
CORS_ORIGINS=https://your-vercel-frontend.vercel.app
YOLO_DEVICE=cpu
```

### 4. Deploy
- Click **"New Deployment"** or **"Manual Deploy"**
- Monitor logs in real-time
- Should start successfully within 5-10 minutes

## Key Changes Made

✅ **runtime.txt** - Forces Python 3.10.14 (Render respects this)
✅ **Updated dependencies** - All have prebuilt wheels:
- pydantic 2.6.4 (no Rust compilation needed)
- fastapi 0.110.1
- torch 2.0.1
- All other packages use prebuilt wheels

✅ **Simplified requirements** - Removed conflicting versions

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Python 3.14.3 still used | Check `backend/runtime.txt` exists |
| Build fails with Rust error | All packages now have prebuilt wheels |
| CORS errors | Make sure CORS_ORIGINS matches your Vercel URL |
| Yolo/Llama errors | These are warnings; app will still start |

## Local Testing

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Test API: `http://localhost:8000/docs`

## Frontend Configuration

Update your frontend API calls to use Render backend URL:

```javascript
const API_URL = 'https://your-render-service-name.onrender.com';
```

Get this URL from your Render service dashboard.
