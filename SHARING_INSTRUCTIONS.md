# Sharing Instructions - Quick Reference

## ✅ No Code Changes Needed!

Your API is already properly secured. The `x-api-key` header authentication is implemented and working.

---

## 📋 What to Share With Your Teammate

### Give them these 3 things:

1. **Your Render URL**
   - Find it: Render Dashboard → Your Service → Copy the URL at the top
   - Format: `https://your-service-name.onrender.com`

2. **Your API Key Value**
   - Find it: Render Dashboard → Your Service → Environment tab → Copy the `API_KEY` value
   - Example: `NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY`

3. **The Testing Guide**
   - Share the file: [POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)

### Example Message to Teammate:
```
Hey [Name],

Here's everything you need for Postman testing:

Base URL: https://scambot-honeypot-xyz123.onrender.com
API Key: [PASTE YOUR API_KEY VALUE FROM RENDER]

1. Add this header to ALL requests to /api/v1/conversation:
   x-api-key: [YOUR API KEY VALUE]

2. See POSTMAN_TESTING_GUIDE.md for:
   - Example requests
   - Test scenarios
   - Expected responses
   - Troubleshooting

The /health endpoint doesn't need authentication - use it to verify the service is up.
```

---

## 📤 What to Submit to GUVI

### The hackathon form asks for 2 things:

**1. x-api-key**
- Go to: Render Dashboard → Your Service → Environment tab
- Copy the value of `API_KEY`
- Paste it into the "x-api-key" field

**2. Honeypot API Endpoint URL**
- Format: `https://[your-render-url]/api/v1/conversation`
- Example: `https://scambot-honeypot-xyz123.onrender.com/api/v1/conversation`

### Finding Your Render URL:
1. Log in to Render: https://dashboard.render.com/
2. Click your service
3. Copy the URL at the top (looks like `https://something.onrender.com`)
4. Add `/api/v1/conversation` to the end

### Example Submission:
```
x-api-key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY

Honeypot API Endpoint URL: https://scambot-honeypot-xyz123.onrender.com/api/v1/conversation
```

For detailed instructions, see: [GUVI_SUBMISSION_GUIDE.md](GUVI_SUBMISSION_GUIDE.md)

---

## 🔑 Understanding API Keys

Confused about API keys? See: [API_KEY_EXPLANATION.md](API_KEY_EXPLANATION.md)

**Quick explanation:**
- `API_KEY` (Render environment variable) = Your secret stored on the server
- `x-api-key` (HTTP header) = How clients send that secret in requests
- **They're the same value!**

---

## ✅ Pre-Submission Checklist

Before sharing or submitting:

### 1. Verify Service is Running
```bash
# Visit this URL in your browser:
https://your-service.onrender.com/health

# Should return:
{"status": "healthy", "active_sessions": 0}
```

### 2. Test Authentication Manually
Use Postman or curl:
```bash
curl -X POST https://your-service.onrender.com/api/v1/conversation \
  -H "x-api-key: YOUR_API_KEY_VALUE" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your account is blocked",
      "timestamp": 1704067200000
    },
    "conversationHistory": []
  }'
```

Should return a response with agent's reply.

### 3. Verify UptimeRobot is Active
- Check UptimeRobot dashboard shows "Up"
- Ensures service won't sleep during testing

### 4. Check Render Environment Variables
- Go to Render Dashboard → Environment
- Verify these are set:
  - ✅ `API_KEY` (strong random value)
  - ✅ `OPENAI_API_KEY` (starts with `sk-`)
  - ✅ `OPENAI_MODEL` (e.g., `gpt-4o`)

---

## 🚨 Common Issues

### Issue: Teammate gets 401 Unauthorized
**Fix:** Double-check they're using the correct API key value and header name is exactly `x-api-key` (lowercase)

### Issue: GUVI test fails
**Fix:**
1. Test with Postman first
2. Check Render logs for errors
3. Verify service is not sleeping (UptimeRobot should be active)

### Issue: Service returns 500 error
**Fix:** Check Render logs - likely OpenAI API issue

---

## 📁 Files Created for You

I've created these guides:

1. **[API_KEY_EXPLANATION.md](API_KEY_EXPLANATION.md)**
   - Clear explanation of API key architecture
   - Diagrams showing how it works
   - What to give to whom

2. **[POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)**
   - Complete Postman setup instructions
   - Example requests and responses
   - Test scenarios
   - Troubleshooting

3. **[GUVI_SUBMISSION_GUIDE.md](GUVI_SUBMISSION_GUIDE.md)**
   - What to submit to GUVI
   - Where to find the values
   - Pre-submission checklist
   - Expected test behavior

4. **[SHARING_INSTRUCTIONS.md](SHARING_INSTRUCTIONS.md)** (this file)
   - Quick reference for everything

---

## 🎯 Quick Actions

### Action 1: Share with Teammate RIGHT NOW
1. Get your Render URL: [Dashboard](https://dashboard.render.com/)
2. Get your API Key: Render → Environment → `API_KEY` value
3. Send them this message:
```
Base URL: [YOUR RENDER URL]
API Key: [YOUR API KEY VALUE]

Read POSTMAN_TESTING_GUIDE.md for instructions.

Add this header to requests: x-api-key: [YOUR API KEY]
```

### Action 2: Submit to GUVI
1. Get API Key: Render → Environment → `API_KEY` value
2. Get Endpoint URL: `https://[your-render-url]/api/v1/conversation`
3. Fill in the GUVI form
4. See GUVI_SUBMISSION_GUIDE.md for details

---

## 📊 Your Service URLs

Replace `[your-service-name]` with your actual Render service name:

| Purpose | URL |
|---------|-----|
| **Health Check** | `https://[your-service-name].onrender.com/health` |
| **Root** | `https://[your-service-name].onrender.com/` |
| **Main Endpoint** (for GUVI) | `https://[your-service-name].onrender.com/api/v1/conversation` |
| **Docs** (if DEBUG=True) | `https://[your-service-name].onrender.com/docs` |

---

## 🔒 Security Reminders

- ✅ API key is stored in Render (encrypted)
- ✅ API key is in .env (not committed to Git)
- ✅ Share API key only with authorized people
- ❌ Never commit API key to GitHub
- ❌ Never post API key publicly

---

## ❓ Need Help?

1. **API Key confusion?** Read [API_KEY_EXPLANATION.md](API_KEY_EXPLANATION.md)
2. **Teammate testing?** Share [POSTMAN_TESTING_GUIDE.md](POSTMAN_TESTING_GUIDE.md)
3. **GUVI submission?** Read [GUVI_SUBMISSION_GUIDE.md](GUVI_SUBMISSION_GUIDE.md)
4. **Service not responding?** Check Render logs and UptimeRobot status

---

**You're all set! No code changes needed.** 🚀

Your API is properly secured with `x-api-key` header authentication. Just share the right values with the right people using the guides above.
