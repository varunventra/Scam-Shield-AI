"""
API routes for the Scambot Honeypot system.
"""
import re
import time
from datetime import datetime, timezone
from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from app.core.security import verify_api_key, verify_admin_key
from app.core.logging import logger
from app.models.requests import ConversationRequest, Message
from app.models.responses import ConversationResponse, EngagementMetrics, FinalResultPayload
from app.services import (
    ScamDetector, AIAgent, IntelligenceExtractor, CallbackHandler, ForensicReporter,
    detect_language, detect_response_language, select_persona, get_persona_prompt,
    detect_identity, lock_identity_after_threshold,
)
from app.services.conversation_strategy import ConversationStrategy
from app.services.scam_detector import DetectionResult
from app.storage import session_manager
from app.storage.mongodb import (
    deduplicate_intelligence,
    find_repeat_matches,
    get_repeat_analysis,
    get_session_doc,
    search_sessions,
    upsert_session,
)
from app.storage.pdf_storage import store_pdf, retrieve_pdf_by_session, check_pdf_exists
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
        detection_result: Optional[DetectionResult] = None

        if not session.agent_activated:
            logger.info(f"First message - checking for scam - Session: {request.sessionId}")

            try:
                should_activate, detection_result = await scam_detector.should_activate_agent(request)

                if should_activate:
                    session_manager.update_session(
                        request.sessionId,
                        scam_detected=detection_result.is_scam,
                        scam_confidence=detection_result.final_confidence,
                        agent_activated=True,
                        rule_score=detection_result.rule_score,
                        ml_score=detection_result.ml_score,
                        scam_type=detection_result.scam_type,
                        detection_method=detection_result.detection_method,
                        detected_indicators=detection_result.detected_indicators,
                    )
                    logger.info(
                        f"Agent activated - Session: {request.sessionId}, "
                        f"Scam: {detection_result.is_scam}, "
                        f"Confidence: {detection_result.final_confidence:.2f}, "
                        f"Method: {detection_result.detection_method}, "
                        f"Type: {detection_result.scam_type}"
                    )
                else:
                    # HONEYPOT FAIL-OPEN
                    logger.info(
                        f"Low confidence - STILL ENGAGING (honeypot mode) - Session: {request.sessionId}"
                    )
                    session_manager.update_session(
                        request.sessionId,
                        scam_detected=False,
                        scam_confidence=detection_result.final_confidence,
                        agent_activated=True,
                        rule_score=detection_result.rule_score,
                        ml_score=detection_result.ml_score,
                        scam_type=detection_result.scam_type,
                        detection_method=detection_result.detection_method,
                        detected_indicators=detection_result.detected_indicators,
                    )

            except Exception as e:
                # CRITICAL FAIL-OPEN
                logger.error(
                    f"Scam detection FAILED - Session: {request.sessionId}, "
                    f"Error type: {type(e).__name__}, Message: {str(e)}"
                )
                logger.warning("FAIL-OPEN: Engaging anyway (honeypot behavior)")
                detection_result = DetectionResult(
                    is_scam=True,
                    final_confidence=0.5,
                    reasoning=f"Detection failed: {type(e).__name__}. FAIL-OPEN.",
                    detection_method="fail_open",
                )
                session_manager.update_session(
                    request.sessionId,
                    scam_detected=True,
                    scam_confidence=0.5,
                    agent_activated=True,
                    detection_method="fail_open",
                )

        # -----------------------------------------------------------------
        # LANGUAGE DETECTION + PERSONA SELECTION
        # -----------------------------------------------------------------
        metadata_language = None
        if request.metadata and hasattr(request.metadata, "language"):
            metadata_language = request.metadata.language

        detected_lang = detect_language(request.message.text, metadata_language)
        response_lang = detect_response_language(detected_lang, request.message.text)

        # Build conversation history text for persona selection context
        history_text = " ".join(
            msg.text for msg in request.conversationHistory
        ) if request.conversationHistory else ""

        chosen_persona = select_persona(
            message_text=request.message.text,
            conversation_history_text=history_text,
            existing_persona=session.persona_selected,
        )

        # -----------------------------------------------------------------
        # IDENTITY DETECTION + LOCKING
        # -----------------------------------------------------------------
        existing_identity = session.detected_identity

        if not existing_identity.locked:
            updated_identity = detect_identity(
                message_text=request.message.text,
                conversation_history_text=history_text,
                existing_identity=existing_identity,
                persona_category=chosen_persona,
            )
            # Force-lock after 3 scammer turns
            scammer_turn_count = len([
                m for m in session.messages if m.sender != "user"
            ])
            updated_identity = lock_identity_after_threshold(
                identity=updated_identity,
                turn_count=scammer_turn_count,
                persona_category=chosen_persona,
            )
        else:
            updated_identity = existing_identity

        # Build persona prompt with detected identity
        persona_prompt = get_persona_prompt(chosen_persona, response_lang, identity=updated_identity)

        # Persist language + persona + identity to in-memory session
        session_manager.update_session(
            request.sessionId,
            detected_language=detected_lang,
            response_language=response_lang,
            persona_selected=chosen_persona,
            detected_identity=updated_identity,
        )

        logger.info(
            f"Language: {detected_lang}, Persona: {chosen_persona}, "
            f"Identity: name={updated_identity.name}, gender={updated_identity.gender}, "
            f"age_group={updated_identity.age_group}, locked={updated_identity.locked} - "
            f"Session: {request.sessionId}"
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
        # INITIALIZE/RETRIEVE CONVERSATION STRATEGY
        # -----------------------------------------------------------------
        if session.conversation_strategy is None:
            session.conversation_strategy = ConversationStrategy()
            logger.info(f"Initialized conversation strategy - Session: {request.sessionId}")

        # -----------------------------------------------------------------
        # GENERATE AGENT RESPONSE (with strategic extraction guidance)
        # -----------------------------------------------------------------
        logger.info(f"Generating agent response - Session: {request.sessionId}")

        session_messages = session.messages
        logger.info(
            f"Session has {len(session_messages)} messages stored - "
            f"Session: {request.sessionId}"
        )

        # Pass extracted intelligence to strategy for informed extraction
        known_intel = early_intel_dict if early_intel_dict else {}

        agent_response = await ai_agent.generate_response(
            request,
            session_messages,
            repeat_matches=repeat_matches_for_prompt,
            persona_prompt=persona_prompt,
            known_intelligence=known_intel,
            language=response_lang,
            identity=updated_identity,
            conversation_strategy=session.conversation_strategy,
        )

        # Add agent's response to session history
        agent_message = Message(
            sender="user",
            text=agent_response,
            timestamp=int(time.time() * 1000)
        )
        session_manager.add_message_to_session(request.sessionId, agent_message)

       
        # -----------------------------------------------------------------
        # FULL INTELLIGENCE EXTRACTION + FORENSIC REPORT (turn 3+)
        # -----------------------------------------------------------------
        intelligence = None
        agent_notes = ""
        message_count = session.get_message_count()

        if message_count >= 3 and session.scam_detected:
            all_messages = session.messages

            intelligence = intelligence_extractor.extract_intelligence(request, all_messages)

            agent_notes = intelligence_extractor.generate_agent_notes(
                request, all_messages, intelligence
            )

            # Save intelligence in memory
            session_manager.update_session(
                request.sessionId,
                intelligence=intelligence
            )

            # Re-run repeat detection with full intelligence
            try:
                intel_dict = deduplicate_intelligence(intelligence.model_dump())
                repeat_info = await find_repeat_matches(request.sessionId, intel_dict)
            except Exception as exc:
                logger.error(f"Repeat detection failed (non-blocking): {exc}")

            # Generate forensic PDF report and store in MongoDB
            # Strategy: Generate at message 3, then update every 3 messages (6, 9, 12, etc.)
            pdf_file_id = None
            pdf_case_id = None
            pdf_generated = False
            pdf_generated_at = None

            # Determine if we should generate/update PDF
            # Generate: First time at message 3
            # Update: Every 3 messages after that (6, 9, 12, 15, etc.)
            should_generate_pdf = (message_count == 3)  # First generation
            should_update_pdf = (message_count > 3 and message_count % 3 == 0)  # Periodic updates

            if should_generate_pdf or should_update_pdf:
                try:
                    # Check if PDF already exists
                    pdf_exists = await check_pdf_exists(request.sessionId)

                    if should_generate_pdf and not pdf_exists:
                        logger.info(
                            f"Generating initial PDF for session {request.sessionId} "
                            f"(Message count: {message_count})"
                        )
                    elif should_update_pdf and pdf_exists:
                        logger.info(
                            f"Updating PDF for session {request.sessionId} "
                            f"(Message count: {message_count}) - Deleting old PDF"
                        )
                        # Delete old PDF before creating new one
                        from app.storage.mongodb import get_session_doc
                        old_doc = await get_session_doc(request.sessionId)
                        if old_doc and old_doc.get("pdfReportFileId"):
                            from app.storage.pdf_storage import delete_pdf
                            deleted = await delete_pdf(old_doc["pdfReportFileId"])
                            if deleted:
                                logger.info(
                                    f"Old PDF deleted (FileID: {old_doc['pdfReportFileId']}) - "
                                    f"Generating updated PDF with {message_count} messages"
                                )
                    elif should_update_pdf and not pdf_exists:
                        # PDF should exist but doesn't - generate it anyway
                        logger.warning(
                            f"PDF should exist but not found for session {request.sessionId} - "
                            f"Generating new PDF"
                        )

                    # Generate PDF bytes with current conversation state
                    pdf_bytes = forensic_reporter.generate_forensic_report_bytes(
                        session_id=request.sessionId,
                        extracted_intelligence=intelligence,
                        conversation_history=session.messages,
                        agent_notes=agent_notes,
                        scam_detected=session.scam_detected,
                        total_messages=message_count
                    )

                    if pdf_bytes:
                        # Generate case ID (consistent for same session)
                        case_id = forensic_reporter._generate_case_id(request.sessionId)

                        # Store in MongoDB GridFS (replaces old one)
                        file_id = await store_pdf(
                            session_id=request.sessionId,
                            pdf_bytes=pdf_bytes,
                            case_id=case_id,
                            metadata={
                                "scamDetected": session.scam_detected,
                                "totalMessages": message_count,
                                "scamType": session.scam_type,
                                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                                "isUpdate": pdf_exists,
                            }
                        )

                        if file_id:
                            pdf_file_id = file_id
                            pdf_case_id = case_id
                            pdf_generated = True
                            pdf_generated_at = datetime.now(timezone.utc)

                            action = "updated" if pdf_exists else "generated"
                            logger.info(
                                f"Forensic PDF {action} successfully - "
                                f"Session: {request.sessionId}, "
                                f"FileID: {file_id}, "
                                f"Case: {case_id}, "
                                f"Messages: {message_count}"
                            )

                except Exception as report_err:
                    logger.error(
                        f"Forensic report generation/update failed (non-blocking) - "
                        f"Session: {request.sessionId}, Error: {report_err}"
                    )


        # -----------------------------------------------------------------
        # CALLBACK LOGIC  (re-send on every qualifying turn so the
        # evaluator always has the latest intelligence snapshot)
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

            safety_trigger = message_count >= 10 and intelligence is not None

            if should_send or safety_trigger:
                # Calculate engagement duration from first message timestamp
                engagement_seconds = 0
                if session.messages and len(session.messages) >= 2:
                    first_ts = session.messages[0].timestamp
                    last_ts = session.messages[-1].timestamp
                    if isinstance(first_ts, (int, float)) and isinstance(last_ts, (int, float)):
                        engagement_seconds = max(int((last_ts - first_ts) / 1000), 1)
                    if engagement_seconds <= 0:
                        engagement_seconds = message_count * 15  # fallback estimate

                final_payload = FinalResultPayload(
                    sessionId=request.sessionId,
                    status="completed",
                    scamDetected=session.scam_detected,
                    totalMessagesExchanged=message_count,
                    extractedIntelligence=intelligence,
                    engagementMetrics=EngagementMetrics(
                        totalMessagesExchanged=message_count,
                        engagementDurationSeconds=engagement_seconds,
                    ),
                    agentNotes=agent_notes,
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


        # -----------------------------------------------------------------
        # PERSIST TO MONGODB (non-blocking – DB failure never breaks API with PDF metadata)
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
                detected_language=session.detected_language,
                response_language=session.response_language,
                persona_selected=session.persona_selected,
                persona_switch_history=session.persona_switch_history,
                rule_score=session.rule_score,
                ml_score=session.ml_score,
                scam_type=session.scam_type,
                detection_method=session.detection_method,
                detected_indicators=session.detected_indicators,
                detected_identity_dict={
                    "name": session.detected_identity.name,
                    "gender": session.detected_identity.gender,
                    "ageGroup": session.detected_identity.age_group,
                    "locked": session.detected_identity.locked,
                },
                pdf_report_generated=pdf_generated if 'pdf_generated' in locals() else False,
                pdf_report_file_id=pdf_file_id if 'pdf_file_id' in locals() else None,
                pdf_report_generated_at=pdf_generated_at if 'pdf_generated_at' in locals() else None,
                pdf_report_case_id=pdf_case_id if 'pdf_case_id' in locals() else None,
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


@router.get("/admin/db-status")
async def admin_db_status(admin_key: str = Depends(verify_admin_key)):
    """Diagnostic: check MongoDB connectivity and report errors."""
    from app.core.config import settings as _s
    uri = _s.mongodb_uri
    # Mask password in URI for safe display
    masked = re.sub(r"://([^:]+):([^@]+)@", r"://\1:****@", uri) if uri else "(empty)"

    result = {"mongodb_uri_set": bool(uri), "mongodb_uri_masked": masked}

    if not uri:
        result["error"] = "MONGODB_URI environment variable is empty"
        return result

    try:
        from motor.motor_asyncio import AsyncIOMotorClient
        client = AsyncIOMotorClient(uri, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        result["connected"] = True
        result["databases"] = await client.list_database_names()
        db = client["honeypot"]
        result["collections"] = await db.list_collection_names()
        col = db["scam_sessions"]
        result["document_count"] = await col.count_documents({})
        client.close()
    except Exception as exc:
        result["connected"] = False
        result["error"] = f"{type(exc).__name__}: {str(exc)}"

    return result


@router.get("/admin/report/{session_id}")
async def download_forensic_report(
    session_id: str,
    admin_key: Optional[str] = Query(None, description="Admin API key (can also use x-admin-key header)")
):
    """
    Download forensic PDF report for a session.

    Returns the PDF file which can be opened directly in the browser.
    Requires admin authentication via query parameter or x-admin-key header.
    """
    # Verify admin key from query parameter
    from app.core.config import settings

    if not admin_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin API key. Provide via ?admin_key= query parameter"
        )

    if admin_key != settings.admin_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )

    # Validate session ID format
    if not validate_session_id(session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid session ID format"
        )

    # Retrieve PDF from MongoDB GridFS
    result = await retrieve_pdf_by_session(session_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No PDF report found for session: {session_id}"
        )

    pdf_bytes, metadata = result

    # Return PDF with inline disposition so it opens in browser
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'inline; filename="{metadata["filename"]}"'
        }
    )
