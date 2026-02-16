"""
Response models for the Scambot Honeypot API.
"""
from typing import Dict, List, Optional
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
    """
    Intelligence extracted from the conversation.

    All evaluation-relevant fields are included in serialization.
    """
    # === REQUIRED FIELDS FOR EVALUATION ===
    bankAccounts: List[str] = Field(default_factory=list, description="Extracted bank account numbers")
    upiIds: List[str] = Field(default_factory=list, description="Extracted UPI IDs")
    phishingLinks: List[str] = Field(default_factory=list, description="Phishing URLs found")
    phoneNumbers: List[str] = Field(default_factory=list, description="Phone numbers extracted")
    emailAddresses: List[str] = Field(default_factory=list, description="Email addresses extracted")
    suspiciousKeywords: List[str] = Field(default_factory=list, description="Suspicious keywords detected")

    # === INTERNAL FIELDS (excluded from callback serialization) ===
    emails: List[str] = Field(default_factory=list, description="Email addresses (internal)", exclude=True)
    amounts: List[str] = Field(default_factory=list, description="Monetary amounts mentioned", exclude=True)
    employeeIds: List[str] = Field(default_factory=list, description="Employee/Reference IDs extracted", exclude=True)
    impersonationTargets: List[str] = Field(default_factory=list, description="Banks/companies being impersonated", exclude=True)


class EngagementMetrics(BaseModel):
    """Engagement metrics for evaluation scoring."""
    totalMessagesExchanged: int = Field(default=0, description="Total messages exchanged")
    engagementDurationSeconds: int = Field(default=0, description="Duration of engagement in seconds")


class FinalResultPayload(BaseModel):
    """Payload sent to evaluation callback endpoint."""
    sessionId: str = Field(..., description="Session identifier")
    status: str = Field(default="completed", description="Session status")
    scamDetected: bool = Field(..., description="Whether scam was detected")
    totalMessagesExchanged: int = Field(..., description="Total message count")
    extractedIntelligence: ExtractedIntelligence = Field(..., description="Extracted intelligence data")
    engagementMetrics: EngagementMetrics = Field(
        default_factory=EngagementMetrics,
        description="Engagement duration and message metrics"
    )
    agentNotes: str = Field(..., description="Summary of scammer behavior")

    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "abc123-session-id",
                "status": "completed",
                "scamDetected": True,
                "totalMessagesExchanged": 18,
                "extractedIntelligence": {
                    "bankAccounts": ["XXXX-XXXX-XXXX"],
                    "upiIds": ["scammer@upi"],
                    "phishingLinks": ["http://malicious-link.example"],
                    "phoneNumbers": ["+91-XXXXXXXXXX"],
                    "emailAddresses": ["scammer@example.com"],
                    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
                },
                "engagementMetrics": {
                    "totalMessagesExchanged": 18,
                    "engagementDurationSeconds": 120
                },
                "agentNotes": "Scammer used urgency tactics and payment redirection"
            }
        }
