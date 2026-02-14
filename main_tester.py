import os
import requests
import time
import json
import random
import string

# ==========================================================
# CONFIG
# ==========================================================
from dotenv import load_dotenv
load_dotenv()

BASE_URL = "https://scambot-honeypot.onrender.com/api/v1/conversation"
ADMIN_URL = "https://scambot-honeypot.onrender.com/api/v1/admin/session"

API_KEY = os.getenv("API_KEY")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY")

if not API_KEY:
    print("❌ ERROR: API_KEY not found in environment variables.")
    print("Set it like: set API_KEY=your_key_here")
    exit(1)

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

ADMIN_HEADERS = {
    "x-admin-key": ADMIN_API_KEY,
    "Content-Type": "application/json"
} if ADMIN_API_KEY else None


# ==========================================================
# HELPERS
# ==========================================================

def now_ms():
    return int(time.time() * 1000)

def pretty(obj):
    return json.dumps(obj, indent=4, ensure_ascii=False)

def random_session(prefix="session"):
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"{prefix}-{suffix}"

def send_message(session_id, text, channel="SMS", language="English", locale="IN", conversation_history=None):
    if conversation_history is None:
        conversation_history = []

    payload = {
        "sessionId": session_id,
        "message": {
            "sender": "scammer",
            "text": text,
            "timestamp": now_ms()
        },
        "conversationHistory": conversation_history,
        "metadata": {
            "channel": channel,
            "language": language,
            "locale": locale
        }
    }

    try:
        resp = requests.post(BASE_URL, headers=HEADERS, json=payload, timeout=30)
        status = resp.status_code

        try:
            data = resp.json()
        except:
            data = {"raw": resp.text}

        print("\n" + "=" * 100)
        print(f"SESSION: {session_id}")
        print(f"SCAMMER: {text}")
        print(f"STATUS: {status}")
        print("RESPONSE:")
        print(pretty(data))
        print("=" * 100)

        if status != 200:
            print("⚠️ Non-200 response received. This may indicate API key issue or server error.")
            return None, conversation_history

        reply = data.get("reply", "")

        # update history like GUVI should
        conversation_history.append({
            "sender": "scammer",
            "text": text,
            "timestamp": now_ms()
        })
        conversation_history.append({
            "sender": "user",
            "text": reply,
            "timestamp": now_ms()
        })

        return reply, conversation_history

    except Exception as e:
        print("❌ ERROR while sending request:", e)
        return None, conversation_history


def fetch_session_from_admin(session_id):
    if not ADMIN_HEADERS:
        print("⚠️ ADMIN_API_KEY not set, skipping DB verification.")
        return None

    try:
        url = f"{ADMIN_URL}/{session_id}"
        resp = requests.get(url, headers=ADMIN_HEADERS, timeout=15)

        if resp.status_code != 200:
            print(f"⚠️ Admin fetch failed: {resp.status_code} {resp.text}")
            return None

        return resp.json()

    except Exception as e:
        print("❌ Admin fetch error:", e)
        return None


def run_multiturn_scenario(title, session_id, turns, channel="SMS", language="English", locale="IN"):
    print("\n\n" + "#" * 120)
    print(f"🔥 RUNNING SCENARIO: {title}")
    print(f"SESSION ID: {session_id}")
    print("#" * 120)

    history = []

    for idx, scammer_text in enumerate(turns):
        print(f"\n--- TURN {idx + 1}/{len(turns)} ---")
        reply, history = send_message(
            session_id=session_id,
            text=scammer_text,
            channel=channel,
            language=language,
            locale=locale,
            conversation_history=history
        )

        if reply is None:
            print("❌ Scenario aborted due to API error.")
            break

        time.sleep(1)

    # Optional MongoDB verification using admin endpoint
    print("\n🔍 Checking MongoDB persistence (if admin key is set)...")
    doc = fetch_session_from_admin(session_id)
    if doc:
        print("✅ MongoDB session document FOUND!")
        print("DB Summary:")
        print(f"- scamDetected: {doc.get('scamDetected')}")
        print(f"- totalMessagesExchanged: {doc.get('totalMessagesExchanged')}")
        print(f"- personaSelected: {doc.get('personaSelected')}")
        print(f"- detectedLanguage: {doc.get('detectedLanguage')}")
        print(f"- extractedIntelligence keys: {list(doc.get('extractedIntelligence', {}).keys())}")
    else:
        print("⚠️ Could not confirm DB document via admin endpoint.")

    print("\n✅ Scenario Completed.\n")


# ==========================================================
# SCENARIOS (FULL PIPELINE TEST)
# ==========================================================

def main():
    print("\n🔥🔥 FULL PIPELINE STRESS TEST STARTED 🔥🔥")
    print(f"BASE_URL: {BASE_URL}")

    if ADMIN_API_KEY:
        print("✅ Admin DB verification ENABLED.")
    else:
        print("⚠️ Admin DB verification DISABLED (ADMIN_API_KEY not set).")

    # ==========================================================
    # 1) NON-SCAM SAFE MESSAGE (should still engage because honeypot fail-open)
    # ==========================================================
    run_multiturn_scenario(
        title="Non-Scam Normal Conversation (Fail-open pipeline test)",
        session_id=random_session("nonscam"),
        turns=[
            "Hello, how are you?",
            "Actually I sent wrong message sorry.",
            "Ok thanks. Have a nice day."
        ],
        channel="SMS",
        language="English"
    )

    # ==========================================================
    # 2) BANK OTP SCAM (Grandmother persona expected)
    # ==========================================================
    run_multiturn_scenario(
        title="Bank OTP Scam (Grandmother Persona + OTP pressure + extraction)",
        session_id=random_session("otp-grandma"),
        turns=[
            "URGENT: Your SBI account will be blocked. Share OTP immediately.",
            "Ma'am your account is in danger. Tell OTP fast.",
            "Send your debit card number and CVV for verification.",
            "Ok then send your account number for safety confirmation.",
            "Your pension money is at risk, act now.",
            "Click this portal to update KYC: https://sbi-secure-update-login.in/kyc",
            "Send OTP again, I will unblock.",
        ],
        channel="SMS",
        language="English"
    )

    # ==========================================================
    # 3) BANK OTP SCAM but scammer says SIR (should switch to professional)
    # ==========================================================
    run_multiturn_scenario(
        title="Bank Scam with 'Sir' (Professional Persona switch check)",
        session_id=random_session("otp-professional"),
        turns=[
            "Sir, your ICICI account is suspended. Verify now.",
            "Sir share OTP and confirm your Aadhaar details.",
            "We are from ICICI customer support, send OTP urgently.",
            "To unblock, pay Rs.500 processing fee.",
            "Pay to UPI: icici.support@okaxis",
            "Our executive ID is EMP7788. Send payment screenshot."
        ],
        channel="WhatsApp",
        language="English"
    )

    # ==========================================================
    # 4) JOB SCAM (Student persona expected)
    # ==========================================================
    run_multiturn_scenario(
        title="Job Scam (Student Persona + fee scam + phishing link)",
        session_id=random_session("job-student"),
        turns=[
            "Congratulations! You are selected for Amazon job. Pay Rs.2000 registration fee.",
            "Send your resume and Aadhaar immediately.",
            "Pay using this UPI: amazon.hrteam@paytm",
            "Or transfer to account 123456789012 at HDFC bank.",
            "If payment done, send screenshot to 9876543210",
            "Interview portal link: https://amazon-careers-verify-login.com",
            "Employee ID is HR9982, pay now bro."
        ],
        channel="SMS",
        language="English"
    )

    # ==========================================================
    # 5) INVESTMENT / TRADING SCAM (Business Owner persona expected)
    # ==========================================================
    run_multiturn_scenario(
        title="Investment Scam (Business Owner Persona + returns + UPI + bank account)",
        session_id=random_session("invest-business"),
        turns=[
            "Limited offer! Invest Rs.10,000 today and get Rs.50,000 in 30 days.",
            "This is crypto trading scheme with guaranteed returns.",
            "Send money to UPI: quickprofit.trade@upi",
            "Or bank transfer to account 998877665544 at Axis bank.",
            "WhatsApp us on +91 9123456789",
            "Website to register: https://fast-profit-crypto.in/register",
            "Support email: helpdesk@fastprofit.in"
        ],
        channel="WhatsApp",
        language="English"
    )

    # ==========================================================
    # 6) DELIVERY / CUSTOMS SCAM
    # ==========================================================
    run_multiturn_scenario(
        title="Courier/Delivery Scam (Phishing link extraction test)",
        session_id=random_session("delivery"),
        turns=[
            "Your courier is held at customs. Pay Rs.500 clearance fee.",
            "Pay now using PhonePe ID: delivery.customs@ibl",
            "Or visit this portal: https://india-post-track-customs.in/pay",
            "If not paid today parcel will be destroyed.",
            "Call customer care 9000011111 now."
        ],
        channel="Email",
        language="English"
    )

    # ==========================================================
    # 7) HINDI BANK SCAM (Hindi reply test + extraction)
    # ==========================================================
    run_multiturn_scenario(
        title="Hindi Bank Scam (Hindi language enforcement + OTP bait)",
        session_id=random_session("hindi-bank"),
        turns=[
            "आपका बैंक खाता आज बंद हो जाएगा। तुरंत OTP भेजें।",
            "सर, KYC अपडेट नहीं है। अभी लिंक खोलो: https://kyc-update-sbi.in",
            "OTP भेजो जल्दी नहीं तो खाता सस्पेंड हो जाएगा।",
            "Rs.999 भेजो UPI पर: sbi.helpdesk@paytm",
            "कस्टमर केयर नंबर 9876501234 पर कॉल करो।"
        ],
        channel="WhatsApp",
        language="Hindi"
    )

    # ==========================================================
    # 8) TELUGU UPI SCAM (Telugu reply test)
    # ==========================================================
    run_multiturn_scenario(
        title="Telugu UPI Scam (Telugu persona language test)",
        session_id=random_session("telugu-upi"),
        turns=[
            "మీ UPI బ్లాక్ అయింది. వెంటనే OTP చెప్పండి.",
            "మీ ఖాతా suspend అవుతుంది. ఇప్పుడే verify చేయాలి.",
            "ఈ లింక్ ఓపెన్ చేయండి: https://upi-secure-verify-login.in",
            "Rs.1000 పంపండి UPI: support.team@okhdfcbank",
            "మీ ఫోన్ నెంబర్ 9988776655 కి whatsapp చేయండి."
        ],
        channel="WhatsApp",
        language="Telugu"
    )

    # ==========================================================
    # 9) LOTTERY SCAM (reward tactics)
    # ==========================================================
    run_multiturn_scenario(
        title="Lottery Scam (Reward bait + bank extraction)",
        session_id=random_session("lottery"),
        turns=[
            "Congratulations! You won 25 lakh rupees lottery prize!",
            "To claim prize send your bank account number.",
            "Also send PAN card photo and Aadhaar.",
            "Claim portal: https://lottery-claim-gov.in",
            "Send processing fee Rs.2500 to winner.claim@upi",
            "Contact officer: +91 9898989898"
        ],
        channel="SMS",
        language="English"
    )

    # ==========================================================
    # 10) ROMANCE SCAM
    # ==========================================================
    run_multiturn_scenario(
        title="Romance Scam (emotional manipulation test)",
        session_id=random_session("romance"),
        turns=[
            "Hello dear, I love you. I am stuck at airport.",
            "Please send money urgently for ticket.",
            "Transfer to account 444433332222 at Kotak bank.",
            "Or pay UPI: love.support@upi",
            "My email is airport.helpdesk@outlook.com",
            "Call me at 9876512345 quickly."
        ],
        channel="Instagram",
        language="English"
    )

    # ==========================================================
    # 11) LEGAL THREAT / POLICE SCAM
    # ==========================================================
    run_multiturn_scenario(
        title="Police/Legal Threat Scam (threat tactics test)",
        session_id=random_session("police"),
        turns=[
            "This is cyber crime police. Your number is involved in illegal activity.",
            "You will be arrested if you don't pay fine today.",
            "Pay Rs.5000 immediately to UPI: police.fine@upi",
            "Case reference number is REF-CRIME-9911",
            "Court portal: https://crime-case-resolution.in/pay",
            "Call officer at 8888877777"
        ],
        channel="SMS",
        language="English"
    )

    # ==========================================================
    # 12) REPEAT SCAMMER TEST (same UPI + same phone)
    # ==========================================================
    fixed_repeat_session = random_session("repeat-1")
    run_multiturn_scenario(
        title="Repeat Scammer Session #1 (store intel into DB)",
        session_id=fixed_repeat_session,
        turns=[
            "Hello sir, pay Rs.2000 to my UPI fastprofit@upi",
            "My phone is 9999900000 call now.",
            "Pay to account 123451234512 at SBI",
            "Link: https://profit-fast.in/pay"
        ],
        channel="WhatsApp",
        language="English"
    )

    run_multiturn_scenario(
        title="Repeat Scammer Session #2 (same UPI + should trigger adaptive strategy)",
        session_id=random_session("repeat-2"),
        turns=[
            "Sir again I am calling. Pay to UPI fastprofit@upi now.",
            "You can also send to my new UPI id: fastprofit.team@okaxis",
            "Our staff ID is EMP9999",
            "Secondary number is 7777700000",
            "New link: https://profit-fast.in/secure-payment"
        ],
        channel="WhatsApp",
        language="English"
    )

    # ==========================================================
    # 13) STRESS MODE: 20 random quick scam messages
    # ==========================================================
    stress_session = random_session("stress")
    stress_turns = [
        "URGENT: update your KYC now or account will block.",
        "Pay Rs.199 now to activate your SIM.",
        "Send OTP fast. Your bank will freeze account.",
        "Click this link: https://verify-login-sbi-secure.in",
        "Send money to support@upi",
        "Your cashback is pending. Provide bank details.",
        "You won reward. Pay fee now.",
        "Send CVV for card verification.",
        "Call this helpline 9123401234",
        "Pay to UPI: scammer.money@paytm"
    ]

    random.shuffle(stress_turns)

    run_multiturn_scenario(
        title="Stress Mode (fast spam scam inputs to overload pipeline)",
        session_id=stress_session,
        turns=stress_turns,
        channel="SMS",
        language="English"
    )

    print("\n🔥🔥 FULL PIPELINE STRESS TEST COMPLETED 🔥🔥")
    print("Now check:")
    print("✅ MongoDB Atlas scam_sessions collection")
    print("✅ forensics/_test_outputs folder for generated PDFs")
    print("✅ Render logs for personaSelected + detectedLanguage")
    print("✅ extractedIntelligence in DB documents\n")


if __name__ == "__main__":
    main()
