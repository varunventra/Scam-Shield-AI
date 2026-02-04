# Deployment Guide

## Quick Deployment Steps

### 1. Prerequisites

- OpenAI API key ([Get it here](https://platform.openai.com/api-keys))
- Docker and Docker Compose installed (or Python 3.11+)

### 2. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
# Required:
#   - API_KEY: Create a strong secret key for your API
#   - OPENAI_API_KEY: Your OpenAI API key
```

Example `.env`:
```env
API_KEY=my-super-secret-api-key-12345
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o
```

### 3. Deploy with Docker (Recommended)

```bash
# Build and start
docker-compose up -d

# Check logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health
```

### 4. Deploy Locally (Alternative)

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Testing Your Deployment

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "scambot-honeypot",
  "active_sessions": 0
}
```

### 2. Test Conversation

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-001",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

Expected response:
```json
{
  "status": "success",
  "reply": "Why is my account being blocked? This is very concerning."
}
```

## Cloud Deployment

### Deploy to Railway

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Add environment variables in Railway dashboard
5. Deploy: `railway up`

### Deploy to Render

1. Create new Web Service in Render dashboard
2. Connect your GitHub repository
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables
6. Deploy

### Deploy to AWS ECS

1. Build Docker image: `docker build -t scambot-honeypot .`
2. Tag image: `docker tag scambot-honeypot:latest your-registry/scambot-honeypot:latest`
3. Push to ECR: `docker push your-registry/scambot-honeypot:latest`
4. Create ECS task definition
5. Create ECS service
6. Configure load balancer

## Environment Variables for Production

```env
# Security
API_KEY=use-a-strong-random-key-here

# OpenAI
OPENAI_API_KEY=sk-proj-your-production-key
OPENAI_MODEL=gpt-4o

# Application
DEBUG=False
LOG_LEVEL=INFO
MAX_CONVERSATION_TURNS=20
SESSION_TIMEOUT=3600

# Agent Configuration
AGENT_NAME=Rahul
AGENT_AGE=28
AGENT_OCCUPATION=Software Engineer

# Scam Detection
SCAM_CONFIDENCE_THRESHOLD=0.7

# Callback
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

## Monitoring

### Check Application Logs

```bash
# Docker
docker-compose logs -f scambot-api

# Local
# Logs output to console
```

### Monitor Performance

- Watch OpenAI API usage in your OpenAI dashboard
- Monitor response times
- Check session counts via `/health` endpoint
- Review error logs

## Troubleshooting

### Port Already in Use

```bash
# Change port in .env
PORT=8001

# Or in docker-compose.yml
ports:
  - "8001:8000"
```

### OpenAI API Errors

- Verify API key is correct
- Check billing status
- Ensure model name is correct (gpt-4o, gpt-4-turbo, gpt-3.5-turbo)

### Out of Memory

- Increase Docker memory limit
- Reduce `MAX_CONVERSATION_TURNS`
- Implement session cleanup

## Production Checklist

- [ ] Set strong `API_KEY`
- [ ] Configure production OpenAI API key
- [ ] Set `DEBUG=False`
- [ ] Configure appropriate `LOG_LEVEL`
- [ ] Set up monitoring/alerting
- [ ] Configure HTTPS/SSL
- [ ] Set up backup for session data (if needed)
- [ ] Test callback to GUVI endpoint
- [ ] Load test the API
- [ ] Document your API endpoint for submission

## Submitting for Evaluation

Your API endpoint should be publicly accessible. Example:

```
https://your-domain.com/api/v1/conversation
```

Provide:
1. Base URL
2. API key for testing
3. Documentation (this README)

---

Good luck with the hackathon!
