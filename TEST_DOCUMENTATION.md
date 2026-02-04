# Test Documentation - Scambot Honeypot API

## Overview

Comprehensive test suite with **25 tests** covering all requirements from the GUVI hackathon problem statement.

## Test Coverage

### 1. API Authentication (Tests 1-3)
- ✅ Test 1: Missing API key returns 401
- ✅ Test 2: Invalid API key returns 401
- ✅ Test 3: Valid API key succeeds

### 2. Scam Detection (Tests 4-8)
- ✅ Test 4: Bank fraud detection with urgency tactics
- ✅ Test 5: UPI fraud detection
- ✅ Test 6: Phishing link detection
- ✅ Test 7: Lottery/prize scam detection
- ✅ Test 8: OTP/credentials request scam detection

### 3. Multi-turn Conversations (Tests 9-14) ⭐ CRITICAL
**This is a CRITICAL requirement from the problem statement**

- ✅ Test 9: 2-turn conversation with context
- ✅ Test 10: 5-turn conversation maintaining context
- ✅ Test 11: Context retention across messages
- ✅ Test 12: 10-turn extended conversation
- ✅ Test 13: First message (empty history)
- ✅ Test 14: Multi-turn across different channels

### 4. Intelligence Extraction (Tests 15-17)
- ✅ Test 15: Extract bank account numbers
- ✅ Test 16: Extract UPI IDs
- ✅ Test 17: Extract phone numbers

### 5. Response Format (Tests 18-19)
- ✅ Test 18: Response structure compliance
- ✅ Test 19: Human-like replies (no bot/AI mentions)

### 6. Edge Cases & Errors (Tests 20-22)
- ✅ Test 20: Missing required fields
- ✅ Test 21: Invalid session ID
- ✅ Test 22: Health endpoint without auth

### 7. API Endpoints (Tests 23-25)
- ✅ Test 23: Root endpoint
- ✅ Test 24: Admin cleanup
- ✅ Test 25: CORS headers

## Running Tests

### Quick Run
```bash
python run_tests.py
```

### Using pytest directly
```bash
# Run all tests
pytest tests/test_api.py -v

# Run specific test class
pytest tests/test_api.py::TestMultiTurnConversations -v

# Run specific test
pytest tests/test_api.py::TestMultiTurnConversations::test_10_five_turn_conversation -v

# Run with coverage
pytest tests/test_api.py --cov=app --cov-report=html

# Run and stop on first failure
pytest tests/test_api.py -x

# Run in parallel (faster)
pytest tests/test_api.py -n auto
```

### Using pytest with filters
```bash
# Run only multi-turn conversation tests
pytest tests/test_api.py -k "multi" -v

# Run only scam detection tests
pytest tests/test_api.py -k "scam" -v

# Run only authentication tests
pytest tests/test_api.py -k "auth" -v
```

## Prerequisites

1. **OpenAI API Key**: Set in `.env` file
2. **API Key**: Set in `.env` file
3. **Dependencies**: Install with `pip install -r requirements.txt`
4. **Server**: API must be importable (doesn't need to be running)

## Test Requirements Mapping

Each test directly maps to problem statement requirements:

| Requirement | Tests | Status |
|-------------|-------|--------|
| Detect scam messages | 4-8 | ✅ |
| Handle multi-turn conversations | 9-14 | ✅ |
| Maintain human-like persona | 18-19 | ✅ |
| Extract intelligence | 15-17 | ✅ |
| API authentication | 1-3 | ✅ |
| Response format compliance | 18 | ✅ |
| Error handling | 20-22 | ✅ |

## Multi-turn Conversation Tests (Critical)

The problem statement specifically requires handling **multi-turn conversations**. We have 6 dedicated tests:

```python
# Example: 5-turn conversation
conversation_history = []
for each_message in messages:
    response = api.post(message, conversation_history)
    conversation_history.append(scammer_message)
    conversation_history.append(agent_response)
```

Tests verify:
- ✓ Context is maintained across turns
- ✓ Agent responds appropriately to previous messages
- ✓ Conversation history is properly used
- ✓ Agent doesn't lose track of the conversation
- ✓ Works across 2, 5, and 10 turn conversations

## Expected Test Results

All tests should pass with output like:

```
tests/test_api.py::TestAPIAuthentication::test_01_missing_api_key PASSED
tests/test_api.py::TestAPIAuthentication::test_02_invalid_api_key PASSED
tests/test_api.py::TestAPIAuthentication::test_03_valid_api_key PASSED
tests/test_api.py::TestScamDetection::test_04_bank_fraud_detection PASSED
tests/test_api.py::TestScamDetection::test_05_upi_fraud_detection PASSED
...
tests/test_api.py::TestMultiTurnConversations::test_12_ten_turn_extended_conversation PASSED
...
======================== 25 passed in 45.23s ========================
```

## Troubleshooting

### Import Errors
```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
# or on Windows:
set PYTHONPATH=%PYTHONPATH%;%CD%
```

### OpenAI API Errors
- Check `.env` has valid `OPENAI_API_KEY`
- Verify API quota/billing is active
- Test: `python -c "from app.core.config import settings; print(settings.openai_api_key)"`

### Slow Tests
Multi-turn tests call OpenAI API multiple times. To speed up:
- Use `gpt-3.5-turbo` instead of `gpt-4o` for testing
- Reduce `MAX_TOKENS` in `.env`
- Mock OpenAI responses (advanced)

### Test Timeouts
If tests timeout:
```bash
pytest tests/test_api.py --timeout=300  # 5 minute timeout per test
```

## Test Data Examples

### Valid Scam Messages Used in Tests
- "Your bank account will be blocked today"
- "Send 1 rupee to verify your UPI: scammer@paytm"
- "Click here to verify: http://fake-bank-verify.com"
- "Congratulations! You won 10 Lakh rupees"
- "Share the OTP sent to your mobile"

### Valid API Request Format
```json
{
  "sessionId": "test-001",
  "message": {
    "sender": "scammer",
    "text": "Your account will be blocked",
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

### Expected Response Format
```json
{
  "status": "success",
  "reply": "Why is my account being blocked? This is concerning."
}
```

## CI/CD Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python run_tests.py
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          API_KEY: test-key-for-ci
```

## Performance Benchmarks

Average test execution times (with OpenAI API calls):

- Authentication tests: ~0.1s each
- Scam detection tests: ~2-3s each (OpenAI API)
- Multi-turn tests: ~5-15s each (multiple OpenAI calls)
- Intelligence extraction: ~2-3s each
- Edge cases: ~0.1s each

**Total estimated time: 2-3 minutes** for full test suite

## Test Coverage Goals

- ✅ Code coverage: >80%
- ✅ API endpoints: 100%
- ✅ Error scenarios: 100%
- ✅ Problem statement requirements: 100%

## Notes for Hackathon Testers

Your API is exposed at: `POST /api/v1/conversation`

**Required Headers:**
```
x-api-key: your_api_key_here
Content-Type: application/json
```

**Test the multi-turn conversation capability:**
1. Send first message with empty `conversationHistory`
2. Send second message with previous messages in `conversationHistory`
3. Continue the conversation by always including full history
4. Agent should maintain context and engage naturally

**Example test sequence:**
```bash
# Message 1
curl -X POST "http://your-api/api/v1/conversation" \
  -H "x-api-key: your_key" \
  -d '{"sessionId":"test1","message":{"sender":"scammer","text":"Your account will be blocked","timestamp":1770005528731},"conversationHistory":[]}'

# Message 2 (include previous exchange in history)
curl -X POST "http://your-api/api/v1/conversation" \
  -H "x-api-key: your_key" \
  -d '{"sessionId":"test1","message":{"sender":"scammer","text":"Share your OTP","timestamp":1770005529731},"conversationHistory":[{"sender":"scammer","text":"Your account will be blocked","timestamp":1770005528731},{"sender":"user","text":"Why is my account being blocked?","timestamp":1770005528831}]}'
```

---

**Ready for evaluation!** All 25 tests validate the complete problem statement requirements.
