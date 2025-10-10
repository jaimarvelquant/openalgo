#!/usr/bin/env python3
"""
Test script to verify Jainam Prop login flow.

This script will:
1. Test authenticate_broker() function
2. Verify it returns 5 values correctly
3. Check the auth token structure
4. Report any issues
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from broker.jainam_prop.api.auth_api import authenticate_broker
from utils.logging import get_logger

logger = get_logger(__name__)

def test_jainam_login():
    """Test Jainam Prop login flow."""
    
    print("=" * 80)
    print("JAINAM PROP LOGIN FLOW TEST")
    print("=" * 80)
    
    # Step 1: Call authenticate_broker()
    print("\n[1] Calling authenticate_broker()...")
    try:
        result = authenticate_broker()
        print(f"✅ Function returned successfully")
        print(f"   Return type: {type(result)}")
        print(f"   Return length: {len(result) if isinstance(result, tuple) else 'N/A'}")
    except Exception as e:
        print(f"❌ Function call failed: {type(e).__name__}: {e}")
        return False
    
    # Step 2: Verify return values
    print("\n[2] Verifying return values...")
    if not isinstance(result, tuple):
        print(f"❌ Expected tuple, got {type(result)}")
        return False
    
    if len(result) != 5:
        print(f"❌ Expected 5 values, got {len(result)}")
        print(f"   Values: {result}")
        return False
    
    print(f"✅ Correct number of return values (5)")
    
    # Step 3: Unpack values
    print("\n[3] Unpacking values...")
    try:
        auth_token, feed_token, user_id, is_investor_client, error_message = result
        print(f"✅ Successfully unpacked 5 values")
        print(f"   auth_token: {auth_token[:20] if auth_token else None}...")
        print(f"   feed_token: {feed_token[:20] if feed_token else None}...")
        print(f"   user_id: {user_id}")
        print(f"   is_investor_client: {is_investor_client}")
        print(f"   error_message: {error_message}")
    except Exception as e:
        print(f"❌ Failed to unpack: {type(e).__name__}: {e}")
        return False
    
    # Step 4: Check for errors
    print("\n[4] Checking for errors...")
    if error_message:
        print(f"❌ Authentication failed: {error_message}")
        return False
    
    if not auth_token:
        print(f"❌ No auth token returned")
        return False
    
    print(f"✅ Authentication successful")
    
    # Step 5: Test auth token JSON structure (as used in brlogin.py)
    print("\n[5] Testing auth token JSON structure...")
    try:
        auth_token_json = json.dumps({
            'token': auth_token,
            'user_id': user_id,
            'clientID': user_id,
            'isInvestorClient': is_investor_client
        })
        print(f"✅ Auth token JSON created successfully")
        print(f"   JSON length: {len(auth_token_json)} chars")
        
        # Parse it back
        parsed = json.loads(auth_token_json)
        print(f"✅ Auth token JSON parsed successfully")
        print(f"   Keys: {list(parsed.keys())}")
        print(f"   user_id: {parsed.get('user_id')}")
        print(f"   isInvestorClient: {parsed.get('isInvestorClient')}")
    except Exception as e:
        print(f"❌ Failed to create/parse auth token JSON: {type(e).__name__}: {e}")
        return False
    
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Login flow is working correctly")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        success = test_jainam_login()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        print(f"\n❌ Test failed with exception: {e}")
        sys.exit(1)

