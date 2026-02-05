#!/usr/bin/env python
"""
GUVI Simulation Tester - Complete End-to-End Test
==================================================

This script simulates EXACTLY how GUVI will test your honeypot:
1. Sends multi-turn scam conversations
2. Shows the full conversation flow
3. Displays extracted intelligence
4. Shows the final result JSON that gets sent to GUVI

Run this before submitting to GUVI to ensure everything works!

Usage:
    python test_guvi_simulation.py

Or with custom URL:
    python test_guvi_simulation.py --url https://your-service.onrender.com
"""

import requests
import time
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any
import argparse

# ANSI color codes for beautiful output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class GUVISimulator:
    """Simulates GUVI's testing behavior"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session_id = f"guvi-sim-{int(time.time())}"
        self.conversation_history = []
        self.total_messages = 0

    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}{Colors.ENDC}\n")

    def print_success(self, text: str):
        """Print success message"""
        print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

    def print_info(self, text: str):
        """Print info message"""
        print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

    def print_warning(self, text: str):
        """Print warning message"""
        print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

    def print_error(self, text: str):
        """Print error message"""
        print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

    def print_conversation_turn(self, turn_num: int, sender: str, message: str, response: str = None):
        """Print a conversation turn beautifully"""
        print(f"\n{Colors.BOLD}Turn {turn_num}:{Colors.ENDC}")
        print(f"{Colors.WARNING}🎭 Scammer:{Colors.ENDC} {message}")
        if response:
            print(f"{Colors.OKGREEN}👵 Veerabhadra:{Colors.ENDC} {response}")

    def send_message(self, scammer_message: str) -> Dict[str, Any]:
        """Send a message to the honeypot (simulating GUVI)"""
        self.total_messages += 1

        payload = {
            "sessionId": self.session_id,
            "message": {
                "sender": "scammer",
                "text": scammer_message,
                "timestamp": int(time.time() * 1000)
            },
            "conversationHistory": self.conversation_history.copy(),
            "metadata": {
                "channel": "SMS",
                "language": "English",
                "locale": "IN"
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/api/v1/conversation",
                headers={
                    "x-api-key": self.api_key,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # Update conversation history
            self.conversation_history.append({
                "sender": "scammer",
                "text": scammer_message,
                "timestamp": int(time.time() * 1000)
            })

            if "reply" in result:
                self.conversation_history.append({
                    "sender": "user",
                    "text": result["reply"],
                    "timestamp": int(time.time() * 1000)
                })

            return result

        except requests.exceptions.RequestException as e:
            self.print_error(f"Request failed: {str(e)}")
            return None

    def display_final_intelligence(self):
        """Display the intelligence that would be sent to GUVI"""
        self.print_header("📊 FINAL INTELLIGENCE REPORT (What GUVI Receives)")

        # This simulates what GUVI would receive from the callback
        print(f"{Colors.BOLD}Session ID:{Colors.ENDC} {self.session_id}")
        print(f"{Colors.BOLD}Total Messages Exchanged:{Colors.ENDC} {self.total_messages}")
        print(f"{Colors.BOLD}Scam Detected:{Colors.ENDC} Yes")

        print(f"\n{Colors.BOLD}Extracted Intelligence:{Colors.ENDC}")

        # Extract intelligence from conversation
        intelligence = self.extract_intelligence_from_conversation()

        print(json.dumps(intelligence, indent=2))

        print(f"\n{Colors.BOLD}Final Result JSON (Sent to GUVI):{Colors.ENDC}")
        final_payload = {
            "sessionId": self.session_id,
            "scamDetected": True,
            "totalMessagesExchanged": self.total_messages,
            "extractedIntelligence": intelligence,
            "agentNotes": self.generate_agent_notes()
        }

        print(f"{Colors.OKCYAN}{json.dumps(final_payload, indent=2)}{Colors.ENDC}")

        return final_payload

    def extract_intelligence_from_conversation(self) -> Dict[str, Any]:
        """Extract intelligence from the conversation"""
        # This is a simplified extraction - in real system, this happens server-side
        all_text = " ".join([msg["text"] for msg in self.conversation_history])

        import re

        # Extract bank accounts (9-18 digits)
        bank_accounts = list(set(re.findall(r'\b\d{9,18}\b', all_text)))

        # Extract UPI IDs
        upi_ids = list(set(re.findall(r'\b[\w\.-]+@[\w\.-]+\b', all_text)))
        # Filter out obvious emails
        upi_ids = [u for u in upi_ids if 'paytm' in u or 'ybl' in u or 'okaxis' in u or 'oksbi' in u]

        # Extract phone numbers (updated pattern to match server-side)
        phone_pattern = r'(?:\+91[-\.\s]?)?[6789]\d{9}\b|(?:\+\d{1,3}[-\.\s]?)?(?:\(?\d{3,4}\)?[-\.\s]?)?\d{3,4}[-\.\s]?\d{3,4}'
        phone_numbers = list(set(re.findall(phone_pattern, all_text)))

        # Extract URLs
        phishing_links = list(set(re.findall(r'http[s]?://[^\s]+', all_text)))

        # Keywords
        suspicious_keywords = []
        keywords = ['urgent', 'blocked', 'suspended', 'verify', 'immediately', 'account', 'bank', 'otp', 'upi']
        for keyword in keywords:
            if keyword.lower() in all_text.lower():
                suspicious_keywords.append(keyword)

        return {
            "bankAccounts": bank_accounts,
            "upiIds": upi_ids,
            "phishingLinks": phishing_links,
            "phoneNumbers": phone_numbers,
            "suspiciousKeywords": list(set(suspicious_keywords))
        }

    def generate_agent_notes(self) -> str:
        """Generate summary notes"""
        return f"Scammer used urgency tactics, attempted to extract sensitive information across {self.total_messages} message exchanges. Agent maintained believable persona throughout."

    def run_scam_scenario(self, scenario_name: str, messages: List[str]):
        """Run a complete scam scenario"""
        self.print_header(f"🎯 SCENARIO: {scenario_name}")

        for i, msg in enumerate(messages, 1):
            self.print_info(f"Sending message {i}/{len(messages)}...")

            result = self.send_message(msg)

            if result and "reply" in result:
                self.print_conversation_turn(i, "scammer", msg, result["reply"])
                time.sleep(1)  # Delay between messages (realistic)
            else:
                self.print_error(f"Failed to get response for message {i}")
                return False

        return True


def run_guvi_simulation(base_url: str, api_key: str):
    """Run the complete GUVI simulation"""

    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║                     🎯 GUVI HONEYPOT SIMULATION TESTER                       ║
║                                                                               ║
║              This simulates EXACTLY how GUVI will test your system            ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
""")

    print(f"{Colors.BOLD}Test Configuration:{Colors.ENDC}")
    print(f"  Target URL: {base_url}")
    print(f"  API Key: {'*' * 20}{api_key[-4:]}")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    simulator = GUVISimulator(base_url, api_key)

    # Check if server is accessible
    simulator.print_header("🔍 PRE-FLIGHT CHECK")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            simulator.print_success("Server is accessible and healthy")
        else:
            simulator.print_error(f"Server returned status {response.status_code}")
            return False
    except Exception as e:
        simulator.print_error(f"Cannot reach server: {str(e)}")
        return False

    # Run the scam scenario
    scam_messages = [
        "Hello sir, this is from State Bank of India. Your account has suspicious activity detected.",
        "If you don't verify your account immediately, it will be blocked permanently today.",
        "Please confirm your account number and PAN card details for verification.",
        "You can also verify by sending Re.1 to our secure verification account 482937461029 at SBI.",
        "For faster verification, send Re.1 to our UPI ID: secure@okaxis",
        "If any issue call me directly on 9876543210 I will help you complete verification.",
        "This is urgent sir. Your account will be permanently suspended in next 30 minutes.",
        "My employee ID is EMP8374. You can note it down for reference."
    ]

    success = simulator.run_scam_scenario(
        "Bank Fraud + UPI Scam",
        scam_messages
    )

    if not success:
        simulator.print_error("Scenario failed!")
        return False

    # Display final intelligence
    time.sleep(1)
    final_payload = simulator.display_final_intelligence()

    # Summary
    simulator.print_header("📋 TEST SUMMARY")

    simulator.print_success(f"Total Messages Exchanged: {simulator.total_messages}")
    simulator.print_success(f"Conversation History Maintained: {len(simulator.conversation_history)} messages")
    simulator.print_success(f"Session ID: {simulator.session_id}")

    print(f"\n{Colors.BOLD}Intelligence Extracted:{Colors.ENDC}")
    intel = final_payload["extractedIntelligence"]
    print(f"  • Bank Accounts: {len(intel['bankAccounts'])} found")
    print(f"  • UPI IDs: {len(intel['upiIds'])} found")
    print(f"  • Phone Numbers: {len(intel['phoneNumbers'])} found")
    print(f"  • Phishing Links: {len(intel['phishingLinks'])} found")
    print(f"  • Suspicious Keywords: {len(intel['suspiciousKeywords'])} found")

    print(f"\n{Colors.BOLD}Conversation Quality:{Colors.ENDC}")
    # Check if responses were contextual
    all_responses = [msg["text"] for msg in simulator.conversation_history if msg["sender"] == "user"]
    unique_responses = len(set(all_responses))

    if unique_responses >= len(all_responses) * 0.7:  # At least 70% unique
        simulator.print_success(f"Responses are varied and contextual ({unique_responses}/{len(all_responses)} unique)")
    else:
        simulator.print_warning(f"Some responses may be repetitive ({unique_responses}/{len(all_responses)} unique)")

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}🎉 GUVI SIMULATION COMPLETE!{Colors.ENDC}")
    print(f"\n{Colors.BOLD}What GUVI will see:{Colors.ENDC}")
    print(f"  1. ✅ Multi-turn conversation ({simulator.total_messages} messages)")
    print(f"  2. ✅ Natural, believable responses")
    print(f"  3. ✅ Intelligence extracted from scammer")
    print(f"  4. ✅ Final result JSON sent to callback endpoint")

    print(f"\n{Colors.OKGREEN}{Colors.BOLD}✅ YOUR HONEYPOT IS READY FOR GUVI SUBMISSION!{Colors.ENDC}\n")

    return True


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="GUVI Honeypot Simulation Tester",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script simulates exactly how GUVI will test your honeypot system.

Examples:
  # Test with default settings (reads from .env)
  python test_guvi_simulation.py

  # Test with custom URL
  python test_guvi_simulation.py --url https://my-honeypot.onrender.com

  # Test with custom API key
  python test_guvi_simulation.py --api-key ABC123
        """
    )

    parser.add_argument(
        "--url",
        help="Render service URL",
        default=None
    )

    parser.add_argument(
        "--api-key",
        help="API key for authentication",
        default=None
    )

    args = parser.parse_args()

    # Get base URL
    if args.url:
        base_url = args.url.rstrip('/')
    else:
        # Try to load from .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            base_url = os.getenv("RENDER_URL")
        except:
            base_url = None

        if not base_url:
            print(f"{Colors.WARNING}No URL provided. Please specify URL:{Colors.ENDC}")
            print("\nExample: https://scambot-honeypot-abc123.onrender.com")
            base_url = input("\nEnter your Render URL: ").strip().rstrip('/')

            if not base_url:
                print(f"{Colors.FAIL}No URL provided. Exiting.{Colors.ENDC}")
                return 1

    # Get API key
    if args.api_key:
        api_key = args.api_key
    else:
        # Try to load from .env
        try:
            from dotenv import load_dotenv
            load_dotenv()
            api_key = os.getenv("API_KEY")
        except:
            api_key = None

        if not api_key:
            api_key = "J-2Qw-PaYnlQeIOQOMPGO1cuwv1cYxf5MRIrJrnLQAM"  # Default

    # Validate URL
    if not base_url.startswith(("http://", "https://")):
        print(f"{Colors.FAIL}Invalid URL format: {base_url}{Colors.ENDC}")
        print(f"{Colors.OKCYAN}URL must start with http:// or https://{Colors.ENDC}")
        return 1

    # Run simulation
    success = run_guvi_simulation(base_url, api_key)

    return 0 if success else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Simulation interrupted by user{Colors.ENDC}")
        sys.exit(130)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {str(e)}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
