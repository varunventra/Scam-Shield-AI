# Postman Testing Guide for Teammate

## Quick Setup

### 1. Base Configuration

**Render Service URL:** `https://your-service-name.onrender.com`
*(Replace with your actual Render URL)*

**API Key:** `[GET THIS FROM RENDER DASHBOARD]`
- Go to your Render dashboard
- Click on your service
- Go to "Environment" tab
- Copy the value of `API_KEY`

### 2. Postman Setup

Create a new request in Postman with these details:

#### Headers (Required for ALL requests)
```
x-api-key: [YOUR_API_KEY_VALUE]
Content-Type: application/json
```

## Test Endpoints

### 1. Health Check (No Auth Required)

**Endpoint:** `GET /health`
**Full URL:** `https://your-service-name.onrender.com/health`

**Expected Response:**
```json
{
  "status": "healthy",
  "active_sessions": 0
}
```

**Purpose:** Verify service is running

---

### 2. Root Endpoint (No Auth Required)

**Endpoint:** `GET /`
**Full URL:** `https://your-service-name.onrender.com/`

**Expected Response:**
```json
{
  "service": "Scambot Honeypot API",
  "version": "1.0.0",
  "status": "running"
}
```

---

### 3. Main Conversation Endpoint (AUTH REQUIRED)

**Endpoint:** `POST /api/v1/conversation`
**Full URL:** `https://your-service-name.onrender.com/api/v1/conversation`

**Headers:**
```
x-api-key: [YOUR_API_KEY_VALUE]
Content-Type: application/json
```

**Request Body:**
```json
{
  "sessionId": "test-session-001",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked immediately. Verify your UPI PIN now.",
    "timestamp": 1704067200000
  },
  "conversationHistory": []
}
```

**Expected Response:**
```json
{
  "status": "success",
  "sessionId": "test-session-001",
  "reply": "What? Why my account will be blocked? I didnt do anything wrong",
  "scamDetected": true,
  "scamConfidence": 0.95,
  "agentActivated": true
}
```

---

## Test Scenarios

### Test 1: High Confidence Scam
```json
{
  "sessionId": "test-high-confidence",
  "message": {
    "sender": "scammer",
    "text": "URGENT: Your account suspended. Send OTP immediately to restore access.",
    "timestamp": 1704067200000
  },
  "conversationHistory": []
}
```
**Expected:** Agent should engage with realistic elderly response

---

### Test 2: Multi-turn Conversation
First message:
```json
{
  "sessionId": "test-conversation-001",
  "message": {
    "sender": "scammer",
    "text": "Hello, this is from bank customer care. Your account needs verification.",
    "timestamp": 1704067200000
  },
  "conversationHistory": []
}
```

Second message (use the reply from first as history):
```json
{
  "sessionId": "test-conversation-001",
  "message": {
    "sender": "scammer",
    "text": "Please share your account number to verify.",
    "timestamp": 1704067260000
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Hello, this is from bank customer care. Your account needs verification.",
      "timestamp": 1704067200000
    },
    {
      "sender": "user",
      "text": "[RESPONSE FROM FIRST CALL]",
      "timestamp": 1704067230000
    }
  ]
}
```

---

## Common Issues

### Issue: 401 Unauthorized
**Cause:** Wrong or missing API key
**Fix:**
1. Check you added `x-api-key` header (not `api-key` or `API-KEY`)
2. Verify the key value from Render dashboard
3. No spaces or quotes around the key value

### Issue: 422 Validation Error
**Cause:** Invalid request body format
**Fix:**
1. Verify JSON is valid
2. Check all required fields are present
3. Ensure `timestamp` is a number (not string)

### Issue: 500 Internal Server Error
**Cause:** Server-side error (likely OpenAI API)
**Fix:**
1. Check Render logs
2. Verify OpenAI API key is set in Render
3. The service should still return a response (fail-open behavior)

---

## Postman Collection Variables

Set these as collection variables for easier testing:

| Variable | Value |
|----------|-------|
| `base_url` | `https://your-service-name.onrender.com` |
| `api_key` | `[YOUR_API_KEY_VALUE]` |

Then use `{{base_url}}` and `{{api_key}}` in your requests.

---

## What to Test

### Functional Tests
- [x] Health check works
- [x] Root endpoint works
- [x] Conversation endpoint requires authentication
- [x] Agent engages with scam messages
- [x] Multi-turn conversations maintain context
- [x] Different scam types are detected

### Security Tests
- [x] Requests without x-api-key header are rejected
- [x] Wrong API key is rejected
- [x] No sensitive info in responses

### Persona Tests
- [x] Responses sound natural (not bookish)
- [x] Responses are short (5-15 words typically)
- [x] Uses Indian English patterns
- [x] Shows appropriate concern/confusion

---

## Expected Behavior

**Agent Persona:** 64-year-old retired teacher (Veerabhadra), grandmother, trusting but cautious

**Response Style:**
- Short messages (5-15 words)
- Simple language
- Indian English: "What is this yaar?", "Tell me no"
- Shows worry: "Oh no", "I am scared"
- Asks simple questions: "Why?", "Who are you?"

**NOT like this:** "I would like to facilitate the verification process. Could you kindly provide further details?"

**Like this:** "What happened? Why you calling me? I am not understanding"

---

## Reporting Results

Please report:
1. Which tests passed/failed
2. Example responses from the agent
3. Any errors or unusual behavior
4. Response times
5. Whether persona sounds realistic

---

**Need the API Key?**
Ask me - it's in the Render dashboard under Environment variables (the value of `API_KEY`)
