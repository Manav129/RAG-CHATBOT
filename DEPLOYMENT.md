# 🚀 Deployment Guide

This guide explains how to deploy the AI Customer Support Agent to **Render (Backend)** and **Vercel (Frontend)** with **GitHub Actions CI/CD**.

## Architecture

- **Backend**: FastAPI + MySQL + Qdrant → Render
- **Frontend**: HTML/CSS/JS → Vercel  
- **CI/CD**: GitHub Actions (auto-deploy on push to main)

---

## Prerequisites

1. **GitHub Account** - to host your code
2. **Render Account** - free at https://render.com
3. **Vercel Account** - free at https://vercel.com
4. **Qdrant Cloud Account** - free at https://cloud.qdrant.io
5. **Groq API Key** - free at https://console.groq.com

---

## Step 1: Setup Qdrant Cloud

1. Go to https://cloud.qdrant.io and sign up
2. Create a new cluster (free tier)
3. Note your:
   - **Cluster URL**: `https://xxxxx.qdrant.io`
   - **API Key**: Click "Generate API Key"

---

## Step 2: Deploy Backend to Render

### 2.1 Push Code to GitHub

```bash
cd "C:\Users\manav\OneDrive\Desktop\AI Customer Support Agent using RAG"
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/Manav129/RAG-CHATBOT.git
git push -u origin main
```

### 2.2 Create Render Account & Services

1. Go to https://render.com and sign up
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub repository
4. Render will detect `render.yaml` and create:
   - Web Service (backend)
   - PostgreSQL Database (free tier)

### 2.3 Set Environment Variables in Render

Go to your web service → **Environment** → Add:

```
GROQ_API_KEY=your_groq_api_key_here
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
ENVIRONMENT=production
```

### 2.4 Get Your Backend URL

After deployment, Render will give you a URL like:
```
https://ai-support-backend-xxxx.onrender.com
```

**Copy this URL** - you'll need it for the frontend!

---

## Step 3: Deploy Frontend to Vercel

### 3.1 Update Frontend API URL

1. Open [frontend/script.js](frontend/script.js)
2. Replace `"https://your-backend-url.onrender.com"` with your actual Render URL:

```javascript
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? ""
    : "https://ai-support-backend-xxxx.onrender.com"; // Your actual Render URL
```

3. Commit and push:
```bash
git add frontend/script.js
git commit -m "Update API URL for production"
git push
```

### 3.2 Deploy to Vercel

1. Go to https://vercel.com and sign up
2. Click **"Import Project"**
3. Select your GitHub repository
4. Vercel will detect `vercel.json` automatically
5. Click **"Deploy"**

Your frontend will be live at: `https://your-project.vercel.app`

---

## Step 4: Setup GitHub Actions CI/CD

### 4.1 Get Render Deploy Hook

1. In Render, go to your web service
2. **Settings** → **Deploy Hook**
3. Copy the webhook URL

### 4.2 Get Vercel Token

1. Go to https://vercel.com/account/tokens
2. Create a new token
3. Copy it

### 4.3 Add GitHub Secrets

1. Go to your GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add these secrets:
   - `RENDER_DEPLOY_HOOK_URL` - your Render webhook
   - `VERCEL_TOKEN` - your Vercel token

### 4.4 Test CI/CD

Push any change to main branch:
```bash
git add .
git commit -m "Test CI/CD"
git push
```

GitHub Actions will automatically:
1. Run tests
2. Deploy backend to Render
3. Deploy frontend to Vercel

---

## Step 5: Ingest Documents to Qdrant Cloud

After backend is deployed, ingest your PDFs:

```bash
curl -X POST https://ai-support-backend-xxxx.onrender.com/ingest
```

This will upload all PDFs from `data/docs/` to Qdrant Cloud.

---

## Step 6: Test Your Live Application

1. Visit your Vercel URL: `https://your-project.vercel.app`
2. Try asking a question
3. Check ticket creation

---

## Environment Variables Summary

### Local Development (.env)
```env
GROQ_API_KEY=your_key
MYSQL_HOST=localhost
MYSQL_PASSWORD=your_password
QDRANT_URL=http://localhost:6333
```

### Production (Render)
```env
GROQ_API_KEY=your_key
DATABASE_URL=postgresql://... (auto-provided by Render)
QDRANT_URL=https://xxxxx.qdrant.io
QDRANT_API_KEY=your_qdrant_key
ENVIRONMENT=production
```

---

## Troubleshooting

### Backend won't start
- Check Render logs: **Logs** tab in your service
- Verify all environment variables are set
- Check `GROQ_API_KEY` is valid

### Frontend can't connect to backend
- Check API URL in [frontend/script.js](frontend/script.js)
- Check Render service is running (not sleeping)
- Check browser console for CORS errors

### Qdrant connection fails
- Verify `QDRANT_URL` is correct (with https://)
- Verify `QDRANT_API_KEY` is set
- Check Qdrant cluster is active

### Database errors
- Render auto-creates PostgreSQL, not MySQL
- Update `render.yaml` if you need MySQL
- Check DATABASE_URL is set correctly

---

## Monitoring

- **Render**: https://dashboard.render.com - view logs, metrics
- **Vercel**: https://vercel.com/dashboard - view deployments, analytics
- **Qdrant**: https://cloud.qdrant.io - view collections, storage

---

## Cost (Free Tier Limits)

- **Render**: 750 hours/month (always-on), 100GB bandwidth
- **Vercel**: 100GB bandwidth, unlimited deployments
- **Qdrant Cloud**: 1GB storage, 1M requests/month
- **Groq**: 14,400 requests/day

All completely **FREE** for this project! 🎉

---

## Next Steps

- Add custom domain to Vercel
- Set up monitoring with Sentry
- Add rate limiting
- Implement user authentication

---

**Need Help?** Check:
- Render Docs: https://render.com/docs
- Vercel Docs: https://vercel.com/docs
- Qdrant Docs: https://qdrant.tech/documentation
