"""
Manual testing script for Scambot Honeypot API.
Loads test cases from test_cases.json and runs them.
"""
import json
import requests
import time
from typing import Dict, Any


class ScambotTester:
    """Test runner for Scambot API"""

    def __init__(self, base_url: str = "http://localhost:8000", api_key: str = None):
        self.base_url = base_url
        self.api_key = api_key or "hackathon-secret-key-2024"
        self.session = requests.Session()
        self.session.headers.update({
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        })

    def test_health(self) -> bool:
        """Test health endpoint"""
        try:
            response = requests.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ Health check passed")
                print(f"   {response.json()}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def send_message(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send a message to the API"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/v1/conversation",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

    def run_single_test(self, test_case: Dict[str, Any]) -> None:
        """Run a single test case"""
        print(f"\n{'='*70}")
        print(f"Test #{test_case['id']}: {test_case['name']}")
        print(f"{'='*70}")
        print(f"Description: {test_case['description']}")
        print(f"\nScammer says:")
        print(f"  '{test_case['request']['message']['text']}'")

        # Send request
        start_time = time.time()
        result = self.send_message(test_case['request'])
        elapsed = time.time() - start_time

        # Display result
        if 'error' in result:
            print(f"\n❌ Error: {result['error']}")
        else:
            print(f"\nAgent responds (in {elapsed:.2f}s):")
            print(f"  '{result.get('reply', 'No reply')}'")
            print(f"\nStatus: {result.get('status', 'unknown')}")

            # Show expected intelligence
            if 'expected_intelligence' in test_case:
                print(f"\nExpected Intelligence:")
                for key, value in test_case['expected_intelligence'].items():
                    print(f"  - {key}: {value}")

    def run_multi_turn_test(self, multi_turn: Dict[str, Any]) -> None:
        """Run a multi-turn conversation test"""
        print(f"\n{'='*70}")
        print(f"Multi-turn Test: {multi_turn['name']}")
        print(f"{'='*70}")
        print(f"Description: {multi_turn['description']}")
        print(f"Total turns: {len(multi_turn['turns'])}")

        for turn_data in multi_turn['turns']:
            turn_num = turn_data['turn']
            print(f"\n--- Turn {turn_num} ---")
            print(f"Scammer: {turn_data['request']['message']['text']}")

            # Send request
            result = self.send_message(turn_data['request'])

            if 'error' in result:
                print(f"❌ Error: {result['error']}")
                break
            else:
                print(f"Agent: {result.get('reply', 'No reply')}")

            # Small delay between turns
            time.sleep(1)

    def load_test_cases(self, file_path: str = "test_cases.json") -> Dict[str, Any]:
        """Load test cases from JSON file"""
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Test cases file not found: {file_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in test cases: {e}")
            return {}

    def run_all_tests(self, test_file: str = "test_cases.json") -> None:
        """Run all test cases"""
        print("""
╔════════════════════════════════════════════════════════════════════╗
║           SCAMBOT HONEYPOT - MANUAL TEST RUNNER                    ║
╚════════════════════════════════════════════════════════════════════╝
""")

        # Health check first
        if not self.test_health():
            print("\n❌ API is not healthy. Please start the server first.")
            return

        # Load test cases
        data = self.load_test_cases(test_file)
        if not data:
            return

        test_cases = data.get('test_cases', [])
        multi_turn_cases = data.get('multi_turn_examples', [])

        # Run single-message tests
        print(f"\n\n{'#'*70}")
        print("# SINGLE MESSAGE TESTS")
        print(f"{'#'*70}")

        for test_case in test_cases:
            self.run_single_test(test_case)
            time.sleep(1)  # Small delay between tests

        # Run multi-turn tests
        if multi_turn_cases:
            print(f"\n\n{'#'*70}")
            print("# MULTI-TURN CONVERSATION TESTS")
            print(f"{'#'*70}")

            for multi_turn in multi_turn_cases:
                self.run_multi_turn_test(multi_turn)
                time.sleep(2)  # Longer delay between multi-turn tests

        print(f"\n\n{'='*70}")
        print("Testing completed!")
        print(f"{'='*70}\n")

    def interactive_mode(self) -> None:
        """Interactive testing mode"""
        print("""
╔════════════════════════════════════════════════════════════════════╗
║           SCAMBOT HONEYPOT - INTERACTIVE TEST MODE                 ║
╚════════════════════════════════════════════════════════════════════╝

Enter scam messages to test the API. Type 'quit' to exit.
""")

        session_id = "interactive-" + str(int(time.time()))
        conversation_history = []

        while True:
            try:
                message = input("\nScammer message: ").strip()

                if message.lower() in ['quit', 'exit', 'q']:
                    print("Goodbye!")
                    break

                if not message:
                    continue

                # Create request
                payload = {
                    "sessionId": session_id,
                    "message": {
                        "sender": "scammer",
                        "text": message,
                        "timestamp": int(time.time() * 1000)
                    },
                    "conversationHistory": conversation_history.copy()
                }

                # Send request
                print("\n⏳ Waiting for agent response...")
                result = self.send_message(payload)

                if 'error' in result:
                    print(f"❌ Error: {result['error']}")
                else:
                    reply = result.get('reply', 'No reply')
                    print(f"\n🤖 Agent: {reply}")

                    # Update conversation history
                    conversation_history.append({
                        "sender": "scammer",
                        "text": message,
                        "timestamp": payload['message']['timestamp']
                    })
                    conversation_history.append({
                        "sender": "user",
                        "text": reply,
                        "timestamp": payload['message']['timestamp'] + 500
                    })

                    print(f"\n💡 Conversation turns: {len(conversation_history) // 2}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main function"""
    import sys

    tester = ScambotTester()

    if len(sys.argv) > 1 and sys.argv[1] in ['-i', '--interactive']:
        # Interactive mode
        tester.interactive_mode()
    else:
        # Run all test cases
        tester.run_all_tests()


if __name__ == "__main__":
    main()
