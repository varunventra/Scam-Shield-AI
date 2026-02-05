# Complete Testing Guide - Local & Remote

## 🎯 Two Ways to Test Your Honeypot

### 1. **Local Testing** - Test on Your Computer
Tests your code running locally on `localhost:8000`

**Use for:** Development, debugging, feature testing

**Command:**
```bash
python run_all_tests.py
```

### 2. **Remote Testing** - Test Your Render Deployment
Tests your production service on Render

**Use for:** Pre-submission validation, production readiness

**Command:**
```bash
python run_remote_tests.py
```

---

## 📊 Quick Comparison

| | Local Tests | Remote Tests |
|---|-------------|--------------|
| **Target** | localhost:8000 | Render URL |
| **Tests** | 49 comprehensive tests | 13 critical tests |
| **Runtime** | 2-3 minutes | 1-2 minutes |
| **Setup** | Start local server | No setup needed |
| **When** | During development | Before submission |
| **Purpose** | Catch bugs fast | Verify production |

---

## 🚀 Complete Testing Workflow

### Step 1: Local Testing (Development)

```bash
# Terminal 1: Start local server
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Run all local tests
python run_all_tests.py
```

**What it tests:**
- ✅ 25 core API tests
- ✅ 13 scenario tests (all from TEST_EXAMPLES.md)
- ✅ 11 persona validation tests
- ✅ Authentication, scam detection, multi-turn conversations
- ✅ Intelligence extraction, error handling
- ✅ Response format, edge cases

**Expected output:**
```
🎉 ALL TESTS PASSED!
Your honeypot is ready for deployment!
```

---

### Step 2: Remote Testing (Before Submission)

```bash
# No server needed - tests your Render deployment
python run_remote_tests.py
```

**What it tests:**
- ✅ Authentication on production
- ✅ Key scam scenarios (bank, UPI, phishing, OTP)
- ✅ Multi-turn conversations (3-turn, 5-turn)
- ✅ Persona validation (realistic, not bookish)

**Expected output:**
```
🎉 ALL REMOTE TESTS PASSED!
Your Render deployment is working perfectly!

🚀 Production Status:
  ✅ Ready for GUVI submission
  ✅ Ready for teammate testing
  ✅ Production-ready
```

---

## 📁 Files Overview

### Test Files

```
tests/
├── test_api.py              ← 25 comprehensive local tests
├── test_all_scenarios.py    ← 13 scenario tests (local)
├── test_persona_validation.py ← 11 persona tests (local)
└── test_remote_api.py       ← 13 critical remote tests
```

### Test Runners

```
run_all_tests.py        ← Run all local tests (49 tests)
run_remote_tests.py     ← Run remote tests (13 tests)
test_honeypot.py        ← Simple validation script
```

### Guides

```
AUTOMATED_TESTING_GUIDE.md    ← Local testing guide
REMOTE_TESTING_GUIDE.md       ← Remote testing guide
TESTING_COMPLETE_GUIDE.md     ← This file (overview)
TESTING_SUMMARY.md            ← Quick reference
```

---

## 🎯 When to Use Which

### Use Local Tests When:
- 🔨 Developing new features
- 🐛 Debugging issues
- 🔄 Making code changes
- ⚡ Want fast feedback
- 💻 Testing before committing code

### Use Remote Tests When:
- 📤 About to submit to GUVI
- 🚀 Deployed to Render
- ✅ Final production validation
- 👥 Before sharing with teammate
- 🎓 Hackathon submission time

---

## 💡 Recommended Workflow

### During Development:
```bash
# 1. Make code changes
# 2. Start local server
python -m uvicorn app.main:app --reload

# 3. Run local tests
python run_all_tests.py

# 4. Fix any failures
# 5. Repeat until all pass
```

### Before Submission:
```bash
# 1. Deploy to Render (push to GitHub)
# 2. Wait for deployment to finish
# 3. Run remote tests
python run_remote_tests.py

# 4. Verify all pass
# 5. Submit to GUVI with confidence!
```

---

## 🔧 Setup Instructions

### For Local Testing:

**1. Start Server:**
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

**2. Run Tests (new terminal):**
```bash
python run_all_tests.py
```

### For Remote Testing:

**1. Add Render URL to .env:**
```bash
# Add this to your .env file
RENDER_URL=https://your-service.onrender.com
```

**2. Run Tests:**
```bash
python run_remote_tests.py
```

Or with command line:
```bash
python run_remote_tests.py --url https://your-service.onrender.com --api-key YOUR_KEY
```

---

## ✅ Success Criteria

### Local Tests Pass When:
- All 49 tests show green checkmarks
- No errors in console
- Agent responds naturally
- Scam detection works
- Multi-turn conversations maintain context

### Remote Tests Pass When:
- All 13 tests show green checkmarks
- Render service is accessible
- Authentication works
- Scam scenarios detected
- Persona is realistic

---

## 🚨 Common Issues

### Local Testing Issues:

**Issue: Server not running**
```
❌ Server is not running on http://localhost:8000
```
**Fix:** Start the server first with uvicorn

**Issue: Port already in use**
```
ERROR: Address already in use
```
**Fix:** Kill the process on port 8000 or use a different port

---

### Remote Testing Issues:

**Issue: Cannot reach Render**
```
❌ Cannot reach Render service at https://...
```
**Fix:**
1. Check URL is correct
2. Service might be sleeping - visit `/health` first
3. Wait 30-60 seconds and try again

**Issue: Tests timeout**
```
⚠️  Tests timed out
```
**Fix:**
1. OpenAI API might be slow
2. Run tests again - subsequent runs are faster
3. Check Render logs for errors

---

## 📊 Test Coverage Summary

### What's Tested:

| Feature | Local | Remote |
|---------|-------|--------|
| **Authentication** | ✅ 3 tests | ✅ 4 tests |
| **Scam Detection** | ✅ 10 types | ✅ 4 types |
| **Multi-Turn** | ✅ 6 tests | ✅ 2 tests |
| **Persona** | ✅ 11 tests | ✅ 3 tests |
| **Intelligence** | ✅ 3 tests | - |
| **Format** | ✅ 2 tests | - |
| **Edge Cases** | ✅ 3 tests | - |
| **Endpoints** | ✅ 3 tests | - |
| **Total** | **49 tests** | **13 tests** |

---

## 🎓 Before GUVI Submission

**Complete Checklist:**

```bash
# ✅ 1. Local tests pass
python run_all_tests.py
# Should see: "🎉 ALL TESTS PASSED!"

# ✅ 2. Deploy to Render
git add .
git commit -m "Ready for submission"
git push

# ✅ 3. Wait for Render deployment
# Check Render dashboard - should show "Live"

# ✅ 4. Remote tests pass
python run_remote_tests.py
# Should see: "🎉 ALL REMOTE TESTS PASSED!"

# ✅ 5. Verify health endpoint
# Visit: https://your-service.onrender.com/health
# Should return: {"status": "healthy", "active_sessions": 0}

# ✅ 6. Check UptimeRobot
# Should show "Up" status

# ✅ 7. Submit to GUVI
# x-api-key: J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM
# Endpoint: https://your-service.onrender.com/api/v1/conversation
```

---

## 🚀 Summary

### One Command for Each:

**Local (during development):**
```bash
python run_all_tests.py
```

**Remote (before submission):**
```bash
python run_remote_tests.py
```

### Both Pass?
✅ Your honeypot is **production-ready**
✅ Safe to submit to GUVI
✅ Ready for teammate testing
✅ All scenarios validated

---

## 📚 Additional Resources

- **AUTOMATED_TESTING_GUIDE.md** - Detailed local testing guide
- **REMOTE_TESTING_GUIDE.md** - Detailed remote testing guide
- **POSTMAN_TESTING_GUIDE.md** - Manual testing with Postman
- **GUVI_SUBMISSION_GUIDE.md** - How to submit to hackathon
- **TEST_EXAMPLES.md** - All test scenarios with curl examples

---

**You're ready to test and submit!** 🎉
