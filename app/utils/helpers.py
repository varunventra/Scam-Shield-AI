"""
Utility helper functions.
"""
from typing import List
from app.models.requests import Message


def format_conversation_for_display(messages: List[Message]) -> str:
    """
    Format conversation messages for display.

    Args:
        messages: List of messages

    Returns:
        Formatted conversation string
    """
    if not messages:
        return "No messages"

    lines = []
    for msg in messages:
        sender_label = "Scammer" if msg.sender == "scammer" else "User"
        lines.append(f"{sender_label}: {msg.text}")

    return "\n".join(lines)


def sanitize_intelligence_data(data: dict) -> dict:
    """
    Sanitize intelligence data for logging.

    Args:
        data: Intelligence data dictionary

    Returns:
        Sanitized data
    """
    sanitized = data.copy()

    # Mask sensitive information for logs
    if 'bankAccounts' in sanitized:
        sanitized['bankAccounts'] = [
            f"****{acc[-4:]}" if len(acc) > 4 else "****"
            for acc in sanitized['bankAccounts']
        ]

    if 'phoneNumbers' in sanitized:
        sanitized['phoneNumbers'] = [
            f"****{phone[-4:]}" if len(phone) > 4 else "****"
            for phone in sanitized['phoneNumbers']
        ]

    return sanitized


def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID format.

    Args:
        session_id: Session identifier

    Returns:
        True if valid
    """
    if not session_id or not isinstance(session_id, str):
        return False

    stripped = session_id.strip()
    if not stripped or len(stripped) > 256:
        return False

    # Allow alphanumeric, hyphens, underscores, dots (UUID-compatible)
    import re
    return bool(re.match(r'^[a-zA-Z0-9_.\-]+$', stripped))
