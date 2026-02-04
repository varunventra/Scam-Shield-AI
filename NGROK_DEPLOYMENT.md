# Ngrok Deployment Guide for Hackathon

## Quick Start (3 Steps)

### Step 1: Install Dependencies

Open your terminal in the honeypot directory and run:

```bash
# Activate virtual environment (if you have one)
.venv\Scripts\activate

# Install dependencies including ngrok
pip install -r requirements.txt
```

### Step 2: Verify Configuration

Make sure your `.env` file has the required settings:

```env
API_KEY=NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY
OPENAI_API_KEY=your-openai-key-here
PORT=8000
HOST=0.0.0.0
DEBUG=True
```

✅ **Your current `.env` file is already configured!**

### Step 3: Run with Ngrok

```bash
python run_with_ngrok.py
```

That's it! The script will:
- Start the FastAPI server
- Create an ngrok tunnel
- Display your public URL
- Show you exactly what to submit for the hackathon

---

## What You'll See

When you run the script, you'll see output like this:

```
╔═══════════════════════════════════════════════════════════════╗
║                   SCAMBOT HONEYPOT API                        ║
║                   With Ngrok Tunnel                           ║
╚═══════════════════════════════════════════════════════════════╝

🚀 Starting FastAPI server...
📍 Local Host: 0.0.0.0
🔌 Local Port: 8000
🤖 Model: gpt-4o
🎯 Confidence Threshold: 0.7

⏳ Waiting for server to start...
🌐 Creating ngrok tunnel...

======================================================================
✅ NGROK TUNNEL CREATED SUCCESSFULLY!
======================================================================

🔗 Public URL: https://abc123def456.ngrok-free.app

======================================================================

📋 HACKATHON SUBMISSION DETAILS:
======================================================================

✨ Honeypot API Endpoint URL:
   https://abc123def456.ngrok-free.app/api/v1/conversation

🔑 API Key (x-api-key header):
   NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY

======================================================================
```

---

## Submit to Hackathon Platform

### What to Copy:

1. **Honeypot API Endpoint URL**: Copy the full URL shown (including `/api/v1/conversation`)
   ```
   https://YOUR-NGROK-URL.ngrok-free.app/api/v1/conversation
   ```

2. **API Key Header**:
   - Header Name: `x-api-key`
   - Header Value: `NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY`

### In the Hackathon Tester:

```
Honeypot API Endpoint URL: https://YOUR-NGROK-URL.ngrok-free.app/api/v1/conversation
Headers: x-api-key
x-api-key value: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY
```

Then click **"Test Honeypot Endpoint"**

---

## Testing Your Endpoint Locally (Optional)

You can test your endpoint before submitting using curl:

```bash
curl -X POST "https://YOUR-NGROK-URL.ngrok-free.app/api/v1/conversation" \
  -H "x-api-key: NqxYkMXOqB1lwnpMPc3lzKs0wuhTUgnOxl9asSEbeyY" \
  -H "Content-Type: application/json" \
  -d "{\"sessionId\":\"test-123\",\"message\":{\"sender\":\"scammer\",\"text\":\"Your bank account will be blocked. Verify now.\",\"timestamp\":1770005528731},\"conversationHistory\":[]}"
```

Expected response:
```json
{
  "status": "success",
  "reply": "Why would my account be blocked? Can you tell me more?"
}
```

---

## Important Notes

### ⚠️ Keep the Terminal Open
- The ngrok tunnel only works while the script is running
- Don't close the terminal window during testing
- If you close it, just run `python run_with_ngrok.py` again

### 🔄 If Ngrok Disconnects
Just restart the script:
```bash
python run_with_ngrok.py
```

You'll get a new URL - update it in the hackathon platform.

### 📊 Monitoring
You can see requests in:
1. Your terminal (shows logs)
2. Ngrok web interface: http://localhost:4040 (opens automatically)

### 🆓 Free Tier Limits
Ngrok free tier:
- ✅ HTTPS tunnels
- ✅ Unlimited requests (with rate limits)
- ⚠️ Tunnel expires after 2 hours (just restart)
- ⚠️ URL changes each time (update in platform)

### 🎯 Want a Fixed URL?
Create a free ngrok account and get a fixed domain:

1. Sign up at https://ngrok.com/
2. Get your auth token
3. Edit `run_with_ngrok.py` and uncomment line 42:
   ```python
   conf.get_default().auth_token = "YOUR_NGROK_AUTH_TOKEN"
   ```

---

## Troubleshooting

### Problem: "Port 8000 already in use"
**Solution**:
1. Change PORT in `.env` to 8001
2. Or stop the other service using port 8000

### Problem: "ModuleNotFoundError: No module named 'pyngrok'"
**Solution**:
```bash
pip install pyngrok
```

### Problem: "OpenAI API error"
**Solution**:
- Verify your OPENAI_API_KEY in `.env` is correct
- Check you have OpenAI credits

### Problem: "Ngrok tunnel failed"
**Solution**:
1. Check your internet connection
2. Make sure no VPN is blocking ngrok
3. Try restarting the script

### Problem: Hackathon tester can't reach endpoint
**Solution**:
1. Make sure the script is running
2. Copy the EXACT URL from terminal (with `/api/v1/conversation`)
3. Verify the API key is correct
4. Check if ngrok tunnel is still active

---

## API Endpoints

Your honeypot exposes these endpoints:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/conversation` | Main honeypot endpoint | Yes |
| GET | `/health` | Health check | No |
| GET | `/` | Root endpoint | No |
| GET | `/docs` | API documentation | No (debug mode only) |

---

## How It Works

1. **Request Received**: Platform sends a message to your endpoint
2. **Authentication**: Your API validates the `x-api-key` header
3. **Scam Detection**: OpenAI analyzes if message is a scam
4. **Agent Activation**: If scam detected (confidence > 0.7), AI agent engages
5. **Response**: Agent generates human-like response
6. **Intelligence Extraction**: After sufficient engagement, extracts:
   - Bank accounts
   - UPI IDs
   - Phone numbers
   - Phishing links
   - Suspicious keywords
7. **Callback**: Sends final results to GUVI evaluation endpoint

---

## Architecture

```
Hackathon Platform
      ↓
   Ngrok Tunnel (Public HTTPS)
      ↓
   Your FastAPI Server (Localhost:8000)
      ↓
   ├─ API Key Validation
   ├─ Scam Detection (OpenAI)
   ├─ AI Agent (OpenAI)
   ├─ Intelligence Extraction
   └─ GUVI Callback
```

---

## Next Steps

1. ✅ Run `python run_with_ngrok.py`
2. ✅ Copy the public URL
3. ✅ Submit to hackathon platform
4. ✅ Test with the platform's tester
5. ✅ Monitor logs in your terminal

---

## Support

- **Ngrok Docs**: https://ngrok.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **OpenAI Docs**: https://platform.openai.com/docs

---

**Good luck with your hackathon! 🚀**
