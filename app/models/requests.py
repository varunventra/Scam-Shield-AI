"""
Request models for the Scambot Honeypot API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Individual message model."""
    sender: str = Field(..., description="Message sender: 'scammer' or 'user'")
    text: str = Field(..., description="Message content")
    timestamp: int = Field(..., description="Epoch time in milliseconds")


class Metadata(BaseModel):
    """Optional metadata about the conversation."""
    channel: Optional[str] = Field(None, description="Communication channel (SMS/WhatsApp/Email/Chat)")
    language: Optional[str] = Field(None, description="Language used in conversation")
    locale: Optional[str] = Field(None, description="Country or region code")


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
