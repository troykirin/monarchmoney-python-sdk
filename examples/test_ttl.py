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


def get_session_ttl():
    """Get session TTL based on environment."""
    env = os.getenv("MONARCH_ENV", "development").lower()
    if env == "production":
        return 0.25  # 15 minutes
    else:
        return 1.0   # 1 hour for development


def check_session():
    """Check if session file exists and is still valid (within TTL)."""
    session_path = Path(_SESSION_FILE_)
    ttl_hours = get_session_ttl()
    env = os.getenv("MONARCH_ENV", "development").lower()
    
    if not session_path.exists():
        print("ℹ️  No existing session file found")
        return False
    
    try:
        # Check session file modification time
        session_mtime = datetime.fromtimestamp(session_path.stat().st_mtime)
        now = datetime.now()
        age = now - session_mtime
        
        if age < timedelta(hours=ttl_hours):
            remaining = timedelta(hours=ttl_hours) - age
            print(f"✅ Valid session found (expires in {remaining}) [{env} mode]")
            return True
        else:
            print(f"⏰ Session expired (age: {age}), clearing... [{env} mode]")
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
    print("=" * 50)
    
    # Test both environments
    for env_name, env_value in [("Development", "development"), ("Production", "production")]:
        print(f"\n🔧 Testing {env_name} Environment:")
        print("-" * 30)
        
        # Set environment
        os.environ["MONARCH_ENV"] = env_value
        ttl_hours = get_session_ttl()
        print(f"   TTL: {ttl_hours} hour(s) ({int(ttl_hours * 60)} minutes)")
        
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
        
        # Test 3: Simulate expired session
        print("\n3️⃣  Simulating expired session:")
        # Set modification time to exceed TTL
        expired_time = time.time() - (int(ttl_hours * 3600) + 300)  # TTL + 5 minutes
        os.utime(session_path, (expired_time, expired_time))
        result = check_session()
        print(f"   Result: {result} (should be False)")
        
        # Test 4: Create session file just under TTL limit
        print("\n4️⃣  Testing session just under TTL limit:")
        session_path.touch()
        # Set modification time to just under TTL
        recent_time = time.time() - (int(ttl_hours * 3600) - 60)  # TTL - 1 minute
        os.utime(session_path, (recent_time, recent_time))
        result = check_session()
        print(f"   Result: {result} (should be True)")
    
    print(f"\n✅ TTL Session Management Test Complete")
    print(f"   Session file: {_SESSION_FILE_}")
    print(f"   Environment variable: MONARCH_ENV")
    print(f"   Development TTL: 1 hour (60 minutes)")
    print(f"   Production TTL: 0.25 hours (15 minutes)")


if __name__ == "__main__":
    test_ttl_logic()
