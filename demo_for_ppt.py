"""
DEMO SCRIPT FOR PPT SCREENSHOTS
================================
Run this script against your deployed Render server.
It demonstrates ALL key features in a clean, screenshot-friendly way.

Usage:  python demo_for_ppt.py

Take screenshots as instructed at each pause.
"""
import httpx
import time
import sys
import json
import os
from dotenv import load_dotenv

load_dotenv()

RENDER_URL = os.getenv("RENDER_URL", "https://scambot-honeypot.onrender.com").rstrip("/")
BASE_URL = f"{RENDER_URL}/api/v1"
API_KEY = os.getenv("API_KEY", "")
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "")

HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}
ADMIN_HEADERS = {"x-admin-key": ADMIN_KEY, "Content-Type": "application/json"}


def send_message(session_id, text, history=None, metadata=None):
    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": int(time.time() * 1000)
        },
        "conversationHistory": history or [],
        "metadata": metadata or {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    r = httpx.post(f"{BASE_URL}/conversation", json=payload, headers=HEADERS, timeout=60)
    return r.status_code, r.json()


def pretty(data):
    return json.dumps(data, indent=2, default=str)


def pause(msg):
    print(f"\n{'='*60}")
    print(f"  SCREENSHOT: {msg}")
    print(f"{'='*60}")
    input("  Press ENTER to continue...")
    print()


# ===========================================================================
print("\n" + "="*70)
print("   SCAMBOT HONEYPOT - LIVE DEMO FOR PPT SCREENSHOTS")
print("="*70)
print(f"\n  Target: {RENDER_URL}")
print(f"  API Key: {API_KEY[:8]}..." if API_KEY else "  WARNING: No API_KEY set!")
print(f"  Admin Key: {ADMIN_KEY[:4]}..." if ADMIN_KEY else "  WARNING: No ADMIN_KEY set!")


# ===================================================================
# DEMO 1: HEALTH CHECK (wake up server)
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 1: HEALTH CHECK")
print("="*60)

print("\n  Waking up Render server (may take ~30s)...")
r = httpx.get(f"{RENDER_URL}/health", timeout=60)
print(f"\n  GET /health")
print(f"  Status: {r.status_code}")
print(f"  Response: {pretty(r.json())}")


# ===================================================================
# DEMO 2: ENGLISH BANK SCAM (Grandmother persona)
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 2: ENGLISH BANK SCAM CONVERSATION")
print("  (Should trigger: Grandmother persona + English)")
print("="*60)

SESSION_ENGLISH = f"demo-english-{int(time.time())}"

scam_msgs = [
    "Dear madam, this is SBI customer care. Your account has been suspended due to KYC expiry. Please verify immediately or account will be blocked.",
    "Ma'am please share your OTP that was sent to your registered mobile number to verify your identity.",
    "Ma'am your account will be permanently blocked in 30 minutes. Send OTP now. Also transfer Rs.500 to account 98765432109876 for verification charges.",
    "Ma'am I am officer Rahul Singh, employee ID SBI-4521. Pay via UPI to sbi.verify@okaxis or visit http://sbi-kyc-verify.com/login",
    "Ma'am this is very urgent. Call us at +91 8899776655 immediately or face legal action.",
]

for i, msg in enumerate(scam_msgs, 1):
    print(f"\n  --- Turn {i} ---")
    print(f"  SCAMMER: {msg[:80]}...")
    code, resp = send_message(SESSION_ENGLISH, msg)
    print(f"  AGENT:   {resp.get('reply', 'ERROR')}")
    print(f"  [Status: {code}, Format: {set(resp.keys())}]")
    time.sleep(2)

pause("SCREENSHOT 1 - Take a screenshot of the full English conversation above")


# ===================================================================
# DEMO 3: HINDI SCAM (Language detection)
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 3: HINDI SCAM CONVERSATION")
print("  (Should trigger: Hindi language detection)")
print("="*60)

SESSION_HINDI = f"demo-hindi-{int(time.time())}"

hindi_msgs = [
    "Madam aapka bank account block ho gaya hai. Turant verify karein warna paisa nikal jayega.",
    "Aapka OTP batao jaldi, nahi to account band ho jayega permanently.",
    "Madam Rs.1000 bhejo account 55667788990011 mein verification ke liye. UPI ID: scammer.hindi@ybl",
]

for i, msg in enumerate(hindi_msgs, 1):
    print(f"\n  --- Turn {i} ---")
    print(f"  SCAMMER: {msg}")
    code, resp = send_message(SESSION_HINDI, msg, metadata={"channel": "WhatsApp", "language": "Hindi", "locale": "IN"})
    print(f"  AGENT:   {resp.get('reply', 'ERROR')}")
    time.sleep(2)

pause("SCREENSHOT 2 - Take a screenshot of the Hindi conversation above")


# ===================================================================
# DEMO 4: JOB SCAM (Student persona)
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 4: JOB SCAM (Student persona)")
print("  (Should trigger: Student persona for job scam)")
print("="*60)

SESSION_JOB = f"demo-job-{int(time.time())}"

job_msgs = [
    "Congratulations! You have been selected for work from home job. Salary 50000 per month. Very urgent, limited vacancy!",
    "Sir just pay registration fee of Rs.2000 to start. Send to account 11223344556677 or UPI: jobfraud@axl",
    "Visit our official portal http://fake-jobs-india.com/register to complete your joining. Send resume to hr@fakejobs.com",
]

for i, msg in enumerate(job_msgs, 1):
    print(f"\n  --- Turn {i} ---")
    print(f"  SCAMMER: {msg[:80]}...")
    code, resp = send_message(SESSION_JOB, msg)
    print(f"  AGENT:   {resp.get('reply', 'ERROR')}")
    time.sleep(2)

pause("SCREENSHOT 3 - Take a screenshot of the Job Scam conversation above")


# ===================================================================
# DEMO 5: ADMIN - Session from MongoDB
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 5: ADMIN PANEL - MongoDB Session Data")
print("="*60)

time.sleep(3)

print(f"\n  GET /admin/session/{SESSION_ENGLISH}")
r = httpx.get(f"{BASE_URL}/admin/session/{SESSION_ENGLISH}", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    doc = r.json()
    print(f"\n  Session ID:        {doc.get('sessionId')}")
    print(f"  Scam Detected:     {doc.get('scamDetected')}")
    print(f"  Risk Level:        {doc.get('riskLevel')}")
    print(f"  Repeat Scammer:    {doc.get('repeatScammer')}")
    print(f"  Total Messages:    {doc.get('totalMessagesExchanged')}")
    print(f"  Persona Selected:  {doc.get('personaSelected')}")
    print(f"  Language Detected: {doc.get('detectedLanguage')}")
    print(f"  Response Language: {doc.get('responseLanguage')}")

    intel = doc.get("extractedIntelligence", {})
    print(f"\n  --- Extracted Intelligence ---")
    print(f"  Phone Numbers:     {intel.get('phoneNumbers', [])}")
    print(f"  Bank Accounts:     {intel.get('bankAccounts', [])}")
    print(f"  UPI IDs:           {intel.get('upiIds', [])}")
    print(f"  Phishing Links:    {intel.get('phishingLinks', [])}")
    print(f"  Keywords:          {intel.get('suspiciousKeywords', [])[:8]}...")

    print(f"\n  --- Conversation Transcript ({len(doc.get('conversationTranscript', []))} msgs) ---")
    for msg in doc.get("conversationTranscript", [])[:6]:
        sender = msg.get("sender", "?")
        text = msg.get("text", "")[:60]
        print(f"    [{sender:8s}] {text}...")
else:
    print(f"  ERROR: {r.status_code} - {r.text[:200]}")

pause("SCREENSHOT 4 - Take a screenshot of the MongoDB session data above")


# ===================================================================
# DEMO 6: ADMIN - Hindi Session (shows persona + language fields)
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 6: ADMIN - Hindi Session (Persona + Language)")
print("="*60)

print(f"\n  GET /admin/session/{SESSION_HINDI}")
r = httpx.get(f"{BASE_URL}/admin/session/{SESSION_HINDI}", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    doc = r.json()
    print(f"\n  Session ID:        {doc.get('sessionId')}")
    print(f"  Persona Selected:  {doc.get('personaSelected')}")
    print(f"  Language Detected: {doc.get('detectedLanguage')}")
    print(f"  Response Language: {doc.get('responseLanguage')}")
    print(f"  Scam Detected:     {doc.get('scamDetected')}")
    print(f"  Risk Level:        {doc.get('riskLevel')}")

    intel = doc.get("extractedIntelligence", {})
    print(f"\n  --- Extracted Intelligence ---")
    print(f"  Phone Numbers:     {intel.get('phoneNumbers', [])}")
    print(f"  Bank Accounts:     {intel.get('bankAccounts', [])}")
    print(f"  UPI IDs:           {intel.get('upiIds', [])}")
else:
    print(f"  ERROR: {r.status_code} - {r.text[:200]}")

pause("SCREENSHOT 5 - Take a screenshot showing persona + language detection")


# ===================================================================
# DEMO 7: REPEAT SCAMMER DETECTION
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 7: REPEAT SCAMMER DETECTION")
print("  (New session reusing phone from Demo 2)")
print("="*60)

SESSION_REPEAT = f"demo-repeat-{int(time.time())}"

repeat_msgs = [
    "Hello your credit card has unusual activity. Call +91 8899776655 now.",
    "Transfer Rs.2000 to 98765432109876 to secure your card. Use UPI: repeat.scam@paytm",
    "Visit http://sbi-kyc-verify.com/secure to confirm your identity.",
]

for i, msg in enumerate(repeat_msgs, 1):
    print(f"\n  --- Turn {i} ---")
    print(f"  SCAMMER: {msg[:80]}...")
    code, resp = send_message(SESSION_REPEAT, msg)
    print(f"  AGENT:   {resp.get('reply', 'ERROR')}")
    time.sleep(2)

time.sleep(3)
print(f"\n  GET /admin/session/{SESSION_REPEAT}")
r = httpx.get(f"{BASE_URL}/admin/session/{SESSION_REPEAT}", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    doc = r.json()
    print(f"\n  Session ID:          {doc.get('sessionId')}")
    print(f"  REPEAT SCAMMER:      {doc.get('repeatScammer')}")
    print(f"  RISK LEVEL:          {doc.get('riskLevel')}")
    print(f"  Repeat Matches:      {json.dumps(doc.get('repeatMatches', {}), indent=4)}")
    print(f"  Repeat Session IDs:  {doc.get('repeatSessionIds', [])}")
else:
    print(f"  ERROR: {r.status_code} - {r.text[:200]}")

pause("SCREENSHOT 6 - Take a screenshot of the repeat scammer detection")


# ===================================================================
# DEMO 8: ADMIN SEARCH
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 8: ADMIN SEARCH (by phone number)")
print("="*60)

print(f"\n  GET /admin/search?phone=8899776655")
r = httpx.get(f"{BASE_URL}/admin/search?phone=8899776655", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    data = r.json()
    print(f"\n  Search Results: {data.get('count')} session(s) found")
    for s in data.get("sessions", []):
        print(f"    - {s.get('sessionId')} | Risk: {s.get('riskLevel')} | Repeat: {s.get('repeatScammer')}")
else:
    print(f"  ERROR: {r.status_code}")

pause("SCREENSHOT 7 - Take a screenshot of the search results")


# ===================================================================
# DEMO 9: GUVI FORMAT COMPLIANCE
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 9: GUVI RESPONSE FORMAT COMPLIANCE")
print("="*60)

SESSION_FMT = f"demo-format-{int(time.time())}"
code, resp = send_message(SESSION_FMT, "Your account will be suspended! Send OTP now!")
print(f"\n  Status Code: {code}")
print(f"  Response Keys: {set(resp.keys())}")
print(f"  Expected Keys: {{'status', 'reply'}}")
print(f"  Match: {set(resp.keys()) == {'status', 'reply'}}")
print(f"\n  Full Response:")
print(f"  {pretty(resp)}")

pause("SCREENSHOT 8 - Take a screenshot of GUVI format compliance")


# ===================================================================
# DEMO 10: ADMIN AUTH SECURITY
# ===================================================================
print("\n\n" + "="*60)
print("  DEMO 10: ADMIN ENDPOINT SECURITY")
print("="*60)

print("\n  Testing with WRONG admin key...")
r1 = httpx.get(f"{BASE_URL}/admin/session/test", headers={"x-admin-key": "wrong-key"}, timeout=10)
print(f"  Bad key -> Status: {r1.status_code} (expected 401)")

print("\n  Testing with NO admin key...")
r2 = httpx.get(f"{BASE_URL}/admin/session/test", timeout=10)
print(f"  No key  -> Status: {r2.status_code} (expected 401)")

print(f"\n  Admin endpoints are SECURED: {'YES' if r1.status_code == 401 and r2.status_code == 401 else 'NO'}")

pause("SCREENSHOT 9 - Take a screenshot of admin security test")


# ===================================================================
# SUMMARY
# ===================================================================
print("\n\n" + "="*70)
print("   DEMO COMPLETE - SCREENSHOTS SUMMARY")
print("="*70)
print(f"""
  Screenshot 1: English bank scam conversation (Grandmother persona)
  Screenshot 2: Hindi scam conversation (multilingual detection)
  Screenshot 3: Job scam conversation (Student persona)
  Screenshot 4: MongoDB admin panel - full session data + intelligence
  Screenshot 5: Hindi session - persona + language fields in DB
  Screenshot 6: Repeat scammer detection across sessions
  Screenshot 7: Admin search by phone number
  Screenshot 8: GUVI response format compliance
  Screenshot 9: Admin endpoint security (401 on bad keys)
  Screenshot 10: Forensic PDF report (check forensics/ folder)

  Sessions created:
    English: {SESSION_ENGLISH}
    Hindi:   {SESSION_HINDI}
    Job:     {SESSION_JOB}
    Repeat:  {SESSION_REPEAT}
""")
print("="*70)
