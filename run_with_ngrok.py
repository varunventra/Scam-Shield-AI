#!/usr/bin/env python
"""
Run the Scambot Honeypot API with ngrok tunnel for public access.
This script starts both the FastAPI server and creates an ngrok tunnel.
"""
import sys
import os
import time
import threading
from pyngrok import ngrok, conf

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def start_server():
    """Start the FastAPI server in a separate thread."""
    import uvicorn
    from app.core.config import settings

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        log_level=settings.log_level.lower()
    )


def main():
    """Main function to start server and ngrok tunnel."""
    from app.core.config import settings

    print("""
╔═══════════════════════════════════════════════════════════════╗
║                   SCAMBOT HONEYPOT API                        ║
║                   With Ngrok Tunnel                           ║
╚═══════════════════════════════════════════════════════════════╝
""")

    print("🚀 Starting FastAPI server...")
    print(f"📍 Local Host: {settings.host}")
    print(f"🔌 Local Port: {settings.port}")
    print(f"🤖 Model: {settings.openai_model}")
    print(f"🎯 Confidence Threshold: {settings.scam_confidence_threshold}")
    print()

    # Start FastAPI server in background thread
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Give server time to start
    print("⏳ Waiting for server to start...")
    time.sleep(3)

    try:
        # Start ngrok tunnel
        print("🌐 Creating ngrok tunnel...")

        # Configure ngrok (optional: set auth token if you have one)
        # Uncomment and set your ngrok auth token if you have one:
        # conf.get_default().auth_token = "YOUR_NGROK_AUTH_TOKEN"

        # Create HTTP tunnel
        tunnel = ngrok.connect(settings.port, bind_tls=True)
        public_url = tunnel.public_url

        print("\n" + "="*70)
        print("✅ NGROK TUNNEL CREATED SUCCESSFULLY!")
        print("="*70)
        print(f"\n🔗 Public URL: {public_url}")
        print(f"\n📍 Local URL: http://localhost:{settings.port}")
        print("\n" + "="*70)
        print("\n📋 HACKATHON SUBMISSION DETAILS:")
        print("="*70)
        print(f"\n✨ Honeypot API Endpoint URL:")
        print(f"   {public_url}/api/v1/conversation")
        print(f"\n🔑 API Key (x-api-key header):")
        print(f"   {settings.api_key}")
        print("\n" + "="*70)
        print("\n📚 Available Endpoints:")
        print(f"   - POST {public_url}/api/v1/conversation (Main endpoint)")
        print(f"   - GET  {public_url}/health (Health check)")
        print(f"   - GET  {public_url}/ (Root endpoint)")

        if settings.debug:
            print(f"   - GET  {public_url}/docs (API Documentation)")

        print("\n" + "="*70)
        print("\n💡 TESTING YOUR ENDPOINT:")
        print("="*70)
        print("\n1. Copy the Honeypot API Endpoint URL above")
        print("2. Go to the hackathon testing platform")
        print("3. Paste the URL and API key")
        print("4. Click 'Test Honeypot Endpoint'")
        print("\n" + "="*70)
        print("\n⚠️  IMPORTANT NOTES:")
        print("="*70)
        print("- Keep this window open to maintain the tunnel")
        print("- The ngrok free tier has session limits")
        print("- If the tunnel disconnects, restart this script")
        print("- Press CTRL+C to stop the server and tunnel")
        print("\n" + "="*70)

        # Keep the script running
        print("\n✅ Server is running. Press CTRL+C to stop...\n")

        # Monitor ngrok tunnels
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
        ngrok.kill()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("1. Make sure no other service is using port", settings.port)
        print("2. Check your internet connection")
        print("3. Install ngrok: pip install pyngrok")
        print("4. For ngrok errors, visit: https://ngrok.com/")
        ngrok.kill()
        sys.exit(1)


if __name__ == "__main__":
    main()
