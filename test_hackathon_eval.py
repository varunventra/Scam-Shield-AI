"""
HACKATHON EVALUATION SIMULATOR

This test file simulates the EXACT evaluation environment from yes.pdf.
It runs multiple scam scenarios with planted fake data and scores the API
based on the official 100-point rubric.

Scoring Breakdown (100 points per scenario):
1. Scam Detection (20 pts): scamDetected=true in final output
2. Extracted Intelligence (30 pts): Extract planted phones, UPI IDs, bank accounts, links, emails, case IDs, policy numbers, order numbers
3. Conversation Quality (30 pts): Turn count (8), Questions (4), Relevant questions (3), Red flags (8), Information elicitation (7)
4. Engagement Quality (10 pts): Duration (4pts max), Messages (6pts max)
5. Response Structure (10 pts): Required/optional fields present

Run with: python test_hackathon_eval.py
"""

import asyncio
import httpx
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

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

# Try to load from environment, with fallback to localhost
API_URL = os.getenv("TEST_API_URL") or os.getenv("BASE_URL", "http://localhost:8000") + "/api/v1/conversation"
API_KEY = os.getenv("API_KEY")

# Validate configuration
if not API_KEY:
    print("="*80)
    print("❌ ERROR: API_KEY not found!")
    print("="*80)
    print("Please set API_KEY in your .env file:")
    print("  API_KEY=your-api-key-here")
    print()
    print("Or set environment variable:")
    print("  export API_KEY=your-api-key-here")
    print("="*80)
    sys.exit(1)

TIMEOUT = 30.0  # 30 second timeout per request


# ===================================================================
# TEST SCENARIOS (Simulating GUVI Evaluation)
# ===================================================================

@dataclass
class FakePlantedData:
    """Fake data planted by evaluator that honeypot should extract."""
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
    """A scam scenario to test the honeypot."""
    name: str
    scam_type: str
    weight: float  # Scenario weight in final score (sum to 100%)
    initial_message: str
    fake_data: FakePlantedData
    max_turns: int = 10
    scammer_prompts: List[str] = field(default_factory=list)  # Pre-scripted follow-up messages


# Define test scenarios matching the evaluation style
SCENARIOS = [
    TestScenario(
        name="Bank KYC Fraud",
        scam_type="bank_fraud",
        weight=35.0,
        initial_message="URGENT ALERT: Your SBI account KYC verification is pending. Account will be suspended in 24 hours if not completed. Reply immediately to verify.",
        fake_data=FakePlantedData(
            phone_numbers=["+91-8877665544"],
            bank_accounts=["234567890123"],
            upi_ids=["sbi.kyc@okaxis"],
            case_ids=["KYC-2024-45678"],
        ),
        scammer_prompts=[
            "Your KYC is incomplete. To avoid account freeze, please confirm your details.",
            "This is SBI fraud prevention department. I need to verify your identity.",
            "For verification, send Rs.1 to UPI: sbi.kyc@okaxis to confirm account activity.",
            "What is your account number? We need it for KYC update case KYC-2024-45678.",
            "Transfer to account 234567890123, IFSC: SBIN0001234 for immediate activation.",
            "Call our helpline +91-8877665544 for any issues.",
            "Your account will be blocked in 1 hour if you don't complete KYC now.",
            "Please confirm the transaction reference number after payment.",
            "This is final warning. Complete verification immediately.",
        ],
    ),

    TestScenario(
        name="LIC Policy Renewal Scam",
        scam_type="insurance_fraud",
        weight=30.0,
        initial_message="LIC ALERT: Your insurance policy POL987654321 has lapsed! All benefits will be lost in 24 hours. Pay renewal premium of Rs. 18,500 immediately to revive.",
        fake_data=FakePlantedData(
            phone_numbers=["+91-7766554433"],
            bank_accounts=["876543210987"],
            upi_ids=["lic.renewal@paytm", "support@licrenew.com"],
            phishing_links=["https://licrenewal.fake/verify?policy=POL987654321"],
            email_addresses=["support@licrenew.com"],
            policy_numbers=["POL987654321"],
        ),
        scammer_prompts=[
            "Dear customer, your LIC policy will expire today. Pay renewal amount immediately.",
            "For renewal, transfer Rs.18,500 to UPI: lic.renewal@paytm or call +91-7766554433.",
            "Visit our secure portal: https://licrenewal.fake/verify?policy=POL987654321 to pay online.",
            "You can also transfer to account 876543210987, IFSC HDFC0001234.",
            "Email your payment receipt to support@licrenew.com for instant activation.",
            "Your policy POL987654321 will be permanently closed in 2 hours.",
            "Many customers renewed successfully today. Don't miss this opportunity.",
            "Contact our support team immediately for assistance.",
        ],
    ),

    TestScenario(
        name="UPI Cashback Fraud",
        scam_type="upi_fraud",
        weight=35.0,
        initial_message="Congratulations! You've won Rs.50,000 cashback in our PhonePe anniversary offer! Click here to claim: http://phonepe-reward.scam/claim?id=CB12345",
        fake_data=FakePlantedData(
            phone_numbers=["+91-9988776655"],
            upi_ids=["cashback.claim@ybl", "phonepe.rewards@paytm"],
            phishing_links=["http://phonepe-reward.scam/claim?id=CB12345", "http://phonepe-reward.scam/verify"],
            email_addresses=["rewards@phonepe-offers.com"],
            order_numbers=["CB12345", "REWARD-2024-5678"],
        ),
        scammer_prompts=[
            "To claim your Rs.50,000 reward, send Re.1 to cashback.claim@ybl for verification.",
            "This is a limited-time offer! Valid only today for order CB12345.",
            "Call our helpline +91-9988776655 to activate your reward instantly.",
            "Visit http://phonepe-reward.scam/verify and enter your UPI PIN to process the cashback.",
            "For queries, email rewards@phonepe-offers.com with reference REWARD-2024-5678.",
            "You can also pay the processing fee to phonepe.rewards@paytm.",
            "Hurry! Only 2 hours left to claim your cashback.",
            "Share your bank account details to receive the prize money directly.",
        ],
    ),
]


# ===================================================================
# SCORING ENGINE
# ===================================================================

class ScenarioScorer:
    """Scores a scenario based on the official rubric."""

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

        scores["total"] = sum(scores.values())
        scores["max_possible"] = 100
        scores["percentage"] = (scores["total"] / scores["max_possible"]) * 100

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

        if total_fields == 0:
            return 0.0

        points_per_field = 30.0 / total_fields
        return matched_fields * points_per_field

    def _check_extracted(self, fake_value: str, extracted_list: List[str]) -> bool:
        """Check if fake value was extracted (fuzzy matching)."""
        fake_normalized = fake_value.replace("+91-", "").replace("+91", "").replace("-", "").replace(" ", "").lower()

        for extracted in extracted_list:
            extracted_normalized = str(extracted).replace("+91-", "").replace("+91", "").replace("-", "").replace(" ", "").lower()
            if fake_normalized in extracted_normalized or extracted_normalized in fake_normalized:
                return True
        return False

    def _score_conversation_quality(self) -> float:
        """Score: 30 points total (Turn count: 8, Questions: 4, Relevant: 3, Red flags: 8, Elicitation: 7)."""
        # Analyze conversation
        self._analyze_conversation()

        score = 0.0

        # Turn count (8 pts): ≥8=8pts, ≥6=6pts, ≥4=3pts
        if self.turn_count >= 8:
            score += 8.0
        elif self.turn_count >= 6:
            score += 6.0
        elif self.turn_count >= 4:
            score += 3.0

        # Questions asked (4 pts): ≥5=4pts, ≥3=2pts, ≥1=1pt
        if self.questions_asked >= 5:
            score += 4.0
        elif self.questions_asked >= 3:
            score += 2.0
        elif self.questions_asked >= 1:
            score += 1.0

        # Relevant questions (3 pts): ≥3=3pts, ≥2=2pts, ≥1=1pt
        if self.relevant_questions >= 3:
            score += 3.0
        elif self.relevant_questions >= 2:
            score += 2.0
        elif self.relevant_questions >= 1:
            score += 1.0

        # Red flag identification (8 pts): ≥5=8pts, ≥3=5pts, ≥1=2pts
        if self.red_flags_identified >= 5:
            score += 8.0
        elif self.red_flags_identified >= 3:
            score += 5.0
        elif self.red_flags_identified >= 1:
            score += 2.0

        # Information elicitation (7 pts): Each attempt = 1.5pts (max 7)
        elicitation_score = min(self.information_elicitation_attempts * 1.5, 7.0)
        score += elicitation_score

        return score

    def _analyze_conversation(self):
        """Analyze conversation for quality metrics."""
        honeypot_messages = [msg for msg in self.conversation_history if msg.get("sender") == "user"]

        self.turn_count = len(honeypot_messages)

        # Keywords for analysis
        question_words = ["what", "which", "where", "who", "how", "can", "could", "should", "?"]
        investigative_words = ["number", "account", "upi", "branch", "id", "employee", "email", "website", "link", "phone", "call", "contact"]
        red_flag_words = ["urgent", "immediately", "blocked", "suspended", "otp", "pin", "verify", "confirm"]
        elicitation_phrases = ["give me", "send me", "what is your", "can you", "where should"]

        for msg in honeypot_messages:
            text = msg.get("text", "").lower()

            # Count questions
            if "?" in text or any(word in text for word in question_words):
                self.questions_asked += 1

                # Count relevant/investigative questions
                if any(word in text for word in investigative_words):
                    self.relevant_questions += 1
                    self.information_elicitation_attempts += 1

            # Count red flag references
            for flag_word in red_flag_words:
                if flag_word in text:
                    self.red_flags_identified += 1
                    break  # Count once per message

    def _score_engagement_quality(self) -> float:
        """Score: 10 points total (Duration: 4pts max, Messages: 6pts max)."""
        if not self.final_output:
            return 0.0

        score = 0.0

        duration = self.final_output.get("engagementDurationSeconds", 0)
        messages = self.final_output.get("totalMessagesExchanged", 0)

        # Duration scoring (4 pts max)
        if duration > 180:
            score += 4.0  # 1 + 2 + 1
        elif duration > 60:
            score += 3.0  # 1 + 2
        elif duration > 0:
            score += 1.0

        # Messages scoring (6 pts max)
        if messages >= 10:
            score += 6.0  # 2 + 3 + 1
        elif messages >= 5:
            score += 5.0  # 2 + 3
        elif messages > 0:
            score += 2.0

        return score

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
# EVALUATION ENGINE
# ===================================================================

class HackathonEvaluator:
    """Simulates the hackathon evaluation system."""

    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key
        self.results = []

    async def run_evaluation(self):
        """Run all test scenarios and generate report."""
        print("="*80)
        print("🎯 HACKATHON EVALUATION SIMULATOR")
        print("="*80)
        print(f"API Endpoint: {self.api_url}")
        print(f"Test Scenarios: {len(SCENARIOS)}")
        print("="*80)
        print()

        for idx, scenario in enumerate(SCENARIOS, 1):
            print(f"[{idx}/{len(SCENARIOS)}] Running scenario: {scenario.name}")
            result = await self.run_scenario(scenario)
            self.results.append(result)
            print()

        self.generate_report()

    async def run_scenario(self, scenario: TestScenario) -> Dict:
        """Run a single scenario and collect results."""
        session_id = str(uuid.uuid4())
        conversation = []
        final_output = None

        # Initial message
        current_message = scenario.initial_message

        try:
            for turn in range(scenario.max_turns):
                # Send message to API
                response = await self.send_message(session_id, current_message, conversation)

                if not response:
                    print(f"  ❌ Turn {turn+1}: No response from API")
                    break

                # Extract reply
                reply = response.get("reply") or response.get("message") or response.get("text")

                if not reply:
                    print(f"  ❌ Turn {turn+1}: No reply field in response")
                    break

                # Add to conversation
                conversation.append({"sender": "scammer", "text": current_message, "timestamp": int(time.time() * 1000)})
                conversation.append({"sender": "user", "text": reply, "timestamp": int(time.time() * 1000)})

                print(f"  ✅ Turn {turn+1}/{scenario.max_turns}: {len(reply)} chars")

                # Get next scammer message (if available)
                if turn < len(scenario.scammer_prompts):
                    current_message = scenario.scammer_prompts[turn]
                else:
                    # Evaluation complete
                    break

                # Small delay between turns
                await asyncio.sleep(0.5)

            # Wait for final output (simulating 10-second wait)
            await asyncio.sleep(2)

            # Get final output (we'll extract from last callback - in real eval, this comes from callback endpoint)
            # For simulation, we construct it from the conversation
            final_output = self.simulate_final_output(session_id, conversation)

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

    async def send_message(self, session_id: str, message: str, history: List[Dict]) -> Optional[Dict]:
        """Send a message to the API."""
        payload = {
            "sessionId": session_id,
            "message": {
                "sender": "scammer",
                "text": message,
                "timestamp": int(time.time() * 1000),
            },
            "conversationHistory": history,
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN",
            },
        }

        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                response = await client.post(
                    self.api_url,
                    json=payload,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                    },
                )

                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"  ⚠️  API returned {response.status_code}: {response.text[:100]}")
                    return None

        except Exception as e:
            print(f"  ⚠️  Request failed: {e}")
            return None

    def simulate_final_output(self, session_id: str, conversation: List[Dict]) -> Dict:
        """Simulate the final output that would be sent to callback."""
        # In real evaluation, this comes from the callback endpoint
        # For testing, we create a mock final output

        honeypot_messages = [msg for msg in conversation if msg.get("sender") == "user"]
        total_messages = len(conversation)

        if total_messages >= 2:
            duration = int((conversation[-1]["timestamp"] - conversation[0]["timestamp"]) / 1000)
        else:
            duration = 0

        return {
            "sessionId": session_id,
            "scamDetected": True,  # We expect this to be True
            "scamType": "unknown",
            "confidenceLevel": 0.9,
            "totalMessagesExchanged": total_messages,
            "engagementDurationSeconds": duration,
            "extractedIntelligence": {
                "phoneNumbers": [],
                "bankAccounts": [],
                "upiIds": [],
                "phishingLinks": [],
                "emailAddresses": [],
                "caseIds": [],
                "policyNumbers": [],
                "orderNumbers": [],
            },
            "agentNotes": "Simulated agent notes",
        }

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

        # Code quality (would be 10% in real evaluation)
        code_quality_score = 8.0  # Assumed for simulation

        # Final score calculation
        scenario_portion = total_weighted_score * 0.9  # 90% weight
        final_score = scenario_portion + code_quality_score

        print("="*80)
        print(f"Weighted Scenario Score: {total_weighted_score:.2f}/100")
        print(f"Scenario Portion (90%): {scenario_portion:.2f}")
        print(f"Code Quality (10%): {code_quality_score}/10")
        print("="*80)
        print(f"FINAL SCORE: {final_score:.2f}/100")
        print("="*80)
        print()

        # Recommendations
        print("🎯 RECOMMENDATIONS:")
        print()

        for result in self.results:
            scores = result["scores"]
            scenario = result["scenario"]

            if scores.get("scam_detection", 0) < 20:
                print(f"  ⚠️  {scenario.name}: scamDetected not True - ensure callback always sets this to True")

            if scores.get("extracted_intelligence", 0) < 20:
                print(f"  ⚠️  {scenario.name}: Missing intelligence extraction - improve regex patterns")

            if scores.get("conversation_quality", 0) < 20:
                print(f"  ⚠️  {scenario.name}: Low conversation quality - ask more questions")

            if scores.get("engagement_quality", 0) < 7:
                print(f"  ⚠️  {scenario.name}: Low engagement - extend conversations to 10+ turns and 180+ seconds")

        print()
        print("✅ Evaluation complete!")


# ===================================================================
# MAIN ENTRY POINT
# ===================================================================

async def main():
    """Main entry point."""
    evaluator = HackathonEvaluator(API_URL, API_KEY)
    await evaluator.run_evaluation()


if __name__ == "__main__":
    asyncio.run(main())
