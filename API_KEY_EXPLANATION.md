# API Key Architecture Explained

## The Confusion

You have an `API_KEY` in multiple places and `x-api-key` in the hackathon form. **They're the same value, just different contexts.**

---

## Simple Explanation

### Server Side (Your Render Service)
**Environment Variable Name:** `API_KEY`
**Location:** Render Dashboard → Environment tab
**Value:** The secret string (e.g., `NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY`)

**What it does:** Your FastAPI server reads this value and uses it to validate incoming requests.

### Client Side (Your Teammate, GUVI, Postman)
**HTTP Header Name:** `x-api-key`
**Location:** HTTP request headers
**Value:** The same secret string (e.g., `NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY`)

**What it does:** Clients include this header in their requests to prove they're authorized.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT (Postman/GUVI)                  │
│                                                             │
│  Sends HTTP Request with header:                           │
│  x-api-key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY   │
│                                                             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       │ POST /api/v1/conversation
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  SERVER (Render Service)                    │
│                                                             │
│  1. Receives request                                        │
│  2. Reads x-api-key header from request                    │
│  3. Compares with API_KEY environment variable             │
│  4. If match → Process request                             │
│     If no match → Return 401 Unauthorized                  │
│                                                             │
│  Environment Variable:                                      │
│  API_KEY=NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## The Same Value in Different Places

| Location | Context | Name | Purpose |
|----------|---------|------|---------|
| `.env` (local) | Local development | `API_KEY=...` | So your local server can validate requests |
| Render Environment Variables | Production server | `API_KEY=...` | So your deployed server can validate requests |
| HTTP Request Header | Client request | `x-api-key: ...` | How clients prove they're authorized |
| GUVI Submission Form | Hackathon testing | `x-api-key: ...` | How GUVI authenticates with your service |

**They all use THE SAME SECRET VALUE.**

---

## Example Flow

### 1. Setup (You've already done this)
```bash
# In Render Dashboard, you set:
API_KEY=NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY
```

### 2. Server Reads It (Automatic)
```python
# In app/core/config.py
class Settings(BaseSettings):
    api_key: str = Field(..., env="API_KEY")  # Reads from environment

settings = Settings()  # Now settings.api_key contains your secret
```

### 3. Server Validates Requests (Automatic)
```python
# In app/core/security.py (or similar)
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key
```

### 4. Client Sends Request (What your teammate/GUVI does)
```bash
curl -X POST https://your-service.onrender.com/api/v1/conversation \
  -H "x-api-key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY" \
  -H "Content-Type: application/json" \
  -d '{"sessionId": "test", "message": {...}}'
```

---

## What to Give to Whom

### Your Teammate (for Postman Testing)

Give them:
1. **Base URL:** `https://your-service-name.onrender.com`
2. **API Key Value:** The value from your Render `API_KEY` environment variable
3. **How to use it:** Add header `x-api-key: [THE VALUE]` to all requests
4. **Guide:** Share `POSTMAN_TESTING_GUIDE.md`

**Example:**
```
Hey [teammate],

For Postman testing, use these:

Base URL: https://scambot-honeypot-xyz123.onrender.com
API Key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY

Add this header to all requests:
x-api-key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY

See POSTMAN_TESTING_GUIDE.md for detailed instructions.
```

### GUVI (for Hackathon Submission)

Submit:
1. **x-api-key field:** Paste the value from your Render `API_KEY` environment variable
2. **Honeypot API Endpoint URL field:** `https://your-service-name.onrender.com/api/v1/conversation`

**Example Submission:**
```
x-api-key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY

Honeypot API Endpoint URL: https://scambot-honeypot-xyz123.onrender.com/api/v1/conversation
```

---

## Security Note

**⚠️ Keep the API key value secret!**

- ✅ Store in Render environment variables (encrypted)
- ✅ Store in local `.env` file (not committed to Git)
- ✅ Share only with authorized people (teammate, GUVI)
- ❌ Never commit to GitHub
- ❌ Never post publicly
- ❌ Never include in code

Your `.env` file should already be in `.gitignore` to prevent accidental commits.

---

## Quick Reference

**Server-side (what you set):**
- Environment variable name: `API_KEY`
- Location: Render Dashboard → Environment
- Value: Your secret string

**Client-side (what they send):**
- HTTP header name: `x-api-key`
- Location: Request headers
- Value: The same secret string

**They're the same value!** Just different contexts (environment variable vs. HTTP header).

---

## Verification

To verify everything is working:

### Test 1: Health Check (No Auth)
```bash
curl https://your-service.onrender.com/health
# Should return: {"status": "healthy", "active_sessions": 0}
```

### Test 2: Conversation (With Auth)
```bash
curl -X POST https://your-service.onrender.com/api/v1/conversation \
  -H "x-api-key: YOUR_API_KEY_VALUE" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test",
    "message": {
      "sender": "scammer",
      "text": "Your account is blocked",
      "timestamp": 1704067200000
    },
    "conversationHistory": []
  }'
# Should return: {"status": "success", "reply": "...", ...}
```

### Test 3: Wrong API Key (Should Fail)
```bash
curl -X POST https://your-service.onrender.com/api/v1/conversation \
  -H "x-api-key: wrong-key" \
  -H "Content-Type: application/json" \
  -d '{...}'
# Should return: 401 Unauthorized
```

---

## Summary

| Question | Answer |
|----------|--------|
| What is `API_KEY`? | Environment variable name on your server |
| What is `x-api-key`? | HTTP header name that clients use |
| Are they the same? | They contain the same secret value |
| Where do I get the value? | Render Dashboard → Environment → API_KEY |
| What do I give to teammate? | The API_KEY value (they put it in x-api-key header) |
| What do I give to GUVI? | The API_KEY value (in the x-api-key form field) |
| What URL for GUVI? | `https://[your-service].onrender.com/api/v1/conversation` |

---

**Still confused?** Think of it like this:
- You have a secret password stored in a safe (API_KEY environment variable)
- When someone wants to enter your house, they show the password at the door (x-api-key header)
- It's the same password, just different locations (safe vs. door)
