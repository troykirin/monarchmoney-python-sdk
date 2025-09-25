#!/usr/bin/env python3
"""
Clear existing session and perform fresh login.
This script helps resolve login issues caused by stale session files.
"""

import asyncio
import os
import sys
from pathlib import Path

from monarchmoney import MonarchMoney

# Session file path
SESSION_FILE = ".mm/mm_session.pickle"


def clear_session():
    """Remove existing session file if it exists."""
    session_path = Path(SESSION_FILE)
    if session_path.exists():
        print(f"🗑️  Removing existing session file: {SESSION_FILE}")
        session_path.unlink()
        print("✅ Session file removed")
    else:
        print("ℹ️  No existing session file found")


async def fresh_login():
    """Perform a fresh login without using saved session."""
    print("🔐 Starting fresh login...")

    # Create MonarchMoney instance
    mm = MonarchMoney(session_file=SESSION_FILE)

    # Perform interactive login without using saved session
    await mm.interactive_login(use_saved_session=False, save_session=True)

    print("✅ Login successful!")

    # Test the connection by getting accounts
    try:
        accounts = await mm.get_accounts()
        print(f"📊 Found {len(accounts.get('accounts', []))} accounts")
        return True
    except Exception as e:
        print(f"❌ Error testing connection: {e}")
        return False


def main():
    """Main function to clear session and login fresh."""
    print("🚀 MonarchMoney Fresh Login Tool")
    print("=" * 40)

    # Clear existing session
    clear_session()

    # Perform fresh login
    try:
        success = asyncio.run(fresh_login())
        if success:
            print("\n🎉 Login completed successfully!")
            print("You can now run the main.py example.")
        else:
            print("\n❌ Login failed. Please check your credentials.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⏹️  Login cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
