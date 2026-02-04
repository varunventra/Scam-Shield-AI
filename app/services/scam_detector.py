"""
Scam detection service using OpenAI API.
"""
from typing import Tuple
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.models.requests import ConversationRequest


class ScamDetector:
    """Detects scam intent in messages using AI."""

    def __init__(self):
        """Initialize the scam detector with OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def detect_scam(self, request: ConversationRequest) -> Tuple[bool, float, str]:
        """
        Analyze message for scam intent.

        Args:
            request: Conversation request containing message and history

        Returns:
            Tuple of (is_scam, confidence_score, reasoning)
        """
        try:
            # Build context from conversation history
            context = self._build_context(request)

            # Create prompt for scam detection
            prompt = self._create_detection_prompt(context, request.message.text)

            logger.info(f"Analyzing message for scam intent - Session: {request.sessionId}")

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert fraud detection system. Analyze messages for scam intent including:
- Bank fraud attempts
- UPI fraud
- Phishing attempts
- Fake offers and lottery scams
- Account verification scams
- Urgency-based manipulation
- Request for sensitive information (OTP, PIN, passwords, account details)

Respond in JSON format with:
{
    "is_scam": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            # Parse response
            result = eval(response.choices[0].message.content)
            is_scam = result.get("is_scam", False)
            confidence = result.get("confidence", 0.0)
            reasoning = result.get("reasoning", "No reasoning provided")

            logger.info(
                f"Scam detection result - Session: {request.sessionId}, "
                f"Scam: {is_scam}, Confidence: {confidence:.2f}"
            )

            return is_scam, confidence, reasoning

        except Exception as e:
            logger.error(f"Error in scam detection: {str(e)}")
            # Default to non-scam in case of error to avoid false positives
            return False, 0.0, f"Error: {str(e)}"

    def _build_context(self, request: ConversationRequest) -> str:
        """Build conversation context from history."""
        if not request.conversationHistory:
            return "This is the first message in the conversation."

        context_parts = ["Previous conversation:"]
        for msg in request.conversationHistory:
            sender_label = "Scammer" if msg.sender == "scammer" else "User"
            context_parts.append(f"{sender_label}: {msg.text}")

        return "\n".join(context_parts)

    def _create_detection_prompt(self, context: str, current_message: str) -> str:
        """Create detection prompt with context."""
        return f"""{context}

Current message to analyze: "{current_message}"

Analyze if this message is a scam attempt. Consider the full conversation context."""

    async def should_activate_agent(self, request: ConversationRequest) -> bool:
        """
        Determine if the AI agent should be activated.

        Args:
            request: Conversation request

        Returns:
            True if agent should be activated (scam detected with sufficient confidence)
        """
        is_scam, confidence, reasoning = await self.detect_scam(request)

        should_activate = is_scam and confidence >= settings.scam_confidence_threshold

        if should_activate:
            logger.info(
                f"Activating agent for session {request.sessionId} - "
                f"Confidence: {confidence:.2f}, Reason: {reasoning}"
            )
        else:
            logger.info(
                f"Not activating agent for session {request.sessionId} - "
                f"Scam: {is_scam}, Confidence: {confidence:.2f}"
            )

        return should_activate
