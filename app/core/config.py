"""
Core configuration module for the Scambot Honeypot system.
"""
import sys
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


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

    @field_validator("openai_api_key")
    def validate_openai_key(cls, v):
        """Validate OpenAI API key format."""
        if not v or len(v) < 20:
            raise ValueError("OpenAI API key appears invalid (too short or empty)")
        if not v.startswith("sk-"):
            print(f"⚠️  WARNING: OpenAI API key doesn't start with 'sk-' - this may be incorrect!")
        return v

    @field_validator("api_key")
    def validate_api_key(cls, v):
        """Validate API key is set."""
        if not v or len(v) < 8:
            raise ValueError("API_KEY must be at least 8 characters long")
        return v

    @field_validator("openai_model")
    def validate_model(cls, v):
        """Validate OpenAI model name."""
        valid_models = ["gpt-4o", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"]
        if v not in valid_models:
            print(f"⚠️  WARNING: Model '{v}' not in common list: {valid_models}")
            print(f"   Make sure your API key has access to this model!")
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


def validate_configuration():
    """
    Validate configuration and test OpenAI connection at startup.
    FAIL-FAST: If configuration is wrong, crash immediately.
    """
    try:
        from openai import OpenAI
        import logging

        logger = logging.getLogger("scambot_honeypot")

        print("\n" + "="*70)
        print("🔧 CONFIGURATION VALIDATION")
        print("="*70)

        print(f"✅ API Key: {'*' * 20}{settings.api_key[-4:]}")
        print(f"✅ OpenAI Model: {settings.openai_model}")
        print(f"✅ OpenAI Key: sk-...{settings.openai_api_key[-4:]}")
        print(f"✅ Host: {settings.host}")
        print(f"✅ Port: {settings.port}")
        print(f"✅ Debug: {settings.debug}")
        print(f"✅ Scam Threshold: {settings.scam_confidence_threshold}")

        # Test OpenAI connection
        print("\n🔄 Testing OpenAI API connection...")
        try:
            client = OpenAI(api_key=settings.openai_api_key)

            # Make a minimal test call
            response = client.chat.completions.create(
                model=settings.openai_model,
                messages=[{"role": "user", "content": "test"}],
                max_tokens=5
            )

            print(f"✅ OpenAI API connection successful!")
            print(f"✅ Model '{settings.openai_model}' is accessible")

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            print(f"\n❌ OPENAI API TEST FAILED!")
            print(f"   Error Type: {error_type}")
            print(f"   Error Message: {error_msg}")

            if "authentication" in error_msg.lower() or "api_key" in error_msg.lower():
                print(f"\n🚨 CRITICAL: Invalid OpenAI API key!")
                print(f"   1. Check your OPENAI_API_KEY in .env file")
                print(f"   2. Verify the key at https://platform.openai.com/api-keys")
                print(f"   3. Ensure the key has proper permissions")
                sys.exit(1)

            elif "model" in error_msg.lower() or "not found" in error_msg.lower():
                print(f"\n🚨 CRITICAL: Model '{settings.openai_model}' not accessible!")
                print(f"   1. Your API key may not have access to {settings.openai_model}")
                print(f"   2. Try setting OPENAI_MODEL=gpt-3.5-turbo in .env")
                print(f"   3. Check https://platform.openai.com/account/limits")
                sys.exit(1)

            elif "rate_limit" in error_msg.lower():
                print(f"\n⚠️  WARNING: Rate limit error (but API key is valid)")
                print(f"   Connection will work during actual operation")

            else:
                print(f"\n⚠️  WARNING: OpenAI test failed but will continue")
                print(f"   The API may still work during actual operation")
                print(f"   Monitor logs for OpenAI errors during testing")

        print("="*70)
        print("✅ Configuration validation complete!\n")

    except Exception as e:
        print(f"\n❌ FATAL: Configuration validation failed!")
        print(f"   Error: {str(e)}")
        print(f"\n   Fix your configuration and restart the server.")
        sys.exit(1)


# Global settings instance
try:
    settings = Settings()
except Exception as e:
    print(f"\n❌ FATAL: Failed to load configuration!")
    print(f"   Error: {str(e)}")
    print(f"\n   Common fixes:")
    print(f"   1. Create .env file in project root")
    print(f"   2. Set API_KEY=your-api-key")
    print(f"   3. Set OPENAI_API_KEY=sk-your-key")
    print(f"\n   See .env.example for reference")
    sys.exit(1)
