"""
Language detection service.

Detects whether incoming scammer messages are in English, Hindi, or Telugu
and determines what language the agent should reply in.
"""
import re
from typing import Optional

from app.core.logging import logger


# Unicode ranges for script detection (fast, no external dep needed)
_DEVANAGARI_RE = re.compile(r"[\u0900-\u097F]")  # Hindi
_TELUGU_RE = re.compile(r"[\u0C00-\u0C7F]")       # Telugu

# Common Hindi words in Latin script (transliterated)
_HINDI_LATIN_MARKERS = [
    "kya", "hai", "nahi", "haan", "aap", "mera", "tera", "karo",
    "bhejo", "paisa", "bhai", "beta", "yaar", "abhi", "turant",
    "khata", "kholein", "rupaye", "didi", "amma", "sahab",
    "batao", "dijiye", "karein", "bhejiye", "kaise", "kyun",
]

SUPPORTED_LANGUAGES = {"english", "hindi", "telugu"}


def detect_language(
    message_text: str,
    metadata_language: Optional[str] = None,
) -> str:
    """
    Detect language from metadata or message text.

    Priority:
    1. metadata.language (if present and supported)
    2. Script-based detection (Devanagari → Hindi, Telugu script → Telugu)
    3. Transliterated Hindi marker words
    4. langdetect library (if installed)
    5. Default → English

    Returns one of: "english", "hindi", "telugu"
    """
    # 1. Metadata hint
    if metadata_language:
        normalized = metadata_language.strip().lower()
        if normalized in SUPPORTED_LANGUAGES:
            logger.debug(f"Language from metadata: {normalized}")
            return normalized
        # Map common variants
        mapping = {
            "en": "english", "eng": "english", "hi": "hindi",
            "hin": "hindi", "te": "telugu", "tel": "telugu",
        }
        if normalized in mapping:
            return mapping[normalized]

    text = message_text.strip()
    if not text:
        return "english"

    # 2. Script detection (most reliable)
    telugu_chars = len(_TELUGU_RE.findall(text))
    hindi_chars = len(_DEVANAGARI_RE.findall(text))
    total_alpha = max(len(re.findall(r"\w", text)), 1)

    if telugu_chars / total_alpha > 0.15:
        logger.debug(f"Telugu detected via script ({telugu_chars} chars)")
        return "telugu"

    if hindi_chars / total_alpha > 0.15:
        logger.debug(f"Hindi detected via script ({hindi_chars} chars)")
        return "hindi"

    # 3. Transliterated Hindi (Latin script)
    text_lower = text.lower()
    hindi_marker_hits = sum(1 for w in _HINDI_LATIN_MARKERS if w in text_lower)
    if hindi_marker_hits >= 2:
        logger.debug(f"Hindi detected via transliteration markers ({hindi_marker_hits} hits)")
        return "hindi"

    # 4. langdetect fallback
    try:
        from langdetect import detect as _ld_detect
        code = _ld_detect(text)
        ld_map = {"hi": "hindi", "te": "telugu", "en": "english"}
        if code in ld_map:
            logger.debug(f"Language from langdetect: {code}")
            return ld_map[code]
    except Exception:
        pass

    # 5. Default
    return "english"


def detect_response_language(
    detected_language: str,
    message_text: str,
) -> str:
    """
    Determine response language.

    If scammer mixes languages (e.g. Hindi + English), we respond in the
    same mix style – which effectively means replying in detected_language.
    """
    return detected_language
