# 🚀 Quick Start - Deploy in 10 Minutes

This is the fastest way to get your honeypot live for the hackathon.

---

## Prerequisites (2 minutes)

1. **GitHub Account**: Sign up at https://github.com
2. **Render Account**: Sign up at https://render.com (free)
3. **UptimeRobot Account**: Sign up at https://uptimerobot.com (free)
4. **OpenAI API Key**: Get from https://platform.openai.com

---

## Step 1: Clean & Push (3 minutes)

### Clean up old files:
```bash
.\cleanup_old_files.bat
```

### Push to GitHub:
```bash
git add .
git commit -m "Production deployment"
git push origin main
```

*If you don't have a repo yet:*
1. Create new repo on GitHub.com
2. Run:
```bash
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy to Render (3 minutes)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub and select your repo
4. Use these settings:

```
Name: scambot-honeypot
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

5. Add environment variables:
   - `API_KEY`: Generate with `python -c "import secrets; print(secrets.token_urlsafe(32))"`
   - `OPENAI_API_KEY`: Your OpenAI key

6. Click **"Create Web Service"**

Wait 2-5 minutes for deployment.

---

## Step 3: Set Up UptimeRobot (2 minutes)

1. Go to https://uptimerobot.com
2. Click **"+ Add New Monitor"**
3. Configure:

```
Type: HTTP(s)
Name: Scambot Honeypot
URL: https://YOUR-SERVICE-NAME.onrender.com/health
Interval: 5 minutes
```

4. Click **"Create Monitor"**

---

## Step 4: Test It (2 minutes)

### Test health endpoint:
```bash
curl https://YOUR-SERVICE-NAME.onrender.com/health
```

### Test API:
```bash
curl -X POST "https://YOUR-SERVICE-NAME.onrender.com/api/v1/conversation" \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test-123","message":{"sender":"scammer","text":"Your account will be blocked","timestamp":1770005528731},"conversationHistory":[]}'
```

---

## ✅ Done!

**Your URLs:**
- API Endpoint: `https://YOUR-SERVICE-NAME.onrender.com/api/v1/conversation`
- Health Check: `https://YOUR-SERVICE-NAME.onrender.com/health`

**Submit to Hackathon:**
1. Copy your API endpoint URL
2. Copy your API key
3. Paste into hackathon testing platform
4. Test!

---

## 📚 Need More Details?

- Full deployment guide: [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
- UptimeRobot setup: [UPTIMEROBOT_SETUP.md](UPTIMEROBOT_SETUP.md)

---

**Good luck! 🎉**
