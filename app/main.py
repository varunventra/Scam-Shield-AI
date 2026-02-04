"""
Main FastAPI application for Scambot Honeypot.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import logger
from app.api import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Scambot Honeypot API")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"OpenAI model: {settings.openai_model}")

    yield

    # Shutdown
    logger.info("Shutting down Scambot Honeypot API")


# Create FastAPI application
app = FastAPI(
    title="Scambot Honeypot API",
    description="AI-powered honeypot system for scam detection and intelligence extraction",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(router, prefix="/api/v1", tags=["conversation"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Scambot Honeypot API",
        "version": "1.0.0",
        "status": "running"
    }
@app.get("/health", include_in_schema=False)
@app.head("/health", include_in_schema=False)
async def health_check():
    """
    Health check endpoint.
    Must be publicly accessible without authentication.
    """
    return {
        "status": "healthy",
        "active_sessions": 0
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )
