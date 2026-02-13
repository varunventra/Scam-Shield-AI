"""
API routes for the Scambot Honeypot system.
"""
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import verify_api_key, verify_admin_key
from app.core.logging import logger
from app.models.requests import ConversationRequest, Message
from app.models.responses import ConversationResponse, FinalResultPayload
from app.services import ScamDetector, AIAgent, IntelligenceExtractor, CallbackHandler, ForensicReporter
from app.storage import session_manager
from app.storage.mongodb import (
    deduplicate_intelligence,
    find_repeat_matches,
    get_repeat_analysis,
    get_session_doc,
    search_sessions,
    upsert_session,
)
from app.utils import validate_session_id

# Create router
router = APIRouter()

# Initialize services
scam_detector = ScamDetector()
ai_agent = AIAgent()
intelligence_extractor = IntelligenceExtractor()
callback_handler = CallbackHandler()
forensic_reporter = ForensicReporter()


# ---------------------------------------------------------------------------
# Helper: build full conversation transcript from all sources
# ---------------------------------------------------------------------------

def _build_transcript(conversation_history, current_message, agent_reply: str) -> list:
    """
    Build an ordered conversation transcript:
      conversationHistory + latest scammer message + AI reply.
    """
    transcript = []
    for msg in conversation_history:
        transcript.append({
            "sender": msg.sender,
            "text": msg.text,
            "timestamp": msg.timestamp,
        })
    transcript.append({
        "sender": current_message.sender,
        "text": current_message.text,
        "timestamp": current_message.timestamp,
    })
    transcript.append({
        "sender": "user",
        "text": agent_reply,
        "timestamp": int(time.time() * 1000),
    })
    return transcript


# ===================================================================
# MAIN CONVERSATION ENDPOINT
# ===================================================================

@router.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(
    request: ConversationRequest,
    api_key: str = Depends(verify_api_key)
) -> ConversationResponse:
    """
    Main endpoint for handling incoming scam messages.

    Flow:
    1. Receives a message from the platform
    2. Detects scam intent
    3. Activates AI agent if scam detected
    4. Checks for repeat scammer and adapts behaviour
    5. Returns agent's response
    6. Extracts intelligence and sends callback when appropriate
    7. Persists everything to MongoDB (non-blocking on failure)
    """
    try:
        # Validate session ID
        if not validate_session_id(request.sessionId):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid session ID"
            )

        logger.info(
            f"Received message - Session: {request.sessionId}, "
            f"Sender: {request.message.sender}, "
            f"History length: {len(request.conversationHistory)}"
        )

        # Get or create session
        session = session_manager.get_or_create_session(request.sessionId)

        # Add current message to session
        session_manager.add_message_to_session(request.sessionId, request.message)

        # Check if agent is already activated for this session
        if not session.agent_activated:
            logger.info(f"First message - checking for scam - Session: {request.sessionId}")

            try:
                should_activate = await scam_detector.should_activate_agent(request)

                if should_activate:
                    is_scam, confidence, reasoning = await scam_detector.detect_scam(request)
                    session_manager.update_session(
                        request.sessionId,
                        scam_detected=is_scam,
                        scam_confidence=confidence,
                        agent_activated=True
                    )
                    logger.info(
                        f"Agent activated - Session: {request.sessionId}, "
                        f"Scam: {is_scam}, Confidence: {confidence:.2f}"
                    )
                else:
                    # HONEYPOT FAIL-OPEN
                    logger.info(
                        f"Low confidence - STILL ENGAGING (honeypot mode) - Session: {request.sessionId}"
                    )
                    session_manager.update_session(
                        request.sessionId,
                        scam_detected=False,
                        scam_confidence=0.3,
                        agent_activated=True
                    )

            except Exception as e:
                # CRITICAL FAIL-OPEN
                logger.error(
                    f"Scam detection FAILED - Session: {request.sessionId}, "
                    f"Error type: {type(e).__name__}, Message: {str(e)}"
                )
                logger.warning("FAIL-OPEN: Engaging anyway (honeypot behavior)")
                session_manager.update_session(
                    request.sessionId,
                    scam_detected=True,
                    scam_confidence=0.5,
                    agent_activated=True
                )

        # -----------------------------------------------------------------
        # REPEAT SCAMMER DETECTION (early pass for adaptive prompt)
        # -----------------------------------------------------------------
        repeat_info = None
        repeat_matches_for_prompt = None
        early_intel_dict = {}

        message_count = session.get_message_count()

        if message_count >= 2:
            try:
                early_intel = intelligence_extractor.extract_intelligence(request, session.messages)
                early_intel_dict = deduplicate_intelligence(early_intel.model_dump())

                repeat_info = await find_repeat_matches(request.sessionId, early_intel_dict)
                if repeat_info and repeat_info.get("repeatScammer"):
                    repeat_matches_for_prompt = repeat_info.get("repeatMatches")
                    logger.info(
                        f"REPEAT SCAMMER detected - Session: {request.sessionId}, "
                        f"matched sessions: {repeat_info.get('repeatSessionIds')}"
                    )
            except Exception as exc:
                logger.error(f"Early repeat detection failed (non-blocking): {exc}")

        # -----------------------------------------------------------------
        # GENERATE AGENT RESPONSE (with adaptive prompt if repeat scammer)
        # -----------------------------------------------------------------
        logger.info(f"Generating agent response - Session: {request.sessionId}")

        session_messages = session.messages
        logger.info(
            f"Session has {len(session_messages)} messages stored - "
            f"Session: {request.sessionId}"
        )

        agent_response = await ai_agent.generate_response(
            request,
            session_messages,
            repeat_matches=repeat_matches_for_prompt,
        )

        # Add agent's response to session history
        agent_message = Message(
            sender="user",
            text=agent_response,
            timestamp=int(time.time() * 1000)
        )
        session_manager.add_message_to_session(request.sessionId, agent_message)

        # -----------------------------------------------------------------
        # FULL INTELLIGENCE EXTRACTION (turn 3+)
        # -----------------------------------------------------------------
        intelligence = None
        agent_notes = ""
        should_end = await ai_agent.should_end_conversation(request)
        message_count = session.get_message_count()

        if message_count >= 3:
            all_messages = session.messages
            intelligence = intelligence_extractor.extract_intelligence(request, all_messages)
            agent_notes = intelligence_extractor.generate_agent_notes(
                request, all_messages, intelligence
            )
            session_manager.update_session(
                request.sessionId,
                intelligence=intelligence
            )

            # Re-run repeat detection with fuller intelligence
            try:
                intel_dict = deduplicate_intelligence(intelligence.model_dump())
                repeat_info = await find_repeat_matches(request.sessionId, intel_dict)
            except Exception as exc:
                logger.error(f"Repeat detection failed (non-blocking): {exc}")

        # -----------------------------------------------------------------
        # CALLBACK LOGIC
        # -----------------------------------------------------------------
        final_callback_payload_dict = None
        callback_sent = session.callback_sent
        callback_sent_at = None

        if intelligence is not None and message_count >= 3:
            should_send = await callback_handler.should_send_callback(
                request.sessionId,
                session.scam_detected,
                message_count,
                intelligence
            )

            safety_trigger = should_end and message_count >= 10 and intelligence is not None

            if (should_send or safety_trigger) and not session.callback_sent:
                final_payload = FinalResultPayload(
                    sessionId=request.sessionId,
                    scamDetected=session.scam_detected,
                    totalMessagesExchanged=message_count,
                    extractedIntelligence=intelligence,
                    agentNotes=agent_notes
                )
                final_callback_payload_dict = final_payload.model_dump()

                callback_success = await callback_handler.send_final_result(final_payload)

                if callback_success:
                    callback_sent = True
                    callback_sent_at = datetime.now(timezone.utc)
                    session_manager.update_session(
                        request.sessionId,
                        callback_sent=True
                    )

                # Generate forensic PDF report
                try:
                    report_path = forensic_reporter.generate_forensic_report(
                        session_id=request.sessionId,
                        extracted_intelligence=intelligence,
                        conversation_history=session.messages,
                        agent_notes=agent_notes,
                        scam_detected=session.scam_detected,
                        total_messages=message_count
                    )
                    if report_path:
                        logger.info(f"Forensic PDF report saved: {report_path}")
                except Exception as report_err:
                    logger.error(f"Forensic report generation failed (non-blocking): {report_err}")

        # -----------------------------------------------------------------
        # PERSIST TO MONGODB (non-blocking – DB failure never breaks API)
        # -----------------------------------------------------------------
        try:
            intel_dict_for_db = (
                intelligence.model_dump() if intelligence else early_intel_dict
            ) or {
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "phoneNumbers": [],
                "suspiciousKeywords": [],
            }

            transcript = _build_transcript(
                request.conversationHistory,
                request.message,
                agent_response,
            )

            metadata_dict = request.metadata.model_dump() if request.metadata else None

            await upsert_session(
                session_id=request.sessionId,
                scam_detected=session.scam_detected,
                total_messages=message_count,
                extracted_intelligence=intel_dict_for_db,
                agent_notes=agent_notes,
                metadata=metadata_dict,
                conversation_transcript=transcript,
                final_callback_payload=final_callback_payload_dict,
                callback_sent=callback_sent,
                callback_sent_at=callback_sent_at,
                repeat_info=repeat_info,
            )
        except Exception as db_err:
            logger.error(f"MongoDB persistence failed (non-blocking): {db_err}")

        # -----------------------------------------------------------------
        # RETURN RESPONSE (unchanged GUVI format)
        # -----------------------------------------------------------------
        return ConversationResponse(
            status="success",
            reply=agent_response
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error handling conversation - Session: {request.sessionId}, "
            f"Error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


# ===================================================================
# HEALTH CHECK
# ===================================================================

@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "scambot-honeypot",
        "active_sessions": session_manager.get_session_count()
    }


# ===================================================================
# ADMIN ENDPOINTS (secured with x-admin-key header)
# ===================================================================

@router.get("/admin/session/{session_id}")
async def admin_get_session(
    session_id: str,
    admin_key: str = Depends(verify_admin_key),
):
    """Fetch the full session record from MongoDB."""
    doc = await get_session_doc(session_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return doc


@router.get("/admin/repeats/{session_id}")
async def admin_get_repeats(
    session_id: str,
    admin_key: str = Depends(verify_admin_key),
):
    """Show repeat scammer analysis for a session."""
    doc = await get_repeat_analysis(session_id)
    if doc is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session {session_id} not found"
        )
    return doc


@router.get("/admin/search")
async def admin_search(
    phone: Optional[str] = Query(None),
    upi: Optional[str] = Query(None),
    account: Optional[str] = Query(None),
    link: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    admin_key: str = Depends(verify_admin_key),
):
    """Search sessions by extracted intelligence fields."""
    results = await search_sessions(
        phone=phone, upi=upi, account=account, link=link, keyword=keyword,
    )
    return {
        "status": "success",
        "count": len(results),
        "sessions": results,
    }


@router.post("/admin/cleanup")
async def cleanup_sessions(api_key: str = Depends(verify_api_key)):
    """Admin endpoint to cleanup expired in-memory sessions."""
    removed_count = session_manager.cleanup_expired_sessions()
    logger.info(f"Cleaned up {removed_count} expired sessions")
    return {
        "status": "success",
        "removed_sessions": removed_count,
        "active_sessions": session_manager.get_session_count()
    }
