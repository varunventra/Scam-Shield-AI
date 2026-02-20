"""
Request models for the Scambot Honeypot API.
"""
import time
from typing import Any, List, Optional
from datetime import datetime, timezone

from pydantic import BaseModel, Field, field_validator


class Message(BaseModel):
    """Individual message model."""
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: Any = Field(..., description="Epoch time in milliseconds or ISO string")

    @field_validator("sender", mode="before")
    @classmethod
    def validate_sender(cls, v):
        """Normalize sender field to lowercase."""
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("text", mode="before")
    @classmethod
    def validate_text(cls, v):
        """Ensure text is non-empty string."""
        if not isinstance(v, str) or not v.strip():
            return "..."  # Fallback for empty messages
        return v.strip()

    @field_validator("timestamp", mode="before")
    @classmethod
    def coerce_timestamp(cls, v):
        """Accept epoch‑ms (int/float) or ISO‑8601 string; normalise to epoch‑ms int."""
        if isinstance(v, (int, float)):
            return int(v)
        if isinstance(v, str):
            v_stripped = v.strip()
            # Pure numeric string
            if v_stripped.replace(".", "", 1).isdigit():
                return int(float(v_stripped))
            # ISO-8601 string
            try:
                dt = datetime.fromisoformat(v_stripped.replace("Z", "+00:00"))
                return int(dt.timestamp() * 1000)
            except ValueError:
                pass
            # Fallback: return current time
            return int(time.time() * 1000)
        # Fallback
        return int(time.time() * 1000)


class Metadata(BaseModel):
    """Optional metadata about the conversation."""
    channel: Optional[str] = Field(None, description="Communication channel (SMS/WhatsApp/Email/Chat)")
    language: Optional[str] = Field(None, description="Language used in conversation")
    locale: Optional[str] = Field(None, description="Country or region code")
    callbackUrl: Optional[str] = Field(None, description="Override callback URL for testing")


class ConversationRequest(BaseModel):
    """Main request model for incoming messages."""
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Latest incoming message")
    conversationHistory: List[Message] = Field(
        default_factory=list,
        description="Previous messages in the conversation"
    )
    metadata: Optional[Metadata] = Field(None, description="Optional conversation metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "wertyu-dfghj-ertyui",
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
            }
        }
