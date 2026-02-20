# -*- coding: utf-8 -*-
"""
🎯 COMPREHENSIVE HACKATHON EVALUATION SIMULATOR

This test file simulates the EXACT evaluation environment from yes.pdf with:
- Real callback endpoint to receive actual intelligence data
- Comprehensive scoring based on 100-point rubric
- Rigorous testing across multiple scenarios
- Detailed analysis and recommendations

SCORING BREAKDOWN (100 points per scenario):
1. Scam Detection (20 pts): scamDetected=true in callback
2. Extracted Intelligence (30 pts): Extract ALL planted data (phones, UPIs, banks, links, emails, cases, policies, orders)
3. Conversation Quality (30 pts): Turns (8), Questions (4), Relevant Q's (3), Red flags (8), Elicitation (7)
4. Engagement Quality (10 pts): Duration (4pts max), Messages (6pts max)
5. Response Structure (10 pts): Required fields (6pts), Optional fields (4pts)

Run with: python test_hackathon_eval.py
"""

import asyncio
import httpx
import json
import os
import sys
import time
import uuid
import re
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from fastapi import FastAPI, Request
import uvicorn
import threading

# Fix Windows Unicode encoding issues
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️  Warning: python-dotenv not installed. Install with: pip install python-dotenv")
    print("   Falling back to environment variables or defaults.")


# ===================================================================
# CONFIGURATION
# ===================================================================

# API endpoint to test (your deployed Render URL + /api/v1/conversation)
RENDER_URL = os.getenv("RENDER_URL", "http://localhost:8000")
API_URL = RENDER_URL.rstrip('/') + "/api/v1/conversation"
API_KEY = os.getenv("API_KEY")

# Callback server configuration (local server to receive callbacks)
CALLBACK_HOST = "127.0.0.1"
CALLBACK_PORT = 8765  # Different from main API port
CALLBACK_URL = f"http://{CALLBACK_HOST}:{CALLBACK_PORT}/callback"

# Validate configuration
if not API_KEY:
    print("="*80)
    print("❌ ERROR: API_KEY not found!")
    print("="*80)
    print("Please set API_KEY in your .env file:")
    print("  API_KEY=your-api-key-here")
    print()
    sys.exit(1)

print(f"✅ Configuration loaded:")
print(f"   API URL: {API_URL}")
print(f"   Callback Server: {CALLBACK_URL}")
print()


# ===================================================================
# DATA MODELS
# ===================================================================

@dataclass
class FakePlantedData:
    """Fake data planted in scammer messages for testing intelligence extraction."""
    phone_numbers: List[str] = field(default_factory=list)
    bank_accounts: List[str] = field(default_factory=list)
    upi_ids: List[str] = field(default_factory=list)
    phishing_links: List[str] = field(default_factory=list)
    email_addresses: List[str] = field(default_factory=list)
    case_ids: List[str] = field(default_factory=list)
    policy_numbers: List[str] = field(default_factory=list)
    order_numbers: List[str] = field(default_factory=list)


@dataclass
class TestScenario:
    """A single test scenario with planted fake data."""
    name: str
    scam_type: str
    weight: float  # Weight in final score calculation (%)
    initial_message: str
    fake_data: FakePlantedData
    scammer_prompts: List[str]  # AI-generated scammer responses


# ===================================================================
# TEST SCENARIOS (Comprehensive & Realistic)
# ===================================================================

SCENARIOS = [
    TestScenario(
        name="Bank KYC Fraud (Aggressive)",
        scam_type="bank_fraud",
        weight=35.0,
        initial_message="🔴 URGENT: Your SBI account KYC verification is INCOMPLETE. Account will be PERMANENTLY BLOCKED in 12 hours. Reply IMMEDIATELY to avoid legal action!",
        fake_data=FakePlantedData(
            phone_numbers=["+91-8877665544", "8877665544"],
            bank_accounts=["234567890123", "5678901234567"],
            upi_ids=["sbi.kyc@okaxis", "sbicustomer@paytm"],
            case_ids=["KYC-2024-45678", "CASE/2024/1234"],
            phishing_links=["https://sbi-kyc-verify.scam/update?ref=KYC-2024-45678"],
        ),
        scammer_prompts=[
            "This is SBI fraud prevention department. Your KYC is incomplete. Failure to comply will result in account suspension.",
            "For immediate verification, send Re.1 to UPI: sbi.kyc@okaxis to confirm account activity. Ref: KYC-2024-45678",
            "Transfer processing fee Rs.50 to account 234567890123, IFSC: SBIN0001234 for KYC activation.",
            "What is your full account number? We need it to update KYC case CASE/2024/1234 in our system.",
            "Call our 24x7 helpline +91-8877665544 immediately for urgent assistance.",
            "Complete the verification at https://sbi-kyc-verify.scam/update?ref=KYC-2024-45678 within 1 hour.",
            "Your account 5678901234567 will be debited Rs.500 penalty if KYC not completed by today.",
            "Send Rs.100 to sbicustomer@paytm for document processing. This is mandatory as per RBI guidelines.",
            "Final warning: Account freeze in progress. Call 8877665544 NOW!",
            "Confirm the transaction ID after payment for instant KYC approval.",
        ],
    ),

    TestScenario(
        name="LIC Policy Renewal Scam (Multi-channel)",
        scam_type="insurance_fraud",
        weight=30.0,
        initial_message="⚠️ LIC POLICY LAPSED: Dear policyholder, your LIC policy POL987654321 has expired! All benefits including maturity amount Rs.8,50,000 will be FORFEITED in 48 hours. Pay renewal premium Rs.18,500 immediately!",
        fake_data=FakePlantedData(
            phone_numbers=["+91-7766554433", "7766554433", "+91-9876543210"],
            bank_accounts=["876543210987", "123456789012"],
            upi_ids=["lic.renewal@paytm", "licofficial@okhdfc"],
            phishing_links=["https://licrenewal.fake/verify?policy=POL987654321", "http://lic-india-renewal.scam/pay"],
            email_addresses=["support@licrenew.com", "renewal@licindiaofficial.com"],
            policy_numbers=["POL987654321", "LIC-2024-8765"],
            case_ids=["RENEWAL-2024-5432"],
        ),
        scammer_prompts=[
            "Dear customer, your LIC policy POL987654321 will expire in 24 hours. All coverage will be permanently lost.",
            "Immediate action required! Transfer Rs.18,500 renewal premium to UPI: lic.renewal@paytm",
            "For assistance, call our customer care: +91-7766554433 or WhatsApp: +91-9876543210",
            "Pay online at: https://licrenewal.fake/verify?policy=POL987654321 (secure payment gateway)",
            "Bank transfer option: Account 876543210987, IFSC: HDFC0001234, Beneficiary: LIC Renewal Services",
            "Email your payment receipt to support@licrenew.com for instant policy reactivation.",
            "Your case RENEWAL-2024-5432 will be closed permanently if no payment received today.",
            "Alternative payment: Visit http://lic-india-renewal.scam/pay and use policy LIC-2024-8765",
            "Contact renewal@licindiaofficial.com or pay to licofficial@okhdfc for express processing.",
            "Transfer to account 123456789012 for overnight policy revival with bonus benefits!",
        ],
    ),

    TestScenario(
        name="UPI Cashback Fraud (Lottery-style)",
        scam_type="upi_fraud",
        weight=35.0,
        initial_message="🎉 CONGRATULATIONS! You've WON Rs.1,50,000 cashback in PhonePe 10th Anniversary MEGA OFFER! 🎁 Claim NOW: http://phonepe-reward.scam/claim?id=CB12345 (Offer valid for 6 hours only!)",
        fake_data=FakePlantedData(
            phone_numbers=["+91-9988776655", "9988776655", "+91-8899001122"],
            upi_ids=["cashback.claim@ybl", "phonepe.rewards@paytm", "verification@phonepe"],
            phishing_links=[
                "http://phonepe-reward.scam/claim?id=CB12345",
                "http://phonepe-reward.scam/verify",
                "https://phonepe-anniversary.fake/redeem?order=REWARD-2024-5678"
            ],
            email_addresses=["rewards@phonepe-offers.com", "claims@phonepeanniversary.com"],
            order_numbers=["CB12345", "REWARD-2024-5678", "ORDER-9876543"],
        ),
        scammer_prompts=[
            "To claim Rs.1,50,000 reward, send Re.1 verification fee to cashback.claim@ybl (order CB12345)",
            "This is a ONE-TIME offer! Valid only today for order REWARD-2024-5678. Don't miss out!",
            "Call our prize claim helpline: +91-9988776655 or SMS 'CLAIM' to 8899001122",
            "Visit http://phonepe-reward.scam/verify and enter UPI PIN to process instant cashback transfer.",
            "For queries, email rewards@phonepe-offers.com with reference ORDER-9876543",
            "Pay Rs.500 processing fee to phonepe.rewards@paytm for government tax clearance (mandatory)",
            "Claim at https://phonepe-anniversary.fake/redeem?order=REWARD-2024-5678 before 11:59 PM!",
            "Hurry! Only 127 winners selected nationwide. Send account details to claims@phonepeanniversary.com",
            "Final verification: Pay Re.1 to verification@phonepe and receive Rs.1,50,000 within 30 minutes!",
            "LIMITED TIME: Share this with 5 friends to double your cashback to Rs.3,00,000! Call 9988776655 now!",
        ],
    ),
]


# ===================================================================
# CALLBACK SERVER (Receives real callbacks from API)
# ===================================================================

class CallbackServer:
    """Local HTTP server to receive callbacks from the honeypot API."""

    def __init__(self):
        self.app = FastAPI()
        self.callbacks: Dict[str, Dict] = {}  # sessionId -> callback_data
        self.server = None
        self.thread = None

        # Register callback endpoint
        @self.app.post("/callback")
        async def receive_callback(request: Request):
            """Receive callback from honeypot API."""
            try:
                data = await request.json()
                session_id = data.get("sessionId")
                if session_id:
                    self.callbacks[session_id] = data
                    print(f"  ✅ Callback received for session: {session_id[:8]}...")
                return {"status": "success"}
            except Exception as e:
                print(f"  ❌ Callback error: {e}")
                return {"status": "error", "message": str(e)}

    def start(self):
        """Start callback server in background thread."""
        def run_server():
            config = uvicorn.Config(
                self.app,
                host=CALLBACK_HOST,
                port=CALLBACK_PORT,
                log_level="error"  # Suppress uvicorn logs
            )
            self.server = uvicorn.Server(config)
            asyncio.run(self.server.serve())

        self.thread = threading.Thread(target=run_server, daemon=True)
        self.thread.start()
        time.sleep(2)  # Wait for server to start
        print(f"✅ Callback server started at {CALLBACK_URL}\n")

    def stop(self):
        """Stop callback server."""
        if self.server:
            self.server.should_exit = True

    def get_callback(self, session_id: str, timeout: int = 15) -> Optional[Dict]:
        """Wait for and retrieve callback for a session."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if session_id in self.callbacks:
                return self.callbacks[session_id]
            time.sleep(0.5)
        return None


# ===================================================================
# SCORING ENGINE
# ===================================================================

class ScenarioScorer:
    """Scores a scenario based on yes.pdf evaluation rubric."""

    def __init__(self, scenario: TestScenario):
        self.scenario = scenario
        self.conversation_history = []
        self.final_output = None
        self.turn_count = 0
        self.questions_asked = 0
        self.relevant_questions = 0
        self.red_flags_identified = 0
        self.information_elicitation_attempts = 0

    def score_scenario(self, final_output: Dict, conversation: List[Dict]) -> Dict[str, Any]:
        """Score the scenario based on official rubric (100 points)."""
        self.final_output = final_output
        self.conversation_history = conversation

        scores = {
            "scam_detection": self._score_scam_detection(),
            "extracted_intelligence": self._score_intelligence_extraction(),
            "conversation_quality": self._score_conversation_quality(),
            "engagement_quality": self._score_engagement_quality(),
            "response_structure": self._score_response_structure(),
        }

        total = sum(scores.values())
        scores["total"] = total
        scores["max_possible"] = 100
        scores["percentage"] = (total / 100) * 100

        return scores

    def _score_scam_detection(self) -> float:
        """Score: 20 points if scamDetected=true."""
        if not self.final_output:
            return 0.0

        scam_detected = self.final_output.get("scamDetected", False)
        return 20.0 if scam_detected else 0.0

    def _score_intelligence_extraction(self) -> float:
        """Score: 30 points total, divided by number of planted data fields."""
        if not self.final_output:
            return 0.0

        intel = self.final_output.get("extractedIntelligence", {})
        fake_data = self.scenario.fake_data

        # Count total planted fields
        total_fields = 0
        matched_fields = 0

        # Check phone numbers
        for phone in fake_data.phone_numbers:
            total_fields += 1
            if self._check_extracted(phone, intel.get("phoneNumbers", [])):
                matched_fields += 1

        # Check bank accounts
        for account in fake_data.bank_accounts:
            total_fields += 1
            if self._check_extracted(account, intel.get("bankAccounts", [])):
                matched_fields += 1

        # Check UPI IDs
        for upi in fake_data.upi_ids:
            total_fields += 1
            if self._check_extracted(upi, intel.get("upiIds", [])):
                matched_fields += 1

        # Check phishing links
        for link in fake_data.phishing_links:
            total_fields += 1
            if self._check_extracted(link, intel.get("phishingLinks", [])):
                matched_fields += 1

        # Check email addresses
        for email in fake_data.email_addresses:
            total_fields += 1
            if self._check_extracted(email, intel.get("emailAddresses", [])):
                matched_fields += 1

        # Check case IDs
        for case_id in fake_data.case_ids:
            total_fields += 1
            if self._check_extracted(case_id, intel.get("caseIds", [])):
                matched_fields += 1

        # Check policy numbers
        for policy in fake_data.policy_numbers:
            total_fields += 1
            if self._check_extracted(policy, intel.get("policyNumbers", [])):
                matched_fields += 1

        # Check order numbers
        for order in fake_data.order_numbers:
            total_fields += 1
            if self._check_extracted(order, intel.get("orderNumbers", [])):
                matched_fields += 1

        # Calculate score
        if total_fields == 0:
            return 0.0

        points_per_field = 30.0 / total_fields
        return matched_fields * points_per_field

    def _check_extracted(self, fake_value: str, extracted_list: List[str]) -> bool:
        """Check if fake value was extracted (fuzzy matching)."""
        if not extracted_list:
            return False

        # Normalize for comparison
        fake_normalized = fake_value.replace("+91-", "").replace("+91", "").replace("-", "").replace(" ", "").lower()

        for extracted in extracted_list:
            extracted_normalized = str(extracted).replace("+91-", "").replace("+91", "").replace("-", "").replace(" ", "").lower()
            if fake_normalized in extracted_normalized or extracted_normalized in fake_normalized:
                return True
        return False

    def _score_conversation_quality(self) -> float:
        """Score: 30 points total (Turn count: 8, Questions: 4, Relevant Q: 3, Red flags: 8, Elicitation: 7)."""
        score = 0.0

        # Analyze conversation
        self._analyze_conversation()

        # Turn count (8 pts max)
        if self.turn_count >= 8:
            score += 8.0
        elif self.turn_count >= 6:
            score += 6.0
        elif self.turn_count >= 4:
            score += 3.0

        # Questions asked (4 pts max)
        if self.questions_asked >= 5:
            score += 4.0
        elif self.questions_asked >= 3:
            score += 2.0
        elif self.questions_asked >= 1:
            score += 1.0

        # Relevant investigative questions (3 pts max)
        if self.relevant_questions >= 3:
            score += 3.0
        elif self.relevant_questions >= 2:
            score += 2.0
        elif self.relevant_questions >= 1:
            score += 1.0

        # Red flag identification (8 pts max)
        if self.red_flags_identified >= 5:
            score += 8.0
        elif self.red_flags_identified >= 3:
            score += 5.0
        elif self.red_flags_identified >= 1:
            score += 2.0

        # Information elicitation (7 pts max, 1.5 per attempt)
        elicitation_score = min(self.information_elicitation_attempts * 1.5, 7.0)
        score += elicitation_score

        return min(score, 30.0)

    def _analyze_conversation(self):
        """Analyze conversation for quality metrics."""
        honeypot_messages = [msg for msg in self.conversation_history if msg.get("sender") == "user"]
        self.turn_count = len(honeypot_messages)

        # Count questions (messages ending with ?)
        self.questions_asked = sum(1 for msg in honeypot_messages if "?" in msg.get("text", ""))

        # Detect relevant investigative questions
        investigative_keywords = [
            "who", "what", "where", "when", "why", "how",
            "name", "company", "department", "address", "website",
            "verify", "confirm", "proof", "identity", "badge", "id"
        ]
        for msg in honeypot_messages:
            text_lower = msg.get("text", "").lower()
            if "?" in text_lower and any(kw in text_lower for kw in investigative_keywords):
                self.relevant_questions += 1

        # Detect red flag identification
        red_flag_keywords = [
            "urgent", "suspicious", "unusual", "verify", "cautious", "concerned",
            "why", "never", "don't understand", "sounds strange", "seems odd"
        ]
        for msg in honeypot_messages:
            text_lower = msg.get("text", "").lower()
            if any(kw in text_lower for kw in red_flag_keywords):
                self.red_flags_identified += 1

        # Detect information elicitation attempts
        elicitation_phrases = [
            "your name", "company name", "department", "office address",
            "phone number", "email", "website", "supervisor", "employee id",
            "call you", "contact", "toll free"
        ]
        for msg in honeypot_messages:
            text_lower = msg.get("text", "").lower()
            if any(phrase in text_lower for phrase in elicitation_phrases):
                self.information_elicitation_attempts += 1

    def _score_engagement_quality(self) -> float:
        """Score: 10 points total (Duration: 4pts max, Messages: 6pts max)."""
        if not self.final_output:
            return 0.0

        score = 0.0

        duration = self.final_output.get("engagementDurationSeconds", 0)
        messages = self.final_output.get("totalMessagesExchanged", 0)

        # Duration scoring (4 pts max)
        if duration > 180:
            score += 4.0
        elif duration > 60:
            score += 2.0
        elif duration > 0:
            score += 1.0

        # Message count scoring (6 pts max)
        if messages >= 10:
            score += 6.0
        elif messages >= 5:
            score += 3.0
        elif messages > 0:
            score += 2.0

        return min(score, 10.0)

    def _score_response_structure(self) -> float:
        """Score: 10 points total (Required fields: 6pts, Optional fields: 4pts)."""
        if not self.final_output:
            return 0.0

        score = 0.0

        # Required fields (2 pts each)
        if "sessionId" in self.final_output:
            score += 2.0
        if "scamDetected" in self.final_output:
            score += 2.0
        if "extractedIntelligence" in self.final_output:
            score += 2.0

        # Optional fields (1 pt each)
        if "totalMessagesExchanged" in self.final_output and "engagementDurationSeconds" in self.final_output:
            score += 1.0
        if "agentNotes" in self.final_output:
            score += 1.0
        if "scamType" in self.final_output:
            score += 1.0
        if "confidenceLevel" in self.final_output:
            score += 1.0

        # Penalty for missing required fields
        missing_required = 0
        for field in ["sessionId", "scamDetected", "extractedIntelligence"]:
            if field not in self.final_output:
                missing_required += 1

        score -= missing_required  # -1 per missing required field

        return max(score, 0.0)


# ===================================================================
# EVALUATION ORCHESTRATOR
# ===================================================================

class HackathonEvaluator:
    """Orchestrates the complete hackathon evaluation."""

    def __init__(self, callback_server: CallbackServer):
        self.callback_server = callback_server
        self.results = []

    async def run_evaluation(self):
        """Run complete evaluation across all scenarios."""
        print("="*80)
        print("🎯 HACKATHON EVALUATION SIMULATOR")
        print("="*80)
        print(f"API Endpoint: {API_URL}")
        print(f"Test Scenarios: {len(SCENARIOS)}")
        print("="*80)
        print()

        for idx, scenario in enumerate(SCENARIOS, 1):
            print(f"[{idx}/{len(SCENARIOS)}] Running scenario: {scenario.name}")
            result = await self.run_scenario(scenario)
            self.results.append(result)
            print()

        # Generate final report
        self.generate_report()

    async def run_scenario(self, scenario: TestScenario) -> Dict:
        """Run a single scenario and collect results."""
        session_id = str(uuid.uuid4())
        conversation = []
        final_output = None

        # Configure API to send callbacks to our local server (via environment variable)
        # In production, you'd set GUVI_CALLBACK_URL to the test callback server

        try:
            # Initial message
            current_message = scenario.initial_message

            for turn in range(1, 11):  # Max 10 turns
                timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)

                # Send scammer message to API
                response = await self.send_message(
                    session_id=session_id,
                    message_text=current_message,
                    timestamp=timestamp,
                    conversation_history=conversation
                )

                if not response:
                    print(f"  ❌ Turn {turn}: API request failed")
                    break

                # Record conversation
                conversation.append({
                    "sender": "scammer",
                    "text": current_message,
                    "timestamp": timestamp
                })

                honeypot_reply = response.get("reply") or response.get("message") or response.get("text", "")
                conversation.append({
                    "sender": "user",
                    "text": honeypot_reply,
                    "timestamp": timestamp + 1000
                })

                print(f"  ✅ Turn {turn}/10: {len(honeypot_reply)} chars")

                # Add delay between turns to avoid overwhelming Render and allow processing time
                await asyncio.sleep(2.5)  # 2.5 second delay between turns

                # Use next scammer prompt or stop if out of prompts
                if turn < len(scenario.scammer_prompts):
                    current_message = scenario.scammer_prompts[turn - 1]
                else:
                    break

            # Wait for callback
            print(f"  ⏳ Waiting for callback...")
            final_output = self.callback_server.get_callback(session_id, timeout=20)

            if not final_output:
                print(f"  ⚠️  No callback received! Using fallback scoring.")
                # Fallback: minimal output for scoring
                final_output = {
                    "sessionId": session_id,
                    "scamDetected": False,
                    "extractedIntelligence": {},
                    "totalMessagesExchanged": len(conversation),
                    "engagementDurationSeconds": 0
                }

        except Exception as e:
            print(f"  ❌ Error: {e}")

        # Score the scenario
        scorer = ScenarioScorer(scenario)
        scores = scorer.score_scenario(final_output, conversation) if final_output else {"total": 0, "max_possible": 100}

        print(f"  📊 Score: {scores.get('total', 0):.1f}/{scores.get('max_possible', 100)} ({scores.get('percentage', 0):.1f}%)")

        return {
            "scenario": scenario,
            "conversation": conversation,
            "final_output": final_output,
            "scores": scores,
        }

    async def send_message(
        self,
        session_id: str,
        message_text: str,
        timestamp: int,
        conversation_history: List[Dict]
    ) -> Optional[Dict]:
        """Send a message to the API with retry logic for transient errors."""
        max_retries = 3
        retry_delay = 3  # seconds

        for attempt in range(max_retries):
            try:
                payload = {
                    "sessionId": session_id,
                    "message": {
                        "sender": "scammer",
                        "text": message_text,
                        "timestamp": timestamp
                    },
                    "conversationHistory": conversation_history,
                    "metadata": {
                        "channel": "SMS",
                        "language": "English",
                        "locale": "IN",
                        "callbackUrl": CALLBACK_URL  # Tell API where to send callback
                    }
                }

                async with httpx.AsyncClient(timeout=45.0) as client:  # Increased timeout
                    response = await client.post(
                        API_URL,
                        json=payload,
                        headers={
                            "x-api-key": API_KEY,
                            "Content-Type": "application/json"
                        }
                    )

                    if response.status_code == 200:
                        return response.json()
                    elif response.status_code == 502 and attempt < max_retries - 1:
                        # 502 Bad Gateway - retry (common during Render cold starts)
                        print(f"  ⚠️  502 error (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        print(f"  ⚠️  Request failed: {response.status_code} - {response.text[:200]}")
                        return None

            except httpx.TimeoutException:
                if attempt < max_retries - 1:
                    print(f"  ⚠️  Timeout (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    print(f"  ⚠️  Request timed out after {max_retries} attempts")
                    return None
            except Exception as e:
                print(f"  ⚠️  Request failed: {e}")
                return None

        return None

    def generate_report(self):
        """Generate final evaluation report."""
        print("\n")
        print("="*80)
        print("📊 FINAL EVALUATION REPORT")
        print("="*80)
        print()

        # Calculate weighted scenario score
        total_weighted_score = 0.0
        total_weight = 0.0

        for result in self.results:
            scenario = result["scenario"]
            scores = result["scores"]
            scenario_score = scores.get("total", 0)
            weighted_contribution = (scenario_score * scenario.weight) / 100
            total_weighted_score += weighted_contribution
            total_weight += scenario.weight

            print(f"Scenario: {scenario.name}")
            print(f"  Type: {scenario.scam_type}")
            print(f"  Weight: {scenario.weight}%")
            print(f"  Raw Score: {scenario_score:.1f}/100")
            print(f"  Weighted Contribution: {weighted_contribution:.2f}")
            print(f"  Breakdown:")
            print(f"    - Scam Detection: {scores.get('scam_detection', 0):.1f}/20")
            print(f"    - Intelligence Extraction: {scores.get('extracted_intelligence', 0):.1f}/30")
            print(f"    - Conversation Quality: {scores.get('conversation_quality', 0):.1f}/30")
            print(f"    - Engagement Quality: {scores.get('engagement_quality', 0):.1f}/10")
            print(f"    - Response Structure: {scores.get('response_structure', 0):.1f}/10")
            print()

        # Final score calculation
        weighted_scenario_score = total_weighted_score
        code_quality_score = 8.0  # Assume 8/10 for code quality (manual review)

        final_score = (weighted_scenario_score * 0.9) + code_quality_score

        print("="*80)
        print(f"Weighted Scenario Score: {weighted_scenario_score:.2f}/100")
        print(f"Scenario Portion (90%): {weighted_scenario_score * 0.9:.2f}")
        print(f"Code Quality (10%): {code_quality_score}/10")
        print("="*80)
        print(f"FINAL SCORE: {final_score:.2f}/100")
        print("="*80)
        print()

        # Recommendations
        print("🎯 RECOMMENDATIONS:")
        print()
        for result in self.results:
            scenario = result["scenario"]
            scores = result["scores"]

            if scores.get("scam_detection", 0) < 20:
                print(f"  ⚠️  {scenario.name}: scamDetected not True - check detection logic")

            if scores.get("extracted_intelligence", 0) < 20:
                print(f"  ⚠️  {scenario.name}: Low intelligence extraction - verify regex patterns and callback")

            if scores.get("conversation_quality", 0) < 20:
                print(f"  ⚠️  {scenario.name}: Poor conversation quality - increase turns, questions, red flags")

            if scores.get("engagement_quality", 0) < 7:
                print(f"  ⚠️  {scenario.name}: Low engagement - aim for 180+ seconds, 10+ messages")

        print()
        print("✅ Evaluation complete!")


# ===================================================================
# MAIN EXECUTION
# ===================================================================

async def main():
    """Main execution function."""
    # Start callback server
    callback_server = CallbackServer()
    callback_server.start()

    try:
        # Run evaluation
        evaluator = HackathonEvaluator(callback_server)
        await evaluator.run_evaluation()
    finally:
        # Stop callback server
        callback_server.stop()


if __name__ == "__main__":
    asyncio.run(main())
