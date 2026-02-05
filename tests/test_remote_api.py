"""
Remote API Tests - Tests against deployed Render service
Run these tests against your production Render deployment.
"""
import pytest
import requests
import time
import os

# Configuration - Set your Render URL here
BASE_URL = os.getenv("TEST_BASE_URL", "https://your-service.onrender.com")
API_KEY = os.getenv("TEST_API_KEY", "J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM")

# Timeout for requests (in seconds)
TIMEOUT = 30


class TestRemoteAPIAuthentication:
    """Test API Authentication on remote server"""

    def test_01_health_check_no_auth(self):
        """Health check should work without authentication"""
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print(f"\n✅ Health check: {data}")

    def test_02_missing_api_key(self):
        """Request without API key should fail"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            json={
                "sessionId": "remote-test-001",
                "message": {
                    "sender": "scammer",
                    "text": "Test message",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 401
        print(f"\n✅ Correctly rejected request without API key")

    def test_03_invalid_api_key(self):
        """Request with invalid API key should fail"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": "invalid-key-123"},
            json={
                "sessionId": "remote-test-002",
                "message": {
                    "sender": "scammer",
                    "text": "Test message",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 401
        print(f"\n✅ Correctly rejected invalid API key")

    def test_04_valid_api_key(self):
        """Request with valid API key should succeed"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-test-003",
                "message": {
                    "sender": "scammer",
                    "text": "Your account will be blocked",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "reply" in data
        print(f"\n✅ Valid API key accepted, got response: {data['reply'][:50]}...")


class TestRemoteScamScenarios:
    """Test all scam scenarios against remote server"""

    def test_05_bank_fraud_urgency(self):
        """Test Case 1: Bank Fraud with Urgency"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-bank-001",
                "message": {
                    "sender": "scammer",
                    "text": "URGENT: Your SBI bank account 123456789012 will be blocked today. Call customer care immediately at +919876543210 to verify your identity.",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert len(data["reply"]) > 0
        print(f"\n✅ Bank fraud detected, reply: {data['reply']}")

    def test_06_upi_fraud(self):
        """Test Case 2: UPI Fraud"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-upi-001",
                "message": {
                    "sender": "scammer",
                    "text": "Your UPI payment failed. To reactivate, send Rs.1 to scammer123@paytm and share the transaction ID.",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"\n✅ UPI fraud detected, reply: {data['reply']}")

    def test_07_phishing_link(self):
        """Test Case 3: Phishing Link"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-phish-001",
                "message": {
                    "sender": "scammer",
                    "text": "Your account has been compromised. Click here immediately to secure it: http://fake-bank-security.com/verify?user=12345",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"\n✅ Phishing detected, reply: {data['reply']}")

    def test_08_otp_request_scam(self):
        """Test Case 5: OTP Request Scam"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-otp-001",
                "message": {
                    "sender": "scammer",
                    "text": "This is HDFC Bank. We have detected suspicious activity. Please share the OTP sent to your mobile to verify.",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        print(f"\n✅ OTP scam detected, reply: {data['reply']}")


class TestRemoteMultiTurn:
    """Test multi-turn conversations on remote server"""

    def test_09_three_turn_conversation(self):
        """Test 3-turn conversation with context"""
        session_id = "remote-multi-001"
        conversation_history = []

        messages = [
            "Your account will be blocked in 2 hours due to failed KYC verification.",
            "To verify, please share your account number and registered mobile number.",
            "The system shows incomplete verification. Also share the OTP that was just sent: 123456"
        ]

        for i, msg in enumerate(messages):
            response = requests.post(
                f"{BASE_URL}/api/v1/conversation",
                headers={"x-api-key": API_KEY},
                json={
                    "sessionId": session_id,
                    "message": {
                        "sender": "scammer",
                        "text": msg,
                        "timestamp": int(time.time() * 1000) + (i * 1000)
                    },
                    "conversationHistory": conversation_history.copy()
                },
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            reply = data["reply"]
            print(f"\n✅ Turn {i+1} - Scammer: {msg[:50]}...")
            print(f"   Agent: {reply}")

            # Update history
            conversation_history.append({
                "sender": "scammer",
                "text": msg,
                "timestamp": int(time.time() * 1000) + (i * 1000)
            })
            conversation_history.append({
                "sender": "user",
                "text": reply,
                "timestamp": int(time.time() * 1000) + (i * 1000) + 500
            })

            # Small delay between requests
            time.sleep(1)

    def test_10_five_turn_conversation(self):
        """Test 5-turn conversation maintaining context"""
        session_id = "remote-multi-002"
        conversation_history = []

        messages = [
            "Your UPI is temporarily blocked due to security reasons.",
            "We need to verify your UPI ID. What is your UPI ID?",
            "To unblock, send Re.1 to this UPI: support@paytm and share the transaction ID.",
            "This is official procedure. Call our helpline: 7654321098",
            "Do it now or lose access permanently."
        ]

        for i, msg in enumerate(messages):
            response = requests.post(
                f"{BASE_URL}/api/v1/conversation",
                headers={"x-api-key": API_KEY},
                json={
                    "sessionId": session_id,
                    "message": {
                        "sender": "scammer",
                        "text": msg,
                        "timestamp": int(time.time() * 1000) + (i * 1000)
                    },
                    "conversationHistory": conversation_history.copy()
                },
                timeout=TIMEOUT
            )
            assert response.status_code == 200
            data = response.json()
            reply = data["reply"]
            print(f"\n✅ Turn {i+1} - Agent: {reply}")

            # Update history
            conversation_history.append({
                "sender": "scammer",
                "text": msg,
                "timestamp": int(time.time() * 1000) + (i * 1000)
            })
            conversation_history.append({
                "sender": "user",
                "text": reply,
                "timestamp": int(time.time() * 1000) + (i * 1000) + 500
            })

            # Delay between requests
            time.sleep(1)


class TestRemotePersonaValidation:
    """Test persona validation on remote server"""

    def test_11_short_natural_responses(self):
        """Responses should be short and natural"""
        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-persona-001",
                "message": {
                    "sender": "scammer",
                    "text": "Your account will be blocked",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        reply = response.json()["reply"]
        assert len(reply) < 200, f"Response too long ({len(reply)} chars): {reply}"
        print(f"\n✅ Response length: {len(reply)} chars - {reply}")

    def test_12_no_bookish_language(self):
        """Should NOT use formal/bookish words"""
        forbidden_words = [
            "facilitate", "assist", "proceed", "kindly",
            "nevertheless", "furthermore", "authenticate"
        ]

        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-persona-002",
                "message": {
                    "sender": "scammer",
                    "text": "You need to verify your account immediately",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        reply = response.json()["reply"].lower()

        found_forbidden = [word for word in forbidden_words if word.lower() in reply]
        assert len(found_forbidden) == 0, f"Found bookish words: {found_forbidden} in: {reply}"
        print(f"\n✅ No bookish language: {reply}")

    def test_13_no_bot_mentions(self):
        """Should NEVER reveal it's a bot"""
        bot_words = ["bot", "ai", "artificial", "automated", "system"]

        response = requests.post(
            f"{BASE_URL}/api/v1/conversation",
            headers={"x-api-key": API_KEY},
            json={
                "sessionId": "remote-persona-003",
                "message": {
                    "sender": "scammer",
                    "text": "Are you a real person?",
                    "timestamp": int(time.time() * 1000)
                },
                "conversationHistory": []
            },
            timeout=TIMEOUT
        )
        reply = response.json()["reply"].lower()

        found_bot_words = [word for word in bot_words if word in reply]
        assert len(found_bot_words) == 0, f"Found bot words: {found_bot_words} in: {reply}"
        print(f"\n✅ No bot mentions: {reply}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "-s"])
