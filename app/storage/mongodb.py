"""
MongoDB storage for persistent session data, repeat scammer detection,
and threat intelligence.
"""
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from app.core.config import settings
from app.core.logging import logger

# Motor (async MongoDB driver) - imported lazily so the app still starts
# even if MongoDB is unavailable.
_client = None
_db = None
_collection = None


async def get_collection():
    """
    Lazily initialise and return the ``scam_sessions`` collection.

    Returns ``None`` when no ``MONGODB_URI`` is configured so the rest of the
    app can degrade gracefully.
    """
    global _client, _db, _collection

    if _collection is not None:
        return _collection

    uri = settings.mongodb_uri
    if not uri:
        logger.warning("MONGODB_URI not set – running without persistent storage")
        return None

    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        _client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        # Ping to verify connectivity
        await _client.admin.command("ping")
        _db = _client["honeypot"]
        _collection = _db["scam_sessions"]

        # Ensure indexes for fast lookups
        await _collection.create_index("sessionId", unique=True)
        await _collection.create_index("extractedIntelligence.phoneNumbers")
        await _collection.create_index("extractedIntelligence.upiIds")
        await _collection.create_index("extractedIntelligence.bankAccounts")
        await _collection.create_index("extractedIntelligence.phishingLinks")
        await _collection.create_index("repeatScammer")
        await _collection.create_index("riskLevel")
        await _collection.create_index("scamType")
        await _collection.create_index("detectionMethod")

        logger.info("MongoDB connected – scam_sessions collection ready")
        return _collection
    except Exception as exc:
        logger.error(f"MongoDB connection failed: {exc}")
        _client = _db = _collection = None
        return None


# ---------------------------------------------------------------------------
# Normalisation helpers
# ---------------------------------------------------------------------------

def normalize_phone(phone: str) -> str:
    """Strip spaces/dashes, ensure +91 prefix for 10-digit Indian numbers."""
    cleaned = re.sub(r"[\s\-\.\(\)]+", "", phone)
    digits = re.sub(r"\D", "", cleaned)
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if len(digits) == 10:
        return f"+91{digits}"
    return cleaned


def normalize_upi(upi: str) -> str:
    return upi.strip().lower()


def normalize_link(link: str) -> str:
    return link.strip().rstrip("/").lower()


def extract_domain(link: str) -> str:
    """Return the domain from a URL for domain-level matching."""
    try:
        parsed = urlparse(link if "://" in link else f"https://{link}")
        return parsed.netloc.lower().lstrip("www.")
    except Exception:
        return link.strip().lower()


def deduplicate_intelligence(intel: Dict[str, Any]) -> Dict[str, Any]:
    """Deduplicate and normalise all extractedIntelligence arrays."""
    if not intel:
        return intel

    if "phoneNumbers" in intel:
        intel["phoneNumbers"] = list({normalize_phone(p) for p in intel["phoneNumbers"]})
    if "upiIds" in intel:
        intel["upiIds"] = list({normalize_upi(u) for u in intel["upiIds"]})
    if "phishingLinks" in intel:
        intel["phishingLinks"] = list({normalize_link(l) for l in intel["phishingLinks"]})
    if "bankAccounts" in intel:
        intel["bankAccounts"] = list(set(intel["bankAccounts"]))
    if "suspiciousKeywords" in intel:
        intel["suspiciousKeywords"] = list({k.lower().strip() for k in intel["suspiciousKeywords"]})
    return intel


# ---------------------------------------------------------------------------
# Repeat-scammer detection
# ---------------------------------------------------------------------------

async def find_repeat_matches(
    session_id: str,
    intelligence: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Search ALL other sessions for overlapping entities.

    Returns a dict with:
      - repeatScammer: bool
      - repeatMatches: {phoneNumbers: [...], upiIds: [...], ...}
      - repeatSessionIds: [...]
    """
    result = {
        "repeatScammer": False,
        "repeatMatches": {
            "phoneNumbers": [],
            "upiIds": [],
            "bankAccounts": [],
            "phishingLinks": [],
        },
        "repeatSessionIds": [],
    }

    col = await get_collection()
    if col is None:
        return result

    phones = intelligence.get("phoneNumbers", [])
    upis = intelligence.get("upiIds", [])
    accounts = intelligence.get("bankAccounts", [])
    links = intelligence.get("phishingLinks", [])
    # Also build domain list for domain-level matching
    domains = [extract_domain(l) for l in links if l]

    or_clauses: List[dict] = []
    if phones:
        or_clauses.append({"extractedIntelligence.phoneNumbers": {"$in": phones}})
    if upis:
        or_clauses.append({"extractedIntelligence.upiIds": {"$in": upis}})
    if accounts:
        or_clauses.append({"extractedIntelligence.bankAccounts": {"$in": accounts}})
    if links:
        or_clauses.append({"extractedIntelligence.phishingLinks": {"$in": links}})
    if domains:
        or_clauses.append({"extractedIntelligence.phishingDomains": {"$in": domains}})

    if not or_clauses:
        return result

    query = {
        "sessionId": {"$ne": session_id},
        "$or": or_clauses,
    }

    try:
        matched_session_ids = set()
        async for doc in col.find(query, {"sessionId": 1, "extractedIntelligence": 1}):
            other_id = doc["sessionId"]
            other_intel = doc.get("extractedIntelligence", {})

            matched_session_ids.add(other_id)

            # Find which entities matched
            for p in phones:
                if p in other_intel.get("phoneNumbers", []):
                    result["repeatMatches"]["phoneNumbers"].append(p)
            for u in upis:
                if u in other_intel.get("upiIds", []):
                    result["repeatMatches"]["upiIds"].append(u)
            for a in accounts:
                if a in other_intel.get("bankAccounts", []):
                    result["repeatMatches"]["bankAccounts"].append(a)
            for l_link in links:
                if l_link in other_intel.get("phishingLinks", []):
                    result["repeatMatches"]["phishingLinks"].append(l_link)
            # Domain-level
            for d in domains:
                if d in other_intel.get("phishingDomains", []):
                    # Add the original link that matched by domain
                    for orig in links:
                        if extract_domain(orig) == d:
                            result["repeatMatches"]["phishingLinks"].append(orig)

        # Deduplicate matches
        for key in result["repeatMatches"]:
            result["repeatMatches"][key] = list(set(result["repeatMatches"][key]))

        result["repeatSessionIds"] = list(matched_session_ids)
        result["repeatScammer"] = len(matched_session_ids) > 0
    except Exception as exc:
        logger.error(f"Repeat-scammer detection query failed: {exc}")

    return result


# ---------------------------------------------------------------------------
# Risk level
# ---------------------------------------------------------------------------

def compute_risk_level(
    repeat_scammer: bool,
    scam_detected: bool,
    rule_score: float = 0.0,
    ml_score: Optional[float] = None,
) -> str:
    if repeat_scammer:
        return "HIGH"
    if scam_detected and (rule_score >= 0.75 or (ml_score is not None and ml_score >= 0.8)):
        return "HIGH"
    if scam_detected:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# Upsert session document
# ---------------------------------------------------------------------------

async def upsert_session(
    session_id: str,
    scam_detected: bool,
    total_messages: int,
    extracted_intelligence: Dict[str, Any],
    agent_notes: str,
    metadata: Optional[Dict[str, Any]],
    conversation_transcript: List[Dict[str, Any]],
    final_callback_payload: Optional[Dict[str, Any]] = None,
    callback_sent: bool = False,
    callback_sent_at: Optional[datetime] = None,
    repeat_info: Optional[Dict[str, Any]] = None,
    detected_language: str = "english",
    response_language: str = "english",
    persona_selected: Optional[str] = None,
    persona_switch_history: Optional[List[str]] = None,
    rule_score: float = 0.0,
    ml_score: Optional[float] = None,
    scam_type: str = "UNKNOWN",
    detection_method: str = "none",
    detected_indicators: Optional[List[str]] = None,
    detected_identity_dict: Optional[Dict[str, Any]] = None,
) -> bool:
    """
    Upsert the full session record into MongoDB.

    Returns True on success, False on failure (never raises).
    """
    col = await get_collection()
    if col is None:
        return False

    now = datetime.now(timezone.utc)

    # Normalise + deduplicate intelligence before storage
    intel = deduplicate_intelligence(dict(extracted_intelligence))

    # Build domain array for domain-level repeat matching
    intel["phishingDomains"] = list({
        extract_domain(l) for l in intel.get("phishingLinks", []) if l
    })

    # Repeat scammer info
    repeat_scammer = (repeat_info or {}).get("repeatScammer", False)
    risk_level = compute_risk_level(repeat_scammer, scam_detected, rule_score, ml_score)

    update_doc: Dict[str, Any] = {
        "$set": {
            "scamDetected": scam_detected,
            "totalMessagesExchanged": total_messages,
            "extractedIntelligence": intel,
            "agentNotes": agent_notes,
            "metadata": metadata or {},
            "conversationTranscript": conversation_transcript,
            "updatedAt": now,
            "repeatScammer": repeat_scammer,
            "repeatMatches": (repeat_info or {}).get("repeatMatches", {}),
            "repeatSessionIds": (repeat_info or {}).get("repeatSessionIds", []),
            "riskLevel": risk_level,
            "detectedLanguage": detected_language,
            "responseLanguage": response_language,
            "personaSelected": persona_selected,
            "personaSwitchHistory": persona_switch_history or [],
            "ruleScore": rule_score,
            "mlScore": ml_score,
            "scamType": scam_type,
            "detectionMethod": detection_method,
            "detectedIndicators": detected_indicators or [],
            "detectedIdentity": detected_identity_dict or {},
        },
        "$setOnInsert": {
            "sessionId": session_id,
            "createdAt": now,
        },
    }

    if final_callback_payload is not None:
        update_doc["$set"]["finalCallbackPayload"] = final_callback_payload
    if callback_sent:
        update_doc["$set"]["callbackSent"] = True
        update_doc["$set"]["callbackSentAt"] = callback_sent_at or now
    else:
        # Don't overwrite an existing True with False
        update_doc["$set"].setdefault("callbackSent", False)

    try:
        await col.update_one(
            {"sessionId": session_id},
            update_doc,
            upsert=True,
        )
        logger.info(f"MongoDB upsert OK – session {session_id}")
        return True
    except Exception as exc:
        logger.error(f"MongoDB upsert failed – session {session_id}: {exc}")
        return False


# ---------------------------------------------------------------------------
# Admin query helpers
# ---------------------------------------------------------------------------

async def get_session_doc(session_id: str) -> Optional[Dict[str, Any]]:
    col = await get_collection()
    if col is None:
        return None
    doc = await col.find_one({"sessionId": session_id}, {"_id": 0})
    return doc


async def get_repeat_analysis(session_id: str) -> Optional[Dict[str, Any]]:
    col = await get_collection()
    if col is None:
        return None
    doc = await col.find_one(
        {"sessionId": session_id},
        {
            "_id": 0,
            "sessionId": 1,
            "repeatScammer": 1,
            "repeatMatches": 1,
            "repeatSessionIds": 1,
            "riskLevel": 1,
            "extractedIntelligence": 1,
        },
    )
    return doc


async def search_sessions(
    phone: Optional[str] = None,
    upi: Optional[str] = None,
    account: Optional[str] = None,
    link: Optional[str] = None,
    keyword: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search sessions by extracted intelligence fields."""
    col = await get_collection()
    if col is None:
        return []

    or_clauses: List[dict] = []
    if phone:
        normalized = normalize_phone(phone)
        or_clauses.append({"extractedIntelligence.phoneNumbers": normalized})
    if upi:
        or_clauses.append({"extractedIntelligence.upiIds": normalize_upi(upi)})
    if account:
        or_clauses.append({"extractedIntelligence.bankAccounts": account.strip()})
    if link:
        or_clauses.append({"extractedIntelligence.phishingLinks": normalize_link(link)})
        domain = extract_domain(link)
        if domain:
            or_clauses.append({"extractedIntelligence.phishingDomains": domain})
    if keyword:
        or_clauses.append({"extractedIntelligence.suspiciousKeywords": keyword.lower().strip()})

    if not or_clauses:
        return []

    query = {"$or": or_clauses}
    results = []
    try:
        async for doc in col.find(query, {
            "_id": 0,
            "sessionId": 1,
            "scamDetected": 1,
            "totalMessagesExchanged": 1,
            "riskLevel": 1,
            "repeatScammer": 1,
            "extractedIntelligence": 1,
            "createdAt": 1,
            "updatedAt": 1,
        }).limit(50):
            results.append(doc)
    except Exception as exc:
        logger.error(f"MongoDB search failed: {exc}")

    return results
