"""
Logging configuration for the application.
"""
import logging
import sys
from typing import Optional
from app.core.config import settings


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Configure and return a logger instance.

    Args:
        log_level: Optional log level override

    Returns:
        Configured logger instance
    """
    level = log_level or settings.log_level

    # Create logger
    logger = logging.getLogger("scambot_honeypot")
    logger.setLevel(getattr(logging, level.upper()))

    # Create console handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)

    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(handler)

    return logger


# Global logger instance
logger = setup_logging()
