# 🚀 Render Deployment Guide - Production Ready

Complete guide to deploy your Scambot Honeypot to Render (Free Tier) for the GUVI Hackathon.

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Step-by-Step Deployment](#step-by-step-deployment)
3. [Environment Variables Setup](#environment-variables-setup)
4. [UptimeRobot Configuration](#uptimerobot-configuration)
5. [Testing Your Deployment](#testing-your-deployment)
6. [Troubleshooting](#troubleshooting)

---

## ✅ Pre-Deployment Checklist

Before deploying, ensure you have:

- [ ] GitHub account (free)
- [ ] Render account (free) - Sign up at https://render.com
- [ ] OpenAI API key with credits
- [ ] UptimeRobot account (free) - Sign up at https://uptimerobot.com
- [ ] Git installed and configured

---

## 🚀 Step-by-Step Deployment

### Step 1: Clean Up Old Files

Run the cleanup script to remove Docker and ngrok files:

```bash
.\cleanup_old_files.bat
```

Or manually delete:
- `Dockerfile`
- `docker-compose.yml`
- `.dockerignore`
- `run_with_ngrok.py`
- `NGROK_DEPLOYMENT.md`

### Step 2: Commit and Push to GitHub

```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit changes
git commit -m "Production-ready deployment for Render"

# Create a new GitHub repository (via GitHub.com)
# Then connect and push:
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy to Render

#### 3.1 Create New Web Service

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub account (if not already connected)
4. Select your honeypot repository
5. Click **"Connect"**

#### 3.2 Configure the Service

Fill in the following settings:

| Field | Value |
|-------|-------|
| **Name** | `scambot-honeypot` (or your preferred name) |
| **Region** | Select closest to you (e.g., Oregon) |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |
| **Plan** | **Free** |

#### 3.3 Advanced Settings (Optional but Recommended)

Click **"Advanced"** and configure:

- **Auto-Deploy**: ✅ Yes (deploys automatically on git push)
- **Health Check Path**: `/health`

---

## 🔐 Environment Variables Setup

### Required Environment Variables

In the Render dashboard, scroll down to **"Environment Variables"** and add:

#### Critical Variables (Must Set):

```
API_KEY=<generate-a-secure-random-key>
OPENAI_API_KEY=<your-openai-api-key>
```

**🔑 To Generate a Secure API Key:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Or use: https://generate-secret.vercel.app/32

#### Optional Variables (Use Defaults if Not Set):

```
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
MAX_TOKENS=1000
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
DEBUG=false
LOG_LEVEL=INFO
MAX_CONVERSATION_TURNS=20
SESSION_TIMEOUT=3600
SCAM_CONFIDENCE_THRESHOLD=0.7
AGENT_NAME=Rahul
AGENT_AGE=28
AGENT_OCCUPATION=Software Engineer
HOST=0.0.0.0
```

**Note:** `PORT` is automatically set by Render - don't add it manually.

### How to Add Environment Variables:

1. In your Render service dashboard, find the **"Environment"** section
2. Click **"Add Environment Variable"**
3. Enter **Key** and **Value**
4. Click **"Save Changes"**
5. Service will automatically redeploy

---

## 🎯 Deploy!

Click **"Create Web Service"** at the bottom.

Render will:
1. ✅ Clone your repository
2. ✅ Install dependencies
3. ✅ Start your application
4. ✅ Provide you with a public URL

**Deployment takes 2-5 minutes.**

Your service URL will be: `https://your-service-name.onrender.com`

---

## 🔍 UptimeRobot Configuration

Render Free Tier **spins down after 15 minutes of inactivity**. UptimeRobot keeps it alive.

### Step 1: Sign Up for UptimeRobot

1. Go to https://uptimerobot.com
2. Sign up for a free account
3. Verify your email

### Step 2: Create a Monitor

1. Click **"+ Add New Monitor"**
2. Configure the monitor:

| Field | Value |
|-------|-------|
| **Monitor Type** | HTTP(s) |
| **Friendly Name** | `Scambot Honeypot` |
| **URL** | `https://your-service-name.onrender.com/health` |
| **Monitoring Interval** | `5 minutes` (free tier) |
| **Monitor Timeout** | `30 seconds` |
| **HTTP Method** | `GET` |

3. Click **"Create Monitor"**

### Step 3: Verify Monitor is Working

- Status should show **"Up"** within a few minutes
- The monitor will ping your service every 5 minutes
- This prevents Render from spinning down your service

**🎉 Your service will now stay alive 24/7!**

---

## ✅ Testing Your Deployment

### 1. Health Check Test

```bash
curl https://your-service-name.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "scambot-honeypot",
  "active_sessions": 0
}
```

### 2. API Endpoint Test

```bash
curl -X POST "https://your-service-name.onrender.com/api/v1/conversation" \
  -H "x-api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify now.",
      "timestamp": 1770005528731
    },
    "conversationHistory": []
  }'
```

Expected response:
```json
{
  "status": "success",
  "reply": "Why would my account be blocked? Can you tell me more?"
}
```

### 3. Submit to Hackathon Platform

Go to the GUVI Hackathon testing platform and enter:

**Honeypot API Endpoint URL:**
```
https://your-service-name.onrender.com/api/v1/conversation
```

**Headers:**
- Header Name: `x-api-key`
- Header Value: `<your-api-key>`

Click **"Test Honeypot Endpoint"**

---

## 📊 Monitoring Your Service

### Render Dashboard

View logs and metrics:
1. Go to your service in Render dashboard
2. Click **"Logs"** to see real-time logs
3. Click **"Metrics"** to see CPU/Memory usage

### UptimeRobot Dashboard

Monitor uptime:
1. View response times
2. Check uptime percentage
3. Get alerts if service goes down

---

## 🐛 Troubleshooting

### Issue: "Build failed"

**Solution:**
1. Check Render logs for error details
2. Verify `requirements.txt` has no syntax errors
3. Ensure all dependencies are available on PyPI

### Issue: "Application failed to start"

**Solution:**
1. Check that `OPENAI_API_KEY` is set in environment variables
2. Verify the start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Check logs for specific error messages

### Issue: "Invalid API key" error when testing

**Solution:**
1. Verify `API_KEY` environment variable is set in Render
2. Make sure you're using the same API key in your test request
3. Check that the header is named `x-api-key` (lowercase)

### Issue: "Service keeps spinning down"

**Solution:**
1. Verify UptimeRobot monitor is active
2. Check monitor interval is set to 5 minutes
3. Ensure monitor URL is correct: `/health` endpoint

### Issue: "OpenAI API error"

**Solution:**
1. Verify `OPENAI_API_KEY` is correct
2. Check OpenAI account has sufficient credits
3. Ensure API key has proper permissions

### Issue: "GUVI callback failing"

**Solution:**
1. Check Render logs for callback errors
2. Verify `GUVI_CALLBACK_URL` is correct
3. Ensure your service has internet access (should be automatic)

### Issue: "502 Bad Gateway"

**Solution:**
1. Service is probably still deploying - wait 2-5 minutes
2. Check Render dashboard for deployment status
3. If persists, check logs for startup errors

---

## 🔄 Updating Your Deployment

To update your service:

```bash
# Make changes to your code
git add .
git commit -m "Your update message"
git push origin main
```

Render will automatically:
1. Detect the push
2. Rebuild your service
3. Deploy the new version
4. Zero-downtime deployment

---

## 📝 Important Notes

### Render Free Tier Limitations:

- ✅ **750 hours/month** of runtime (enough for 24/7 with one service)
- ✅ **Automatic HTTPS** (SSL certificates included)
- ⚠️ **Spins down after 15 minutes** of inactivity (UptimeRobot solves this)
- ⚠️ **Cold start delay** (~30 seconds if spun down)
- ⚠️ **Ephemeral filesystem** (sessions lost on restart - acceptable for honeypot)

### Session Management:

- Sessions are stored **in-memory**
- Sessions expire after **1 hour** of inactivity (configurable)
- On service restart, all sessions are lost
- This is **acceptable for a honeypot** - each conversation is independent

### Security:

- ✅ All secrets in environment variables (not in code)
- ✅ API key authentication enabled
- ✅ CORS configured
- ✅ HTTPS enabled by default
- ✅ `.env` file in `.gitignore` (never committed)

---

## 🎯 Hackathon Submission Checklist

Before submitting:

- [ ] Service is deployed and accessible
- [ ] Health check endpoint returns 200 OK
- [ ] API endpoint accepts requests with x-api-key header
- [ ] Scam detection is working
- [ ] AI agent generates human-like responses
- [ ] Intelligence extraction is functional
- [ ] GUVI callback is being sent
- [ ] UptimeRobot monitor is active
- [ ] Service has been tested with hackathon tester

---

## 📞 Support Resources

- **Render Documentation**: https://render.com/docs
- **Render Community**: https://community.render.com
- **UptimeRobot Docs**: https://uptimerobot.com/help
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **OpenAI Docs**: https://platform.openai.com/docs

---

## 🎉 Success!

Your honeypot is now deployed and ready for the hackathon!

**Your deployment URLs:**
- **API Endpoint**: `https://your-service-name.onrender.com/api/v1/conversation`
- **Health Check**: `https://your-service-name.onrender.com/health`
- **Root**: `https://your-service-name.onrender.com/`

**Good luck with the hackathon! 🚀**

---

## 📄 Quick Reference

### Render Service Settings:
```yaml
Name: scambot-honeypot
Runtime: Python 3
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
Plan: Free
```

### Required Environment Variables:
```
API_KEY=<your-secure-key>
OPENAI_API_KEY=<your-openai-key>
```

### UptimeRobot Monitor:
```
Type: HTTP(s)
URL: https://your-service-name.onrender.com/health
Interval: 5 minutes
```

### Test Command:
```bash
curl https://your-service-name.onrender.com/health
```

---

**End of Guide**
