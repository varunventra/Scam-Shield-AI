# GUVI Hackathon Submission Guide

## What to Submit

The hackathon "Agentic Honey-pot Endpoint Tester" requires two pieces of information:

### 1. x-api-key
**Value:** Get this from your Render dashboard
- Log in to Render
- Go to your service
- Click "Environment" tab
- Copy the value of `API_KEY` environment variable
- **This is what you paste into the "x-api-key" field**

### 2. Honeypot API Endpoint URL
**Value:** `https://your-service-name.onrender.com/api/v1/conversation`

**Format:**
- **Protocol:** `https://`
- **Domain:** Your Render service URL (e.g., `scambot-honeypot-xyz123.onrender.com`)
- **Path:** `/api/v1/conversation`

**Example:**
```
https://scambot-honeypot-abc123.onrender.com/api/v1/conversation
```

---

## Finding Your Render URL

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click on your service
3. At the top, you'll see the URL (e.g., `https://your-service.onrender.com`)
4. Add `/api/v1/conversation` to the end

---

## What GUVI Will Test

According to the hackathon description, GUVI will test:

### ✅ API authentication using headers
- They'll send the `x-api-key` header with your API key
- Your service validates it

### ✅ Endpoint availability and connectivity
- They'll make a POST request to your endpoint
- Your service should respond (not timeout)

### ✅ Proper request handling
- They'll send a JSON body in the correct format
- Your service should parse and process it

### ✅ Response structure and status codes
- Your service should return HTTP 200 with proper JSON
- The response should have required fields

### ✅ Basic honeypot behavior validation
- Your service should detect scam intent
- Your agent should engage in conversation
- Responses should be context-appropriate

---

## Expected Test Request

GUVI will likely send something like this:

**Method:** `POST`

**URL:** `https://your-service.onrender.com/api/v1/conversation`

**Headers:**
```
x-api-key: your-api-key-value
Content-Type: application/json
```

**Body:**
```json
{
  "sessionId": "guvi-test-session-001",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked. Verify your UPI PIN immediately.",
    "timestamp": 1704067200000
  },
  "conversationHistory": []
}
```

---

## Expected Response

Your service should return:

**Status Code:** `200 OK`

**Response Body:**
```json
{
  "status": "success",
  "sessionId": "guvi-test-session-001",
  "reply": "What? Why my account will be blocked? I didnt do anything wrong",
  "scamDetected": true,
  "scamConfidence": 0.95,
  "agentActivated": true
}
```

**Key Points:**
- ✅ Returns within reasonable time (< 30 seconds)
- ✅ Contains a human-like reply from the agent
- ✅ Indicates scam was detected
- ✅ Shows agent was activated
- ✅ Reply is contextually appropriate (not generic)

---

## Pre-Submission Checklist

Before submitting to GUVI, verify:

### 1. Service is Running
- [ ] Visit `https://your-service.onrender.com/health`
- [ ] Should return: `{"status": "healthy", "active_sessions": 0}`

### 2. UptimeRobot is Active
- [ ] Service won't sleep during testing
- [ ] Check UptimeRobot dashboard shows "Up"

### 3. Test with Postman
- [ ] POST to `/api/v1/conversation` with `x-api-key` header
- [ ] Verify you get a realistic response
- [ ] Check response has all required fields

### 4. Environment Variables Set
- [ ] `API_KEY` is set in Render
- [ ] `OPENAI_API_KEY` is set in Render
- [ ] No placeholder values

### 5. API Key Security
- [ ] API key is strong (32+ characters)
- [ ] API key is NOT committed to GitHub
- [ ] Only share with authorized people

---

## What to Submit to GUVI

### Field 1: x-api-key
```
[PASTE YOUR API_KEY VALUE FROM RENDER]
```
**Example:** `NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY`

### Field 2: Honeypot API Endpoint URL
```
https://[your-service-name].onrender.com/api/v1/conversation
```
**Example:** `https://scambot-honeypot-xyz123.onrender.com/api/v1/conversation`

---

## Troubleshooting

### Issue: GUVI test returns 401 Unauthorized
**Cause:** Wrong API key
**Fix:**
1. Double-check the API key value from Render
2. Ensure no extra spaces or characters
3. Re-submit with correct key

### Issue: GUVI test returns 503 Service Unavailable
**Cause:** Render service is sleeping (free tier)
**Fix:**
1. Check UptimeRobot is running and monitoring `/health`
2. Visit your service URL to wake it up
3. Wait 2-3 minutes for service to start
4. Re-submit

### Issue: GUVI test returns 500 Internal Server Error
**Cause:** Server-side issue (likely OpenAI API)
**Fix:**
1. Check Render logs for errors
2. Verify `OPENAI_API_KEY` is set correctly in Render
3. Test manually with Postman first

### Issue: GUVI test times out
**Cause:** Service is slow to respond (cold start or OpenAI delay)
**Fix:**
1. Ensure UptimeRobot is keeping service warm
2. OpenAI calls may take 5-10 seconds (this is normal)
3. Service has 30s timeout - should be enough

---

## After Submission

### Monitor Your Service
1. **Render Logs:** Check for incoming requests from GUVI
2. **UptimeRobot:** Ensure service stays up during evaluation
3. **Response Times:** Should be < 30 seconds

### Expected Behavior
- GUVI will send test messages
- Your agent should respond naturally
- Scam detection should work
- No crashes or errors

---

## Quick Reference

| What | Where to Get It | Example |
|------|----------------|---------|
| **x-api-key** | Render Dashboard → Environment → API_KEY value | `NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY` |
| **Endpoint URL** | `https://[your-render-url]/api/v1/conversation` | `https://scambot-honeypot.onrender.com/api/v1/conversation` |
| **Health Check** | `https://[your-render-url]/health` | `https://scambot-honeypot.onrender.com/health` |

---

## Example Submission

```
x-api-key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY

Honeypot API Endpoint URL: https://scambot-honeypot-abc123.onrender.com/api/v1/conversation
```

---

## Need Help?

### Before Submitting
1. Test with Postman using the guide above
2. Check Render logs for any errors
3. Verify UptimeRobot is active
4. Ensure service responds within 30 seconds

### During Evaluation
- Monitor Render logs for incoming requests
- Check for any errors in real-time
- Service should handle all test scenarios automatically

---

**Remember:**
- The `x-api-key` is the VALUE of your `API_KEY` environment variable
- The endpoint URL must include `/api/v1/conversation` at the end
- Test manually before submitting to GUVI
- Keep UptimeRobot running during evaluation period

Good luck! 🚀
