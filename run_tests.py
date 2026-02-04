"""
Test runner for Scambot Honeypot API
Runs all 25 comprehensive tests
"""
import sys
import pytest


def main():
    """Run all tests with detailed output"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║           SCAMBOT HONEYPOT API - TEST SUITE                        ║
║           25 Comprehensive Tests                                   ║
╚════════════════════════════════════════════════════════════════════╝

Running tests covering:
✓ API Authentication (3 tests)
✓ Scam Detection (5 tests)
✓ Multi-turn Conversations (6 tests) - CRITICAL REQUIREMENT
✓ Intelligence Extraction (3 tests)
✓ Response Format (2 tests)
✓ Edge Cases & Errors (3 tests)
✓ API Endpoints (3 tests)

""")

    # Run pytest with verbose output
    exit_code = pytest.main([
        "tests/test_api.py",
        "-v",                    # Verbose
        "--tb=short",            # Short traceback
        "--color=yes",           # Colored output
        "-x",                    # Stop on first failure (remove to run all)
        "--maxfail=5",           # Stop after 5 failures
        "-p", "no:warnings"      # Disable warnings
    ])

    if exit_code == 0:
        print("""
╔════════════════════════════════════════════════════════════════════╗
║                    ✅ ALL TESTS PASSED!                            ║
║                                                                    ║
║  Your API is ready for hackathon evaluation!                      ║
║                                                                    ║
║  Next steps:                                                       ║
║  1. Deploy to production (Railway/Render/AWS)                     ║
║  2. Get public URL                                                 ║
║  3. Test with curl or Postman                                     ║
║  4. Submit to GUVI platform                                       ║
╚════════════════════════════════════════════════════════════════════╝
""")
    else:
        print(f"""
╔════════════════════════════════════════════════════════════════════╗
║                    ❌ TESTS FAILED                                 ║
║                                                                    ║
║  {exit_code} test(s) failed. Review the output above.            ║
║                                                                    ║
║  Common issues:                                                    ║
║  - OpenAI API key not set or invalid                              ║
║  - Missing environment variables                                   ║
║  - API not running or import errors                               ║
╚════════════════════════════════════════════════════════════════════╝
""")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
