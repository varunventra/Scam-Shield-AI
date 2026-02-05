"""
Callback handler for sending final results to GUVI evaluation endpoint.
"""
import httpx
from typing import Optional, TYPE_CHECKING
from app.core.config import settings
from app.core.logging import logger
from app.models.responses import FinalResultPayload

if TYPE_CHECKING:
    from app.models.responses import ExtractedIntelligence


class CallbackHandler:
    """Handles callbacks to GUVI evaluation endpoint."""

    def __init__(self):
        """Initialize callback handler."""
        self.callback_url = settings.guvi_callback_url
        self.timeout = 10.0  # seconds

    async def send_final_result(self, payload: FinalResultPayload) -> bool:
        """
        Send final result to GUVI evaluation endpoint.

        Args:
            payload: Final result data to send

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(
                f"Sending final result to GUVI - Session: {payload.sessionId}, "
                f"Scam: {payload.scamDetected}, Messages: {payload.totalMessagesExchanged}"
            )

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.callback_url,
                    json=payload.model_dump(),
                    headers={"Content-Type": "application/json"}
                )

                if response.status_code == 200:
                    logger.info(
                        f"Successfully sent final result - Session: {payload.sessionId}, "
                        f"Response: {response.text}"
                    )
                    return True
                else:
                    logger.error(
                        f"Failed to send final result - Session: {payload.sessionId}, "
                        f"Status: {response.status_code}, Response: {response.text}"
                    )
                    return False

        except httpx.TimeoutException:
            logger.error(
                f"Timeout sending final result - Session: {payload.sessionId}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Error sending final result - Session: {payload.sessionId}, "
                f"Error: {str(e)}"
            )
            return False

    async def should_send_callback(
        self,
        session_id: str,
        scam_detected: bool,
        message_count: int,
        intelligence: Optional['ExtractedIntelligence'] = None
    ) -> bool:
        """
        Determine if callback should be sent.

        GUVI REQUIREMENT: Prioritize thoroughness over speed.
        HARD FLOOR: Only send callback after 18+ messages to ensure maximum intelligence extraction.

        Args:
            session_id: Session identifier
            scam_detected: Whether scam was detected
            message_count: Number of messages exchanged
            intelligence: Extracted intelligence (not used for trigger decision)

        Returns:
            True if callback should be sent
        """
        # HARD FLOOR: Only send after substantial engagement (18+ messages)
        # This ensures we capture ALL intelligence before reporting to GUVI
        # No early triggers - thoroughness over speed
        should_send = scam_detected and message_count >= 18

        if should_send:
            logger.info(
                f"Callback criteria met - Session: {session_id}, "
                f"Messages: {message_count} (threshold: 18)"
            )
        else:
            logger.debug(
                f"Callback criteria not met - Session: {session_id}, "
                f"Scam: {scam_detected}, Messages: {message_count} (need 18+)"
            )

        return should_send
