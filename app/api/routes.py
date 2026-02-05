"""
API routes for the Scambot Honeypot system.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import verify_api_key
from app.core.logging import logger
from app.models.requests import ConversationRequest
from app.models.responses import ConversationResponse, FinalResultPayload
from app.services import ScamDetector, AIAgent, IntelligenceExtractor, CallbackHandler
from app.storage import session_manager
from app.utils import validate_session_id

# Create router
router = APIRouter()

# Initialize services
scam_detector = ScamDetector()
ai_agent = AIAgent()
intelligence_extractor = IntelligenceExtractor()
callback_handler = CallbackHandler()


@router.post("/conversation", response_model=ConversationResponse)
async def handle_conversation(
    request: ConversationRequest,
    api_key: str = Depends(verify_api_key)
) -> ConversationResponse:
    """
    Main endpoint for handling incoming scam messages.

    This endpoint:
    1. Receives a message from the platform
    2. Detects scam intent
    3. Activates AI agent if scam detected
    4. Returns agent's response
    5. Extracts intelligence and sends callback when appropriate

    Args:
        request: Conversation request containing message and history
        api_key: Validated API key

    Returns:
        Agent's response to the message
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
            # First message or agent not yet activated - check for scam
            logger.info(f"🔎 First message - checking for scam - Session: {request.sessionId}")

            try:
                should_activate = await scam_detector.should_activate_agent(request)

                if should_activate:
                    # Detect scam with full analysis
                    is_scam, confidence, reasoning = await scam_detector.detect_scam(request)

                    # Update session
                    session_manager.update_session(
                        request.sessionId,
                        scam_detected=is_scam,
                        scam_confidence=confidence,
                        agent_activated=True
                    )

                    logger.info(
                        f"✅ Agent activated - Session: {request.sessionId}, "
                        f"Scam: {is_scam}, Confidence: {confidence:.2f}"
                    )
                else:
                    # HONEYPOT FAIL-OPEN BEHAVIOR:
                    # Even if detection says "no scam", still engage!
                    # This is a HONEYPOT - better to over-engage than miss a scam
                    logger.info(
                        f"⚠️ Low confidence - but STILL ENGAGING (honeypot mode) - Session: {request.sessionId}"
                    )

                    # Mark as activated anyway for continued engagement
                    session_manager.update_session(
                        request.sessionId,
                        scam_detected=False,
                        scam_confidence=0.3,
                        agent_activated=True  # STILL ACTIVATE - FAIL OPEN!
                    )

            except Exception as e:
                # CRITICAL FAIL-OPEN BEHAVIOR:
                # If scam detection completely fails, STILL ENGAGE!
                logger.error(
                    f"🚨 Scam detection FAILED - Session: {request.sessionId}, "
                    f"Error type: {type(e).__name__}, Message: {str(e)}"
                )
                logger.warning(f"⚠️ FAIL-OPEN: Engaging anyway (honeypot behavior)")

                # Activate agent despite error
                session_manager.update_session(
                    request.sessionId,
                    scam_detected=True,  # Assume suspicious
                    scam_confidence=0.5,
                    agent_activated=True
                )

        # Agent is ALWAYS activated at this point - generate response
        logger.info(f"💬 Generating agent response - Session: {request.sessionId}")

        # Use session messages for conversation history (not request history)
        # This ensures context is maintained even if client doesn't send history
        session_messages = session.messages
        logger.info(
            f"📚 Session has {len(session_messages)} messages stored - "
            f"Session: {request.sessionId}"
        )

        agent_response = await ai_agent.generate_response(request, session_messages)

        # Add agent's response to session history
        from app.models.requests import Message
        import time
        agent_message = Message(
            sender="user",
            text=agent_response,
            timestamp=int(time.time() * 1000)
        )
        session_manager.add_message_to_session(request.sessionId, agent_message)

        # Check if we should extract intelligence and send callback
        # GUVI REQUIREMENT: No artificial conversation limit - let GUVI decide when to stop
        should_end = await ai_agent.should_end_conversation(request)
        message_count = session.get_message_count()

        # GUVI REQUIREMENT: Prioritize thoroughness over speed
        # Extract intelligence on every turn (starting from turn 3) but ONLY send callback at 18+ messages
        # This ensures final payload contains ALL intelligence from the entire conversation
        intelligence = None
        if message_count >= 3:  # Start extracting after minimum engagement
            # Extract intelligence from ALL messages in conversation (turns 1 to current)
            all_messages = session.messages
            intelligence = intelligence_extractor.extract_intelligence(request, all_messages)

            # Generate agent notes
            agent_notes = intelligence_extractor.generate_agent_notes(
                request, all_messages, intelligence
            )

            # Update session with intelligence (cumulative extraction)
            session_manager.update_session(
                request.sessionId,
                intelligence=intelligence
            )

            # HARD FLOOR: Check if callback should be sent (ONLY at 18+ messages)
            should_send = await callback_handler.should_send_callback(
                request.sessionId,
                session.scam_detected,
                message_count,
                intelligence
            )

            if should_send and not session.callback_sent:
                # Prepare and send final result
                final_payload = FinalResultPayload(
                    sessionId=request.sessionId,
                    scamDetected=session.scam_detected,
                    totalMessagesExchanged=message_count,
                    extractedIntelligence=intelligence,
                    agentNotes=agent_notes
                )

                callback_success = await callback_handler.send_final_result(final_payload)

                if callback_success:
                    session_manager.update_session(
                        request.sessionId,
                        callback_sent=True
                    )

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


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "scambot-honeypot",
        "active_sessions": session_manager.get_session_count()
    }


@router.post("/admin/cleanup")
async def cleanup_sessions(api_key: str = Depends(verify_api_key)):
    """
    Admin endpoint to cleanup expired sessions.

    Args:
        api_key: Validated API key

    Returns:
        Cleanup results
    """
    removed_count = session_manager.cleanup_expired_sessions()
    logger.info(f"Cleaned up {removed_count} expired sessions")

    return {
        "status": "success",
        "removed_sessions": removed_count,
        "active_sessions": session_manager.get_session_count()
    }
