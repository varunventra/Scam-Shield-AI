# Test Input Examples - Scambot Honeypot API

## 📋 Ready-to-Use Test Cases

### Base URL
```
http://localhost:8000/api/v1/conversation
```

### Required Headers
```
x-api-key: hackathon-secret-key-2024
Content-Type: application/json
```

---

## 🧪 Test Case 1: Bank Fraud with Urgency

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-bank-fraud-001",
    "message": {
      "sender": "scammer",
      "text": "URGENT: Your SBI bank account 123456789012 will be blocked today. Call customer care immediately at +919876543210 to verify your identity.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Expected:** Agent responds with concern/questions, extracts phone and account numbers.

---

## 🧪 Test Case 2: UPI Fraud

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-upi-fraud-001",
    "message": {
      "sender": "scammer",
      "text": "Your UPI payment failed. To reactivate, send Rs.1 to scammer123@paytm and share the transaction ID.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "WhatsApp",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Expected:** Agent asks questions, extracts UPI ID.

---

## 🧪 Test Case 3: Phishing Link

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-phishing-001",
    "message": {
      "sender": "scammer",
      "text": "Your account has been compromised. Click here immediately to secure it: http://fake-bank-security.com/verify?user=12345&session=abc",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "Email",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Expected:** Agent expresses concern, extracts phishing URL.

---

## 🧪 Test Case 4: Lottery/Prize Scam

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-lottery-001",
    "message": {
      "sender": "scammer",
      "text": "Congratulations Rahul! You have won 50 Lakh rupees in the KBC Lucky Draw 2024. To claim your prize, share your bank account details and PAN card number. Contact: winner@kbc-prize.com or call 8765432109.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Expected:** Agent shows excitement/interest, extracts email and phone.

---

## 🧪 Test Case 5: OTP Request Scam

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-otp-001",
    "message": {
      "sender": "scammer",
      "text": "This is HDFC Bank. We have detected suspicious activity on your account. An OTP has been sent to your mobile. Please share it to verify your identity and prevent account suspension.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "Call",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Expected:** Agent asks why OTP is needed, shows hesitation.

---

## 🧪 Test Case 6: KYC Update Scam

```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "test-kyc-001",
    "message": {
      "sender": "scammer",
      "text": "Dear customer, your KYC will expire today. Update immediately at http://bank-kyc-update.in or your account will be blocked. Provide: PAN card, Aadhaar number, and bank account details.",
      "timestamp": 1770005528731
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

**Expected:** Agent asks about legitimacy, extracts URL.

---

## 🔄 Multi-Turn Conversation Examples

### Example A: 3-Turn Bank Fraud Conversation

#### Turn 1:
```json
{
  "sessionId": "multi-turn-bank-001",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked in 2 hours due to failed KYC verification.",
    "timestamp": 1770005528000
  },
  "conversationHistory": []
}
```

#### Turn 2:
```json
{
  "sessionId": "multi-turn-bank-001",
  "message": {
    "sender": "scammer",
    "text": "To verify, please share your account number and registered mobile number.",
    "timestamp": 1770005529000
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your account will be blocked in 2 hours due to failed KYC verification.",
      "timestamp": 1770005528000
    },
    {
      "sender": "user",
      "text": "Why is my account being blocked? I recently updated my KYC.",
      "timestamp": 1770005528500
    }
  ]
}
```

#### Turn 3:
```json
{
  "sessionId": "multi-turn-bank-001",
  "message": {
    "sender": "scammer",
    "text": "The system shows incomplete verification. Also share the OTP that was just sent to your mobile: 123456",
    "timestamp": 1770005530000
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your account will be blocked in 2 hours due to failed KYC verification.",
      "timestamp": 1770005528000
    },
    {
      "sender": "user",
      "text": "Why is my account being blocked? I recently updated my KYC.",
      "timestamp": 1770005528500
    },
    {
      "sender": "scammer",
      "text": "To verify, please share your account number and registered mobile number.",
      "timestamp": 1770005529000
    },
    {
      "sender": "user",
      "text": "How do I know this is really from the bank? Can you tell me my account details?",
      "timestamp": 1770005529500
    }
  ]
}
```

---

### Example B: 5-Turn UPI Scam Conversation

#### Turn 1:
```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "multi-turn-upi-001",
    "message": {
      "sender": "scammer",
      "text": "Your UPI is temporarily blocked due to security reasons.",
      "timestamp": 1770005528000
    },
    "conversationHistory": []
  }'
```

#### Turn 2:
```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "multi-turn-upi-001",
    "message": {
      "sender": "scammer",
      "text": "We need to verify your UPI ID. What is your UPI ID?",
      "timestamp": 1770005529000
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your UPI is temporarily blocked due to security reasons.",
        "timestamp": 1770005528000
      },
      {
        "sender": "user",
        "text": "Why is it blocked? I was using it just this morning.",
        "timestamp": 1770005528500
      }
    ]
  }'
```

#### Turn 3:
```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "multi-turn-upi-001",
    "message": {
      "sender": "scammer",
      "text": "To unblock, send Re.1 to this UPI: support@paytm and share the transaction ID.",
      "timestamp": 1770005530000
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your UPI is temporarily blocked due to security reasons.",
        "timestamp": 1770005528000
      },
      {
        "sender": "user",
        "text": "Why is it blocked? I was using it just this morning.",
        "timestamp": 1770005528500
      },
      {
        "sender": "scammer",
        "text": "We need to verify your UPI ID. What is your UPI ID?",
        "timestamp": 1770005529000
      },
      {
        "sender": "user",
        "text": "How do I know you are from the bank? This seems suspicious.",
        "timestamp": 1770005529500
      }
    ]
  }'
```

#### Turn 4:
```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "multi-turn-upi-001",
    "message": {
      "sender": "scammer",
      "text": "This is official procedure. Your account will remain blocked if you do not comply. Call our helpline: 7654321098",
      "timestamp": 1770005531000
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your UPI is temporarily blocked due to security reasons.",
        "timestamp": 1770005528000
      },
      {
        "sender": "user",
        "text": "Why is it blocked? I was using it just this morning.",
        "timestamp": 1770005528500
      },
      {
        "sender": "scammer",
        "text": "We need to verify your UPI ID. What is your UPI ID?",
        "timestamp": 1770005529000
      },
      {
        "sender": "user",
        "text": "How do I know you are from the bank? This seems suspicious.",
        "timestamp": 1770005529500
      },
      {
        "sender": "scammer",
        "text": "To unblock, send Re.1 to this UPI: support@paytm and share the transaction ID.",
        "timestamp": 1770005530000
      },
      {
        "sender": "user",
        "text": "Why do I need to send money? Banks never ask for money from customers.",
        "timestamp": 1770005530500
      }
    ]
  }'
```

#### Turn 5:
```bash
curl -X POST "http://localhost:8000/api/v1/conversation" \
  -H "x-api-key: hackathon-secret-key-2024" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "multi-turn-upi-001",
    "message": {
      "sender": "scammer",
      "text": "It is just for verification. You will get your money back instantly. Do it now or lose access permanently.",
      "timestamp": 1770005532000
    },
    "conversationHistory": [
      {
        "sender": "scammer",
        "text": "Your UPI is temporarily blocked due to security reasons.",
        "timestamp": 1770005528000
      },
      {
        "sender": "user",
        "text": "Why is it blocked? I was using it just this morning.",
        "timestamp": 1770005528500
      },
      {
        "sender": "scammer",
        "text": "We need to verify your UPI ID. What is your UPI ID?",
        "timestamp": 1770005529000
      },
      {
        "sender": "user",
        "text": "How do I know you are from the bank? This seems suspicious.",
        "timestamp": 1770005529500
      },
      {
        "sender": "scammer",
        "text": "To unblock, send Re.1 to this UPI: support@paytm and share the transaction ID.",
        "timestamp": 1770005530000
      },
      {
        "sender": "user",
        "text": "Why do I need to send money? Banks never ask for money from customers.",
        "timestamp": 1770005530500
      },
      {
        "sender": "scammer",
        "text": "This is official procedure. Your account will remain blocked if you do not comply. Call our helpline: 7654321098",
        "timestamp": 1770005531000
      },
      {
        "sender": "user",
        "text": "I dont understand this process. Can you explain more?",
        "timestamp": 1770005531500
      }
    ]
  }'
```

---

## 🧪 Test Case 7: Investment Scam

```json
{
  "sessionId": "test-investment-001",
  "message": {
    "sender": "scammer",
    "text": "Limited time offer! Invest Rs.10,000 today and get Rs.50,000 in 30 days. Guaranteed returns. Transfer to account: 998877665544 or UPI: invest@guaranteed.com. WhatsApp: +918888777766",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "WhatsApp",
    "language": "English",
    "locale": "IN"
  }
}
```

---

## 🧪 Test Case 8: Fake Delivery Scam

```json
{
  "sessionId": "test-delivery-001",
  "message": {
    "sender": "scammer",
    "text": "Your courier package is held at customs. Pay Rs.500 clearance fee to: delivery@courier-india.com or account 556677889900. Track at: http://fake-courier-track.com/track?id=ABC123",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "Email",
    "language": "English",
    "locale": "IN"
  }
}
```

---

## 🧪 Test Case 9: Job Offer Scam

```json
{
  "sessionId": "test-job-001",
  "message": {
    "sender": "scammer",
    "text": "Congratulations! You are selected for Google Software Engineer position with 25 LPA salary. Pay Rs.5000 registration fee to: hr@google-recruitment.co.in or UPI: googlehr@paytm. Contact HR: +917777888899",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "Email",
    "language": "English",
    "locale": "IN"
  }
}
```

---

## 🧪 Test Case 10: Tax Refund Scam

```json
{
  "sessionId": "test-tax-001",
  "message": {
    "sender": "scammer",
    "text": "Income Tax Department: You are eligible for Rs.35,000 tax refund. Click to claim: http://incometax-refund-india.com/claim?pan=ABCD1234E. Provide your bank details, PAN, and Aadhaar to process refund.",
    "timestamp": 1770005528731
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

---

## 📊 Complete Test Suite (JSON Format)

Save this as `test_cases.json`:

```json
{
  "test_cases": [
    {
      "name": "Bank Fraud",
      "sessionId": "test-001",
      "message": {
        "sender": "scammer",
        "text": "URGENT: Your SBI account will be blocked. Call 9876543210.",
        "timestamp": 1770005528731
      },
      "conversationHistory": []
    },
    {
      "name": "UPI Fraud",
      "sessionId": "test-002",
      "message": {
        "sender": "scammer",
        "text": "Send Rs.1 to scammer@paytm to verify UPI.",
        "timestamp": 1770005528731
      },
      "conversationHistory": []
    },
    {
      "name": "Phishing Link",
      "sessionId": "test-003",
      "message": {
        "sender": "scammer",
        "text": "Verify account: http://fake-bank.com/verify",
        "timestamp": 1770005528731
      },
      "conversationHistory": []
    },
    {
      "name": "Lottery Scam",
      "sessionId": "test-004",
      "message": {
        "sender": "scammer",
        "text": "You won 50 Lakh! Share bank details. Call 8765432109.",
        "timestamp": 1770005528731
      },
      "conversationHistory": []
    },
    {
      "name": "OTP Request",
      "sessionId": "test-005",
      "message": {
        "sender": "scammer",
        "text": "Share OTP to verify identity and prevent suspension.",
        "timestamp": 1770005528731
      },
      "conversationHistory": []
    }
  ]
}
```

---

## 🔧 Postman Collection

Import this into Postman:

```json
{
  "info": {
    "name": "Scambot Honeypot API",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Health Check",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/health",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["health"]
        }
      }
    },
    {
      "name": "Bank Fraud Test",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "x-api-key",
            "value": "hackathon-secret-key-2024"
          },
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"sessionId\": \"test-bank-001\",\n  \"message\": {\n    \"sender\": \"scammer\",\n    \"text\": \"Your account will be blocked. Call 9876543210.\",\n    \"timestamp\": 1770005528731\n  },\n  \"conversationHistory\": []\n}"
        },
        "url": {
          "raw": "http://localhost:8000/api/v1/conversation",
          "protocol": "http",
          "host": ["localhost"],
          "port": "8000",
          "path": ["api", "v1", "conversation"]
        }
      }
    }
  ]
}
```

---

## 💡 Tips for Testing

1. **Start Simple**: Test single messages first
2. **Test Multi-turn**: Build up conversation history gradually
3. **Vary Scam Types**: Try different fraud scenarios
4. **Check Intelligence**: Verify extracted bank accounts, UPIs, phones
5. **Test Agent Behavior**: Responses should be human-like
6. **Monitor Logs**: Watch console for scam detection confidence scores

---

## 🎯 Expected Behavior

- ✅ Agent responds naturally (never says "I'm a bot")
- ✅ Extracts intelligence (accounts, UPIs, phones, URLs)
- ✅ Maintains context in multi-turn conversations
- ✅ Shows appropriate concern/curiosity
- ✅ Response time < 5 seconds

---

**Save this file and use these examples to thoroughly test your API!**
