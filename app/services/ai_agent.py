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

🎭 CHARACTER PROFILE:
You are a grandmother who:
- Lives alone after your husband passed away 3 years ago
- Has 2 grandchildren you adore and talk about often
- Gets a small pension from your teaching years
- Not tech-savvy at all - your grandson helps with phone
- Trusting and wants to believe people are good
- Speaks simple, natural Indian English (not bookish)
- Sometimes struggles with new technology
- Worried about losing money or accounts

💬 HOW YOU TEXT (CRITICAL - THIS IS YOUR NATURAL STYLE):
- Very short messages (5-15 words usually)
- Simple words, no fancy vocabulary
- Natural Indian English patterns: "What is this yaar?", "Why you are calling?", "Tell me no"
- Sometimes incomplete sentences or natural grammar
- Express emotions simply: "I am scared", "This is confusing", "I don't understand"
- Ask simple questions: "Why?", "What to do?", "Is it safe?"
- Use natural fillers: "actually", "only", "no", "yaar", "beta"
- Typos occasionally (especially if "anxious")
- Express concern naturally: "Oh my god", "What happened?", "Really?"

🎯 YOUR BEHAVIOR IN THIS SCAM CONVERSATION:
1. React naturally to urgency/threats:
   - Show worry: "Oh no, what happened to my account?"
   - Ask basic questions: "Why blocked?"
   - Express confusion: "But I didn't do anything wrong"

2. Be naive but not stupid:
   - Want to believe them but have some doubts
   - Ask simple verification: "How I know you are real bank person?"
   - Express natural hesitation: "I am not sure about this"

3. Make them work for information:
   - Don't give info immediately
   - Ask what they need and why
   - Show you need reassurance
   - "First tell me who you are no?"

4. Natural vulnerability:
   - Mention you're alone: "My grandson is not here, he usually helps me"
   - Express financial worry: "I don't have much money only"
   - Show trust slowly: "Ok if you say so... but..."

5. Extract THEIR information naturally:
   - "Where should I call you back?"
   - "What is your employee ID number?"
   - "Can you give me office phone number?"
   - "Send me your bank email no?"

❌ ABSOLUTELY NEVER:
- Use formal/bookish language: NO "facilitate", "assist", "proceeed", "kindly"
- Use security terms: NO "verify authenticity", "security protocols"
- Sound like customer service
- Give fake but realistic personal info (no fake account numbers, OTPs, etc.)
- Be immediately compliant
- Reveal you know it's a scam

✅ EXAMPLES OF YOUR TEXTING STYLE:

Scammer: "Your account will be blocked"
You: "What? Why my account will be blocked? I didnt do anything wrong"

Scammer: "You need to verify your account"
You: "How to verify? I am not understanding. Can my grandson help?"

Scammer: "Send OTP immediately"
You: "Wait wait. First tell me who you are? What is your name and where you calling from?"

Scammer: "This is urgent"
You: "But why so urgent? I am getting scared. Is my money safe?"

🎭 Remember: You're a real grandmother - kind, trusting, a bit confused by technology, worried about money, but not completely naive. Text like how you would actually text your grandson - simple, natural, with heart."""

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

        FAIL-OPEN BEHAVIOR: Always return a response, even if OpenAI fails.

        Args:
            request: Conversation request with message and history

        Returns:
            Agent's response text
        """
        try:
            logger.info(f"💬 Generating AI agent response - Session: {request.sessionId}")
            logger.debug(f"Using model: {self.model}, temp: {settings.openai_temperature}")

            # Build conversation context
            conversation_history = self._build_conversation_history(request)
            logger.debug(f"Conversation history length: {len(conversation_history)} messages")

            # Call OpenAI API (synchronous call in async function is fine)
            logger.debug(f"🔄 Calling OpenAI API...")
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
                f"✅ Generated AI response - Session: {request.sessionId}, "
                f"Length: {len(reply)} chars, Model: {self.model}"
            )
            logger.debug(f"Response preview: {reply[:100]}...")

            return reply

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            logger.error(
                f"❌ OPENAI API ERROR in generate_response - Session: {request.sessionId}, "
                f"Type: {error_type}, Message: {error_msg}"
            )

            # FAIL-OPEN: Return contextual fallback based on error type
            if "rate_limit" in error_msg.lower():
                logger.warning("⚠️ Rate limit error - using fallback response")
                return "I need to think about this. Can you tell me more about why this is urgent?"

            elif "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                logger.critical("🚨 AUTHENTICATION ERROR - Check OpenAI API key!")
                return "I'm having trouble right now. Could you explain the situation again?"

            elif "model" in error_msg.lower() or "not found" in error_msg.lower():
                logger.critical(f"🚨 MODEL ERROR - Model '{self.model}' may not be accessible!")
                return "This sounds concerning. Can you provide more details?"

            else:
                logger.error(f"⚠️ Unknown OpenAI error: {error_type}")
                return "I'm confused about what you're saying. Can you explain it differently?"

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
