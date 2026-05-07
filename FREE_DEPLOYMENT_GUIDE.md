# VISIONZ Backend - Hugging Face Spaces Deployment

## ✅ Deploy on Hugging Face Spaces

**Why Hugging Face?**
- ✅ **100% FREE** - No credit card needed
- ✅ Easy GitHub integration
- ✅ Docker support built-in
- ✅ Perfect for FastAPI apps
- ✅ Unlimited projects
- ✅ Automatic deployment

---

## Step-by-Step: Deploy on Hugging Face Spaces

### **Step 1: Create Hugging Face Account**

1. Go to https://huggingface.co
2. Click **Sign up**
3. Create free account (email or GitHub)
4. Verify email

### **Step 2: Create New Space**

1. Click your **profile** → **My Spaces**
2. Click **New Space** button
3. Fill in:
   - **Space name:** `visionz-backend`
   - **License:** OpenRAIL-M (or choose your preference)
   - **Space SDK:** `Docker`
   - **Visibility:** Public or Private (your choice)
4. Click **Create Space**

### **Step 3: Connect GitHub Repository**

1. In the new Space, click **⚙️ Settings**
2. Scroll to **Repository settings**
3. Click **Connect to GitHub** 
4. Select: `Nivethitha-1131/VISIONZ`
5. Choose **Branch:** `main`
6. **Automatic sync:** Enable
7. **Save**

### **Step 4: Configure Environment Variables**

1. In Space settings, go to **Secrets**
2. Add these environment variables:

| Key | Value |
|-----|-------|
| `ENVIRONMENT` | `production` |
| `DEBUG` | `false` |
| `LOG_LEVEL` | `INFO` |
| `CORS_ORIGINS` | `https://visionz.vercel.app` |
| `OLLAMA_TIMEOUT` | `300` |

3. Click **Save**

### **Step 5: Configure Dockerfile Location**

1. Go to **Space settings** → **Docker**
2. Set **Dockerfile path:** `backend/Dockerfile`
3. Set **Build context:** `backend/`
4. Click **Save**

### **Step 6: Deploy**

1. Hugging Face automatically builds when you save settings
2. Watch the build logs in the **Logs** tab
3. Wait for **"Running on public URL"** message
4. Your Space is live! 🎉

### **Step 7: Get Your Backend URL**

Your backend URL will be:
```
https://[your-username]-visionz-backend.hf.space
```

Example:
```
https://nivethitha-visionz-backend.hf.space
```

---

## Update Frontend with Hugging Face URL

### **Edit `frontend/js/api.js`:**

Replace this line:
```javascript
const API_BASE = 'https://visionz-backend.fly.dev/api';
```

With your Hugging Face URL:
```javascript
const API_BASE = 'https://[your-username]-visionz-backend.hf.space/api';
```

**Example:**
```javascript
const API_BASE = 'https://nivethitha-visionz-backend.hf.space/api';
```

Then push to GitHub - Vercel auto-updates!

---

## Test Your Deployment

After deployment, test these endpoints:

**1. Health Check:**
```
https://[your-username]-visionz-backend.hf.space/api/health
```

**2. API Docs (OpenAPI):**
```
https://[your-username]-visionz-backend.hf.space/docs
```

**3. Test with cURL:**
```bash
curl https://[your-username]-visionz-backend.hf.space/api/health
```

If you see a response, it's working! ✅

---

## Hugging Face Space Settings Tips

### **Make it Private (Optional)**
- Settings → **Visibility** → Private
- Only people with link can access

### **Change Compute (Optional)**
- Settings → **Compute** → Upgrade if needed
- Free tier is GPU-enabled! 🚀

### **View Logs**
- Click **Logs** tab to see deployment progress
- Useful for debugging

### **Manual Rebuild**
- Settings → **Factory reboot** if needed
- Restarts the Space

---

## Troubleshooting

### **Build fails?**
- Check the **Logs** tab for errors
- Ensure `Dockerfile` path is `backend/Dockerfile`
- Verify `requirements.txt` exists in backend folder

### **App crashes after build?**
- Check **Logs** for runtime errors
- Verify port is set to `7860` in Dockerfile
- Check environment variables are set correctly

### **CORS errors on frontend?**
- Update `CORS_ORIGINS` in Space settings to match your Vercel URL
- Exact match required (including https://)

### **Port already in use?**
- Hugging Face uses port `7860`
- Dockerfile already configured for this

### **Can't connect from frontend?**
1. Check Space is running (green "Running" badge)
2. Verify API URL is correct in `frontend/js/api.js`
3. Check CORS_ORIGINS matches Vercel domain
4. Test health endpoint in browser

---

## Full Deployment Status

| Component | Platform | Status | URL |
|-----------|----------|--------|-----|
| **Frontend** | Vercel | ✅ Live | https://visionz.vercel.app |
| **Backend** | Hugging Face | ✅ ReadyToDeploy | https://[username]-visionz-backend.hf.space |
| **Database** | SQLite | ✅ Included | Local (app/database) |
| **API Integration** | FastAPI | ✅ Configured | /api endpoints |

---

## After Everything Works

Once backend is live on Hugging Face:

1. ✅ Update `frontend/js/api.js` with your Hugging Face URL
2. ✅ Push to GitHub
3. ✅ Vercel auto-redeploys frontend
4. ✅ Test full integration

Your full stack is now deployed for FREE! 🎉

---

## Need Help?

- **Hugging Face Docs:** https://huggingface.co/docs/hub/spaces
- **Docker Docs:** https://docs.docker.com
- **FastAPI Docs:** https://fastapi.tiangolo.com



