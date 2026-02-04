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
                    f"Agent activated - Session: {request.sessionId}, "
                    f"Confidence: {confidence:.2f}"
                )
            else:
                # Not a scam or confidence too low
                logger.info(f"No scam detected - Session: {request.sessionId}")
                return ConversationResponse(
                    status="success",
                    reply="I'm sorry, I didn't understand that."
                )

        # Agent is activated - generate response
        agent_response = await ai_agent.generate_response(request)

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
        should_end = await ai_agent.should_end_conversation(request)
        message_count = session.get_message_count()

        if should_end or message_count >= 6:  # Send callback after sufficient engagement
            # Extract intelligence from all messages
            all_messages = session.messages
            intelligence = intelligence_extractor.extract_intelligence(request, all_messages)

            # Generate agent notes
            agent_notes = intelligence_extractor.generate_agent_notes(
                request, all_messages, intelligence
            )

            # Update session with intelligence
            session_manager.update_session(
                request.sessionId,
                intelligence=intelligence
            )

            # Check if callback should be sent
            should_send = await callback_handler.should_send_callback(
                request.sessionId,
                session.scam_detected,
                message_count
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
