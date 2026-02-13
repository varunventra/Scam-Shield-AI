"""
Integration test for MongoDB storage, repeat scammer detection,
adaptive agent, and admin endpoints.

Run:  python test_mongodb_integration.py

Tests against your deployed Render server.
"""
import httpx
import time
import sys
import json
from dotenv import load_dotenv
import os

load_dotenv()

RENDER_URL = os.getenv("RENDER_URL", "https://scambot-honeypot.onrender.com").rstrip("/")
BASE_URL = f"{RENDER_URL}/api/v1"

API_KEY = os.getenv("API_KEY", "")
ADMIN_KEY = os.getenv("ADMIN_API_KEY", "")

HEADERS = {"x-api-key": API_KEY, "Content-Type": "application/json"}
ADMIN_HEADERS = {"x-admin-key": ADMIN_KEY, "Content-Type": "application/json"}

passed = 0
failed = 0

print(f"\nTarget: {RENDER_URL}")
print(f"API Key: {API_KEY[:8]}...") if API_KEY else print("WARNING: No API_KEY set")
print(f"Admin Key: {ADMIN_KEY[:4]}...") if ADMIN_KEY else print("WARNING: No ADMIN_API_KEY set")


def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  PASS  {name}")
        passed += 1
    else:
        print(f"  FAIL  {name} -- {detail}")
        failed += 1


def send_message(session_id, text, history=None, metadata=None):
    """Send a scammer message and return response JSON."""
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


# ===========================================================================
print("\n" + "=" * 60)
print("  MONGODB INTEGRATION TEST SUITE (RENDER)")
print("=" * 60)

# ------------------------------------------------------------------
# 0. Wake up Render + health check
# ------------------------------------------------------------------
print("\n--- 0. Health check (may take ~30s if Render is sleeping) ---")
try:
    r = httpx.get(f"{RENDER_URL}/health", timeout=60)
    test("Health endpoint returns 200", r.status_code == 200)
except Exception as e:
    print(f"  Server unreachable: {e}")
    print("  Make sure your Render service is deployed with the latest code.")
    sys.exit(1)

# ------------------------------------------------------------------
# 1. Basic conversation + DB storage
# ------------------------------------------------------------------
print("\n--- 1. Basic conversation flow (Session A) ---")
SESSION_A = f"test-A-{int(time.time())}"

code, resp = send_message(SESSION_A, "Your bank account has been blocked. Call +91 9876543210 immediately to verify.")
test("Conversation returns 200", code == 200, f"got {code}")
test("Response has status=success", resp.get("status") == "success")
test("Response has reply", len(resp.get("reply", "")) > 0, resp.get("reply", ""))
print(f"  Agent reply: {resp.get('reply', '')[:100]}")

time.sleep(2)
code2, resp2 = send_message(SESSION_A, "Send Rs.500 to account 12345678901234 for verification")
test("Second message OK", code2 == 200)

time.sleep(2)
code3, resp3 = send_message(SESSION_A, "Use UPI ID scammer@okaxis to pay now. Visit http://fake-bank-verify.com/login")
test("Third message OK", code3 == 200)

# ------------------------------------------------------------------
# 2. Admin - fetch session from MongoDB
# ------------------------------------------------------------------
print("\n--- 2. Admin: fetch session from MongoDB ---")
time.sleep(3)

r = httpx.get(f"{BASE_URL}/admin/session/{SESSION_A}", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    doc = r.json()
    test("Session doc returned", True)
    test("sessionId matches", doc.get("sessionId") == SESSION_A)
    test("Has extractedIntelligence", "extractedIntelligence" in doc)
    test("Has conversationTranscript", "conversationTranscript" in doc)
    test("Has createdAt", "createdAt" in doc)
    test("Has updatedAt", "updatedAt" in doc)
    test("Has riskLevel", "riskLevel" in doc)
    test("Has repeatScammer field", "repeatScammer" in doc)
    test("Has metadata", "metadata" in doc)

    intel = doc.get("extractedIntelligence", {})
    print(f"\n  Stored intelligence:")
    print(f"    phoneNumbers:  {intel.get('phoneNumbers', [])}")
    print(f"    bankAccounts:  {intel.get('bankAccounts', [])}")
    print(f"    upiIds:        {intel.get('upiIds', [])}")
    print(f"    phishingLinks: {intel.get('phishingLinks', [])}")
    print(f"    keywords:      {intel.get('suspiciousKeywords', [])[:5]}...")
    print(f"  Risk level:      {doc.get('riskLevel')}")
    print(f"  Repeat scammer:  {doc.get('repeatScammer')}")
    print(f"  Transcript msgs: {len(doc.get('conversationTranscript', []))}")
    print(f"  Callback sent:   {doc.get('callbackSent')}")
elif r.status_code == 404:
    test("Session doc returned", False, "404 - MongoDB may not be connected. Check MONGODB_URI on Render.")
else:
    test("Session doc returned", False, f"status {r.status_code}: {r.text[:200]}")

# ------------------------------------------------------------------
# 3. Admin - repeat analysis
# ------------------------------------------------------------------
print("\n--- 3. Admin: repeat analysis ---")
r = httpx.get(f"{BASE_URL}/admin/repeats/{SESSION_A}", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    doc = r.json()
    test("Repeat analysis returned", True)
    test("Has repeatScammer", "repeatScammer" in doc)
    test("Has repeatMatches", "repeatMatches" in doc)
    test("Has riskLevel", "riskLevel" in doc)
else:
    test("Repeat analysis returned", False, f"status {r.status_code}: {r.text[:200]}")

# ------------------------------------------------------------------
# 4. Admin - search by phone
# ------------------------------------------------------------------
print("\n--- 4. Admin: search by phone ---")
r = httpx.get(f"{BASE_URL}/admin/search?phone=9876543210", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    data = r.json()
    test("Search returns results", data.get("count", 0) > 0, f"count={data.get('count')}")
    print(f"  Found {data.get('count')} session(s) matching phone 9876543210")
else:
    test("Search endpoint works", False, f"status {r.status_code}: {r.text[:200]}")

# ------------------------------------------------------------------
# 5. REPEAT SCAMMER DETECTION (Session B reuses same phone)
# ------------------------------------------------------------------
print("\n--- 5. Repeat scammer detection (Session B) ---")
SESSION_B = f"test-B-{int(time.time())}"

code, _ = send_message(SESSION_B, "This is bank officer. Your card is blocked.")
test("Session B msg 1 OK", code == 200)
time.sleep(2)

code, _ = send_message(SESSION_B, "Call +91 9876543210 now or account frozen. Send to 99887766554433")
test("Session B msg 2 OK (reuses phone from A)", code == 200)
time.sleep(2)

code, _ = send_message(SESSION_B, "Pay via newscammer@ybl immediately")
test("Session B msg 3 OK", code == 200)
time.sleep(3)

r = httpx.get(f"{BASE_URL}/admin/session/{SESSION_B}", headers=ADMIN_HEADERS, timeout=30)
if r.status_code == 200:
    doc = r.json()
    is_repeat = doc.get("repeatScammer")
    risk = doc.get("riskLevel")
    repeat_matches = doc.get("repeatMatches", {})
    repeat_sessions = doc.get("repeatSessionIds", [])

    test("Session B is repeat scammer", is_repeat == True, f"got {is_repeat}")
    test("Risk level is HIGH", risk == "HIGH", f"got {risk}")

    matched_phones = repeat_matches.get("phoneNumbers", [])
    test("Matched phone found", len(matched_phones) > 0, f"matches: {repeat_matches}")
    test("Session A in repeatSessionIds", SESSION_A in repeat_sessions, f"got {repeat_sessions}")

    print(f"\n  repeatScammer:    {is_repeat}")
    print(f"  riskLevel:        {risk}")
    print(f"  repeatMatches:    {json.dumps(repeat_matches, indent=4)}")
    print(f"  repeatSessionIds: {repeat_sessions}")
else:
    test("Session B doc fetched", False, f"status {r.status_code}: {r.text[:200]}")

# ------------------------------------------------------------------
# 6. Admin auth rejection
# ------------------------------------------------------------------
print("\n--- 6. Admin auth (should reject bad/missing key) ---")
bad_headers = {"x-admin-key": "wrong-key"}
r = httpx.get(f"{BASE_URL}/admin/session/{SESSION_A}", headers=bad_headers, timeout=30)
test("Bad admin key returns 401", r.status_code == 401, f"got {r.status_code}")

r2 = httpx.get(f"{BASE_URL}/admin/session/{SESSION_A}", timeout=30)
test("Missing admin key returns 401", r2.status_code == 401, f"got {r2.status_code}")

# ------------------------------------------------------------------
# 7. GUVI response format unchanged
# ------------------------------------------------------------------
print("\n--- 7. GUVI response format check ---")
SESSION_C = f"test-C-{int(time.time())}"
code, resp = send_message(SESSION_C, "Your account will be suspended!")
test("Response has exactly status + reply", set(resp.keys()) == {"status", "reply"}, f"keys: {set(resp.keys())}")
test("status is 'success'", resp.get("status") == "success")
test("reply is a string", isinstance(resp.get("reply"), str))

# ===========================================================================
print("\n" + "=" * 60)
print(f"  RESULTS: {passed} passed, {failed} failed")
print("=" * 60 + "\n")

if failed > 0:
    print("  Some tests failed. Common causes:")
    print("  - MONGODB_URI not set on Render -> admin endpoints return 404")
    print("  - ADMIN_API_KEY not set on Render -> admin endpoints return 401")
    print("  - Code not deployed yet -> push to git and wait for Render rebuild")
    print()

sys.exit(1 if failed > 0 else 0)
