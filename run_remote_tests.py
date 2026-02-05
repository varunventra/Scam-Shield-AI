#!/usr/bin/env python
"""
Remote Test Runner - Tests your Render deployment
Runs ALL tests against your production Render service.

Usage:
    python run_remote_tests.py

Or with custom URL and API key:
    python run_remote_tests.py --url https://your-service.onrender.com --api-key YOUR_KEY
"""
import subprocess
import sys
import os
import argparse
from datetime import datetime
import requests

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def check_server_available(base_url):
    """Check if remote server is accessible"""
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                return True, data
    except Exception as e:
        return False, str(e)
    return False, "Server not responding correctly"


def run_remote_tests(base_url, api_key):
    """Run all remote tests"""
    start_time = datetime.now()

    print_header("🧪 HONEYPOT REMOTE TESTING - RENDER DEPLOYMENT")

    print(f"{Colors.BOLD}Test Target:{Colors.ENDC} {base_url}")
    print(f"{Colors.BOLD}API Key:{Colors.ENDC} {'*' * 20}{api_key[-4:]}")
    print(f"{Colors.BOLD}Started:{Colors.ENDC} {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check if server is available
    print_info("Checking if Render service is accessible...")
    available, result = check_server_available(base_url)

    if not available:
        print_error(f"Cannot reach Render service at {base_url}")
        print_error(f"Error: {result}")
        print("\n" + "="*70)
        print(f"{Colors.WARNING}Troubleshooting:{Colors.ENDC}")
        print("  1. Check if Render URL is correct")
        print("  2. Verify service is not sleeping (check Render dashboard)")
        print("  3. Check if UptimeRobot is active")
        print("  4. Try accessing the health endpoint in browser:")
        print(f"     {base_url}/health")
        return 1
    else:
        print_success(f"Render service is accessible: {result}\n")

    # Set environment variables for tests
    os.environ["TEST_BASE_URL"] = base_url
    os.environ["TEST_API_KEY"] = api_key

    # Run tests
    try:
        print_info("Running remote API tests...\n")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_remote_api.py", "-v", "--tb=short", "-s"],
            timeout=600  # 10 minute timeout
        )

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print_header("📊 REMOTE TEST SUMMARY")

        print(f"{Colors.BOLD}Test Duration:{Colors.ENDC} {duration:.2f} seconds")
        print(f"{Colors.BOLD}Target:{Colors.ENDC} {base_url}")

        if result.returncode == 0:
            print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL REMOTE TESTS PASSED!{Colors.ENDC}")
            print(f"{Colors.OKGREEN}Your Render deployment is working perfectly!{Colors.ENDC}\n")

            print(f"{Colors.BOLD}✅ What was validated on production:{Colors.ENDC}")
            print("  • API Authentication (x-api-key)")
            print("  • Scam detection (bank, UPI, phishing, OTP)")
            print("  • Multi-turn conversations (3-turn, 5-turn)")
            print("  • Persona validation (realistic responses)")
            print("  • Response format compliance")
            print("  • No bookish language")
            print("  • Agent never reveals it's a bot")

            print(f"\n{Colors.BOLD}🚀 Production Status:{Colors.ENDC}")
            print(f"  {Colors.OKGREEN}✅ Ready for GUVI submission{Colors.ENDC}")
            print(f"  {Colors.OKGREEN}✅ Ready for teammate testing{Colors.ENDC}")
            print(f"  {Colors.OKGREEN}✅ Production-ready{Colors.ENDC}")

            print(f"\n{Colors.BOLD}📤 Submit to GUVI:{Colors.ENDC}")
            print(f"  x-api-key: {api_key}")
            print(f"  Endpoint URL: {base_url}/api/v1/conversation")

            return 0
        else:
            print(f"\n{Colors.FAIL}{Colors.BOLD}❌ SOME REMOTE TESTS FAILED{Colors.ENDC}")
            print(f"{Colors.FAIL}Check the output above for details.{Colors.ENDC}\n")

            print(f"{Colors.BOLD}Common Issues:{Colors.ENDC}")
            print("  • OpenAI API key not configured in Render")
            print("  • Rate limits on OpenAI API")
            print("  • Render environment variables not set")
            print("  • Service cold start (try running again)")

            print(f"\n{Colors.BOLD}Debugging:{Colors.ENDC}")
            print("  • Check Render logs for errors")
            print("  • Verify environment variables in Render dashboard")
            print("  • Ensure OpenAI API key is valid and has credits")
            print("  • Run tests again (first run may be slower)")

            return 1

    except subprocess.TimeoutExpired:
        print_error("Tests timed out (exceeded 10 minutes)")
        print_warning("This usually means OpenAI API is very slow")
        print_info("Try running the tests again")
        return 1
    except Exception as e:
        print_error(f"Error running tests: {str(e)}")
        return 1


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Test your Honeypot deployment on Render",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test with default settings (reads from .env)
  python run_remote_tests.py

  # Test with custom URL and API key
  python run_remote_tests.py --url https://my-honeypot.onrender.com --api-key ABC123

  # Quick test (skip some scenarios)
  python run_remote_tests.py --quick
        """
    )

    parser.add_argument(
        "--url",
        help="Render service URL (default: from .env or prompt)",
        default=None
    )

    parser.add_argument(
        "--api-key",
        help="API key (default: from .env)",
        default=None
    )

    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run quick tests only (skip some scenarios)"
    )

    args = parser.parse_args()

    # Get base URL
    if args.url:
        base_url = args.url.rstrip('/')
    else:
        # Try to load from .env
        from dotenv import load_dotenv
        load_dotenv()

        base_url = os.getenv("RENDER_URL")

        if not base_url:
            print_header("🔧 CONFIGURATION")
            print("No Render URL found. Please provide your Render service URL.")
            print("\nExample: https://scambot-honeypot-abc123.onrender.com")
            base_url = input("\nEnter your Render URL: ").strip().rstrip('/')

            if not base_url:
                print_error("No URL provided. Exiting.")
                return 1

    # Get API key
    if args.api_key:
        api_key = args.api_key
    else:
        # Try to load from .env
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv("API_KEY")

        if not api_key:
            print("\nNo API key found in .env")
            api_key = input("Enter your API key: ").strip()

            if not api_key:
                print_error("No API key provided. Exiting.")
                return 1

    # Validate URL format
    if not base_url.startswith(("http://", "https://")):
        print_error(f"Invalid URL format: {base_url}")
        print_info("URL must start with http:// or https://")
        return 1

    # Run tests
    return run_remote_tests(base_url, api_key)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
