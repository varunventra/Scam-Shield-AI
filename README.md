# Scambot Honeypot API

An enterprise-level AI-powered honeypot system that detects scam messages, autonomously engages scammers in human-like conversations, and extracts actionable intelligence.

## Features

- **Scam Detection**: AI-powered detection of various scam types (bank fraud, UPI fraud, phishing, fake offers)
- **Autonomous AI Agent**: Maintains believable human persona to engage scammers
- **Multi-turn Conversations**: Handles complex conversation flows
- **Intelligence Extraction**: Extracts bank accounts, UPI IDs, phone numbers, phishing links, and suspicious keywords
- **API-First Design**: RESTful API with authentication
- **Enterprise-Ready**: Structured codebase, logging, error handling, Docker support

## Architecture

```
scambot-honeypot/
├── app/
│   ├── api/              # API routes and endpoints
│   ├── core/             # Core configuration, logging, security
│   ├── models/           # Pydantic data models
│   ├── services/         # Business logic services
│   ├── storage/          # Session management
│   └── utils/            # Helper utilities
├── tests/                # Test suite
├── Dockerfile            # Docker configuration
├── docker-compose.yml    # Docker Compose setup
└── requirements.txt      # Python dependencies
```

## Prerequisites

- Python 3.11+
- OpenAI API key
- Docker (optional)

## Quick Start

### 1. Clone and Setup

```bash
cd hackathon-scambot
```

### 2. Create Environment File

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
API_KEY=your_secret_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run with Docker (Recommended)

```bash
docker-compose up --build
```

### 4. Run Locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API Usage

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
All requests require `x-api-key` header:

```bash
x-api-key: your_secret_api_key_here
```

### Endpoints

#### 1. Handle Conversation

**POST** `/api/v1/conversation`

Send a message to the honeypot system.

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked. Verify immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Why is my account being blocked? This is concerning."
}
```

#### 2. Health Check

**GET** `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "scambot-honeypot",
  "active_sessions": 5
}
```

#### 3. Cleanup Sessions (Admin)

**POST** `/api/v1/admin/cleanup`

Remove expired sessions.

**Response:**
```json
{
  "status": "success",
  "removed_sessions": 3,
  "active_sessions": 2
}
```

## Configuration

Key environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `API_KEY` | API authentication key | Required |
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `OPENAI_MODEL` | OpenAI model to use | `gpt-4o` |
| `SCAM_CONFIDENCE_THRESHOLD` | Minimum confidence to activate agent | `0.7` |
| `MAX_CONVERSATION_TURNS` | Maximum messages per conversation | `20` |
| `AGENT_NAME` | AI agent persona name | `Rahul` |
| `AGENT_AGE` | AI agent persona age | `28` |
| `AGENT_OCCUPATION` | AI agent persona occupation | `Software Engineer` |

## How It Works

1. **Message Reception**: Platform sends suspected scam message
2. **Scam Detection**: AI analyzes message for scam indicators
3. **Agent Activation**: If scam detected (confidence ≥ threshold), agent engages
4. **Conversation**: Agent maintains human-like persona to extract intelligence
5. **Intelligence Extraction**: System extracts bank accounts, UPI IDs, links, etc.
6. **Callback**: Final results sent to GUVI evaluation endpoint

## Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

## Example cURL Request

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-session-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked. Verify immediately.",
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

## Logging

Logs are written to stdout with structured format:

```
2024-02-04 10:30:15 - scambot_honeypot - INFO - Received message - Session: abc123
```

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## Security

- API key authentication on all endpoints
- No storage of real personal information
- Session timeout (default 1 hour)
- Input validation with Pydantic models
- Secure environment variable handling

## Production Deployment

### Docker Deployment

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Environment Variables in Production

1. Set strong `API_KEY`
2. Use production OpenAI API key
3. Set `DEBUG=False`
4. Configure `LOG_LEVEL=INFO` or `WARNING`
5. Adjust `MAX_CONVERSATION_TURNS` based on needs

## Monitoring

Monitor these metrics:

- Active sessions: `GET /health`
- Response times
- OpenAI API usage
- Error rates in logs

## Troubleshooting

### OpenAI API Errors

- Check API key is valid
- Verify API quota/billing
- Check model name is correct

### Sessions Not Persisting

- Sessions are in-memory (cleared on restart)
- Consider adding Redis for production

### High Response Times

- Check OpenAI API latency
- Reduce `MAX_TOKENS` if needed
- Consider caching strategies

## License

This project is created for the GUVI Hackathon challenge.

## Support

For issues or questions, check the logs first:

```bash
docker-compose logs -f scambot-api
```

---

Built with FastAPI, OpenAI, and enterprise best practices.
