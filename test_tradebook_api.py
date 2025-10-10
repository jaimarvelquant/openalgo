#!/usr/bin/env python3
"""
Test script to debug Jainam tradebook API issue.

This script will:
1. Load credentials from keyring
2. Authenticate with Jainam API
3. Test tradebook retrieval with different parameter combinations
4. Report results
"""

import sys
import os
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from broker.jainam_prop.api.auth_api import authenticate_direct
from broker.jainam_prop.api.order_api import OrderAPIClient
from broker.jainam_prop.api.routes import get_route
from utils.logging import get_logger

logger = get_logger(__name__)

def test_tradebook_api():
    """Test tradebook API with different parameter combinations."""
    
    print("=" * 80)
    print("JAINAM TRADEBOOK API DEBUG TEST")
    print("=" * 80)
    
    # Step 1: Authenticate
    print("\n[1] Authenticating with Jainam...")
    interactive_token, market_token, user_id, is_investor, error = authenticate_direct()
    
    if error:
        print(f"❌ Authentication failed: {error}")
        return False
    
    print(f"✅ Authentication successful")
    print(f"   User ID: {user_id}")
    print(f"   Is Investor Client: {is_investor}")
    print(f"   Interactive Token: {interactive_token[:20]}...")
    
    # Step 2: Create API client
    print("\n[2] Creating OrderAPIClient...")
    client = OrderAPIClient(auth_token=interactive_token)
    print(f"✅ Client created")
    
    # Step 3: Test tradebook WITHOUT clientID parameter
    print("\n[3] Testing tradebook API WITHOUT clientID parameter...")
    print(f"   Route: 'trades' -> {get_route('trades')}")
    try:
        response = client.get_tradebook(client_id=None)
        print(f"✅ SUCCESS - Response type: {response.get('type')}")
        print(f"   Response keys: {list(response.keys())}")
        if response.get('type') == 'success':
            result = response.get('result', [])
            print(f"   Trade count: {len(result) if isinstance(result, list) else 'N/A'}")
            if result and isinstance(result, list):
                print(f"   First trade: {result[0]}")
        else:
            print(f"   Error: {response.get('description')}")
            print(f"   Code: {response.get('code')}")
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {str(e)}")
        # Try to get the response body
        if hasattr(e, 'response'):
            try:
                error_data = e.response.json()
                print(f"   Error details: {error_data}")
            except:
                print(f"   Error response: {e.response.text}")
    
    # Step 4: Test tradebook WITH clientID parameter
    print(f"\n[4] Testing tradebook API WITH clientID parameter (clientID={user_id})...")
    print(f"   Route: 'trades' -> {get_route('trades')}")
    try:
        response = client.get_tradebook(client_id=user_id)
        print(f"✅ SUCCESS - Response type: {response.get('type')}")
        print(f"   Response keys: {list(response.keys())}")
        if response.get('type') == 'success':
            result = response.get('result', [])
            print(f"   Trade count: {len(result) if isinstance(result, list) else 'N/A'}")
            if result and isinstance(result, list):
                print(f"   First trade: {result[0]}")
        else:
            print(f"   Error: {response.get('description')}")
            print(f"   Code: {response.get('code')}")
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {str(e)}")
    
    # Step 5: Test dealer tradebook endpoint (for comparison)
    print(f"\n[5] Testing DEALER tradebook API WITH clientID parameter (clientID={user_id})...")
    print(f"   Route: 'dealer.trades' -> {get_route('dealer.trades')}")
    try:
        response = client.get_dealer_tradebook(client_id=user_id)
        print(f"✅ SUCCESS - Response type: {response.get('type')}")
        print(f"   Response keys: {list(response.keys())}")
        if response.get('type') == 'success':
            result = response.get('result', [])
            print(f"   Trade count: {len(result) if isinstance(result, list) else 'N/A'}")
        else:
            print(f"   Error: {response.get('description')}")
            print(f"   Code: {response.get('code')}")
    except Exception as e:
        print(f"❌ FAILED - {type(e).__name__}: {str(e)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    return True

if __name__ == "__main__":
    try:
        test_tradebook_api()
    except Exception as e:
        logger.error(f"Test failed with exception: {e}", exc_info=True)
        print(f"\n❌ Test failed with exception: {e}")
        sys.exit(1)

