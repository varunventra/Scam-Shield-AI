#!/usr/bin/env python
"""
Convenient script to run the Scambot Honeypot API.
"""
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    from app.core.config import settings

    print(f"""
╔═══════════════════════════════════════════════════════════════╗
║                   SCAMBOT HONEYPOT API                        ║
║                   Enterprise AI Security                      ║
╚═══════════════════════════════════════════════════════════════╝

🚀 Starting server...
📍 Host: {settings.host}
🔌 Port: {settings.port}
🤖 Model: {settings.openai_model}
🎯 Confidence Threshold: {settings.scam_confidence_threshold}
📊 Debug: {settings.debug}

🔗 API Documentation: http://localhost:{settings.port}/docs
💚 Health Check: http://localhost:{settings.port}/health

Press CTRL+C to stop
""")

    try:
        uvicorn.run(
            "app.main:app",
            host=settings.host,
            port=settings.port,
            reload=settings.debug,
            log_level=settings.log_level.lower()
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        sys.exit(1)
