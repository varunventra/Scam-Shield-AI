"""
Core configuration module for the Scambot Honeypot system.
"""
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_key: str = Field(..., env="API_KEY")
    port: int = Field(default=8000, env="PORT")
    host: str = Field(default="0.0.0.0", env="HOST")

    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.7, env="OPENAI_TEMPERATURE")
    max_tokens: int = Field(default=1000, env="MAX_TOKENS")

    # GUVI Callback
    guvi_callback_url: str = Field(
        default="https://hackathon.guvi.in/api/updateHoneyPotFinalResult",
        env="GUVI_CALLBACK_URL"
    )

    # Application Settings
    debug: bool = Field(default=False, env="DEBUG")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    max_conversation_turns: int = Field(default=20, env="MAX_CONVERSATION_TURNS")
    session_timeout: int = Field(default=3600, env="SESSION_TIMEOUT")

    # Scam Detection
    scam_confidence_threshold: float = Field(default=0.7, env="SCAM_CONFIDENCE_THRESHOLD")

    # Agent Persona
    agent_name: str = Field(default="Rahul", env="AGENT_NAME")
    agent_age: int = Field(default=28, env="AGENT_AGE")
    agent_occupation: str = Field(default="Software Engineer", env="AGENT_OCCUPATION")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
