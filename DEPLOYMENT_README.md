# VISIONZ Deployment Guide

## Architecture

This project uses a **separated deployment strategy**:

| Component | Platform | Configuration |
|-----------|----------|---|
| **Frontend** | Vercel | `frontend/vercel.json` |
| **Backend** | Render | `render.yaml` |

---

## Frontend Deployment - Vercel

### Prerequisites
- GitHub repository synced
- Vercel account (free or paid)

### Steps

1. **Go to Vercel Dashboard:**
   - https://vercel.com/dashboard

2. **Import Project:**
   - Click "Add New" → "Project"
   - Select GitHub repo: `Nivethitha-1131/VISIONZ`
   - Click "Import"

3. **Configure:**
   - **Framework Preset:** Other
   - **Root Directory:** `frontend/`
   - Vercel auto-detects `frontend/vercel.json`

4. **Deploy:**
   - Click "Deploy"
   - ✅ Frontend is live at: `https://visionz.vercel.app`

### Configuration File
- **Location:** `frontend/vercel.json`
- **Contains:** URL rewrites for SPA routing

---

## Backend Deployment - Render

### Prerequisites
- GitHub repository synced
- Render account (free tier available)

### Steps

1. **Go to Render Dashboard:**
   - https://dashboard.render.com

2. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect GitHub repo: `Nivethitha-1131/VISIONZ`

3. **Configure Service:**
   - **Name:** `visionz-backend`
   - **Root Directory:** `backend/`
   - **Runtime:** Python 3
   - **Build Command:** (auto-detected from render.yaml)
   - **Start Command:** (auto-detected from render.yaml)

4. **Set Environment Variables:**
   - Render auto-reads from `render.yaml`
   - Additional vars in Render Dashboard if needed

5. **Deploy:**
   - Click "Create Web Service"
   - ⏳ Build takes 5-10 minutes
   - ✅ Backend is live at: `https://visionz-backend.onrender.com`

### Configuration File
- **Location:** `render.yaml`
- **Contains:** Build commands, start command, environment variables

---

## Integration

### Update Frontend API URL

After backend is deployed, update `frontend/js/api.js`:

```javascript
const API_BASE = 'https://visionz-backend.onrender.com/api';
```

### Commit and Push

```bash
git add frontend/js/api.js
git commit -m "Update backend URL to Render deployment"
git push
```

✅ Vercel auto-redeploys frontend with new API URL

---

## Test Deployment

### Frontend
```
https://visionz.vercel.app
```
Should load the login page ✅

### Backend Health
```
https://visionz-backend.onrender.com/api/health
```
Should return JSON response ✅

### API Documentation
```
https://visionz-backend.onrender.com/docs
```
Should show FastAPI Swagger UI ✅

---

## Troubleshooting

### Backend won't deploy on Render
- Check `render.yaml` syntax
- Verify `requirements.txt` has all dependencies
- Check logs in Render Dashboard

### Frontend shows 404 errors
- Verify `frontend/vercel.json` routing rules
- Ensure `frontend/` folder is set as root directory
- Check browser cache (hard refresh)

### API calls fail from frontend
- Verify CORS_ORIGINS in render.yaml matches Vercel URL
- Check backend is showing "Running" status on Render
- Test health endpoint manually in browser

---

## Deployment Status

After both are deployed:

```
✅ Frontend: https://visionz.vercel.app
✅ Backend: https://visionz-backend.onrender.com
✅ Integration: Working
```

---

## Next Steps

1. Deploy frontend on Vercel
2. Deploy backend on Render
3. Update API URL in frontend
4. Test full integration
5. Done! 🎉
