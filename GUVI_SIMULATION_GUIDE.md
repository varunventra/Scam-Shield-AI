# GUVI Simulation Tester - Complete Guide

## 🎯 What Is This?

**`test_guvi_simulation.py`** is a comprehensive tester that simulates EXACTLY how GUVI will test your honeypot system.

Instead of manually testing with Postman or wondering if your system works correctly, this script:

✅ Simulates a complete scam conversation (8 messages)
✅ Shows the full conversation flow turn-by-turn
✅ Displays all extracted intelligence
✅ Shows the exact JSON that gets sent to GUVI
✅ Validates your system is ready for submission

**Run this BEFORE submitting to GUVI to ensure everything works!**

---

## 🚀 Quick Start

### Option 1: Simple (No Configuration Needed)

```bash
python test_guvi_simulation.py
```

The script will:
1. Try to read URL from `.env` (RENDER_URL)
2. If not found, prompt you to enter your Render URL
3. Use the default API key from `.env`

### Option 2: Specify URL

```bash
python test_guvi_simulation.py --url https://your-honeypot.onrender.com
```

### Option 3: Specify Both URL and API Key

```bash
python test_guvi_simulation.py --url https://your-honeypot.onrender.com --api-key YOUR_KEY
```

---

## 📊 What You'll See

### 1. Pre-Flight Check

```
🔍 PRE-FLIGHT CHECK
✅ Server is accessible and healthy
```

### 2. Full Conversation Flow

```
🎯 SCENARIO: Bank Fraud + UPI Scam

Turn 1:
🎭 Scammer: Hello sir, this is from State Bank of India...
👵 Veerabhadra: Oh my god! What happened? Is my account safe?

Turn 2:
🎭 Scammer: If you don't verify your account immediately...
👵 Veerabhadra: Ok ok I will verify. What should I do beta?

Turn 3:
🎭 Scammer: Please confirm your account number and PAN card...
👵 Veerabhadra: I am scared. Please help me. What information you need?

... (continues for 8 turns)
```

### 3. Extracted Intelligence

```
📊 FINAL INTELLIGENCE REPORT

Extracted Intelligence:
{
  "bankAccounts": ["482937461029"],
  "upiIds": ["secure@okaxis"],
  "phishingLinks": [],
  "phoneNumbers": ["9876543210"],
  "suspiciousKeywords": ["urgent", "blocked", "verify", "account", "bank"]
}
```

### 4. Final Result JSON (What GUVI Receives)

```
Final Result JSON (Sent to GUVI):
{
  "sessionId": "guvi-sim-1738752800",
  "scamDetected": true,
  "totalMessagesExchanged": 8,
  "extractedIntelligence": {
    "bankAccounts": ["482937461029"],
    "upiIds": ["secure@okaxis"],
    "phishingLinks": [],
    "phoneNumbers": ["9876543210"],
    "suspiciousKeywords": ["urgent", "blocked", "verify", "account", "bank"]
  },
  "agentNotes": "Scammer used urgency tactics, attempted to extract sensitive information across 8 message exchanges..."
}
```

### 5. Test Summary

```
📋 TEST SUMMARY

✅ Total Messages Exchanged: 8
✅ Conversation History Maintained: 16 messages
✅ Session ID: guvi-sim-1738752800

Intelligence Extracted:
  • Bank Accounts: 1 found
  • UPI IDs: 1 found
  • Phone Numbers: 1 found
  • Phishing Links: 0 found
  • Suspicious Keywords: 5 found

Conversation Quality:
✅ Responses are varied and contextual (8/8 unique)

🎉 GUVI SIMULATION COMPLETE!

What GUVI will see:
  1. ✅ Multi-turn conversation (8 messages)
  2. ✅ Natural, believable responses
  3. ✅ Intelligence extracted from scammer
  4. ✅ Final result JSON sent to callback endpoint

✅ YOUR HONEYPOT IS READY FOR GUVI SUBMISSION!
```

---

## 🎯 What Gets Tested

### Scam Scenario: Bank Fraud + UPI Scam

The simulation sends 8 realistic scam messages:

1. **Initial contact** - Claims to be from SBI, mentions suspicious activity
2. **Urgency** - Threatens account blocking
3. **Information request** - Asks for account number and PAN
4. **Bank account scam** - Provides fake verification account number
5. **UPI scam** - Provides fake UPI ID for verification
6. **Phone number** - Gives scammer's phone number
7. **More urgency** - 30-minute deadline
8. **Employee ID** - Provides fake employee credentials

This covers all major scam types GUVI tests for.

---

## ✅ Success Criteria

Your system passes if:

1. ✅ **All 8 messages get responses** - No failures
2. ✅ **Responses are contextual** - Not repetitive generic answers
3. ✅ **Intelligence extracted** - At least 3-4 types found
4. ✅ **Conversation maintained** - Each response builds on previous context
5. ✅ **Persona maintained** - Veerabhadra stays in character

---

## 🐛 Troubleshooting

### "Cannot reach server"

**Problem:** Render service not accessible

**Solutions:**
1. Check if your Render URL is correct
2. Verify service is not sleeping (check Render dashboard)
3. Try accessing `/health` endpoint in browser
4. Check if UptimeRobot is active

### "Server returned status 401"

**Problem:** API key authentication failed

**Solutions:**
1. Verify API key is correct: `J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM`
2. Check Render environment variables include `API_KEY`
3. Try specifying API key explicitly: `--api-key YOUR_KEY`

### "Responses are repetitive"

**Problem:** Agent giving same response every time

**Solutions:**
1. This was already fixed in the latest deployment
2. Redeploy to Render with latest changes
3. Wait 2-3 minutes for deployment
4. Run the test again

### "Failed to get response for message X"

**Problem:** Request timeout or error

**Solutions:**
1. OpenAI API might be slow - run test again
2. Check Render logs for errors
3. Verify OpenAI API key is set in Render
4. Check OpenAI API credits/limits

---

## 📝 Before GUVI Submission Checklist

Run this checklist BEFORE submitting to GUVI:

```bash
# 1. Deploy latest changes to Render
git add .
git commit -m "Final deployment for GUVI submission"
git push

# 2. Wait for Render deployment (2-3 minutes)

# 3. Run GUVI simulation
python test_guvi_simulation.py

# 4. Verify output shows:
# ✅ All 8 messages got responses
# ✅ Responses are contextual and varied
# ✅ Intelligence was extracted
# ✅ Final JSON looks correct

# 5. Run full remote test suite (optional but recommended)
python run_remote_tests.py
```

**If both pass → You're ready for GUVI submission!**

---

## 🎯 Understanding the Output

### What GUVI Actually Tests

When you submit to GUVI, their system will:

1. **Send scam messages** (similar to this simulation)
2. **Expect responses** from your `/api/v1/conversation` endpoint
3. **Track conversation** across multiple turns
4. **Receive final callback** at `https://hackathon.guvi.in/api/updateHoneyPotFinalResult`
5. **Evaluate quality** based on:
   - Response naturalness
   - Intelligence extraction
   - Multi-turn coherence
   - Persona believability

This simulation replicates steps 1-3 and shows you what data would be sent in step 4.

### What The Final JSON Means

```json
{
  "sessionId": "guvi-sim-1738752800",           // Unique conversation ID
  "scamDetected": true,                         // Was scam detected?
  "totalMessagesExchanged": 8,                  // How many messages?
  "extractedIntelligence": {                    // What intelligence was gathered?
    "bankAccounts": ["482937461029"],
    "upiIds": ["secure@okaxis"],
    "phishingLinks": [],
    "phoneNumbers": ["9876543210"],
    "suspiciousKeywords": ["urgent", "blocked", "verify"]
  },
  "agentNotes": "Scammer used urgency tactics..." // Summary
}
```

This JSON gets sent to GUVI's callback endpoint after the conversation ends (6+ messages).

---

## 🚀 Next Steps After Successful Simulation

1. **✅ Simulation passed?** → Proceed to GUVI submission
2. **❌ Simulation failed?** → Check troubleshooting section, fix issues, redeploy, test again

### GUVI Submission Details

**Your API Endpoint:**
```
POST https://your-service.onrender.com/api/v1/conversation
```

**Authentication:**
```
x-api-key: J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM
```

**GUVI will send:**
- Multiple scam messages
- Empty or filled `conversationHistory`
- Expect natural responses
- Receive final intelligence callback

---

## 📚 Related Documentation

- [REQUIREMENTS_VERIFICATION.md](REQUIREMENTS_VERIFICATION.md) - Requirements checklist
- [REMOTE_TESTING_GUIDE.md](REMOTE_TESTING_GUIDE.md) - Full test suite (28 tests)
- [CONVERSATION_HISTORY_FIX.md](CONVERSATION_HISTORY_FIX.md) - History bug fix
- [REPETITIVE_RESPONSE_FIX.md](REPETITIVE_RESPONSE_FIX.md) - Contextual response fix
- [STRATEGIC_INTELLIGENCE_EXTRACTION.md](STRATEGIC_INTELLIGENCE_EXTRACTION.md) - Strategy guide

---

## ✅ Summary

**This simulation tester ensures:**
- ✅ Your honeypot responds correctly to scam messages
- ✅ Conversation flows naturally across multiple turns
- ✅ Intelligence is extracted accurately
- ✅ Final callback format is correct
- ✅ System is ready for GUVI submission

**Run it before submitting to GUVI to be 100% confident!** 🎯
