"""
Generate a secure API key for the Scambot Honeypot.
"""
import secrets
import os


def generate_api_key(length: int = 32) -> str:
    """Generate a cryptographically secure API key."""
    return secrets.token_urlsafe(length)


def update_env_file(api_key: str, env_path: str = ".env"):
    """Update the .env file with the new API key."""
    if not os.path.exists(env_path):
        print(f"❌ {env_path} file not found!")
        return False

    # Read existing .env
    with open(env_path, 'r') as f:
        lines = f.readlines()

    # Update API_KEY line
    updated = False
    for i, line in enumerate(lines):
        if line.strip().startswith('API_KEY='):
            lines[i] = f'API_KEY={api_key}\n'
            updated = True
            break

    # Write back
    with open(env_path, 'w') as f:
        f.writelines(lines)

    return updated


if __name__ == "__main__":
    print("🔐 Scambot Honeypot - API Key Generator\n")

    # Generate new API key
    new_key = generate_api_key(32)

    print(f"✅ Generated API Key:\n")
    print(f"   {new_key}\n")

    # Ask if user wants to update .env
    response = input("Do you want to update your .env file with this key? (y/n): ")

    if response.lower() == 'y':
        if update_env_file(new_key):
            print("\n✅ .env file updated successfully!")
            print(f"\n📋 Your API key is: {new_key}")
            print("\n💡 Use this key in your API requests:")
            print(f'   -H "x-api-key: {new_key}"')
        else:
            print("\n❌ Failed to update .env file")
    else:
        print("\n📋 Copy this key and manually add it to your .env file:")
        print(f"   API_KEY={new_key}")

    print("\n" + "="*60)
    print("🔒 Keep this key secure and don't share it publicly!")
    print("="*60)
