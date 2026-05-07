# VISIONZ Backend Deployment Guide

## Supported Platforms

### **Recommended: Koyeb** (FREE with option to pay)
- **Sign up:** https://koyeb.com
- **Free:** 2 services + $50/month credits
- **Cost after free tier:** ~$6-12/month

### **Alternative 1: DigitalOcean**
- **Sign up:** https://digitalocean.com
- **Free:** $200 credits (3-6 months)
- **Cost after:** ~$5-12/month

### **Alternative 2: PythonAnywhere** 
- **Sign up:** https://pythonanywhere.com
- **Free:** Limited tier available
- **Cost after:** ~$5/month

---

## Deploy on Koyeb (Easiest)

### **Step 1: Sign Up**
1. Go to https://koyeb.com
2. Click **Sign up with GitHub**
3. Authorize Koyeb to access your GitHub repos

### **Step 2: Create Service**
1. Click **Deployments** → **New Service**
2. Choose **GitHub**
3. Select repository: `Nivethitha-1131/VISIONZ`
4. Click **Connect**

### **Step 3: Configure Service**
- **Builder:** Buildpack (Auto-detect)
- **Port:** 8000
- **Routes:** `/api` → Backend service

### **Step 4: Environment Variables**
Add these in Koyeb Dashboard:

```
PYTHON_VERSION=3.10.14
PYTHONUNBUFFERED=1
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./database.db
CORS_ORIGINS=https://visionz.vercel.app
OLLAMA_TIMEOUT=300
```

### **Step 5: Deploy**
1. Click **Deploy Service**
2. Wait 3-5 minutes for deployment
3. Copy your service URL from the dashboard

---

## Deploy on DigitalOcean

### **Step 1: Create App**
1. Go to https://cloud.digitalocean.com
2. Create new **App Platform** project
3. Connect GitHub repo: `Nivethitha-1131/VISIONZ`

### **Step 2: Configure**
- **Source:** GitHub repository
- **Branch:** main
- **Build command:** `pip install -r requirements.txt`
- **Run command:** `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### **Step 3: Set Environment Variables**
```
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
DATABASE_URL=sqlite:///./database.db
CORS_ORIGINS=https://visionz.vercel.app
```

### **Step 4: Deploy**
- Click **Deploy** and wait

---

## After Deployment

Once deployed on your chosen platform:

1. **Get your backend URL** (e.g., `https://visionz-backend-abc123.koyeb.app`)
2. **Update frontend API URL** in `frontend/js/api.js`:
   ```javascript
   const API_BASE = 'https://your-backend-url.koyeb.app/api';
   ```
3. **Update CORS in environment variables** to match your Vercel frontend URL
4. **Push to GitHub** - both platforms will auto-redeploy

---

## Test Your Deployment

After deployment, test these endpoints:

- **Health Check:** `https://your-backend-url/api/health`
- **API Docs:** `https://your-backend-url/docs`

If both work, your backend is live! ✅

---

## Troubleshooting

**Port Error?** 
- Ensure port is set to 8000
- Check `--port $PORT` or `--port 8000` in start command

**Dependencies Missing?**
- Verify `requirements.txt` is in backend folder
- Check build logs for pip install errors

**CORS Error?**
- Update `CORS_ORIGINS` to match your frontend URL
- Restart service after changing environment variables

---

## Cost Comparison

| Platform | Free Amount | Paid Price | Best For |
|----------|------------|-----------|----------|
| **Koyeb** | $50/month credits | $6-12/mo | Recommended |
| **DigitalOcean** | $200 credits | $5-12/mo | Reliable |
| **Railway** | Free trial ended | $5+/mo | Previously used |
| **PythonAnywhere** | Limited | $5/mo | Simplest |
| **Render** | Free tier | $7+/mo | Similar to Railway |

