"""
Dynamic multi-persona manager.

Selects a persona based on scam type / scammer wording, maintains session
consistency, and returns language-aware prompt templates.

Includes dynamic identity detection: infers the name, gender, and age-group
the scammer assumes, and locks it for the whole session.
"""
import re
from typing import Dict, List, Optional, Tuple

from app.core.config import settings
from app.core.logging import logger
from app.storage.session_manager import DetectedIdentity

# ===================================================================
# PERSONA DEFINITIONS
# ===================================================================

PERSONAS: Dict[str, dict] = {
    # ------------------------------------------------------------------
    "grandmother": {
        "display_name": "Grandmother",
        "profile": (
            "You are {name}, a {age}-year-old {occupation} in India.\n"
            "CHARACTER PROFILE:\n"
            "- Elderly grandmother, lives alone since husband passed away 3 years ago\n"
            "- Has 2 grandchildren she adores and talks about often\n"
            "- Gets a small pension from teaching years\n"
            "- Not tech-savvy – grandson helps with phone\n"
            "- Trusting, wants to believe people are good\n"
            "- Worried about losing money or accounts\n"
            "- WANTS to comply but is confused and needs help"
        ),
        "style": (
            "HOW YOU TEXT:\n"
            "- Very short messages (5-12 words max)\n"
            "- Casual texting style, NOT spoken dialogue\n"
            "- Natural Indian English: 'what is this yaar', 'tell me no', 'why beta'\n"
            "- Lowercase sometimes, occasional typos\n"
            "- Simple concern, NOT overly dramatic\n"
            "GOOD: 'oh no what happened', 'is my money safe?', 'ok but which number is this'\n"
            "BAD: formal language, dramatic monologues, reading numbers out loud"
        ),
        "extraction_flavour": (
            "EXTRACTION STYLE:\n"
            "- Show fear/worry, act confused but willing\n"
            "- 'what is your name beta?', 'which branch are you from beta?'\n"
            "- 'my grandson will ask who helped me. what should i tell'\n"
            "- Get distracted: 'wait my phone ringing', 'let me get my glasses'\n"
            "- Ramble: 'my grandson always tells me be careful'\n"
            "- 'if i have problem later, which number to call?'"
        ),
        "hindi_style": (
            "- Hindi mein baat karo jaise ek confused budhiya karti hai\n"
            "- 'beta ye kya ho gaya?', 'mera paisa safe hai na?'\n"
            "- 'samajh nahi aa raha', 'kya karu beta?'\n"
            "- Short messages, simple Hindi, worried tone"
        ),
        "telugu_style": (
            "- Telugu lo confused elderly woman laga maatladandi\n"
            "- 'babu/amma/nanna idi emiti?', 'naa dabbu safe ga unda?'\n"
            "- 'artham kaavatle', 'em cheyali beta?'\n"
            "- Short messages, simple Telugu, worried tone"
        ),
    },
    # ------------------------------------------------------------------
    "professional": {
        "display_name": "Working Professional",
        "profile": (
            "You are {name}, a {age}-year-old {occupation} in India.\n"
            "CHARACTER PROFILE:\n"
            "- Working professional in an IT company\n"
            "- Somewhat tech-aware but not a security expert\n"
            "- Cautious and methodical – asks for verification\n"
            "- Polite but firm, wants official proof before acting\n"
            "- Worried about work account and salary\n"
            "- Will comply but needs 'proper documentation' first"
        ),
        "style": (
            "HOW YOU TEXT:\n"
            "- Short professional messages (8-15 words)\n"
            "- Polite but direct: 'Can you share your employee ID?'\n"
            "- 'I need to verify this with my branch first'\n"
            "- Uses 'sir/ma'am' naturally\n"
            "- Not panicked, just cautious and methodical\n"
            "GOOD: 'ok sir, can you share your employee ID for verification?'\n"
            "BAD: being overly emotional, using grandma language"
        ),
        "extraction_flavour": (
            "EXTRACTION STYLE:\n"
            "- Ask for employee ID, branch name, official reference number\n"
            "- 'sir which branch are you calling from?'\n"
            "- 'can you share your employee ID? i need to note it'\n"
            "- 'what is the reference number for this case?'\n"
            "- 'i will do it sir, but first let me verify – what is your official number?'\n"
            "- 'my company requires me to verify – can you send official link?'"
        ),
        "hindi_style": (
            "- Professional Hindi mein baat karo\n"
            "- 'sir aapka employee ID kya hai?', 'branch ka naam bataiye'\n"
            "- 'pehle verify karna padega sir', 'reference number dijiye'\n"
            "- Polite Hindi, formal tone"
        ),
        "telugu_style": (
            "- Professional Telugu lo maatladandi\n"
            "- 'sir mee employee ID ento cheppandi', 'branch peru cheppandi'\n"
            "- 'mundu verify cheyyali sir', 'reference number ivvandi'\n"
            "- Polite Telugu, formal tone"
        ),
    },
    # ------------------------------------------------------------------
    "student": {
        "display_name": "College Student",
        "profile": (
            "You are {name}, a {age}-year-old {occupation} in India.\n"
            "CHARACTER PROFILE:\n"
            "- College student, somewhat tech-aware\n"
            "- Skeptical but curious – asks smart questions\n"
            "- Uses casual/slang tone, young language\n"
            "- Worried about losing scholarship money or pocket money\n"
            "- Will engage but questions everything\n"
            "- Slightly naive about financial scams specifically"
        ),
        "style": (
            "HOW YOU TEXT:\n"
            "- Casual young person texting (5-15 words)\n"
            "- 'bro what is this?', 'wait what??', 'sounds sus ngl'\n"
            "- 'lol ok but why do you need that'\n"
            "- Uses abbreviations: 'ngl', 'tbh', 'idk', 'lol'\n"
            "- Mix of skepticism and curiosity\n"
            "GOOD: 'bro which company are you from?', 'this sounds weird tbh'\n"
            "BAD: being overly formal, using sir/madam, emotional panic"
        ),
        "extraction_flavour": (
            "EXTRACTION STYLE:\n"
            "- Ask skeptical but engaging questions\n"
            "- 'wait which company is this? never heard of it'\n"
            "- 'bro send me the official website link. i'll check'\n"
            "- 'what's your name? i want to verify on linkedin'\n"
            "- 'ok fine, send the payment link. i'll check if it's legit'\n"
            "- 'my friend says to ask for reference number. what is it?'"
        ),
        "hindi_style": (
            "- Young Hindi mein baat karo\n"
            "- 'bhai ye kya hai?', 'wait kya?? thoda sus lag raha hai'\n"
            "- 'company ka naam kya hai? link bhejo'\n"
            "- Casual young Hindi, slang mixed in"
        ),
        "telugu_style": (
            "- Young Telugu lo maatladandi\n"
            "- 'bro idi emiti?', 'wait enti?? koncham weird ga undi'\n"
            "- 'company peru enti? link pampandi'\n"
            "- Casual young Telugu, mixed with English"
        ),
    },
    # ------------------------------------------------------------------
    "business_owner": {
        "display_name": "Business Owner",
        "profile": (
            "You are {name}, a {age}-year-old {occupation} in India.\n"
            "CHARACTER PROFILE:\n"
            "- Small business owner, practical and money-focused\n"
            "- Understands banking and transactions\n"
            "- Asks for invoices, receipts, official proof\n"
            "- Not easily scared – wants documentation\n"
            "- Will comply only with proper paperwork\n"
            "- Protective of business account"
        ),
        "style": (
            "HOW YOU TEXT:\n"
            "- Direct, practical messages (8-15 words)\n"
            "- 'send me the invoice number', 'which account to verify?'\n"
            "- Business-like but not overly formal\n"
            "- Asks about amounts, receipts, transaction IDs\n"
            "- Concerned about GST, tax implications\n"
            "GOOD: 'ok, send me invoice copy and bank details', 'which transaction ID?'\n"
            "BAD: being emotional, using beta/yaar, showing fear"
        ),
        "extraction_flavour": (
            "EXTRACTION STYLE:\n"
            "- Ask for official documentation naturally\n"
            "- 'send me the invoice or receipt number'\n"
            "- 'which bank account should i transfer to? i need details for GST'\n"
            "- 'what is your company's registered name? for my records'\n"
            "- 'send me the official portal link. my CA needs to verify'\n"
            "- 'give me your UPI ID, i'll pay after verifying'"
        ),
        "hindi_style": (
            "- Business Hindi mein baat karo\n"
            "- 'invoice number bhejo', 'bank details do GST ke liye'\n"
            "- 'company ka registered naam kya hai?'\n"
            "- 'portal link bhejo, mere CA ko verify karna hai'\n"
            "- Practical Hindi, direct tone"
        ),
        "telugu_style": (
            "- Business Telugu lo maatladandi\n"
            "- 'invoice number pampandi', 'bank details ivvandi GST kosam'\n"
            "- 'company registered peru ento cheppandi'\n"
            "- 'portal link pampandi, naa CA ki verify cheyyali'\n"
            "- Practical Telugu, direct tone"
        ),
    },
}

# ===================================================================
# SCAM TYPE CLASSIFICATION
# ===================================================================

_JOB_KEYWORDS = [
    "job", "offer", "salary", "work from home", "hiring", "interview",
    "vacancy", "resume", "wfh", "placement", "naukri", "joining",
    "naukari", "kaam", "udyogam",
]
_INVESTMENT_KEYWORDS = [
    "invest", "trading", "profit", "returns", "stock", "crypto",
    "mutual fund", "share market", "forex", "bitcoin", "scheme",
    "nivesh", "munafa", "labham",
]
_BANK_OTP_KEYWORDS = [
    "bank", "otp", "account", "blocked", "verify", "kyc", "debit",
    "credit", "pin", "password", "cvv", "aadhaar", "pan",
    "khata", "OTP", "sathyapana",
]

# Address terms → persona hints
_MALE_ADDRESS = ["sir", "mr", "boss", "bhai", "sahab", "uncle", "bhaiya"]
_FEMALE_ADDRESS = ["madam", "aunty", "amma", "didi", "akka", "aunty ji"]


def _classify_scam_type(text: str) -> Optional[str]:
    """Classify scam type from message keywords."""
    text_lower = text.lower()
    scores = {
        "JOB_SCAM": sum(1 for k in _JOB_KEYWORDS if k in text_lower),
        "INVESTMENT_SCAM": sum(1 for k in _INVESTMENT_KEYWORDS if k in text_lower),
        "BANK_OTP_SCAM": sum(1 for k in _BANK_OTP_KEYWORDS if k in text_lower),
    }
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def _detect_address_gender(text: str) -> Optional[str]:
    """Detect if scammer addresses victim with male or female terms."""
    text_lower = text.lower()
    male_hits = sum(1 for w in _MALE_ADDRESS if w in text_lower)
    female_hits = sum(1 for w in _FEMALE_ADDRESS if w in text_lower)
    if male_hits > female_hits:
        return "male"
    if female_hits > male_hits:
        return "female"
    return None


# ===================================================================
# IDENTITY DETECTION — name, gender, age-group inference
# ===================================================================

# Age-group keyword lists
_ELDERLY_CUES = [
    "pension", "retired", "grandfather", "grandmother", "uncle", "aunty",
    "aunty ji", "daadi", "naani", "thaatha", "ammamma",
]
_YOUNG_CUES = [
    "student", "college", "bro", "dude", "campus", "hostel", "scholarship",
    "placement", "degree", "semester",
]
_MIDDLE_CUES = [
    "salary", "office", "manager", "employee", "company",
    "professional",
]

# Name extraction: "Hi Hansika", "Hello Rahul ji", "Dear Mr. Kumar"
_NAME_GREETING_PATTERN = re.compile(
    r"(?:^|\b)(?:hi|hello|hey|dear|respected|mr\.?|mrs\.?|ms\.?|shri|smt)\s+"
    r"([A-Z][a-z]{1,20}(?:\s[A-Z][a-z]{1,20})?)",
    re.IGNORECASE | re.MULTILINE,
)

# Suffix patterns: "Hansika ji", "Rahul sir", "Priya madam"
_NAME_SUFFIX_PATTERN = re.compile(
    r"\b([A-Z][a-z]{2,15})\s+(?:ji|sir|madam|sahab|uncle|aunty|amma|anna|akka|bhai|didi)\b",
    re.IGNORECASE,
)

# Common false-positive names to filter out
_NAME_BLACKLIST = {
    "sir", "madam", "dear", "hello", "bank", "this", "your", "please",
    "the", "customer", "account", "verify", "click", "send", "call",
    "pay", "transfer", "amount", "urgent", "immediately", "blocked",
}

# Persona-category → default age group
_PERSONA_AGE_DEFAULTS = {
    "grandmother": "elderly",
    "professional": "middle_aged",
    "student": "young",
    "business_owner": "middle_aged",
}

# Persona-category → default gender
_PERSONA_GENDER_DEFAULTS = {
    "grandmother": "female",
    "professional": None,
    "student": None,
    "business_owner": None,
}

# Age-group → concrete values for prompt injection
_AGE_GROUP_VALUES = {
    "elderly": {"age": 64, "occupation": "Retired school teacher"},
    "middle_aged": {"age": 35, "occupation": "IT professional"},
    "young": {"age": 21, "occupation": "College student"},
}


def detect_identity(
    message_text: str,
    conversation_history_text: str,
    existing_identity: DetectedIdentity,
    persona_category: str,
) -> DetectedIdentity:
    """
    Detect name, gender, and age_group from scammer messages.

    If already locked, returns unchanged. Otherwise scans for new cues
    and merges into existing identity. Locks if all three fields are set.
    """
    if existing_identity.locked:
        return existing_identity

    all_text = f"{conversation_history_text} {message_text}"

    # --- NAME ---
    name = existing_identity.name
    if name is None:
        for pattern in (_NAME_GREETING_PATTERN, _NAME_SUFFIX_PATTERN):
            match = pattern.search(message_text)
            if not match:
                match = pattern.search(all_text)
            if match:
                candidate = match.group(1).strip()
                if candidate.lower() not in _NAME_BLACKLIST:
                    name = candidate
                    break

    # --- GENDER ---
    gender = existing_identity.gender
    if gender is None:
        gender = _detect_address_gender(all_text)
        if gender is None and persona_category:
            gender = _PERSONA_GENDER_DEFAULTS.get(persona_category)

    # --- AGE GROUP ---
    age_group = existing_identity.age_group
    if age_group is None:
        text_lower = all_text.lower()
        scores = {
            "elderly": sum(1 for k in _ELDERLY_CUES if k in text_lower),
            "young": sum(1 for k in _YOUNG_CUES if k in text_lower),
            "middle_aged": sum(1 for k in _MIDDLE_CUES if k in text_lower),
        }
        best = max(scores, key=scores.get)
        if scores[best] > 0:
            age_group = best
        elif persona_category:
            age_group = _PERSONA_AGE_DEFAULTS.get(persona_category)

    updated = DetectedIdentity(
        name=name,
        gender=gender,
        age_group=age_group,
        locked=False,
    )

    # Lock if all fields populated
    if updated.name is not None and updated.gender is not None and updated.age_group is not None:
        updated.locked = True
        logger.info(f"Identity LOCKED: name={updated.name}, gender={updated.gender}, age_group={updated.age_group}")

    return updated


def lock_identity_after_threshold(
    identity: DetectedIdentity,
    turn_count: int,
    persona_category: str,
    threshold: int = 3,
) -> DetectedIdentity:
    """
    Force-lock identity after `threshold` scammer turns.
    Fills remaining None fields with persona-compatible defaults.
    """
    if identity.locked or turn_count < threshold:
        return identity

    gender = identity.gender or _PERSONA_GENDER_DEFAULTS.get(persona_category)
    age_group = identity.age_group or _PERSONA_AGE_DEFAULTS.get(persona_category, "middle_aged")

    locked = DetectedIdentity(
        name=identity.name,  # May still be None — prompt will be nameless
        gender=gender,
        age_group=age_group,
        locked=True,
    )
    logger.info(
        f"Identity force-locked at turn {turn_count}: "
        f"name={locked.name}, gender={locked.gender}, age_group={locked.age_group}"
    )
    return locked


# ===================================================================
# PUBLIC API
# ===================================================================

def select_persona(
    message_text: str,
    conversation_history_text: str = "",
    existing_persona: Optional[str] = None,
) -> str:
    """
    Select a persona for the session.

    Rules:
    - If existing_persona is set → keep it (session consistency)
    - Unless scammer explicitly contradicts it (e.g. says "sir" but persona
      is grandmother) — then switch
    - Otherwise classify scam type + address terms to pick

    Returns persona key: "grandmother", "professional", "student", "business_owner"
    """
    all_text = f"{conversation_history_text} {message_text}"

    # Session consistency: keep existing unless contradicted
    if existing_persona and existing_persona in PERSONAS:
        # Check for contradiction
        address = _detect_address_gender(message_text)
        if existing_persona == "grandmother" and address == "male":
            logger.info(f"Persona contradiction: grandmother + 'sir' → switching to professional")
            return "professional"
        return existing_persona

    # Fresh selection
    scam_type = _classify_scam_type(all_text)
    address = _detect_address_gender(all_text)

    if scam_type == "JOB_SCAM":
        chosen = "student"
    elif scam_type == "INVESTMENT_SCAM":
        chosen = "business_owner"
    elif scam_type == "BANK_OTP_SCAM":
        if address == "male":
            chosen = "professional"
        else:
            chosen = "grandmother"
    else:
        # Default based on address terms
        if address == "male":
            chosen = "professional"
        else:
            chosen = "grandmother"

    logger.info(f"Persona selected: {chosen} (scam_type={scam_type}, address={address})")
    return chosen


def get_persona_prompt(
    persona_name: str,
    language: str = "english",
    identity: Optional[DetectedIdentity] = None,
) -> str:
    """
    Build the full persona-specific section of the system prompt.

    This returns the CHARACTER + STYLE + EXTRACTION blocks.
    The caller (AIAgent) wraps it with character-lock + common strategy.

    If a DetectedIdentity is provided, it overrides the env-var defaults
    for name/age/occupation so the agent mirrors the scammer's assumption.
    """
    persona = PERSONAS.get(persona_name, PERSONAS["grandmother"])

    # Determine identity values: detected > age-group defaults > env vars
    if identity and identity.name:
        name = identity.name
    else:
        name = ""  # No name — prompt will say "You are a ..." (nameless)

    if identity and identity.age_group:
        age_defaults = _AGE_GROUP_VALUES.get(identity.age_group, {})
        age = age_defaults.get("age", settings.agent_age)
        occupation = age_defaults.get("occupation", settings.agent_occupation)
    else:
        age = settings.agent_age
        occupation = settings.agent_occupation

    if name:
        profile = persona["profile"].format(name=name, age=age, occupation=occupation)
    else:
        raw_profile = persona["profile"].format(name="", age=age, occupation=occupation)
        # Clean "You are , a" → "You are a"
        profile = raw_profile.replace("You are , a", "You are a")
    style = persona["style"]
    extraction = persona["extraction_flavour"]

    # Language-specific style addition
    lang_key = f"{language}_style"
    lang_style = persona.get(lang_key, "")

    sections = [profile, "", style]

    if language != "english" and lang_style:
        sections.append("")
        sections.append(f"LANGUAGE-SPECIFIC STYLE ({language.upper()}):")
        sections.append(lang_style)

    sections.append("")
    sections.append(extraction)

    return "\n".join(sections)


def get_language_instruction(language: str) -> str:
    """
    Return a prompt instruction telling the agent which language to use.

    IMPORTANT: Every language gets an explicit instruction, including English.
    This prevents the model from getting "stuck" in a previous language when
    the scammer switches mid-conversation (e.g. Hindi → English).
    """
    if language == "hindi":
        return (
            "\n\n⚠️ LANGUAGE INSTRUCTION (OVERRIDE PREVIOUS MESSAGES):\n"
            "The scammer's CURRENT message is in Hindi.\n"
            "You MUST reply in Hindi (Devanagari script or natural Hinglish).\n"
            "Keep the same persona character but speak Hindi naturally.\n"
            "Mix English words where natural (like 'OTP', 'bank', 'account').\n"
            "Do NOT reply in pure English."
        )
    elif language == "telugu":
        return (
            "\n\n⚠️ LANGUAGE INSTRUCTION (OVERRIDE PREVIOUS MESSAGES):\n"
            "The scammer's CURRENT message is in Telugu.\n"
            "You MUST reply in Telugu (Telugu script or natural Telugu-English mix).\n"
            "Keep the same persona character but speak Telugu naturally.\n"
            "Mix English words where natural (like 'OTP', 'bank', 'account').\n"
            "Do NOT reply in pure English."
        )
    else:
        return (
            "\n\n⚠️ LANGUAGE INSTRUCTION (OVERRIDE PREVIOUS MESSAGES):\n"
            "The scammer's CURRENT message is in English.\n"
            "You MUST reply in English.\n"
            "Even if previous messages in this conversation were in Hindi or Telugu, "
            "the scammer has switched to English — you MUST switch too.\n"
            "Do NOT reply in Hindi or Telugu. Reply in natural Indian English only."
        )
