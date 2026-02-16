# ScamShield - Agentic Honeypot for Scam Detection & Intelligence Extraction

An AI-powered honeypot system that detects scam messages, autonomously engages scammers using dynamic personas, and extracts actionable intelligence (phone numbers, bank accounts, UPI IDs, phishing links, emails) in real time.

Built for the **India AI Impact Buildathon** hackathon.

---

## How It Works

```
Scammer Message ──> Scam Detection (Rules + ML + LLM) ──> Persona Selection
                                                              │
                    Intelligence Extraction <── AI Agent <─────┘
                           │                   (GPT-4o)
                           v
              MongoDB + PDF Forensic Report + Callback
```

1. **Scam Detection** - 3-tier hybrid system (rule engine + trained ML model + LLM fallback) classifies incoming messages with confidence scoring
2. **Persona Selection** - Picks one of 4 victim personas (grandmother, student, professional, shopkeeper) based on scam type and scammer cues
3. **Identity Mirroring** - Detects and locks the identity the scammer assumes (name, gender, age) to stay consistent
4. **Strategic Engagement** - AI agent uses a 3-phase extraction strategy to naturally elicit phone numbers, UPI IDs, bank accounts, and phishing links from the scammer
5. **Intelligence Extraction** - Regex + NLP pipeline extracts structured data from every message
6. **Multilingual Support** - Detects and mirrors English, Hindi, and Telugu automatically
7. **Forensic Reporting** - Auto-generates PDF reports stored in MongoDB GridFS
8. **Repeat Scammer Detection** - Cross-references extracted intelligence against previous sessions

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (Python 3.11+) |
| AI/LLM | OpenAI GPT-4o |
| ML Model | scikit-learn (TF-IDF + Logistic Regression, 100% test accuracy) |
| Database | MongoDB Atlas (async via Motor) |
| PDF Reports | fpdf2 (in-memory generation, GridFS storage) |
| Language Detection | Unicode script analysis + langdetect |
| Deployment | Render (free tier) |

---

## Project Structure

```
honeypot/
├── app/
│   ├── api/
│   │   └── routes.py              # API endpoints (conversation, admin, PDF download)
│   ├── core/
│   │   ├── config.py              # Environment config (Pydantic Settings)
│   │   ├── logging.py             # Structured logging
│   │   └── security.py            # API key authentication
│   ├── models/
│   │   ├── requests.py            # Request schemas (Message, ConversationRequest)
│   │   └── responses.py           # Response schemas (ExtractedIntelligence, FinalResultPayload)
│   ├── services/
│   │   ├── ai_agent.py            # GPT-4o conversation engine with persona prompts
│   │   ├── callback_handler.py    # Evaluation callback submission
│   │   ├── conversation_strategy.py # 3-phase extraction strategy engine
│   │   ├── forensic_reporter.py   # PDF forensic report generator
│   │   ├── intelligence_extractor.py # Regex + NLP intelligence extraction
│   │   ├── language_detector.py   # Hindi/Telugu/English detection
│   │   ├── ml_detector.py         # Trained ML scam classifier
│   │   ├── persona_manager.py     # 4 dynamic victim personas
│   │   └── scam_detector.py       # Hybrid detection orchestrator
│   ├── storage/
│   │   ├── mongodb.py             # MongoDB session persistence
│   │   ├── pdf_storage.py         # GridFS PDF storage
│   │   └── session_manager.py     # In-memory session state
│   └── main.py                    # FastAPI app entry point
├── ml/
│   ├── models/                    # Trained model artifacts (.pkl)
│   ├── train_model.py             # Model training script
│   └── train_model_optimized.py   # Optimized training with GridSearchCV
├── data/
│   ├── scam_dataset.csv           # Base training dataset
│   └── scam_dataset_enhanced.csv  # Augmented dataset (1600+ samples)
├── tests/                         # Test suite
├── demo_conversation.py           # Automated demo script (9-message scenario)
├── render.yaml                    # Render deployment config
├── requirements.txt               # Python dependencies
└── .env.example                   # Environment variable template
```

---

## Setup Instructions

### Prerequisites

- Python 3.11+
- OpenAI API key (with GPT-4o access)
- MongoDB Atlas cluster (free tier works)

### 1. Clone and Install

```bash
git clone https://github.com/varunventra/honeypot.git
cd honeypot
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your actual keys:

```env
API_KEY=your-api-key-here
OPENAI_API_KEY=sk-your-openai-key
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net/?retryWrites=true&w=majority
ADMIN_API_KEY=your-admin-key
```

### 3. Run Locally

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Deploy to Render

The repo includes `render.yaml` for one-click deployment:

1. Push to GitHub
2. Connect repo to Render
3. Set `API_KEY`, `OPENAI_API_KEY`, `MONGODB_URI` in Render environment
4. Deploy

---

## API Endpoint

### POST `/api/v1/conversation`

**Headers:**
```
Content-Type: application/json
x-api-key: your-api-key
```

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": {
    "sender": "scammer",
    "text": "URGENT: Your SBI account has been compromised. Share OTP immediately.",
    "timestamp": 1739600000000
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
  "reply": "oh no is my money safe? what number can i call you back on?"
}
```

The `timestamp` field accepts both epoch milliseconds (int) and ISO-8601 strings.

### GET `/api/v1/health`

Health check endpoint (no auth required).

---

## Approach

### Scam Detection

Three detection layers run in parallel and combine scores:

1. **Rule Engine** - 40+ keyword/pattern rules with weighted scoring for urgency, threats, credential requests, payment demands, and authority impersonation
2. **ML Classifier** - TF-IDF vectorizer + Logistic Regression trained on 1600+ labeled samples (scam/legitimate). Achieves 100% accuracy on test set with optimized hyperparameters
3. **LLM Analysis** - GPT-4o as final arbiter for ambiguous cases

Detection is **fail-open**: if all detectors fail, the honeypot still engages (it's a honeypot, not a filter).

### Intelligence Extraction

Extracts from every message using regex patterns:

| Data Type | Pattern |
|-----------|---------|
| Phone Numbers | Indian mobile (10-digit, +91 prefix variants) |
| Bank Accounts | 11-18 digit numbers |
| UPI IDs | `user@provider` format with known UPI providers |
| Phishing Links | HTTP/HTTPS URLs |
| Email Addresses | Standard email regex |
| Amounts | Rs./INR patterns |
| Employee IDs | Reference/ticket number patterns |

Phone numbers are stored in multiple formats (`+91-XXXXXXXXXX`, `+91XXXXXXXXXX`, `XXXXXXXXXX`) to maximize matching against evaluation criteria.

### Conversation Strategy

The AI agent uses a turn-aware 3-phase strategy optimized for 10-turn conversations:

- **Phase 1 (Turn 1):** Show fear + immediately ask a question ("oh god is my money safe? what number can i call you on?")
- **Phase 2 (Turns 2-4):** Active extraction - every response ends with a direct question for missing intelligence
- **Phase 3 (Turns 5+):** Deep extraction - persistent, compliance-based questioning

Authority-specific tactics adapt based on detected scam type (bank, police, job, lottery, delivery, phishing).

### Dynamic Personas

4 victim personas, each with distinct speech patterns:

| Persona | Profile | Speech Style |
|---------|---------|-------------|
| Grandmother | Elderly, lives alone, pension income | "beta help me", "my grandson helps with phone" |
| Student | College student, part-time job | "bro what is this", casual slang |
| Professional | Working adult, busy schedule | "I'm in a meeting", formal but trusting |
| Shopkeeper | Small business owner | "I have customers", practical concerns |

Persona selection is automatic based on scam type and scammer cues. Identity (name, gender, age) is mirrored from scammer assumptions and locked after 3 turns.

---

## Final Output Structure

After the conversation, the system submits a final output via callback:

```json
{
  "sessionId": "abc123",
  "status": "completed",
  "scamDetected": true,
  "totalMessagesExchanged": 10,
  "extractedIntelligence": {
    "phoneNumbers": ["+91-9876543210"],
    "bankAccounts": ["1234567890123456"],
    "upiIds": ["scammer.fraud@fakebank"],
    "phishingLinks": ["http://fake-site.com/verify"],
    "emailAddresses": ["scammer@fake.com"]
  },
  "engagementMetrics": {
    "totalMessagesExchanged": 10,
    "engagementDurationSeconds": 120
  },
  "agentNotes": "Successfully extracted: target bank account, normalized phone number, baited payment credentials. Tactics: urgency, threats. Impersonating: SBI."
}
```

---

## Testing

```bash
# Run unit tests
pytest tests/

# Run automated demo (9-message SBI impersonation scenario)
python demo_conversation.py --fast

# Test against live deployment
python demo_conversation.py --count 3
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `API_KEY` | Yes | - | API authentication key |
| `OPENAI_API_KEY` | Yes | - | OpenAI API key |
| `MONGODB_URI` | No | `""` | MongoDB connection string |
| `ADMIN_API_KEY` | No | `""` | Admin endpoint authentication |
| `OPENAI_MODEL` | No | `gpt-4o` | OpenAI model |
| `OPENAI_TEMPERATURE` | No | `0.7` | Response creativity |
| `SCAM_CONFIDENCE_THRESHOLD` | No | `0.7` | Detection threshold |
| `GUVI_CALLBACK_URL` | No | hackathon URL | Evaluation callback endpoint |
| `BASE_URL` | No | auto-detected | Base URL for PDF download links |

---

## License

Built for the India AI Impact Buildathon hackathon.
