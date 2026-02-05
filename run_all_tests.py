#!/usr/bin/env python
"""
Comprehensive Automated Test Runner
Runs ALL tests for the Scambot Honeypot API automatically.

Usage:
    python run_all_tests.py

This runs all tests without needing Postman or manual testing.
"""
import subprocess
import sys
import os
from datetime import datetime
import json

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


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


def run_test_suite(test_file, description):
    """Run a specific test suite"""
    print_header(f"Running: {description}")

    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short", "-s"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        print(result.stdout)

        if result.returncode == 0:
            print_success(f"{description} - ALL PASSED")
            return True
        else:
            print_error(f"{description} - SOME FAILED")
            if result.stderr:
                print(result.stderr)
            return False

    except subprocess.TimeoutExpired:
        print_error(f"{description} - TIMEOUT (exceeded 5 minutes)")
        return False
    except Exception as e:
        print_error(f"{description} - ERROR: {str(e)}")
        return False


def check_server_running():
    """Check if the server is running"""
    import requests
    try:
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            return True
    except:
        pass
    return False


def main():
    """Main test runner"""
    start_time = datetime.now()

    print_header("🧪 SCAMBOT HONEYPOT - COMPREHENSIVE AUTOMATED TEST SUITE")

    print(f"{Colors.BOLD}Test Execution Started:{Colors.ENDC} {start_time.strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Check if server is running
    print_info("Checking if server is running...")
    if not check_server_running():
        print_warning("Server is not running on http://localhost:8000")
        print_info("Please start the server first:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        print("\nOr run tests against your Render deployment by updating BASE_URL")
        sys.exit(1)
    else:
        print_success("Server is running on http://localhost:8000\n")

    # Test suites to run
    test_suites = [
        ("tests/test_api.py", "Core API Tests (Authentication, Endpoints, Format)"),
        ("tests/test_all_scenarios.py", "All Scam Scenarios from TEST_EXAMPLES.md"),
        ("tests/test_persona_validation.py", "Persona Validation (Realistic Responses)"),
        ("tests/test_intelligence_extraction.py", "Intelligence Extraction (Critical)"),
    ]

    results = {}

    # Run each test suite
    for test_file, description in test_suites:
        if not os.path.exists(test_file):
            print_warning(f"Test file not found: {test_file} - SKIPPING")
            results[description] = "skipped"
            continue

        success = run_test_suite(test_file, description)
        results[description] = "passed" if success else "failed"

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print_header("📊 TEST EXECUTION SUMMARY")

    print(f"{Colors.BOLD}Total Duration:{Colors.ENDC} {duration:.2f} seconds\n")

    passed = sum(1 for r in results.values() if r == "passed")
    failed = sum(1 for r in results.values() if r == "failed")
    skipped = sum(1 for r in results.values() if r == "skipped")
    total = len(results)

    print(f"{Colors.BOLD}Test Suites:{Colors.ENDC}")
    print(f"  Total:   {total}")
    print(f"  Passed:  {Colors.OKGREEN}{passed}{Colors.ENDC}")
    print(f"  Failed:  {Colors.FAIL}{failed}{Colors.ENDC}")
    print(f"  Skipped: {Colors.WARNING}{skipped}{Colors.ENDC}\n")

    print(f"{Colors.BOLD}Results by Suite:{Colors.ENDC}")
    for desc, result in results.items():
        if result == "passed":
            print(f"  {Colors.OKGREEN}✅{Colors.ENDC} {desc}")
        elif result == "failed":
            print(f"  {Colors.FAIL}❌{Colors.ENDC} {desc}")
        else:
            print(f"  {Colors.WARNING}⏭️ {Colors.ENDC} {desc}")

    print("\n" + "="*70)

    if failed == 0 and passed > 0:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 ALL TESTS PASSED!{Colors.ENDC}")
        print(f"{Colors.OKGREEN}Your honeypot is ready for deployment!{Colors.ENDC}\n")

        print(f"{Colors.BOLD}✅ What was tested:{Colors.ENDC}")
        print("  • API Authentication (x-api-key header)")
        print("  • All 10 scam scenarios from TEST_EXAMPLES.md")
        print("  • Multi-turn conversations (up to 10 turns)")
        print("  • Persona validation (realistic, not bookish)")
        print("  • Response format compliance")
        print("  • Edge cases and error handling")
        print("  • Intelligence extraction")
        print("  • Session management")

        print(f"\n{Colors.BOLD}🚀 Next Steps:{Colors.ENDC}")
        print("  1. Deploy to Render (if not already done)")
        print("  2. Update API_KEY in Render environment variables")
        print("  3. Share API key and URL with teammate for Postman")
        print("  4. Submit to GUVI hackathon")

        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}❌ SOME TESTS FAILED{Colors.ENDC}")
        print(f"{Colors.FAIL}Please review the failures above and fix issues.{Colors.ENDC}\n")

        print(f"{Colors.BOLD}Common Issues:{Colors.ENDC}")
        print("  • OpenAI API key not configured or invalid")
        print("  • Rate limits on OpenAI API")
        print("  • Server configuration errors")
        print("  • Network connectivity issues")

        print(f"\n{Colors.BOLD}Debugging:{Colors.ENDC}")
        print("  • Check server logs for errors")
        print("  • Verify .env file configuration")
        print("  • Test OpenAI API key separately")
        print("  • Run individual test files for details")

        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Tests interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {str(e)}{Colors.ENDC}")
        sys.exit(1)
