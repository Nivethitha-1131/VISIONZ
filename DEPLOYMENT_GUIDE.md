# VISIONZ Deployment Configuration

## Frontend Deployment (Vercel)

**Files Used:**
- `frontend/vercel.json` - Frontend deployment configuration
- `frontend/` - All static HTML/JS files

**Steps:**
1. Create a new project in Vercel
2. Connect your GitHub repository
3. Set Root Directory to `frontend/`
4. Vercel will automatically use `frontend/vercel.json`
5. Deploy

**Environment Variables (if needed):** None required for static frontend

---

## Backend Deployment (Railway)

**Files Used:**
- `backend/Procfile` - Process file telling Railway how to start the app
- `backend/railway.json` - Railway configuration
- `backend/requirements.txt` - Python dependencies
- `backend/.env.example` - Environment variables template

**Steps:**
1. Create a new project in Railway
2. Connect your GitHub repository
3. Set the Root Directory to `backend/`
4. Add environment variables from `backend/.env.example`:
   - `ENVIRONMENT=production`
   - `DATABASE_URL` - Set your database connection
   - `SECRET_KEY` - Generate a strong secret key
   - `CORS_ORIGINS` - Set to your Vercel frontend URL
   - All other required variables from `.env.example`
5. Railway will auto-detect Procfile and start the app
6. Deploy

**Important Environment Variables for Railway:**
- `CORS_ORIGINS`: Must match your Vercel frontend URL (e.g., https://your-app.vercel.app)
- `DATABASE_URL`: Configure Railway PostgreSQL or external database
- `SECRET_KEY`: Generate using: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
- `ENVIRONMENT`: Set to `production`

---

## Communication Between Frontend & Backend

Update your frontend API calls to use the Railway backend URL:
```javascript
const BACKEND_URL = 'https://your-railway-api-url.up.railway.app';
```

---

## Directory Structure for Deployment

```
/
├── frontend/              # Vercel deployment
│   ├── vercel.json       # ✅ Frontend config
│   ├── index.html
│   ├── landing.html
│   ├── js/
│   └── ...
│
├── backend/              # Railway deployment
│   ├── Procfile          # ✅ Railway startup command
│   ├── railway.json      # ✅ Railway config
│   ├── .env.example      # ✅ Environment template
│   ├── requirements.txt   # ✅ Python dependencies
│   ├── index.py          # (Vercel only - unused for Railway)
│   ├── app/
│   │   ├── main.py
│   │   └── ...
│   └── ...
│
└── vercel.json           # ⚠️ REMOVE - Not needed for separate deployments
```

---

## Next Steps

1. ✅ Push code to GitHub
2. ✅ Deploy Frontend on Vercel
3. ✅ Deploy Backend on Railway
4. ✅ Configure CORS_ORIGINS on Railway to match Vercel frontend URL
5. ✅ Test API connectivity from frontend to backend
