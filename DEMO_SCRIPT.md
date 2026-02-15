# ScamShield Live Demo Script

**Duration:** 2–3 minutes
**Setup:** Two browser tabs open side by side
- **Left:** Postman / API client (sending scammer messages)
- **Right:** MongoDB Atlas (showing session document updating live)

---

## Pre-Demo Setup

1. Open MongoDB Atlas → `scam_sessions` collection → clear test data or filter by new session
2. Open Postman with the `/api/v1/conversation` endpoint ready
3. Set headers: `x-api-key: YOUR_API_KEY`
4. Use a fresh session ID: `demo-live-001`
5. Keep the request body template ready (just change `text` for each message)

### Request Template

```json
{
  "sessionId": "demo-live-001",
  "currentMessage": {
    "sender": "scammer",
    "text": "MESSAGE_HERE",
    "timestamp": 1739600000000
  },
  "conversationHistory": [],
  "metadata": {
    "platform": "whatsapp",
    "phoneNumber": "+919876543210"
  }
}
```

**Important:** After each response, copy the growing conversation into `conversationHistory` for the next request. Or use a Postman pre-request script to automate this.

---

## The Scenario: SBI Bank Impersonation Scam

Why this scenario works:
- SBI is instantly recognizable to any Indian jury
- Bank impersonation is the most common real scam type
- It naturally escalates from soft to aggressive
- It forces multiple intelligence reveals (phone, UPI, bank account, link)
- Hindi switch mid-conversation feels authentic
- The AI persona response will be visibly impressive

---

## Scammer Messages (Send These In Order)

### Message 1 — Ambiguous Opening
```
Hello, this is regarding your bank account. We noticed some activity that needs your attention. Can you please confirm your name?
```

**What jury sees:**
- System detects scam with moderate confidence (~0.6)
- Persona selected (likely Grandmother or Professional based on tone)
- AI responds naturally, gives a name, sounds genuinely concerned
- MongoDB: `scamDetected: true`, `scamType: BANK_IMPERSONATION`, `personaSelected` appears

**Narrator:** *"A scammer sends an ambiguous opening. The system immediately classifies this as a potential bank impersonation scam and selects a persona — watch the database."*

---

### Message 2 — Authority Claim
```
Madam, I am Vikram Sharma, Senior Manager from SBI Main Branch, Hyderabad. Your account ending in 4532 has been flagged for suspicious transaction of Rs.48,000. We need to verify your identity immediately or your account will be frozen within 2 hours.
```

**What jury sees:**
- Confidence jumps (urgency + authority + threat + amount)
- Identity detection: gender=female (from "Madam"), name may be extracted
- AI responds with fear and compliance, asks "What should I do sir?"
- MongoDB: `detectedIdentity` updates, `extractedIntelligence.amounts` shows Rs.48000
- Strategy: Phase 1 — building trust, showing panic

**Narrator:** *"The scammer claims to be an SBI manager and applies pressure. Our system detects the authority claim, locks the identity as female based on 'Madam', and the AI persona responds with convincing panic — while quietly tracking every detail."*

---

### Message 3 — Phone Number Reveal + OTP Request
```
For verification, I am sending an OTP to your registered mobile number. Please share the 6-digit code when you receive it. My direct number is 9876543210 if the call drops. This is urgent madam.
```

**What jury sees:**
- Phone number `9876543210` extracted and appears in MongoDB
- AI does NOT share any real OTP — stalls naturally ("I'm checking my phone, one moment sir")
- Strategy: Phase 2 begins — AI starts asking innocent questions
- MongoDB: `phoneNumbers: ["+919876543210"]` appears live

**Narrator:** *"The scammer reveals a phone number. Instantly captured. The AI stalls on the OTP request — it never gives real information — but keeps the scammer engaged."*

---

### Message 4 — Language Switch to Hindi
```
Madam jaldi kijiye, aapka account block ho jayega. OTP batayiye turant. Yeh bahut zaroori hai.
```

**What jury sees:**
- Language detected: Hindi (transliterated)
- AI responds in Hindi/Hinglish automatically, matching the persona style
- Pressure tracking: urgency_count and threat_count increase
- MongoDB: `detectedLanguage: hindi`, `responseLanguage: hindi`

**Narrator:** *"The scammer switches to Hindi mid-conversation. Watch the AI mirror the language instantly — responding in natural Hinglish while staying in character."*

---

### Message 5 — UPI Payment Request
```
Madam OTP nahi aa raha toh koi baat nahi. Account verify karne ke liye Rs.10 ka test payment kijiye is UPI pe: vikram.sbi@ybl — yeh official SBI verification process hai.
```

**What jury sees:**
- UPI ID `vikram.sbi@ybl` extracted
- Amount `Rs.10` captured
- AI agrees enthusiastically but asks a natural question: "Sir yeh payment karne ke baad account safe ho jayega na? Aur aapka employee ID kya hai, main apne bete ko bata doon"
- Strategy: Phase 2/3 — extracting employee ID through natural concern
- MongoDB: `upiIds: ["vikram.sbi@ybl"]` appears

**Narrator:** *"A UPI ID is revealed. Captured instantly. But watch what the AI does — it agrees to pay, then naturally asks for an employee ID. The scammer thinks they're winning. The system is extracting."*

---

### Message 6 — Bank Account + Link Reveal
```
Haan madam bilkul safe hai. Mera employee ID hai SBI-VK-4821. Agar UPI se nahi hota toh yeh account mein transfer karein: 34927581046, IFSC: SBIN0001234. Ya phir is link pe verify karein: https://sbi-secure-verify.com/auth
```

**What jury sees:**
- Bank account `34927581046` extracted
- Phishing link `https://sbi-secure-verify.com/auth` extracted
- Employee ID `SBI-VK-4821` captured in keywords
- MongoDB lights up with all fields populated
- PDF generated at this point (message 6 = update interval)

**Narrator:** *"And there it is. Bank account, phishing link, employee ID — all captured. The AI asked one natural question and the scammer handed over everything. The PDF report just updated with the complete transcript."*

---

### Message 7+ (Optional — if time permits)

Send 3 more short messages to reach message 9 for another PDF update:

```
Jaldi kijiye madam, time khatam ho raha hai
```
```
Madam aap sun rahi hain? Account freeze ho jayega 30 minutes mein
```
```
Last warning madam, iske baad main kuch nahi kar paunga aapke liye
```

These show escalating pressure while the AI maintains composure and keeps extracting.

---

## What to Show the Jury (Right Panel — MongoDB Atlas)

After message 6, click refresh on the MongoDB document. Highlight these fields:

```
sessionId:              "demo-live-001"
scamDetected:           true
scamType:               "BANK_IMPERSONATION"
detectionMethod:        "hybrid"
totalMessagesExchanged: 6

personaSelected:        "grandmother"
detectedLanguage:       "hindi"
responseLanguage:       "hindi"
detectedIdentity:
  name:                 null or extracted
  gender:               "female"
  ageGroup:             "elderly"
  locked:               true

extractedIntelligence:
  phoneNumbers:         ["+919876543210"]
  upiIds:               ["vikram.sbi@ybl"]
  bankAccounts:         ["34927581046"]
  phishingLinks:        ["https://sbi-secure-verify.com/auth"]
  suspiciousKeywords:   ["urgent", "freeze", "verify", "otp", "block"]

riskLevel:              "HIGH"
pdfReportGenerated:     true
pdfReportCaseId:        "CFA-2026-DEMO-LI"
pdfReportUrl:           "https://scambot-honeypot.onrender.com/api/v1/admin/report/demo-live-001?admin_key=YOUR_ADMIN_KEY"
```

**Then click the `pdfReportUrl` link** — PDF opens in browser showing the full forensic report.

---

## PDF Report — What Jury Sees

When the PDF opens, quickly scroll through:

1. **Header:** Case ID, date, CONFIDENTIAL stamp
2. **Executive Summary:** "Scam DETECTED — BANK_IMPERSONATION — 6 messages — High Risk"
3. **Suspect Data Table:**
   - Phone: +919876543210
   - UPI: vikram.sbi@ybl
   - Bank Account: 34927581046
   - Phishing URL: https://sbi-secure-verify.com/auth
4. **Behavioral Markers:** CRITICAL threat level — urgency, threats, payment request, OTP demand
5. **Full Conversation Transcript:** Every message, color-coded, timestamped

**Narrator:** *"And here's the auto-generated forensic report. Case ID, extracted intelligence, behavioral analysis, and the complete conversation transcript. Ready for law enforcement."*

---

## Presenter Narration (Full Script — ~40 seconds)

Read this naturally during the demo. Do not rush. Pause where indicated.

---

> "We're going to show you a live scam interception."
>
> *[Send Message 1]*
>
> "A scammer sends an ambiguous message. The system detects the intent immediately, selects a persona, and responds."
>
> *[Send Message 2]*
>
> "Authority claim — SBI manager, account freeze threat. The AI responds with convincing panic. It's now tracking every detail."
>
> *[Send Message 3]*
>
> "Phone number revealed. Captured. The AI stalls on the OTP but keeps the conversation alive."
>
> *[Send Message 4]*
>
> "Language switch to Hindi. The AI mirrors it instantly."
>
> *[Send Message 5]*
>
> "UPI payment request. Captured. And watch — the AI asks for an employee ID. That's not scripted. It's strategic extraction."
>
> *[Send Message 6]*
>
> "Bank account, phishing link, employee ID — all handed over. One question did that."
>
> *[Switch to MongoDB]*
>
> "Here's the live database. Phone, UPI, bank account, phishing link — all captured in real time."
>
> *[Click pdfReportUrl]*
>
> "And the forensic report. Auto-generated. Case ID, full intelligence, complete transcript. Ready for law enforcement."
>
> *[Pause]*
>
> "Six messages. Zero human intervention. That's ScamShield."

---

## Timing Breakdown

| Time | Action | Duration |
|------|--------|----------|
| 0:00 | Send Message 1 + read response | 15 sec |
| 0:15 | Send Message 2 + narrate | 15 sec |
| 0:30 | Send Message 3 + narrate | 15 sec |
| 0:45 | Send Message 4 + narrate language switch | 15 sec |
| 1:00 | Send Message 5 + narrate UPI + extraction | 15 sec |
| 1:15 | Send Message 6 + narrate bank/link capture | 15 sec |
| 1:30 | Switch to MongoDB Atlas + highlight fields | 20 sec |
| 1:50 | Click PDF link + scroll through report | 20 sec |
| 2:10 | Closing line | 10 sec |
| **Total** | | **~2:20** |

---

## Backup Plan

If API is slow (Render cold start):
- Hit the endpoint once 5 minutes before demo to warm it up
- Send a throwaway message to `warmup-session` beforehand

If MongoDB Atlas is slow to refresh:
- Have the session document pre-opened in Atlas, just hit refresh
- Use the Atlas Data Explorer's auto-refresh if available

If PDF doesn't load:
- Have a backup PDF already downloaded from a previous test run
- Keep it in a browser tab ready to show

---

## Pre-Demo Checklist

- [ ] Render service is awake (send warmup request 5 min before)
- [ ] Postman has all 6 messages saved as separate requests in order
- [ ] MongoDB Atlas is open to `scam_sessions` collection
- [ ] Fresh session ID that doesn't exist yet
- [ ] Screen sharing shows both Postman and MongoDB side by side
- [ ] Backup PDF downloaded and ready in a browser tab
- [ ] Test the full flow once in private before going on stage
