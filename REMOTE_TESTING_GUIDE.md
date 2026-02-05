# Remote Testing Guide - Test Your Render Deployment

## 🎯 Test Your Production Render Service

This guide shows you how to run automated tests against your **deployed Render service** (not localhost).

---

## 🚀 Quick Start

### Step 1: Add Render URL to .env

Edit your `.env` file and add:

```bash
# Add this line to your .env file
RENDER_URL=https://your-service-name.onrender.com
```

Replace `your-service-name` with your actual Render service name.

### Step 2: Run Remote Tests

```bash
python run_remote_tests.py
```

That's it! The script will:
1. ✅ Check if Render service is accessible
2. ✅ Run all tests against production
3. ✅ Show detailed results
4. ✅ Confirm if ready for submission

---

## 📋 What Gets Tested (Remote)

### Tests Against Your Render Deployment:

**Authentication Tests (4 tests):**
- ✅ Health check (no auth required)
- ✅ Missing API key (should fail)
- ✅ Invalid API key (should fail)
- ✅ Valid API key (should succeed)

**Scam Scenario Tests (4 tests):**
- ✅ Bank fraud with urgency
- ✅ UPI fraud
- ✅ Phishing link
- ✅ OTP request scam

**Multi-Turn Conversation Tests (2 tests):**
- ✅ 3-turn conversation with context
- ✅ 5-turn conversation maintaining context

**Persona Validation Tests (3 tests):**
- ✅ Short, natural responses (not bookish)
- ✅ No formal language
- ✅ Never reveals it's a bot

**Total: 13 production tests**

---

## 🔧 Alternative Usage

### Method 1: With Command Line Arguments

```bash
python run_remote_tests.py --url https://your-service.onrender.com --api-key YOUR_API_KEY
```

### Method 2: Interactive (Script Will Prompt)

```bash
python run_remote_tests.py
# Script will ask for URL and API key if not in .env
```

### Method 3: Just Test Specific File

```bash
# Set environment variables
set TEST_BASE_URL=https://your-service.onrender.com
set TEST_API_KEY=J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM

# Run specific test file
python -m pytest tests/test_remote_api.py -v -s
```

---

## ✅ Success Output

When all tests pass, you'll see:

```
🧪 HONEYPOT REMOTE TESTING - RENDER DEPLOYMENT

Test Target: https://your-service.onrender.com
API Key: ********************LQAM
Started: 2026-02-05 12:30:45

ℹ️  Checking if Render service is accessible...
✅ Render service is accessible: {'status': 'healthy', 'active_sessions': 0}

ℹ️  Running remote API tests...

tests/test_remote_api.py::TestRemoteAPIAuthentication::test_01_health_check_no_auth PASSED
✅ Health check: {'status': 'healthy', 'active_sessions': 0}

tests/test_remote_api.py::TestRemoteAPIAuthentication::test_02_missing_api_key PASSED
✅ Correctly rejected request without API key

tests/test_remote_api.py::TestRemoteAPIAuthentication::test_03_invalid_api_key PASSED
✅ Correctly rejected invalid API key

tests/test_remote_api.py::TestRemoteAPIAuthentication::test_04_valid_api_key PASSED
✅ Valid API key accepted, got response: What? Why my account will be blocked? I didnt do...

... (more tests) ...

======================================================================
📊 REMOTE TEST SUMMARY
======================================================================

Test Duration: 45.32 seconds
Target: https://your-service.onrender.com

🎉 ALL REMOTE TESTS PASSED!
Your Render deployment is working perfectly!

✅ What was validated on production:
  • API Authentication (x-api-key)
  • Scam detection (bank, UPI, phishing, OTP)
  • Multi-turn conversations (3-turn, 5-turn)
  • Persona validation (realistic responses)
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

## 🐛 Troubleshooting

### Issue: "Cannot reach Render service"

**Symptoms:**
```
❌ Cannot reach Render service at https://your-service.onrender.com
Error: Server not responding correctly
```

**Fixes:**
1. **Check URL is correct**
   - Go to Render Dashboard → Your Service
   - Copy the URL at the top
   - Make sure it's `https://something.onrender.com` (no trailing slash)

2. **Service might be sleeping (Free Tier)**
   - Visit the URL in your browser first: `https://your-service.onrender.com/health`
   - Wait 30-60 seconds for service to wake up
   - Then run tests again

3. **Check UptimeRobot is active**
   - UptimeRobot should be pinging `/health` every 5 minutes
   - Check UptimeRobot dashboard shows "Up"

4. **Check Render logs**
   - Go to Render Dashboard → Your Service → Logs
   - Look for errors or service stopped

### Issue: "Tests timing out"

**Symptoms:**
```
⚠️  Tests timed out (exceeded 10 minutes)
```

**Fixes:**
1. **OpenAI API slowness**
   - First run may be slower due to cold start
   - Run tests again - subsequent runs are faster

2. **Rate limits**
   - Check OpenAI API rate limits
   - Wait a few minutes and try again

3. **Service cold start**
   - Render free tier has cold starts
   - First request takes longer
   - Subsequent requests are fast

### Issue: "Some tests failed"

**Symptoms:**
```
❌ SOME REMOTE TESTS FAILED
```

**Fixes:**
1. **Check Render environment variables**
   - Go to Render Dashboard → Your Service → Environment
   - Verify `OPENAI_API_KEY` is set
   - Verify `API_KEY` matches what you're testing with

2. **Check Render logs**
   - Look for OpenAI API errors
   - Check for authentication failures
   - Verify model access

3. **Check OpenAI credits**
   - Visit https://platform.openai.com/account/billing
   - Ensure you have available credits
   - Check usage limits

---

## ⏱️ Expected Runtime

| Test Category | Tests | Time |
|---------------|-------|------|
| Authentication | 4 | ~5-10 seconds |
| Scam Scenarios | 4 | ~20-40 seconds |
| Multi-Turn | 2 | ~15-30 seconds |
| Persona | 3 | ~10-20 seconds |
| **TOTAL** | **13** | **~50-100 seconds** |

*Note: First run may be 2-3x slower due to Render cold start*

---

## 📊 Comparison: Local vs Remote

| Aspect | Local Tests | Remote Tests |
|--------|-------------|--------------|
| **Target** | localhost:8000 | Render deployment |
| **Tests** | 49 tests | 13 critical tests |
| **Runtime** | 2-3 minutes | 1-2 minutes |
| **When to Use** | Development | Before submission |
| **Command** | `python run_all_tests.py` | `python run_remote_tests.py` |

**Recommendation:** Run both!
1. **Local tests** during development to catch issues fast
2. **Remote tests** before submission to verify production

---

## 🎯 Before GUVI Submission

**Final Checklist:**

```bash
# 1. Test local (optional, for development)
python run_all_tests.py

# 2. Test remote (REQUIRED before submission)
python run_remote_tests.py

# 3. Verify all green checkmarks
# Should see: "🎉 ALL REMOTE TESTS PASSED!"

# 4. Check Render service is accessible
# Visit: https://your-service.onrender.com/health

# 5. Submit to GUVI with confidence!
```

---

## 📝 What to Share with Teammate

If your teammate wants to test your Render deployment:

**Give them:**
1. **Render URL:** `https://your-service.onrender.com`
2. **API Key:** `J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM`
3. **This file:** `POSTMAN_TESTING_GUIDE.md` (for manual Postman testing)

**Or they can run automated tests:**
```bash
python run_remote_tests.py --url https://your-service.onrender.com --api-key YOUR_KEY
```

---

## 💡 Tips

### Tip 1: Keep Service Warm
- UptimeRobot pings `/health` every 5 minutes
- Service won't sleep during testing
- First test request may still be slow (cold start)

### Tip 2: Run Tests Multiple Times
- First run: May be slower (cold start, OpenAI initialization)
- Second run: Much faster
- If first run fails, try again

### Tip 3: Monitor Render Logs
While tests run, watch Render logs in another window:
- Go to Render Dashboard → Your Service → Logs
- See real-time API requests and responses
- Helpful for debugging failures

### Tip 4: Test During Low Traffic
- Run tests when GUVI/others aren't testing
- Avoids OpenAI rate limits
- Faster response times

---

## 🚀 Summary

### To test your Render deployment:

```bash
# One command
python run_remote_tests.py
```

### If all pass:
✅ Your Render deployment is working
✅ Ready for GUVI submission
✅ Ready for teammate testing
✅ Production-ready

### Submit to GUVI:
- **x-api-key:** `J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM`
- **Endpoint URL:** `https://your-service.onrender.com/api/v1/conversation`

**Done!** 🎉
