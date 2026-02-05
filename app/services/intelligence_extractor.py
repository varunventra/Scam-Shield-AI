"""
ENHANCED Intelligence extraction service with AI-powered extraction.
Extracts comprehensive scam-related information from conversations.
"""
import re
from typing import List, Dict, Any
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.models.requests import ConversationRequest, Message
from app.models.responses import ExtractedIntelligence


class IntelligenceExtractor:
    """Enhanced intelligence extractor with AI-powered analysis."""

    def __init__(self):
        """Initialize with OpenAI client for AI-powered extraction."""
        self.client = OpenAI(api_key=settings.openai_api_key)

    # Enhanced regex patterns
    BANK_ACCOUNT_PATTERN = r'\b\d{9,18}\b'
    UPI_ID_PATTERN = r'\b[\w\.-]+@[\w\.-]+\b'
    PHONE_PATTERN = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}'
    URL_PATTERN = r'https?://[^\s]+'
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    # New patterns for enhanced extraction
    AMOUNT_PATTERN = r'(?:Rs\.?|₹|INR)\s*(\d+(?:,\d+)*(?:\.\d+)?)'
    EMPLOYEE_ID_PATTERN = r'(?:employee\s*id|emp\s*id|staff\s*id|emp\.?\s*no)[\s:]+([A-Z0-9]+)'

    # Company/Bank names
    BANK_NAMES = [
        'sbi', 'state bank', 'hdfc', 'icici', 'axis', 'pnb', 'punjab national',
        'kotak', 'bank of baroda', 'canara', 'union bank', 'yes bank', 'idbi'
    ]

    COMPANY_NAMES = [
        'paytm', 'phonepe', 'gpay', 'google pay', 'amazon', 'flipkart',
        'ola', 'uber', 'swiggy', 'zomato', 'irctc', 'aadhaar', 'income tax'
    ]

    # Suspicious keywords (expanded)
    SUSPICIOUS_KEYWORDS = [
        'urgent', 'immediately', 'verify', 'suspended', 'blocked', 'expire',
        'confirm', 'update', 'security', 'alert', 'limited time', 'act now',
        'click here', 'reset password', 'account locked', 'unauthorized',
        'refund', 'prize', 'winner', 'congratulations', 'claim', 'otp',
        'pin', 'cvv', 'card number', 'bank details', 'payment failed',
        'kyc', 'aadhaar', 'pan card', 'debit card', 'credit card',
        'transaction', 'transfer', 'won', 'lottery', 'cashback', 'reward'
    ]

    # Scam tactics
    URGENCY_INDICATORS = ['urgent', 'immediately', 'now', 'today', 'within', 'deadline']
    THREAT_INDICATORS = ['blocked', 'suspended', 'locked', 'terminated', 'frozen', 'cancelled']
    REWARD_INDICATORS = ['won', 'prize', 'reward', 'cashback', 'free', 'gift', 'lucky']

    def extract_intelligence(
        self,
        request: ConversationRequest,
        all_messages: List[Message]
    ) -> ExtractedIntelligence:
        """
        Extract comprehensive intelligence from conversation.

        Args:
            request: Current conversation request
            all_messages: All messages in the conversation

        Returns:
            Extracted intelligence data
        """
        logger.info(f"🔍 Enhanced intelligence extraction - Session: {request.sessionId}")

        # Combine all message texts
        all_text = " ".join([msg.text for msg in all_messages])
        scammer_messages = [msg.text for msg in all_messages if msg.sender == "scammer"]
        scammer_text = " ".join(scammer_messages)

        # Extract using regex patterns
        bank_accounts = self._extract_bank_accounts(all_text)
        upi_ids = self._extract_upi_ids(all_text)
        phishing_links = self._extract_urls(all_text)
        phone_numbers = self._extract_phone_numbers(all_text)
        emails = self._extract_emails(all_text)
        amounts = self._extract_amounts(all_text)
        employee_ids = self._extract_employee_ids(all_text)

        # Extract company/bank names
        impersonation_targets = self._extract_companies_banks(scammer_text)

        # Extract tactics used
        tactics = self._analyze_tactics(scammer_text)

        # Combine all findings
        suspicious_keywords = self._extract_keywords(all_text)
        suspicious_keywords.extend(tactics)  # Add tactics to keywords

        # Create intelligence object
        intelligence = ExtractedIntelligence(
            bankAccounts=bank_accounts,
            upiIds=upi_ids,
            phishingLinks=phishing_links,
            phoneNumbers=phone_numbers,
            suspiciousKeywords=list(set(suspicious_keywords)),  # Deduplicate
            emails=emails,
            amounts=amounts,
            employeeIds=employee_ids,
            impersonationTargets=impersonation_targets
        )

        logger.info(
            f"✅ Intelligence extracted - Session: {request.sessionId}, "
            f"Banks: {len(bank_accounts)}, UPI: {len(upi_ids)}, "
            f"Links: {len(phishing_links)}, Phones: {len(phone_numbers)}, "
            f"Emails: {len(emails)}, Amounts: {len(amounts)}, "
            f"Targets: {len(impersonation_targets)}, Keywords: {len(suspicious_keywords)}"
        )

        return intelligence

    def _extract_bank_accounts(self, text: str) -> List[str]:
        """Extract bank account numbers."""
        accounts = re.findall(self.BANK_ACCOUNT_PATTERN, text)
        # Filter out timestamps and other numbers
        valid_accounts = [acc for acc in accounts if 9 <= len(acc) <= 18]
        return list(set(valid_accounts))

    def _extract_upi_ids(self, text: str) -> List[str]:
        """Extract UPI IDs."""
        upi_ids = re.findall(self.UPI_ID_PATTERN, text)
        valid_upis = [
            upi for upi in upi_ids
            if any(provider in upi.lower() for provider in
                   ['paytm', 'phonepe', 'gpay', 'upi', 'ybl', 'okaxis', 'okhdfcbank', 'ibl', 'axl'])
            or '@' in upi
        ]
        return list(set(valid_upis))

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs/phishing links."""
        urls = re.findall(self.URL_PATTERN, text)
        return list(set(urls))

    def _extract_phone_numbers(self, text: str) -> List[str]:
        """Extract phone numbers."""
        phones = re.findall(self.PHONE_PATTERN, text)
        # Clean and validate
        valid_phones = []
        for phone in phones:
            cleaned = re.sub(r'\D', '', phone)
            if 10 <= len(cleaned) <= 15:
                valid_phones.append(phone.strip())
        return list(set(valid_phones))

    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses."""
        emails = re.findall(self.EMAIL_PATTERN, text)
        return list(set(emails))

    def _extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts."""
        amounts = []

        # Pattern 1: Rs.500, Rs 500, ₹500
        pattern1 = re.findall(r'(?:Rs\.?\s*|₹\s*)(\d+(?:,\d+)*(?:\.\d+)?)', text, re.IGNORECASE)
        amounts.extend([f"Rs.{amt}" for amt in pattern1])

        # Pattern 2: 500 rupees, 500 rs
        pattern2 = re.findall(r'(\d+(?:,\d+)*(?:\.\d+)?)\s*(?:rupees?|rs\.?|inr)', text, re.IGNORECASE)
        amounts.extend([f"Rs.{amt}" for amt in pattern2])

        return list(set(amounts))

    def _extract_employee_ids(self, text: str) -> List[str]:
        """Extract employee IDs or reference numbers."""
        # Pattern for employee IDs
        emp_ids = re.findall(self.EMPLOYEE_ID_PATTERN, text, re.IGNORECASE)

        # Also look for generic reference numbers
        ref_patterns = [
            r'(?:reference|ref|ticket|case)\s*(?:no|number|#)[\s:]*([A-Z0-9-]+)',
            r'\b([A-Z]{2,}\d{4,})\b'  # Format like EMP1234, REF12345
        ]

        for pattern in ref_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            emp_ids.extend(matches)

        return list(set(emp_ids))

    def _extract_companies_banks(self, text: str) -> List[str]:
        """Extract names of banks/companies being impersonated."""
        text_lower = text.lower()
        targets = []

        # Check for bank names
        for bank in self.BANK_NAMES:
            if bank in text_lower:
                targets.append(bank.upper())

        # Check for company names
        for company in self.COMPANY_NAMES:
            if company in text_lower:
                targets.append(company.title())

        return list(set(targets))

    def _analyze_tactics(self, text: str) -> List[str]:
        """Analyze scam tactics used."""
        text_lower = text.lower()
        tactics = []

        # Check for urgency tactics
        if any(word in text_lower for word in self.URGENCY_INDICATORS):
            tactics.append("URGENCY_TACTICS")

        # Check for threat tactics
        if any(word in text_lower for word in self.THREAT_INDICATORS):
            tactics.append("THREAT_TACTICS")

        # Check for reward tactics
        if any(word in text_lower for word in self.REWARD_INDICATORS):
            tactics.append("REWARD_TACTICS")

        # Check for credential requests
        credential_words = ['otp', 'pin', 'password', 'cvv', 'pan', 'aadhaar']
        if any(word in text_lower for word in credential_words):
            tactics.append("CREDENTIAL_REQUEST")

        # Check for payment redirection
        if 'transfer' in text_lower or 'send' in text_lower or 'pay' in text_lower:
            tactics.append("PAYMENT_REDIRECTION")

        return tactics

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
        Generate detailed summary notes about scammer behavior.
        """
        notes = []

        # Analyze tactics
        tactics_found = [kw for kw in intelligence.suspiciousKeywords
                        if kw.endswith('_TACTICS') or kw.endswith('_REQUEST') or kw.endswith('_REDIRECTION')]
        if tactics_found:
            notes.append(f"Tactics: {', '.join(tactics_found)}")

        # Impersonation
        if intelligence.impersonationTargets:
            notes.append(f"Impersonating: {', '.join(intelligence.impersonationTargets)}")

        # Payment info
        payment_methods = []
        if intelligence.bankAccounts:
            payment_methods.append(f"{len(intelligence.bankAccounts)} bank account(s)")
        if intelligence.upiIds:
            payment_methods.append(f"{len(intelligence.upiIds)} UPI ID(s)")
        if payment_methods:
            notes.append(f"Payment redirection: {', '.join(payment_methods)}")

        # Contact info extracted
        contacts = []
        if intelligence.phoneNumbers:
            contacts.append(f"{len(intelligence.phoneNumbers)} phone(s)")
        if intelligence.emails:
            contacts.append(f"{len(intelligence.emails)} email(s)")
        if contacts:
            notes.append(f"Contact info: {', '.join(contacts)}")

        # Links
        if intelligence.phishingLinks:
            notes.append(f"{len(intelligence.phishingLinks)} suspicious link(s)")

        # Amounts
        if intelligence.amounts:
            notes.append(f"Amounts mentioned: {', '.join(intelligence.amounts[:3])}")  # First 3

        # Employee IDs
        if intelligence.employeeIds:
            notes.append(f"Reference IDs: {', '.join(intelligence.employeeIds[:2])}")

        # Message count
        notes.append(f"{len(all_messages)} messages exchanged")

        return ". ".join(notes) if notes else "Scam conversation detected"
