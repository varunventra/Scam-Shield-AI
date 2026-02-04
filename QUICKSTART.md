# Quick Start Guide - 5 Minutes to Deploy

## Step 1: Configure Environment (2 minutes)

Copy the environment template:
```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```env
# REQUIRED - Set these two values:
API_KEY=my-secret-key-123
OPENAI_API_KEY=sk-proj-your-openai-key-here

# Optional - Keep defaults or customize:
OPENAI_MODEL=gpt-4o
PORT=8000
```

## Step 2: Choose Your Deployment Method

### Option A: Docker (Easiest) ⭐

```bash
# Start everything
docker-compose up -d

# View logs
docker-compose logs -f
```

Done! API is running at `http://localhost:8000`

### Option B: Local Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run server
python run.py
```

Done! API is running at `http://localhost:8000`

## Step 3: Test It (1 minute)

### Health Check
```bash
curl http://localhost:8000/health
```

### Test Scam Detection
```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: my-secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your bank account will be blocked. Click here to verify.",
      "timestamp": 1770005528731
    },
    "conversationHistory": []
  }'
```

You should get a response like:
```json
{
  "status": "success",
  "reply": "Why would my account be blocked? This seems suspicious."
}
```

## Step 4: API Documentation

Visit: `http://localhost:8000/docs` (only in debug mode)

## Common Issues

**Problem**: Port 8000 already in use
**Solution**: Change `PORT=8001` in `.env`

**Problem**: OpenAI API error
**Solution**: Verify your API key and billing status

**Problem**: "Module not found"
**Solution**: Run `pip install -r requirements.txt`

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Check [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
3. Submit your API endpoint to GUVI hackathon platform

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/health` | Health check |
| POST | `/api/v1/conversation` | Handle scam messages |
| POST | `/api/v1/admin/cleanup` | Cleanup sessions |
| GET | `/docs` | API documentation (debug mode) |

## Architecture Quick Reference

```
Your Request → API Authentication → Scam Detection → AI Agent → Intelligence Extraction → GUVI Callback
```

**That's it!** You're ready to detect and engage scammers with AI.

---

Need help? Check the logs:
- Docker: `docker-compose logs -f`
- Local: Check console output
