#!/usr/bin/env python
"""
Quick test script to validate honeypot fixes.
Tests all critical scenarios to ensure fail-open behavior.
"""
import requests
import json
import time
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY")  # Read from .env file

# Test messages
TEST_CASES = [
    {
        "name": "High Confidence Scam",
        "message": "Your bank account will be blocked immediately. Verify your UPI PIN now or face legal action.",
        "expected": "Should activate agent and engage"
    },
    {
        "name": "Medium Confidence Scam",
        "message": "Urgent: Your account needs verification. Click here to update KYC.",
        "expected": "Should activate agent and engage"
    },
    {
        "name": "Low Keywords Scam",
        "message": "Congratulations! You won a lottery. Share your bank details.",
        "expected": "Should still engage (fail-open)"
    },
    {
        "name": "Ambiguous Message",
        "message": "Hello, I need help with my account.",
        "expected": "Should engage anyway (honeypot mode)"
    },
    {
        "name": "Normal Message",
        "message": "How are you today?",
        "expected": "Should still engage (fail-open behavior)"
    }
]


def print_header(text):
    """Print formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)


def print_result(success, message):
    """Print test result."""
    emoji = "✅" if success else "❌"
    print(f"{emoji} {message}")


def test_health_check():
    """Test health endpoint."""
    print_header("🏥 Testing Health Check")

    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print_result(True, f"Health check passed: {data}")
            return True
        else:
            print_result(False, f"Health check failed: {response.status_code}")
            return False

    except Exception as e:
        print_result(False, f"Health check error: {str(e)}")
        print("\n⚠️  Make sure the server is running:")
        print("   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload")
        return False


def test_conversation(test_case, session_id):
    """Test conversation endpoint with a specific message."""
    print(f"\n📨 Test: {test_case['name']}")
    print(f"   Message: \"{test_case['message'][:60]}...\"" if len(test_case['message']) > 60 else f"   Message: \"{test_case['message']}\"")
    print(f"   Expected: {test_case['expected']}")

    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": test_case['message'],
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": []
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()

            # Check if we got a meaningful response (not generic error message)
            reply = data.get("reply", "")

            if reply and reply != "I'm sorry, I didn't understand that.":
                print_result(True, f"Agent engaged successfully!")
                print(f"   Reply: \"{reply[:100]}...\"" if len(reply) > 100 else f"   Reply: \"{reply}\"")
                return True
            else:
                print_result(False, f"Got passive/generic response: \"{reply}\"")
                print("   ⚠️  This suggests fail-closed behavior - agent didn't engage!")
                return False

        elif response.status_code == 401:
            print_result(False, "Authentication failed - check API_KEY")
            print(f"   Update API_KEY in this script: {__file__}")
            return False

        else:
            print_result(False, f"HTTP {response.status_code}: {response.text}")
            return False

    except requests.exceptions.Timeout:
        print_result(False, "Request timed out (30s) - OpenAI might be slow")
        print("   ⚠️  This is not necessarily a failure - check server logs")
        return False

    except Exception as e:
        print_result(False, f"Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  🧪 HONEYPOT FIX VALIDATION TEST")
    print("="*70)
    print("\n⚠️  SETUP:")
    print("   1. Make sure server is running on port 8000")
    print("   2. Update API_KEY in this script")
    print("   3. Ensure OpenAI API key is configured")

    input("\nPress Enter to start tests...")

    # Test 1: Health check
    if not test_health_check():
        print("\n❌ Health check failed - fix server setup first")
        sys.exit(1)

    # Test 2: Run conversation tests
    print_header("💬 Testing Conversation Endpoint")

    results = []
    for i, test_case in enumerate(TEST_CASES):
        session_id = f"test-{int(time.time())}-{i}"
        result = test_conversation(test_case, session_id)
        results.append((test_case['name'], result))

        # Small delay between tests
        time.sleep(2)

    # Summary
    print_header("📊 TEST SUMMARY")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")

    print("\n" + "-"*70)
    for name, result in results:
        emoji = "✅" if result else "❌"
        print(f"{emoji} {name}")

    print("-"*70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Honeypot has FAIL-OPEN behavior")
        print("✅ Agent engages with all message types")
        print("✅ No passive/generic responses")
        print("\n🚀 Your honeypot is production-ready!")
        return 0
    elif passed > 0:
        print(f"\n⚠️  PARTIAL SUCCESS: {passed}/{total} tests passed")
        print("   Check server logs for errors")
        print("   Ensure OpenAI API is working")
        return 1
    else:
        print("\n❌ ALL TESTS FAILED")
        print("   Common issues:")
        print("   1. Wrong API_KEY in this script")
        print("   2. OpenAI API key not configured")
        print("   3. Server not running or wrong port")
        print("   4. Network/firewall issues")
        return 1


if __name__ == "__main__":
    # Check if API key was loaded from .env
    if not API_KEY:
        print("\n❌ ERROR: API_KEY not found in .env file!")
        print(f"   Make sure .env file exists in: {os.getcwd()}")
        print(f"   And contains: API_KEY=your-key-here")
        sys.exit(1)

    print(f"✅ Loaded API_KEY from .env: {'*' * 20}{API_KEY[-4:]}")
    sys.exit(main())
