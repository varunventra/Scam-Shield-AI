# Scambot Honeypot - Complete Project Context

> **Purpose**: Full source code and documentation dump for new chat context.
> **Project**: AI-powered honeypot for the GUVI/India AI Impact Buildathon Grand Finale.
> **Stack**: FastAPI + OpenAI GPT-4o + MongoDB Atlas + scikit-learn ML + Render deployment.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture & File Tree](#2-architecture--file-tree)
3. [Config Files](#3-config-files)
4. [App Core](#4-app-core)
5. [App Models](#5-app-models)
6. [App Services](#6-app-services)
7. [App Storage](#7-app-storage)
8. [App Utils](#8-app-utils)
9. [API Routes](#9-api-routes)
10. [ML Pipeline](#10-ml-pipeline)
11. [Tests](#11-tests)
12. [Demo Script](#12-demo-script)
13. [Problem Statement](#13-problem-statement)
14. [Current State & Known Gaps](#14-current-state--known-gaps)

---

## 1. Project Overview

An AI-powered honeypot system that:
- **Detects scam messages** via a 3-tier hybrid pipeline: Rule-based keywords → ML (TF-IDF + Logistic Regression) → OpenAI fallback
- **Engages scammers autonomously** using OpenAI GPT-4o with dynamic personas (grandmother, professional, student, business_owner)
- **Extracts intelligence**: bank accounts, UPI IDs, phone numbers, phishing links, emails, amounts, employee IDs
- **Supports multilingual**: English, Hindi (Devanagari + transliterated), Telugu (Telugu script + transliterated)
- **Persists to MongoDB Atlas** with repeat scammer detection, risk levels, and full conversation transcripts
- **Generates forensic PDF reports** for law enforcement
- **Sends GUVI callback** after 18+ messages with extracted intelligence
- **Fail-open at every level** — this is a honeypot, so always engage

**Response format (GUVI requirement)**:
```json
{"status": "success", "reply": "..."}
```

**Deployed on**: Render (free tier, Oregon) at `https://scambot-honeypot.onrender.com/`

---

## 2. Architecture & File Tree

```
honeypot/
├── .env                              # Environment variables (API keys, DB URI, agent config)
├── .gitignore                        # Standard Python gitignore + .claude/
├── pyproject.toml                    # hackathon-scambot, Python >=3.11
├── requirements.txt                  # All dependencies
├── render.yaml                       # Render deployment config
├── README.md                         # Project documentation
├── ML_IMPLEMENTATION_OVERVIEW.md     # ML hybrid detection documentation
├── AI for Fraud Detection...txt      # GUVI problem statement
├── demo_for_ppt.py                   # Live demo script for PPT screenshots
│
├── app/
│   ├── __init__.py                   # Version 1.0.0
│   ├── main.py                       # FastAPI app + lifespan (ML model loading)
│   │
│   ├── api/
│   │   ├── __init__.py               # Exports router
│   │   └── routes.py                 # Main conversation endpoint + admin endpoints
│   │
│   ├── core/
│   │   ├── __init__.py               # Exports settings, logger, verify_api_key
│   │   ├── config.py                 # Settings (pydantic-settings) + validate_configuration()
│   │   ├── logging.py                # Logger setup (scambot_honeypot)
│   │   └── security.py              # verify_api_key, verify_admin_key
│   │
│   ├── models/
│   │   ├── __init__.py               # Exports all models
│   │   ├── requests.py               # Message, Metadata, ConversationRequest
│   │   └── responses.py              # ConversationResponse, ExtractedIntelligence, FinalResultPayload
│   │
│   ├── services/
│   │   ├── __init__.py               # Exports all services + ml_detector
│   │   ├── ai_agent.py               # AIAgent with system prompt, adaptive repeat scammer handling
│   │   ├── callback_handler.py       # GUVI callback after 18+ messages
│   │   ├── forensic_reporter.py      # PDF report generation (fpdf2)
│   │   ├── intelligence_extractor.py # Regex extraction of all intelligence
│   │   ├── language_detector.py      # Script detection + transliteration + langdetect
│   │   ├── ml_detector.py            # Singleton ML model loader + predict_scam_probability()
│   │   ├── persona_manager.py        # 4 personas, scam type classification, persona selection
│   │   └── scam_detector.py          # Hybrid 3-tier detection pipeline
│   │
│   ├── storage/
│   │   ├── __init__.py               # Exports SessionManager, SessionData, session_manager
│   │   ├── session_manager.py        # In-memory session management with hybrid detection fields
│   │   └── mongodb.py                # MongoDB Atlas async storage, repeat detection, risk levels
│   │
│   └── utils/
│       ├── __init__.py               # Exports helpers
│       └── helpers.py                # format_conversation, sanitize_intelligence, validate_session_id
│
├── ml/
│   ├── __init__.py                   # Package init
│   ├── train_model.py                # TF-IDF + LogisticRegression training pipeline
│   ├── test_model.py                 # 25-case test suite with accuracy tracking
│   └── models/
│       ├── scam_model.pkl            # Trained Logistic Regression model
│       └── vectorizer.pkl            # Trained TF-IDF vectorizer
│
├── data/
│   └── scam_dataset.csv              # Training data (~2200 rows, text + label columns)
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py                   # 25 API tests (auth, detection, multi-turn, format, edge cases)
│   ├── test_all_scenarios.py         # 13 scenario tests (all scam types + multi-turn)
│   ├── test_forensic_reporter.py     # PDF generation tests (standalone, no server needed)
│   ├── test_intelligence_extraction.py # Intelligence extraction tests
│   ├── test_persona_validation.py    # Persona realism tests
│   └── test_remote_api.py           # Remote Render deployment tests
│
└── forensics/                        # Generated forensic PDF reports (gitignored)
```

---

## 3. Config Files

### `.env`
```env
# API Configuration
API_KEY=J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM
PORT=8000
HOST=0.0.0.0

# OpenAI Configuration - REPLACE WITH YOUR KEY
OPENAI_API_KEY=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
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
MAX_TOKENS=1000

# GUVI Callback
GUVI_CALLBACK_URL=https://hackathon.guvi.in/api/updateHoneyPotFinalResult

# Application Settings
DEBUG=True
LOG_LEVEL=INFO
MAX_CONVERSATION_TURNS=20
SESSION_TIMEOUT=3600

# Scam Detection
SCAM_CONFIDENCE_THRESHOLD=0.7

# Agent Persona
AGENT_NAME=Veerabadhra
AGENT_AGE=64
AGENT_OCCUPATION=Retired preschool teacher (Grandparent)(She's very naive)(Very likely to fall for a scammers ploy)(She texts realistically like how normal people do and not bookishly)

# Render URL
RENDER_URL=https://scambot-honeypot.onrender.com/

#db
MONGODB_URI=mongodb+srv://forensic_admin:honeypot123@cluster0.xj5ems4.mongodb.net/?appName=Cluster0
ADMIN_API_KEY=honeypot123
```

### `requirements.txt`
```
# Core Framework
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0

# OpenAI
openai==1.12.0

# HTTP Client
httpx==0.26.0

# Environment Variables
python-dotenv==1.0.0

# MongoDB (async driver)
motor==3.3.2
pymongo==4.6.1

# PDF Report Generation
fpdf2==2.8.5

# Language Detection
langdetect==1.0.9

# ML Scam Detection
scikit-learn>=1.3.0
joblib>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
```

### `pyproject.toml`
```toml
[project]
name = "hackathon-scambot"
version = "0.1.0"
description = "Add your description here"
readme = "README.md"
requires-python = ">=3.11"
dependencies = []
```

### `render.yaml`
```yaml
services:
  - type: web
    name: scambot-honeypot
    env: python
    region: oregon
    plan: free
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /health
    envVars:
      - key: API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: OPENAI_MODEL
        value: gpt-4o
      - key: OPENAI_TEMPERATURE
        value: 0.7
      - key: MAX_TOKENS
        value: 1000
      - key: GUVI_CALLBACK_URL
        value: https://hackathon.guvi.in/api/updateHoneyPotFinalResult
      - key: DEBUG
        value: false
      - key: LOG_LEVEL
        value: INFO
      - key: MAX_CONVERSATION_TURNS
        value: 20
      - key: SESSION_TIMEOUT
        value: 3600
      - key: SCAM_CONFIDENCE_THRESHOLD
        value: 0.7
      - key: AGENT_NAME
        value: Rahul
      - key: AGENT_AGE
        value: 28
      - key: AGENT_OCCUPATION
        value: Software Engineer
      - key: HOST
        value: 0.0.0.0
      - key: PORT
        fromService:
          type: web
          name: scambot-honeypot
          property: port
```

### `.gitignore`
```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Environment variables
.env
.env.local

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3

# OS
.DS_Store
Thumbs.db

# Testing
.pytest_cache/
.coverage
htmlcov/

# Docker
.dockerignore

.claude/
```

---

## 4. App Core

### `app/__init__.py`
```python
"""Scambot Honeypot Application."""
__version__ = "1.0.0"
```

### `app/main.py`
```python
"""
Main FastAPI application for Scambot Honeypot.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import logger
from app.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup - Validate configuration
    from app.core.config import validate_configuration

    logger.info("="*70)
    logger.info("🚀 Starting Scambot Honeypot API")
    logger.info("="*70)

    # Validate configuration (will exit if critical errors)
    validate_configuration()

    # Load ML scam detection model (optional — app runs fine without it)
    try:
        from app.services.ml_detector import load_model
        loaded = load_model()
        if loaded:
            logger.info("ML scam detection model loaded successfully")
        else:
            logger.warning("ML model not loaded — hybrid detection will use rules only")
    except Exception as ml_exc:
        logger.warning(f"ML model loading failed (non-blocking): {ml_exc}")

    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"OpenAI model: {settings.openai_model}")
    logger.info("🎯 Honeypot is LIVE and ready to engage!")
    logger.info("="*70)

    yield

    # Shutdown
    logger.info("="*70)
    logger.info("👋 Shutting down Scambot Honeypot API")
    logger.info("="*70)


# Create FastAPI application
app = FastAPI(
    title="Scambot Honeypot API",
    description="AI-powered honeypot system for scam detection and intelligence extraction",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1", tags=["conversation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Scambot Honeypot API",
        "version": "1.0.0",
        "status": "running"
    }
@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
async def health_check():
    """
    Health check endpoint.
    Must be publicly accessible without authentication.
    """
    return {
        "status": "healthy",
        "active_sessions": 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
```

### `app/core/__init__.py`
```python
"""Core application components."""
from app.core.config import settings
from app.core.logging import logger
from app.core.security import verify_api_key

__all__ = ["settings", "logger", "verify_api_key"]
```

### `app/core/config.py`
```python
"""
Core configuration module for the Scambot Honeypot system.
"""
import sys
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_key: str = Field(..., env="API_KEY")
    port: int = Field(default=8000, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    max_tokens: int = Field(default=1000, env="MAX_TOKENS")

    # MongoDB Configuration
    mongodb_uri: str = Field(default="", env="MONGODB_URI")

    # Admin API Key
    admin_api_key: str = Field(default="", env="ADMIN_API_KEY")

    # GUVI Callback
    guvi_callback_url: str = Field(
        default="https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
        env="GUVI_CALLBACK_URL"
    )

    # Application Settings
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_conversation_turns: int = Field(default=20, env="MAX_CONVERSATION_TURNS")
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")

    # Scam Detection
    scam_confidence_threshold: float = Field(default=0.7, env="SCAM_CONFIDENCE_THRESHOLD")

    # Agent Persona
    agent_name: str = Field(default="Rahul", env="AGENT_NAME")
    agent_age: int = Field(default=28, env="AGENT_AGE")
    agent_occupation: str = Field(default="Software Engineer", env="AGENT_OCCUPATION")

    @field_validator("openai_api_key")
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format."""
        if not v or len(v) < 20:
            raise ValueError("OpenAI API key appears invalid (too short or empty)")
        if not v.startswith("sk-"):
            print(f"⚠️  WARNING: OpenAI API key doesn't start with 'sk-' - this may be incorrect!")
        return v

    @field_validator("api_key")
    def validate_api_key(cls, v):
        """Validate API key is set."""
        if not v or len(v) < 8:
            raise ValueError("API_KEY must be at least 8 characters long")
        return v

    @field_validator("openai_model")
    def validate_model(cls, v):
        """Validate OpenAI model name."""
        valid_models = ["gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        if v not in valid_models:
            print(f"⚠️  WARNING: Model '{v}' not in common list: {valid_models}")
            print(f"   Make sure your API key has access to this model!")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


def validate_configuration():
    """
    Validate configuration and test OpenAI connection at startup.
    FAIL-FAST: If configuration is wrong, crash immediately.
    """
    try:
        from openai import OpenAI
        import logging

        logger = logging.getLogger("scambot_honeypot")

        print("\n" + "="*70)
        print("🔧 CONFIGURATION VALIDATION")
        print("="*70)

        print(f"✅ API Key: {'*' * 20}{settings.api_key[-4:]}")
        print(f"✅ OpenAI Model: {settings.openai_model}")
        print(f"✅ OpenAI Key: sk-...{settings.openai_api_key[-4:]}")
        print(f"✅ Host: {settings.host}")
        print(f"✅ Port: {settings.port}")
        print(f"✅ Debug: {settings.debug}")
        print(f"✅ Scam Threshold: {settings.scam_confidence_threshold}")

        # Test OpenAI connection
        print("\n🔄 Testing OpenAI API connection...")
        try:
            client = OpenAI(api_key=settings.openai_api_key)
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )
            print(f"✅ OpenAI API connection successful!")
            print(f"✅ Model '{settings.openai_model}' is accessible")
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            print(f"\n❌ OPENAI API TEST FAILED!")
            print(f"   Error Type: {error_type}")
            print(f"   Error Message: {error_msg}")

            if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                print(f"\n🚨 CRITICAL: Invalid OpenAI API key!")
                sys.exit(1)
            elif "model" in error_msg.lower() or "not found" in error_msg.lower():
                print(f"\n🚨 CRITICAL: Model '{settings.openai_model}' not accessible!")
                sys.exit(1)
            elif "rate_limit" in error_msg.lower():
                print(f"\n⚠️  WARNING: Rate limit error (but API key is valid)")
            else:
                print(f"\n⚠️  WARNING: OpenAI test failed but will continue")

        print("="*70)
        print("✅ Configuration validation complete!\n")

    except Exception as e:
        print(f"\n❌ FATAL: Configuration validation failed!")
        print(f"   Error: {str(e)}")
        sys.exit(1)


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"\n❌ FATAL: Failed to load configuration!")
    print(f"   Error: {str(e)}")
    sys.exit(1)
```

### `app/core/logging.py`
```python
"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    level = log_level or settings.log_level
    logger = logging.getLogger("scambot_honeypot")
    logger.setLevel(getattr(logging, level.upper()))
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger


# Global logger instance
logger = setup_logging()
```

### `app/core/security.py`
```python
"""
Security utilities including API key validation.
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings
from app.core.logging import logger

api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
admin_key_header = APIKeyHeader(name="x-admin-key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    if not api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
    if api_key != settings.api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return api_key


async def verify_admin_key(admin_key: str = Security(admin_key_header)) -> str:
    if not admin_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing admin API key")
    if not settings.admin_api_key or admin_key != settings.admin_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin API key")
    return admin_key
```

---

## 5. App Models

### `app/models/__init__.py`
```python
"""Data models for requests and responses."""
from app.models.requests import ConversationRequest, Message, Metadata
from app.models.responses import (
    ConversationResponse, ExtractedIntelligence, FinalResultPayload
)

__all__ = [
    "ConversationRequest", "Message", "Metadata",
    "ConversationResponse", "ExtractedIntelligence", "FinalResultPayload"
]
```

### `app/models/requests.py`
```python
"""
Request models for the Scambot Honeypot API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: int = Field(..., description="Epoch time in milliseconds")


class Metadata(BaseModel):
    channel: Optional[str] = Field(None, description="Communication channel (SMS/WhatsApp/Email/Chat)")
    language: Optional[str] = Field(None, description="Language used in conversation")
    locale: Optional[str] = Field(None, description="Country or region code")


class ConversationRequest(BaseModel):
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Latest incoming message")
    conversationHistory: List[Message] = Field(default_factory=list)
    metadata: Optional[Metadata] = Field(None)
```

### `app/models/responses.py`
```python
"""
Response models for the Scambot Honeypot API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):
    status: str = Field(..., description="Response status (success/error)")
    reply: str = Field(..., description="Agent's response to the scammer")


class ExtractedIntelligence(BaseModel):
    """
    GUVI REQUIREMENTS: Only these 5 fields are required for evaluation.
    Extra fields are excluded from serialization to GUVI callback.
    """
    # === REQUIRED FIELDS FOR GUVI (these 5 ONLY) ===
    bankAccounts: List[str] = Field(default_factory=list)
    upiIds: List[str] = Field(default_factory=list)
    phishingLinks: List[str] = Field(default_factory=list)
    phoneNumbers: List[str] = Field(default_factory=list)
    suspiciousKeywords: List[str] = Field(default_factory=list)

    # === INTERNAL FIELDS (excluded from GUVI callback) ===
    emails: List[str] = Field(default_factory=list, exclude=True)
    amounts: List[str] = Field(default_factory=list, exclude=True)
    employeeIds: List[str] = Field(default_factory=list, exclude=True)
    impersonationTargets: List[str] = Field(default_factory=list, exclude=True)


class FinalResultPayload(BaseModel):
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str
```

---

## 6. App Services

### `app/services/__init__.py`
```python
"""Service layer modules."""
from app.services.scam_detector import ScamDetector, ScamType, DetectionResult
from app.services.ai_agent import AIAgent
from app.services.intelligence_extractor import IntelligenceExtractor
from app.services.callback_handler import CallbackHandler
from app.services.forensic_reporter import ForensicReporter
from app.services.language_detector import detect_language, detect_response_language
from app.services.persona_manager import select_persona, get_persona_prompt
from app.services import ml_detector

__all__ = [
    "ScamDetector", "ScamType", "DetectionResult",
    "AIAgent", "IntelligenceExtractor", "CallbackHandler", "ForensicReporter",
    "detect_language", "detect_response_language",
    "select_persona", "get_persona_prompt", "ml_detector",
]
```

### `app/services/scam_detector.py`
*(Full hybrid 3-tier detection — 492 lines)*

Key components:
- `ScamType` enum: OTP_FRAUD, UPI_FRAUD, PHISHING, BANK_IMPERSONATION, JOB_SCAM, INVESTMENT_SCAM, LOTTERY_SCAM, DELIVERY_SCAM, UNKNOWN
- `DetectionResult` dataclass: is_scam, final_confidence, reasoning, rule_score, ml_score, scam_type, detected_indicators, detection_method
- `_CATEGORY_KEYWORDS`: dict mapping ScamType to keyword sets (English + Hindi Devanagari + Telugu script)
- `ScamDetector` class:
  - `SCAM_KEYWORDS`: 146 keywords across English, Hindi (transliterated + Devanagari), Telugu (transliterated + script)
  - `_rule_based_detection()`: returns (is_scam, confidence, reasoning, indicators, scam_type)
  - `_classify_scam_type()`: category counts from matched keywords
  - `_openai_detection()`: OpenAI JSON response for scam classification
  - `detect_scam_hybrid()`: 3-tier pipeline (rule >= 0.75 → SCAM; else ML >= 0.65 → SCAM; ML unavailable → rules alone)
  - `detect_scam()`: legacy OpenAI-based detection with rule fallback
  - `should_activate_agent()`: returns `Tuple[bool, DetectionResult]` with FAIL-OPEN behavior

```python
"""
Scam detection service with hybrid detection:
  Rule-based → ML model → OpenAI fallback.
"""
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Tuple

from openai import OpenAI

from app.core.config import settings
from app.core.logging import logger
from app.models.requests import ConversationRequest
from app.services.ml_detector import predict_scam_probability, is_model_loaded


# ---------------------------------------------------------------------------
# ScamType enum
# ---------------------------------------------------------------------------

class ScamType(str, Enum):
    OTP_FRAUD = "OTP_FRAUD"
    UPI_FRAUD = "UPI_FRAUD"
    PHISHING = "PHISHING"
    BANK_IMPERSONATION = "BANK_IMPERSONATION"
    JOB_SCAM = "JOB_SCAM"
    INVESTMENT_SCAM = "INVESTMENT_SCAM"
    LOTTERY_SCAM = "LOTTERY_SCAM"
    DELIVERY_SCAM = "DELIVERY_SCAM"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------------------------
# DetectionResult dataclass
# ---------------------------------------------------------------------------

@dataclass
class DetectionResult:
    is_scam: bool = False
    final_confidence: float = 0.0
    reasoning: str = ""
    rule_score: float = 0.0
    ml_score: Optional[float] = None
    scam_type: str = "UNKNOWN"
    detected_indicators: List[str] = field(default_factory=list)
    detection_method: str = "none"  # "rule_based", "ml", "hybrid", "openai", "fail_open"


# ---------------------------------------------------------------------------
# Keyword category sets for ScamType classification
# ---------------------------------------------------------------------------

_CATEGORY_KEYWORDS = {
    ScamType.OTP_FRAUD: {
        "otp", "pin", "password", "cvv",
        "ओटीपी", "पासवर्ड", "पिन", "आधार",
        "ఓటీపీ", "పాస్‌వర్డ్", "పిన్", "ఆధార్",
    },
    ScamType.UPI_FRAUD: {
        "upi", "paytm", "phonepe", "gpay", "transfer",
        "भेजो", "ट्रांसफर", "जमा",
        "పంపండి", "చెల్లింపులు", "ట్రాన్స్‌ఫర్",
    },
    ScamType.PHISHING: {
        "click here", "link", "http", "https", "bit.ly",
    },
    ScamType.BANK_IMPERSONATION: {
        "bank", "account", "kyc", "debit", "credit", "sbi", "rbi",
        "बैंक", "खाता", "खाता बंद", "सस्पेंड", "केवाईसी",
        "బ్యాంక్", "ఖాతా", "ఖాతా బంద్", "కేవైసీ",
    },
    ScamType.JOB_SCAM: {
        "job", "salary", "hiring", "work from home", "vacancy",
    },
    ScamType.INVESTMENT_SCAM: {
        "invest", "trading", "profit", "returns", "stock", "crypto",
    },
    ScamType.LOTTERY_SCAM: {
        "won", "lottery", "prize", "reward", "cashback",
        "इनाम", "लॉटरी", "जीत",
        "బహుమతి", "లాటరీ", "గెలవడం",
    },
    ScamType.DELIVERY_SCAM: {
        "delivery", "package", "shipment", "courier", "tracking",
    },
}


class ScamDetector:
    """Detects scam intent using a 3-tier hybrid pipeline."""

    # Full scam keywords list (English + Hindi + Telugu) — 146 keywords
    SCAM_KEYWORDS = [
        # Urgency (English)
        "urgent", "immediately", "now", "today", "suspended", "blocked", "expire",
        # Verification/Authentication
        "verify", "confirm", "authenticate", "validate", "update", "kYC", "kyc",
        # Account/Banking
        "account", "bank", "upi", "paytm", "phonepe", "gpay", "debit", "credit",
        # Threats
        "legal action", "police", "arrest", "fine", "penalty", "court",
        # Requests for sensitive info
        "otp", "pin", "password", "cvv", "card", "aadhaar", "aadhar", "pan",
        # Common scam phrases
        "won", "lottery", "prize", "reward", "refund", "cashback",
        "click here", "link", "http", "https", "bit.ly",
        # Impersonation
        "customer care", "customer support", "helpline", "helpdesk",
        # Hindi / Hinglish (transliterated)
        "turant", "abhi", "fauran", "jaldi",
        "khata", "paisa", "rupaye", "rashi",
        "band", "block", "suspend",
        "kanooni karwai", "police", "giraftar",
        "jama", "bhejo", "transfer",
        "sathyapan", "jaanch",
        "inam", "lottery", "jeet",
        # Hindi (Devanagari script)
        "तुरंत", "अभी", "फौरन", "जल्दी",
        "खाता", "पैसा", "रुपये", "राशि",
        "बंद", "ब्लॉक", "निलंबित",
        "कानूनी कार्रवाई", "पुलिस", "गिरफ्तार",
        "भेजो", "ट्रांसफर", "जमा",
        "सत्यापन", "जाँच", "केवाईसी",
        "इनाम", "लॉटरी", "जीत",
        "ओटीपी", "पासवर्ड", "पिन", "आधार",
        "बैंक", "खाता बंद", "सस्पेंड",
        # Telugu (transliterated)
        "urgentuga", "ventane", "ippudu",
        "khata", "dabbu", "mottam",
        "nilipi", "block",
        "chattapara charya", "arrest",
        "pampandi", "chellimpulu",
        "dhruvikarana",
        "bahumathi", "lottery", "gelavadam",
        # Telugu (Telugu script)
        "తురంతుగా", "వెంటనే", "ఇప్పుడు",
        "ఖాతా", "డబ్బు", "మొత్తం", "రూపాయలు",
        "నిలిపి", "బ్లాక్", "సస్పెండ్",
        "చట్టపర చర్య", "పోలీసు", "అరెస్ట్",
        "పంపండి", "చెల్లింపులు", "ట్రాన్స్‌ఫర్",
        "ధృవీకరణ", "కేవైసీ",
        "బహుమతి", "లాటరీ", "గెలవడం",
        "ఓటీపీ", "పాస్‌వర్డ్", "పిన్", "ఆధార్",
        "బ్యాంక్", "ఖాతా బంద్",
    ]

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def _rule_based_detection(self, message_text: str) -> Tuple[bool, float, str, List[str], str]:
        message_lower = message_text.lower()
        matches = [kw for kw in self.SCAM_KEYWORDS if kw.lower() in message_lower]
        match_count = len(matches)
        scam_type = self._classify_scam_type(matches)

        if match_count >= 3:
            return True, 0.9, f"Rule-based: High match ({match_count} keywords)", matches, scam_type
        elif match_count >= 2:
            return True, 0.75, f"Rule-based: Medium match ({match_count} keywords)", matches, scam_type
        elif match_count >= 1:
            return True, 0.6, f"Rule-based: Low match (1 keyword: {matches[0]})", matches, scam_type
        else:
            return False, 0.3, "Rule-based: No scam keywords detected", matches, scam_type

    def _classify_scam_type(self, matched_keywords: List[str]) -> str:
        if not matched_keywords:
            return ScamType.UNKNOWN.value
        category_counts = {}
        matched_lower = {kw.lower() for kw in matched_keywords}
        for scam_type, keywords in _CATEGORY_KEYWORDS.items():
            count = len(matched_lower & {kw.lower() for kw in keywords})
            if count > 0:
                category_counts[scam_type] = count
        if not category_counts:
            return ScamType.UNKNOWN.value
        best = max(category_counts, key=category_counts.get)
        return best.value

    async def detect_scam_hybrid(self, request: ConversationRequest) -> DetectionResult:
        """
        Hybrid 3-tier: rule_score >= 0.75 → SCAM (skip ML);
        else ML >= 0.65 → SCAM; ML unavailable → rules alone.
        """
        dr = DetectionResult()

        # Tier 1: Rule-based
        try:
            is_scam_rule, rule_score, reasoning, indicators, scam_type = \
                self._rule_based_detection(request.message.text)
            dr.rule_score = rule_score
            dr.detected_indicators = indicators
            dr.scam_type = scam_type
        except Exception:
            is_scam_rule, rule_score, reasoning = False, 0.0, "Rule-based detection failed"
            indicators, scam_type = [], ScamType.UNKNOWN.value

        if rule_score >= 0.75:
            dr.is_scam = True
            dr.final_confidence = rule_score
            dr.reasoning = reasoning
            dr.detection_method = "rule_based"
            return dr

        # Tier 2: ML model
        ml_score = predict_scam_probability(request.message.text)
        dr.ml_score = ml_score

        if ml_score is not None:
            if ml_score >= 0.65:
                dr.is_scam = True
                dr.final_confidence = max(rule_score, ml_score)
                dr.reasoning = f"ML: score={ml_score:.4f} >= 0.65. Rule={rule_score:.2f}"
                dr.detection_method = "ml" if rule_score < 0.6 else "hybrid"
                return dr
            else:
                dr.is_scam = is_scam_rule and rule_score >= 0.6
                dr.final_confidence = max(rule_score, ml_score)
                dr.reasoning = f"ML: score={ml_score:.4f} < 0.65. Rule={rule_score:.2f}"
                dr.detection_method = "hybrid"
                return dr

        # ML unavailable
        dr.is_scam = is_scam_rule
        dr.final_confidence = rule_score
        dr.reasoning = f"{reasoning} (ML unavailable)"
        dr.detection_method = "rule_based"
        return dr

    async def should_activate_agent(self, request: ConversationRequest) -> Tuple[bool, DetectionResult]:
        """FAIL-OPEN: If in doubt, engage! This is a honeypot."""
        try:
            dr = await self.detect_scam_hybrid(request)
            should_activate = (dr.is_scam and dr.final_confidence >= 0.5)
            return should_activate, dr
        except Exception as exc:
            fail_dr = DetectionResult(
                is_scam=True, final_confidence=0.5,
                reasoning=f"Pipeline failed: {type(exc).__name__}. FAIL-OPEN.",
                detection_method="fail_open",
            )
            return True, fail_dr

    # Legacy OpenAI detection kept as _openai_detection() and detect_scam() — see full file
```

### `app/services/ml_detector.py`
```python
"""
ML-based scam detection using a pre-trained scikit-learn model.
Module-level singleton: load_model() once at startup, predict_scam_probability() per request.
"""
import os
from typing import Optional
from app.core.logging import logger

_vectorizer = None
_model = None
_model_loaded = False

_DEFAULT_MODEL_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "ml", "models",
)


def load_model(model_dir: Optional[str] = None) -> bool:
    global _vectorizer, _model, _model_loaded
    if model_dir is None:
        model_dir = _DEFAULT_MODEL_DIR
    vectorizer_path = os.path.join(model_dir, "vectorizer.pkl")
    model_path = os.path.join(model_dir, "scam_model.pkl")

    if not os.path.exists(vectorizer_path) or not os.path.exists(model_path):
        logger.warning(f"ML model files not found at {model_dir}. ML detection disabled.")
        _model_loaded = False
        return False

    try:
        import joblib
        _vectorizer = joblib.load(vectorizer_path)
        _model = joblib.load(model_path)
        _model_loaded = True
        return True
    except Exception as exc:
        logger.error(f"Failed to load ML model: {exc}")
        _vectorizer = _model = None
        _model_loaded = False
        return False


def is_model_loaded() -> bool:
    return _model_loaded


def predict_scam_probability(text: str) -> Optional[float]:
    if not _model_loaded or _vectorizer is None or _model is None:
        return None
    try:
        features = _vectorizer.transform([text])
        probability = _model.predict_proba(features)[0][1]  # P(scam)
        return float(probability)
    except Exception as exc:
        logger.error(f"ML prediction failed: {exc}")
        return None
```

### `app/services/ai_agent.py`
*(Full AIAgent — 481 lines)*

Key features:
- `_create_system_prompt()`: Character lock + persona section + common strategy + language instruction
- `_build_adaptive_prompt_section()`: Extra prompting for repeat scammers (already-known entities)
- `_build_conversation_history()`: Prioritizes client history, falls back to session storage
- `generate_response()`: OpenAI API call with fail-open fallback responses
- `should_end_conversation()`: Always returns False (GUVI controls conversation length)
- 3-phase extraction strategy: Build Trust (1-3) → Gradual Questions (4-6) → Comfortable Extraction (7+)

### `app/services/persona_manager.py`
*(Full persona manager — 360 lines)*

4 personas with English + Hindi + Telugu styles:
- **grandmother**: Elderly, confused, trusting, uses "beta", "yaar"
- **professional**: IT worker, cautious, asks for employee IDs
- **student**: Skeptical, uses "bro", "ngl", "tbh"
- **business_owner**: Practical, asks for invoices, GST

Selection logic:
- JOB_SCAM → student
- INVESTMENT_SCAM → business_owner
- BANK_OTP_SCAM + male address → professional, else → grandmother
- Default: male address → professional, else → grandmother
- Session consistency: keeps existing persona unless contradicted

### `app/services/language_detector.py`
*(Full language detector — 108 lines)*

Detection priority:
1. metadata.language (if present and supported)
2. Script detection (Devanagari → Hindi, Telugu script → Telugu)
3. Transliterated Hindi marker words (23 markers, threshold: 2+)
4. langdetect library fallback
5. Default → English

### `app/services/intelligence_extractor.py`
*(Full intelligence extractor — 360 lines)*

Regex patterns for: bank accounts (11-18 digits), UPI IDs, phone numbers (Indian 10-digit), URLs, emails, amounts (Rs./₹), employee IDs.

Also detects: impersonation targets (13 banks + 12 companies), tactics (urgency, threats, rewards, credential requests, payment redirection).

### `app/services/callback_handler.py`
*(Full callback handler — 109 lines)*

Sends to `https://hackathon.guvi.in/api/updateHoneyPotFinalResult` after 18+ messages with scam detected.

### `app/services/forensic_reporter.py`
*(Full forensic PDF reporter — 456 lines)*

Generates professional forensic PDF reports with:
- Header banner (Navy/Blue palette)
- Executive summary with status badge
- Primary suspect data table
- Behavioral markers with threat level (CRITICAL/HIGH/MODERATE)
- Evidence log (full conversation transcript with colored backgrounds)
- Forensic integrity notice footer

---

## 7. App Storage

### `app/storage/__init__.py`
```python
"""Storage and session management."""
from app.storage.session_manager import SessionManager, SessionData, session_manager
__all__ = ["SessionManager", "SessionData", "session_manager"]
```

### `app/storage/session_manager.py`
*(Full session manager — 220 lines)*

`SessionData` dataclass with fields:
- session_id, scam_detected, scam_confidence, agent_activated
- messages (List[Message]), intelligence, created_at, last_updated
- callback_sent, detected_language, response_language
- persona_selected, persona_switch_history
- **Hybrid detection**: rule_score, ml_score, scam_type, detection_method, detected_indicators

Uses sentinel pattern (`_UNSET = object()`) for ml_score to distinguish "not passed" from "passed as None".

### `app/storage/mongodb.py`
*(Full MongoDB storage — 414 lines)*

Features:
- Lazy async connection via Motor driver
- 8 indexes (sessionId unique, intelligence fields, repeatScammer, riskLevel, scamType, detectionMethod)
- Normalization: phone (+91 prefix), UPI (lowercase), links (strip trailing /)
- Domain extraction for domain-level repeat matching
- `find_repeat_matches()`: Cross-session entity matching
- `compute_risk_level()`: HIGH (repeat or high confidence), MEDIUM (scam detected), LOW
- `upsert_session()`: Full document with all hybrid detection fields
- Admin queries: get_session_doc, get_repeat_analysis, search_sessions

---

## 8. App Utils

### `app/utils/__init__.py`
```python
"""Utility functions."""
from app.utils.helpers import (
    format_conversation_for_display, sanitize_intelligence_data, validate_session_id
)
__all__ = ["format_conversation_for_display", "sanitize_intelligence_data", "validate_session_id"]
```

### `app/utils/helpers.py`
```python
"""Utility helper functions."""
from typing import List
from app.models.requests import Message


def format_conversation_for_display(messages: List[Message]) -> str:
    if not messages:
        return "No messages"
    return "\n".join(
        f"{'Scammer' if msg.sender == 'scammer' else 'User'}: {msg.text}"
        for msg in messages
    )


def sanitize_intelligence_data(data: dict) -> dict:
    sanitized = data.copy()
    if 'bankAccounts' in sanitized:
        sanitized['bankAccounts'] = [f"****{acc[-4:]}" if len(acc) > 4 else "****" for acc in sanitized['bankAccounts']]
    if 'phoneNumbers' in sanitized:
        sanitized['phoneNumbers'] = [f"****{phone[-4:]}" if len(phone) > 4 else "****" for phone in sanitized['phoneNumbers']]
    return sanitized


def validate_session_id(session_id: str) -> bool:
    if not session_id or not isinstance(session_id, str):
        return False
    return len(session_id.strip()) > 0
```

---

## 9. API Routes

### `app/api/__init__.py`
```python
"""API routes and dependencies."""
from app.api.routes import router
__all__ = ["router"]
```

### `app/api/routes.py`
*(Full routes — 520 lines)*

**Main endpoint**: `POST /api/v1/conversation`

Flow:
1. Validate session ID
2. Get/create session
3. Scam detection via `should_activate_agent()` → returns `(bool, DetectionResult)`
4. Language detection + persona selection
5. Repeat scammer detection (early pass at message 2+)
6. Generate AI response with adaptive prompt for repeat scammers
7. Full intelligence extraction (turn 3+)
8. Callback logic (18+ messages)
9. Forensic PDF generation
10. MongoDB persistence (non-blocking)
11. Return `{"status": "success", "reply": "..."}`

**Admin endpoints** (secured with x-admin-key):
- `GET /admin/session/{session_id}` — Full session from MongoDB
- `GET /admin/repeats/{session_id}` — Repeat scammer analysis
- `GET /admin/search?phone=&upi=&account=&link=&keyword=` — Search sessions
- `POST /admin/cleanup` — Remove expired in-memory sessions
- `GET /admin/db-status` — MongoDB connectivity diagnostic

---

## 10. ML Pipeline

### `ml/__init__.py`
```python
# ML training and inference package
```

### `ml/train_model.py`
```python
"""
CYBER-FORENSIC AGENT: Optimized ML Training Script
"""
import argparse, os, re
import pandas as pd, numpy as np, joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

def detect_columns(df):
    cols = {c.lower().strip(): c for c in df.columns}
    label_col = cols.get('label', cols.get('is_scam', cols.get('v1')))
    text_col = cols.get('text', cols.get('scammer_message', cols.get('v2')))
    if not label_col or not text_col:
        raise ValueError(f"Required columns not found. Found: {list(df.columns)}")
    return label_col, text_col

def preprocess_text(text):
    if not isinstance(text, str): return ""
    text = text.lower().strip()
    text = re.sub(r'\S+@\S+', ' <upi_id> ', text)
    text = re.sub(r'http\S+|www\S+', ' <link> ', text)
    text = re.sub(r'\d{4,}', ' <number_long> ', text)
    text = re.sub(r'\d+', ' <num> ', text)
    text = re.sub(r'\b[a-z]\b', '', text)
    text = re.sub(r'[^\w\s<>]', ' ', text)
    return re.sub(r'\s+', ' ', text)

def train_model(data_path, output_dir="ml/models/"):
    df = pd.read_csv(data_path, encoding="latin-1")
    label_col, text_col = detect_columns(df)
    df = df.dropna(subset=[text_col, label_col])
    df['clean_text'] = df[text_col].astype(str).apply(preprocess_text)
    df['label'] = df[label_col].apply(lambda x: 1 if str(x) in ['1', '1.0', 'scam', 'spam'] else 0)

    vectorizer = TfidfVectorizer(max_features=2000, ngram_range=(1,2), stop_words="english")
    X = vectorizer.fit_transform(df['clean_text'])
    y = df['label'].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    model = LogisticRegression(max_iter=2000, C=1.0, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {accuracy:.4f}")
    print(classification_report(y_test, y_pred))

    os.makedirs(output_dir, exist_ok=True)
    joblib.dump(vectorizer, os.path.join(output_dir, "vectorizer.pkl"))
    joblib.dump(model, os.path.join(output_dir, "scam_model.pkl"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True)
    args = parser.parse_args()
    train_model(args.data)
```

### `ml/test_model.py`
*(Full test suite — 157 lines, 25 test cases: 15 scam + 10 safe)*

Run: `python -m ml.test_model` or `python -m ml.test_model --text "message"`

Last test results: 80% accuracy (20/25), 3 false positives, 2 false negatives.

### `data/scam_dataset.csv`
~2200 rows with columns: `text`, `label` (0=safe, 1=scam).

### Known ML Gap
`train_model.py` preprocesses text (replaces UPI IDs, URLs, numbers with tokens) but `ml_detector.py` passes raw text at inference time — preprocessing mismatch.

---

## 11. Tests

### `tests/__init__.py`
```python
"""Tests for Scambot Honeypot."""
```

### `tests/test_api.py`
*(624 lines)* — 25 tests covering:
- API Authentication (missing key, invalid key, valid key)
- Scam Detection (bank fraud, UPI, phishing, lottery, OTP)
- Multi-Turn Conversations (2-turn, 5-turn, 10-turn, context retention, cross-channel)
- Intelligence Extraction (bank accounts, UPI IDs, phone numbers)
- Response Format (structure compliance, human-like replies)
- Edge Cases (missing fields, invalid session ID, health check)

### `tests/test_all_scenarios.py`
*(453 lines)* — 13 scenario tests:
- 10 single-message scam types (bank, UPI, phishing, lottery, OTP, KYC, investment, delivery, job, tax)
- 3 multi-turn tests (3-turn, 5-turn, 10-turn)

### `tests/test_forensic_reporter.py`
*(388 lines)* — Standalone PDF tests (no server needed):
- Full SBI scam report, empty intelligence, partial intelligence
- Filename convention, case ID generation
- Unicode handling, very long messages
- Critical/moderate threat levels, multiple sessions

### `tests/test_intelligence_extraction.py`
*(374 lines)* — Intelligence extraction tests:
- Bank accounts (single, multiple), UPI IDs (Paytm, PhonePe)
- Phone numbers (Indian, multiple), emails, phishing links, amounts
- Comprehensive single-message extraction
- Agent proactive extraction behavior
- Multi-turn intelligence accumulation

### `tests/test_persona_validation.py`
*(324 lines)* — Persona realism tests:
- Short natural responses, no bookish language
- Natural emotions, simple questions, no bot mentions
- Indian English patterns, vulnerability expression
- Hesitation behavior, natural info extraction
- Character consistency across turns

### `tests/test_remote_api.py`
*(896 lines)* — Remote Render deployment tests:
- Authentication, scam scenarios, multi-turn, persona validation
- Intelligence extraction (bank, UPI, phone, email, links, amounts)
- Comprehensive extraction, agent extraction behavior
- **Critical**: History maintained without client-sent history (GUVI bug fix)
- Multi-turn intelligence accumulation

---

## 12. Demo Script

### `demo_for_ppt.py`
*(353 lines)*

Live demo against deployed Render server covering:
1. Health check (wake up server)
2. English bank scam (Grandmother persona)
3. Hindi scam (language detection)
4. Job scam (Student persona)
5. Admin panel — MongoDB session data
6. Hindi session — persona + language fields
7. Repeat scammer detection
8. Admin search by phone number
9. GUVI response format compliance
10. Admin endpoint security (401 on bad keys)

---

## 13. Problem Statement

**GUVI/India AI Impact Buildathon**: Build an AI-powered agentic honeypot API that:
- Detects scam messages
- Activates autonomous AI Agent
- Maintains believable human persona
- Handles multi-turn conversations
- Extracts intelligence (bankAccounts, upiIds, phishingLinks, phoneNumbers, suspiciousKeywords)
- Returns `{"status": "success", "reply": "..."}`
- Sends mandatory callback to `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`

Evaluation: Scam detection accuracy, engagement quality, intelligence extraction, API stability, ethical behavior.

---

## 14. Current State & Known Gaps

### Working
- Full API with hybrid detection (rules + ML + OpenAI fallback)
- 4 dynamic personas with multilingual support (English, Hindi, Telugu)
- MongoDB Atlas persistence with repeat scammer detection
- Forensic PDF report generation
- GUVI callback after 18+ messages
- Fail-open at every level
- Comprehensive test suite

### Known Gaps
1. **ML preprocessing mismatch**: Training preprocesses text (token replacement) but inference passes raw text
2. **ML test accuracy**: 80% on custom test cases (3 FP, 2 FN) — rule-based Tier 1 catches these in production
3. **Render deployment**: render.yaml has different agent persona (Rahul/28/Software Engineer) vs .env (Veerabadhra/64/Retired teacher)
4. **Feature request pending**: Dynamic Persona Detection and Persona Locking (scammer-driven identity mirroring) — explored but not implemented

### Pending Feature: Dynamic Persona Detection & Locking
From team discussion — the agent should:
- Mirror whatever identity the scammer assumes (detect name, gender, role from scammer messages)
- Lock the persona for the session once established
- Start with neutral default before any cues
- Anti-contradiction safeguards (if scammer says "sir" but persona is grandmother → switch)
- This was explored in plan mode but not implemented yet
