"""
Security utilities including API key validation.
"""
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from app.core.config import settings
from app.core.logging import logger


api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
admin_key_header = APIKeyHeader(name="x-admin-key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """
    Verify the API key from request headers.

    Args:
        api_key: API key from header

    Returns:
        Validated API key

    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        logger.warning("Request received without API key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API key"
        )

    if api_key != settings.api_key:
        logger.warning(f"Invalid API key attempted: {api_key[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )

    return api_key


async def verify_admin_key(admin_key: str = Security(admin_key_header)) -> str:
    """
    Verify the admin API key from request headers.

    Args:
        admin_key: Admin key from x-admin-key header

    Returns:
        Validated admin key

    Raises:
        HTTPException: If admin key is invalid or missing
    """
    if not admin_key:
        logger.warning("Admin request received without admin key")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin API key"
        )

    if not settings.admin_api_key or admin_key != settings.admin_api_key:
        logger.warning("Invalid admin API key attempted")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin API key"
        )

    return admin_key
