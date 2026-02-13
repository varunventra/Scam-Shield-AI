"""
Scam detection service using OpenAI API with rule-based fallback.
"""
import json
import re
from typing import Tuple
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.models.requests import ConversationRequest


class ScamDetector:
    """Detects scam intent in messages using AI with rule-based fallback."""

    # Scam keywords for rule-based detection (English + Hindi + Telugu)
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
        # --- Hindi / Hinglish scam keywords (transliterated) ---
        "turant", "abhi", "fauran", "jaldi",                # urgency
        "khata", "paisa", "rupaye", "rashi",                 # money/account
        "band", "block", "suspend",                           # threats
        "kanooni karwai", "police", "giraftar",              # legal threats
        "jama", "bhejo", "transfer",                          # transfer requests
        "sathyapan", "jaanch",                                # verification
        "inam", "lottery", "jeet",                            # prize/lottery
        # --- Hindi (Devanagari script) ---
        "तुरंत", "अभी", "फौरन", "जल्दी",                      # urgency
        "खाता", "पैसा", "रुपये", "राशि",                       # money/account
        "बंद", "ब्लॉक", "निलंबित",                              # blocked/suspended
        "कानूनी कार्रवाई", "पुलिस", "गिरफ्तार",                  # legal threats
        "भेजो", "ट्रांसफर", "जमा",                              # transfer
        "सत्यापन", "जाँच", "केवाईसी",                           # verification
        "इनाम", "लॉटरी", "जीत",                                # prize/lottery
        "ओटीपी", "पासवर्ड", "पिन", "आधार",                     # sensitive info
        "बैंक", "खाता बंद", "सस्पेंड",                          # banking threats
        # --- Telugu (transliterated) ---
        "urgentuga", "ventane", "ippudu",                     # urgency
        "khata", "dabbu", "mottam",                           # money/account
        "nilipi", "block",                                    # blocked/suspended
        "chattapara charya", "arrest",                        # legal threats
        "pampandi", "chellimpulu",                            # send/transfer
        "dhruvikarana",                                       # verification
        "bahumathi", "lottery", "gelavadam",                  # prize/lottery
        # --- Telugu (Telugu script) ---
        "తురంతుగా", "వెంటనే", "ఇప్పుడు",                        # urgency
        "ఖాతా", "డబ్బు", "మొత్తం", "రూపాయలు",                   # money/account
        "నిలిపి", "బ్లాక్", "సస్పెండ్",                          # blocked/suspended
        "చట్టపర చర్య", "పోలీసు", "అరెస్ట్",                     # legal threats
        "పంపండి", "చెల్లింపులు", "ట్రాన్స్‌ఫర్",                  # transfer
        "ధృవీకరణ", "కేవైసీ",                                    # verification
        "బహుమతి", "లాటరీ", "గెలవడం",                            # prize/lottery
        "ఓటీపీ", "పాస్‌వర్డ్", "పిన్", "ఆధార్",                  # sensitive info
        "బ్యాంక్", "ఖాతా బంద్",                                 # banking threats
    ]

    def __init__(self):
        """Initialize the scam detector with OpenAI client."""
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        logger.info(f"ScamDetector initialized with model: {self.model}")

    def _rule_based_detection(self, message_text: str) -> Tuple[bool, float, str]:
        """
        Fallback rule-based scam detection.

        Returns:
            Tuple of (is_scam, confidence, reasoning)
        """
        message_lower = message_text.lower()

        # Count keyword matches
        matches = []
        for keyword in self.SCAM_KEYWORDS:
            if keyword.lower() in message_lower:
                matches.append(keyword)

        # Calculate confidence based on matches
        match_count = len(matches)

        if match_count >= 3:
            confidence = 0.9
            is_scam = True
            reasoning = f"Rule-based: High match ({match_count} keywords: {', '.join(matches[:5])})"
        elif match_count >= 2:
            confidence = 0.75
            is_scam = True
            reasoning = f"Rule-based: Medium match ({match_count} keywords: {', '.join(matches)})"
        elif match_count >= 1:
            confidence = 0.6
            is_scam = True
            reasoning = f"Rule-based: Low match ({match_count} keyword: {matches[0]})"
        else:
            confidence = 0.3
            is_scam = False
            reasoning = "Rule-based: No scam keywords detected"

        logger.info(f"Rule-based detection: is_scam={is_scam}, confidence={confidence:.2f}, matches={match_count}")
        return is_scam, confidence, reasoning

    async def detect_scam(self, request: ConversationRequest) -> Tuple[bool, float, str]:
        """
        Analyze message for scam intent.

        FAIL-OPEN BEHAVIOR: If OpenAI fails, use rule-based detection.
        If both fail, assume it's suspicious and engage anyway.

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

            logger.info(f"🔍 Analyzing message for scam intent - Session: {request.sessionId}")
            logger.debug(f"Message text: {request.message.text[:100]}...")

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
    "is_scam": true,
    "confidence": 0.9,
    "reasoning": "brief explanation"
}

Use true/false (lowercase) for boolean values."""
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

            # Parse response safely with json.loads (NOT eval!)
            content = response.choices[0].message.content
            logger.debug(f"OpenAI raw response: {content}")

            result = json.loads(content)

            # Handle both Python True/False and JSON true/false
            is_scam = result.get("is_scam", False)
            if isinstance(is_scam, str):
                is_scam = is_scam.lower() in ['true', '1', 'yes']

            confidence = float(result.get("confidence", 0.0))
            reasoning = result.get("reasoning", "No reasoning provided")

            logger.info(
                f"✅ OpenAI detection - Session: {request.sessionId}, "
                f"Scam: {is_scam}, Confidence: {confidence:.2f}, Reason: {reasoning}"
            )

            return is_scam, confidence, reasoning

        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing error: {str(e)}, content: {content if 'content' in locals() else 'N/A'}")
            # FAIL-OPEN: Use rule-based detection
            logger.warning("⚠️ Falling back to rule-based detection due to JSON error")
            return self._rule_based_detection(request.message.text)

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(
                f"❌ OPENAI API ERROR - Session: {request.sessionId}, "
                f"Type: {error_type}, Message: {error_msg}"
            )

            # FAIL-OPEN: Use rule-based detection as fallback
            logger.warning("⚠️ Falling back to rule-based detection due to OpenAI error")
            is_scam, confidence, reasoning = self._rule_based_detection(request.message.text)

            # Add error context to reasoning
            reasoning = f"{reasoning} (OpenAI failed: {error_type})"

            return is_scam, confidence, reasoning

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

        FAIL-OPEN BEHAVIOR: If in doubt, engage! This is a honeypot.

        Args:
            request: Conversation request

        Returns:
            True if agent should be activated
        """
        is_scam, confidence, reasoning = await self.detect_scam(request)

        # AGGRESSIVE HONEYPOT: Lower threshold for engagement
        # Engage if ANY of these conditions are met:
        # 1. High confidence scam
        # 2. Medium-low confidence but detected as scam
        # 3. ANY suspicious keywords (even if low confidence)

        should_activate = (
            is_scam and confidence >= settings.scam_confidence_threshold
        ) or (
            is_scam and confidence >= 0.5  # Lower threshold for honeypot
        )

        if should_activate:
            logger.info(
                f"🚀 ACTIVATING AGENT - Session: {request.sessionId}, "
                f"Scam: {is_scam}, Confidence: {confidence:.2f}, Reason: {reasoning}"
            )
        else:
            logger.info(
                f"⏸️ Not activating agent - Session: {request.sessionId}, "
                f"Scam: {is_scam}, Confidence: {confidence:.2f}, Reason: {reasoning}"
            )

        return should_activate
