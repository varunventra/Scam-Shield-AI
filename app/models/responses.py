"""
Response models for the Scambot Honeypot API.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class ConversationResponse(BaseModel):
    """Response model for conversation endpoint."""
    status: str = Field(..., description="Response status (success/error)")
    reply: str = Field(..., description="Agent's response to the scammer")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "success",
                "reply": "Why is my account being suspended?"
            }
        }


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from the conversation."""
    bankAccounts: List[str] = Field(default_factory=list, description="Extracted bank account numbers")
    upiIds: List[str] = Field(default_factory=list, description="Extracted UPI IDs")
    phishingLinks: List[str] = Field(default_factory=list, description="Phishing URLs found")
    phoneNumbers: List[str] = Field(default_factory=list, description="Phone numbers extracted")
    suspiciousKeywords: List[str] = Field(default_factory=list, description="Suspicious keywords detected")


class FinalResultPayload(BaseModel):
    """Payload sent to GUVI callback endpoint."""
    sessionId: str = Field(..., description="Session identifier")
    scamDetected: bool = Field(..., description="Whether scam was detected")
    totalMessagesExchanged: int = Field(..., description="Total message count")
    extractedIntelligence: ExtractedIntelligence = Field(..., description="Extracted intelligence data")
    agentNotes: str = Field(..., description="Summary of scammer behavior")

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "abc123-session-id",
                "scamDetected": True,
                "totalMessagesExchanged": 18,
                "extractedIntelligence": {
                    "bankAccounts": ["XXXX-XXXX-XXXX"],
                    "upiIds": ["scammer@upi"],
                    "phishingLinks": ["http://malicious-link.example"],
                    "phoneNumbers": ["+91XXXXXXXXXX"],
                    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
                },
                "agentNotes": "Scammer used urgency tactics and payment redirection"
            }
        }
