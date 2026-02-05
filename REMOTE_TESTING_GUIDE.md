# Remote Testing Guide - Render Deployment

## 🎯 Overview

This guide covers comprehensive testing of your Honeypot deployment on Render, including **intelligence extraction validation**.

---

## 🚀 Quick Start

### Run All Remote Tests

```bash
python run_remote_tests.py
```

This will:
1. Check if Render service is accessible
2. Run all 27 tests against production
3. Validate intelligence extraction capabilities
4. Provide comprehensive test report

---

## 📋 What Gets Tested (28 Tests Total)

### 1. Authentication Tests (4 tests)
- ✅ Health check without auth
- ✅ Missing API key rejection
- ✅ Invalid API key rejection
- ✅ Valid API key acceptance

### 2. Scam Scenario Tests (4 tests)
- ✅ Bank fraud with urgency
- ✅ UPI fraud detection
- ✅ Phishing link detection
- ✅ OTP request scam

### 3. Multi-Turn Conversations (2 tests)
- ✅ 3-turn conversation with context
- ✅ 5-turn conversation maintaining context

### 4. Persona Validation (3 tests)
- ✅ Short natural responses (< 200 chars)
- ✅ No bookish language
- ✅ Never reveals it's a bot

### 5. Intelligence Extraction - Bank Accounts (2 tests)
- ✅ Single bank account extraction
- ✅ Multiple bank accounts extraction

### 6. Intelligence Extraction - UPI IDs (2 tests)
- ✅ Paytm UPI extraction
- ✅ PhonePe/YBL UPI extraction

### 7. Intelligence Extraction - Phone Numbers (2 tests)
- ✅ Single phone number extraction
- ✅ Multiple phone numbers extraction

### 8. Intelligence Extraction - Emails (1 test)
- ✅ Email address extraction

### 9. Intelligence Extraction - Links (1 test)
- ✅ Phishing URL extraction

### 10. Intelligence Extraction - Amounts (1 test)
- ✅ Monetary amounts (Rs., ₹) extraction

### 11. Intelligence Extraction - Comprehensive (1 test)
- ✅ All 9 types from single message

### 12. Strategic Agent Extraction (3 tests)
- ✅ Phase 1: Agent builds trust (first 1-3 messages)
- ✅ Phase 2: Agent gradually extracts info (messages 4-6)
- ✅ Phase 3: Agent comfortable extraction (messages 7+)

### 13. Conversation History Maintenance (1 test) **CRITICAL**
- ✅ History maintained without client sending conversationHistory (GUVI bug fix)

### 14. Multi-Turn Intelligence (1 test)
- ✅ Intelligence accumulation across conversation turns

---

## 🔧 Configuration

### Option 1: Use .env File

Add to your `.env`:
```bash
RENDER_URL=https://your-service.onrender.com
API_KEY=J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM
```

Then run:
```bash
python run_remote_tests.py
```

### Option 2: Command Line Arguments

```bash
python run_remote_tests.py --url https://your-service.onrender.com --api-key YOUR_KEY
```

### Option 3: Interactive Prompt

If no configuration is found, the script will prompt you:
```bash
python run_remote_tests.py
# Will prompt for URL and API key
```

---

## 📊 Test Output Example

```
🧪 HONEYPOT REMOTE TESTING - RENDER DEPLOYMENT
==================================================================

Test Target: https://scambot-honeypot-abc123.onrender.com
API Key: ********************QAM
Started: 2026-02-05 14:30:00

ℹ️  Checking if Render service is accessible...
✅ Render service is accessible: {'status': 'healthy', ...}

ℹ️  Running remote API tests...

tests/test_remote_api.py::TestRemoteAPIAuthentication::test_01_health_check_no_auth PASSED
✅ Health check: {'status': 'healthy', ...}

tests/test_remote_api.py::TestRemoteAPIAuthentication::test_04_valid_api_key PASSED
✅ Valid API key accepted, got response: Oh god what happened? Is my money safe?...

tests/test_remote_api.py::TestRemoteIntelligenceExtractionBankAccounts::test_14_extract_single_bank_account PASSED
✅ Test passed - bank account extraction on remote server

tests/test_remote_api.py::TestRemoteAgentExtractsScammerInfo::test_24_agent_asks_for_scammer_details PASSED
✅ Agent Phase 1 response (builds trust): oh my god! what happened beta?...

... (27 tests total)

📊 REMOTE TEST SUMMARY
==================================================================

Test Duration: 245.67 seconds
Target: https://scambot-honeypot-abc123.onrender.com

🎉 ALL REMOTE TESTS PASSED!
Your Render deployment is working perfectly!

✅ What was validated on production:
  • API Authentication (x-api-key)
  • Scam detection (bank, UPI, phishing, OTP)
  • Multi-turn conversations (3-turn, 5-turn)
  • Persona validation (realistic responses)
  • Intelligence extraction (9 types: bank accounts, UPI IDs,
    phones, emails, amounts, employee IDs, links, impersonation targets)
  • Strategic 3-phase extraction (build trust → gradual → comfortable)
  • Agent proactive information gathering
  • Response format compliance
  • No bookish language
  • Agent never reveals it's a bot

🚀 Production Status:
  ✅ Ready for GUVI submission
  ✅ Ready for teammate testing
  ✅ Production-ready

📤 Submit to GUVI:
  x-api-key: J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM
  Endpoint URL: https://your-service.onrender.com/api/v1/conversation
```

---

## 🎯 Intelligence Extraction Validation

### What Gets Extracted and Tested:

**1. Bank Account Numbers:**
```
Input: "Transfer to account 123456789012"
Extracts: ["123456789012"]
```

**2. UPI IDs:**
```
Input: "Send Rs.1 to scammer@paytm"
Extracts: ["scammer@paytm"]
```

**3. Phone Numbers:**
```
Input: "Call +919876543210"
Extracts: ["+919876543210"]
```

**4. Email Addresses:**
```
Input: "Contact support@scam.com"
Extracts: ["support@scam.com"]
```

**5. Monetary Amounts:**
```
Input: "Pay Rs.500 processing fee"
Extracts: ["Rs.500"]
```

**6. Employee IDs:**
```
Input: "My employee ID is EMP12345"
Extracts: ["EMP12345"]
```

**7. Phishing Links:**
```
Input: "Visit http://fake-bank.com"
Extracts: ["http://fake-bank.com"]
```

**8. Impersonation Targets:**
```
Input: "This is SBI Bank calling"
Extracts: ["SBI"]
```

**9. Scam Tactics:**
```
Input: "Urgent! Account blocked! Send OTP!"
Extracts: ["URGENCY_TACTICS", "THREAT_TACTICS", "CREDENTIAL_REQUEST"]
```

---

## 🎭 Strategic Extraction Phases

### Phase 1: Build Trust (Messages 1-3)
**Agent Behavior:**
- Shows genuine fear/worry
- Expresses confusion but willingness
- Does NOT ask for credentials yet
- Builds scammer's confidence

**Example:**
```
Scammer: "Your account will be blocked"
Agent: "Oh god what happened? Is my money safe? I am so worried"
```

### Phase 2: Gradual Extraction (Messages 4-6)
**Agent Behavior:**
- Shows willingness to comply
- Asks "innocent" clarifying questions
- Extracts info naturally through confusion
- Makes scammer explain everything

**Example:**
```
Scammer: "Send me the OTP"
Agent: "Ok I will send. But my grandson will ask who I sent to. What is your name beta?"
```

### Phase 3: Comfortable Extraction (Messages 7+)
**Agent Behavior:**
- Scammer thinks they've won
- Agent asks for details "to do it right"
- Be grateful for their "help"
- Extract freely through natural chat

**Example:**
```
Scammer: "Good, now do it quickly"
Agent: "Thank you for helping me beta. What is your employee number? I will tell bank later"
```

---

## 🧪 Test Files

### Primary Test File
- **tests/test_remote_api.py** - All 27 remote tests

### Test Runner
- **run_remote_tests.py** - Automated test execution

### Related Files
- **tests/test_intelligence_extraction.py** - Local intelligence tests
- **run_all_tests.py** - Local test runner

---

## ⚠️ Common Issues

### Issue 1: Render Service Sleeping
**Symptom:** Tests timeout or fail to connect

**Solution:**
1. Check Render dashboard - service may be sleeping
2. Wait for UptimeRobot to wake it (check your UptimeRobot config)
3. Manually access health endpoint in browser: `https://your-service.onrender.com/health`

### Issue 2: OpenAI Rate Limits
**Symptom:** Some tests pass, some fail with timeouts

**Solution:**
1. Wait a few minutes (rate limit cooldown)
2. Run tests again
3. Check OpenAI API credits/limits

### Issue 3: First Test Slow
**Symptom:** First few tests take 30+ seconds

**Solution:**
- This is normal - Render cold start
- Subsequent tests will be faster
- Just wait for completion

---

## 📈 Success Criteria

**All 27 tests must pass for production readiness:**

✅ Authentication working
✅ All scam scenarios detected
✅ Multi-turn conversations working
✅ Persona maintained (no bot reveals)
✅ Intelligence extracted (all 9 types)
✅ Strategic 3-phase extraction working
✅ Agent proactive questioning validated
✅ No bookish language
✅ Short, natural responses

---

## 🚀 After Tests Pass

### 1. For GUVI Submission
Use these details:
```
Endpoint URL: https://your-service.onrender.com/api/v1/conversation
x-api-key: J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM
```

### 2. For Teammate Testing
Share:
```
Base URL: https://your-service.onrender.com
API Key: J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM

Postman Collection: POSTMAN_TESTING_GUIDE.md
API Documentation: API_DOCUMENTATION.md
```

### 3. For Production Use
Your Render deployment is:
- ✅ Validated against all requirements
- ✅ Intelligence extraction confirmed working
- ✅ Strategic agent behavior validated
- ✅ Ready for real scammer engagement

---

## 📝 Summary

**Remote testing validates:**
1. Production deployment works correctly
2. All 9 intelligence extraction types functional
3. Strategic 3-phase agent behavior validated
4. Multi-turn conversation context maintained
5. Persona realistic and believable
6. Ready for GUVI submission and team testing

**Run the tests:**
```bash
python run_remote_tests.py
```

**Your honeypot is production-ready!** 🎉
