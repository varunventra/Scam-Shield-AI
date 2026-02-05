"""
Intelligence extraction service to identify scam-related information.
"""
import re
from typing import List
from app.core.logging import logger
from app.models.requests import ConversationRequest, Message
from app.models.responses import ExtractedIntelligence


class IntelligenceExtractor:
    """Extracts intelligence from scam conversations."""

    # Regex patterns for extraction
    BANK_ACCOUNT_PATTERN = r'\b\d{9,18}\b'  # 9-18 digit account numbers
    UPI_ID_PATTERN = r'\b[\w\.-]+@[\w\.-]+\b'  # UPI ID format
    PHONE_PATTERN = r'\+?\d{10,15}\b'  # Phone numbers
    URL_PATTERN = r'https?://[^\s]+'  # URLs

    # Suspicious keywords
    SUSPICIOUS_KEYWORDS = [
        'urgent', 'immediately', 'verify', 'suspended', 'blocked', 'expire',
        'confirm', 'update', 'security', 'alert', 'limited time', 'act now',
        'click here', 'reset password', 'account locked', 'unauthorized',
        'refund', 'prize', 'winner', 'congratulations', 'claim', 'otp',
        'pin', 'cvv', 'card number', 'bank details', 'payment failed'
    ]

    def extract_intelligence(
        self,
        request: ConversationRequest,
        all_messages: List[Message]
    ) -> ExtractedIntelligence:
        """
        Extract intelligence from conversation messages.

        Args:
            request: Current conversation request
            all_messages: All messages in the conversation

        Returns:
            Extracted intelligence data
        """
        logger.info(f"Extracting intelligence - Session: {request.sessionId}")

        # Combine all message texts
        all_text = " ".join([msg.text for msg in all_messages])

        # Extract different types of intelligence
        bank_accounts = self._extract_bank_accounts(all_text)
        upi_ids = self._extract_upi_ids(all_text)
        phishing_links = self._extract_urls(all_text)
        phone_numbers = self._extract_phone_numbers(all_text)
        suspicious_keywords = self._extract_keywords(all_text)

        intelligence = ExtractedIntelligence(
            bankAccounts=bank_accounts,
            upiIds=upi_ids,
            phishingLinks=phishing_links,
            phoneNumbers=phone_numbers,
            suspiciousKeywords=suspicious_keywords
        )

        logger.info(
            f"Intelligence extracted - Session: {request.sessionId}, "
            f"Banks: {len(bank_accounts)}, UPI: {len(upi_ids)}, "
            f"Links: {len(phishing_links)}, Phones: {len(phone_numbers)}, "
            f"Keywords: {len(suspicious_keywords)}"
        )

        return intelligence

    def _extract_bank_accounts(self, text: str) -> List[str]:
        """Extract bank account numbers."""
        accounts = re.findall(self.BANK_ACCOUNT_PATTERN, text)
        return list(set(accounts))  # Remove duplicates

    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs."""
        upi_ids = re.findall(self.UPI_ID_PATTERN, text)
        # Filter to only keep valid UPI-like patterns
        valid_upis = [
            upi for upi in upi_ids
            if any(provider in upi.lower() for provider in ['paytm', 'phonepe', 'gpay', 'upi', 'ybl', 'okaxis', 'okhdfcbank'])
            or upi.count('@') == 1
        ]
        return list(set(valid_upis))

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs."""
        urls = re.findall(self.URL_PATTERN, text)
        return list(set(urls))

    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers."""
        phones = re.findall(self.PHONE_PATTERN, text)
        # Filter out numbers that are likely not phone numbers
        valid_phones = [
            phone for phone in phones
            if 10 <= len(re.sub(r'\D', '', phone)) <= 15
        ]
        return list(set(valid_phones))

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract suspicious keywords."""
        text_lower = text.lower()
        found_keywords = [
            keyword for keyword in self.SUSPICIOUS_KEYWORDS
            if keyword in text_lower
        ]
        return list(set(found_keywords))

    def generate_agent_notes(
        self,
        request: ConversationRequest,
        all_messages: List[Message],
        intelligence: ExtractedIntelligence
    ) -> str:
        """
        Generate summary notes about scammer behavior.

        Args:
            request: Conversation request
            all_messages: All messages in conversation
            intelligence: Extracted intelligence

        Returns:
            Summary notes
        """
        notes = []

        # Analyze tactics
        if any(keyword in intelligence.suspiciousKeywords for keyword in ['urgent', 'immediately', 'limited time']):
            notes.append("Used urgency tactics")

        if any(keyword in intelligence.suspiciousKeywords for keyword in ['verify', 'confirm', 'update']):
            notes.append("Requested verification/update")

        if intelligence.bankAccounts or intelligence.upiIds:
            notes.append("Provided payment redirection")

        if intelligence.phishingLinks:
            notes.append("Shared suspicious links")

        if any(keyword in intelligence.suspiciousKeywords for keyword in ['otp', 'pin', 'cvv', 'password']):
            notes.append("Requested sensitive credentials")

        # Message count
        notes.append(f"Conversation length: {len(all_messages)} messages")

        return ". ".join(notes) if notes else "Suspicious behavior detected"
