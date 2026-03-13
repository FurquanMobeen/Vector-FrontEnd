#!/usr/bin/env python3
import bcrypt
import getpass

def main():
    print("=" * 60)
    print("  Password Hash Generator for Vector Search Authentication")
    print("=" * 60)
    print()

    password = getpass.getpass("Enter password to hash: ")

    if not password:
        print("\nError: Password cannot be empty")
        return

    # Generate hash using bcrypt
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    print()
    print("✅ Generated bcrypt hash:")
    print("-" * 60)
    print(hashed_password)
    print("-" * 60)
    print()
    print("📋 Next steps:")
    print("1. Copy the hash above")
    print("2. Open config/auth_config.yaml")
    print("3. Paste it under the 'password' field for your user")
    print()
    print("Example:")
    print("  credentials:")
    print("    usernames:")
    print("      your_username:")
    print("        email: user@example.com")
    print("        name: Your Name")
    print(f"        password: {hashed_password}")
    print()

if __name__ == "__main__":
    main()
