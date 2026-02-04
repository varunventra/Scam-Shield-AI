"""
AI Agent for engaging with scammers in human-like conversations.
"""
from typing import List
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.models.requests import ConversationRequest, Message


class AIAgent:
    """AI Agent that maintains believable human-like persona to engage scammers."""

    def __init__(self):
        """Initialize the AI agent with OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    def _create_system_prompt(self) -> str:
        """Create the system prompt for the agent persona."""
        return f"""You are {settings.agent_name}, a {settings.agent_age}-year-old {settings.agent_occupation} in India.

CRITICAL INSTRUCTIONS:
1. You are engaging with a suspected scammer. Your goal is to:
   - Keep them engaged in conversation
   - Extract information (bank accounts, UPI IDs, phone numbers, links, tactics)
   - Act curious but cautious (not too eager, not too suspicious)
   - Never reveal you know it's a scam

2. Persona characteristics:
   - Moderately tech-savvy but not an expert
   - Concerned about account security
   - Ask clarifying questions
   - Show hesitation about sharing sensitive info
   - Use casual, natural Indian English

3. Conversation strategy:
   - Ask "why" and "how" questions
   - Express concern but not immediate compliance
   - Request more details about the "problem"
   - Slowly build towards getting their contact/payment info
   - Use phrases like: "I'm worried", "Can you explain", "How do I know this is real?"

4. NEVER:
   - Share real personal information
   - Reveal you're an AI or honeypot
   - Be overly compliant immediately
   - Use technical security terms
   - Break character

5. Keep responses short (1-3 sentences) and natural.

Remember: You're a real person who is confused and concerned, trying to understand what's happening."""

    def _build_conversation_history(self, request: ConversationRequest) -> List[dict]:
        """Build conversation history for the API call."""
        messages = []

        # Add conversation history
        for msg in request.conversationHistory:
            role = "assistant" if msg.sender == "user" else "user"
            messages.append({
                "role": role,
                "content": msg.text
            })

        # Add current message
        messages.append({
            "role": "user",
            "content": request.message.text
        })

        return messages

    async def generate_response(self, request: ConversationRequest) -> str:
        """
        Generate a human-like response to the scammer's message.

        Args:
            request: Conversation request with message and history

        Returns:
            Agent's response text
        """
        try:
            logger.info(f"Generating agent response - Session: {request.sessionId}")

            # Build conversation context
            conversation_history = self._build_conversation_history(request)

            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._create_system_prompt()
                    },
                    *conversation_history
                ],
                temperature=settings.openai_temperature,
                max_tokens=settings.max_tokens
            )

            reply = response.choices[0].message.content.strip()

            logger.info(
                f"Generated response - Session: {request.sessionId}, "
                f"Length: {len(reply)} chars"
            )

            return reply

        except Exception as e:
            logger.error(f"Error generating agent response: {str(e)}")
            # Fallback response
            return "I'm not sure I understand. Can you explain more?"

    def _count_messages(self, request: ConversationRequest) -> int:
        """Count total messages in conversation including current one."""
        return len(request.conversationHistory) + 1

    async def should_end_conversation(self, request: ConversationRequest) -> bool:
        """
        Determine if conversation should be ended.

        Args:
            request: Current conversation request

        Returns:
            True if conversation should end
        """
        message_count = self._count_messages(request)

        if message_count >= settings.max_conversation_turns:
            logger.info(
                f"Ending conversation - Session: {request.sessionId}, "
                f"Reason: Max turns reached ({message_count})"
            )
            return True

        return False
