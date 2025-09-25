#!/usr/bin/env python3
"""
Test script to verify TTL session management functionality.
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta

# Define constants locally to avoid importing main.py
_SESSION_FILE_ = ".mm/mm_session.pickle"
_SESSION_TTL_HOURS_ = 1


def check_session():
    """Check if session file exists and is still valid (within TTL)."""
    session_path = Path(_SESSION_FILE_)
    
    if not session_path.exists():
        print("ℹ️  No existing session file found")
        return False
    
    try:
        # Check session file modification time
        session_mtime = datetime.fromtimestamp(session_path.stat().st_mtime)
        now = datetime.now()
        age = now - session_mtime
        
        if age < timedelta(hours=_SESSION_TTL_HOURS_):
            remaining = timedelta(hours=_SESSION_TTL_HOURS_) - age
            print(f"✅ Valid session found (expires in {remaining})")
            return True
        else:
            print(f"⏰ Session expired (age: {age}), clearing...")
            session_path.unlink()
            print("🗑️  Session cleared")
            return False
            
    except Exception as e:
        print(f"❌ Error checking session: {e}")
        print("🗑️  Clearing corrupted session...")
        session_path.unlink()
        return False


def test_ttl_logic():
    """Test the TTL session management logic."""
    print("🧪 Testing TTL Session Management")
    print("=" * 40)
    
    # Clean up any existing session
    session_path = Path(_SESSION_FILE_)
    if session_path.exists():
        session_path.unlink()
        print("🗑️  Cleaned up existing session")
    
    # Test 1: No session file
    print("\n1️⃣  Testing with no session file:")
    result = check_session()
    print(f"   Result: {result} (should be False)")
    
    # Test 2: Create a fresh session file
    print("\n2️⃣  Creating fresh session file:")
    session_path.parent.mkdir(exist_ok=True)
    session_path.touch()
    result = check_session()
    print(f"   Result: {result} (should be True)")
    
    # Test 3: Simulate expired session by modifying timestamp
    print("\n3️⃣  Simulating expired session:")
    # Set modification time to 2 hours ago
    expired_time = time.time() - (2 * 3600)  # 2 hours ago
    os.utime(session_path, (expired_time, expired_time))
    result = check_session()
    print(f"   Result: {result} (should be False)")
    
    # Test 4: Create session file just under TTL limit
    print("\n4️⃣  Testing session just under TTL limit:")
    session_path.touch()
    # Set modification time to 59 minutes ago
    recent_time = time.time() - (59 * 60)  # 59 minutes ago
    os.utime(session_path, (recent_time, recent_time))
    result = check_session()
    print(f"   Result: {result} (should be True)")
    
    print(f"\n✅ TTL Session Management Test Complete")
    print(f"   TTL: {_SESSION_TTL_HOURS_} hour(s)")
    print(f"   Session file: {_SESSION_FILE_}")


if __name__ == "__main__":
    test_ttl_logic()
