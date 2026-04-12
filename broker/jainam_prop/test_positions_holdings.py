"""
Test script for get_positions and get_holdings functions
"""
import json
from broker.jainam_prop.api.order_api import get_positions, get_holdings

def test_positions():
    """Test get_positions function"""
    print("Testing get_positions()...")

    # Test with mock auth token
    mock_auth = {
        'token': 'test_token_12345',
        'client_id': 'TEST_USER'
    }

    # This will fail without real credentials, but tests the function structure
    result = get_positions(json.dumps(mock_auth))
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")

    # Verify error handling works
    assert isinstance(result, dict), "Result should be a dictionary"
    assert 'status' in result or 'data' in result, "Result should have status or data key"
    print("✓ get_positions structure test passed")

def test_holdings():
    """Test get_holdings function"""
    print("\nTesting get_holdings()...")

    # Test with mock auth token
    mock_auth = {
        'token': 'test_token_12345',
        'client_id': 'TEST_USER'
    }

    # This will fail without real credentials, but tests the function structure
    result = get_holdings(json.dumps(mock_auth))
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")

    # Verify error handling works
    assert isinstance(result, dict), "Result should be a dictionary"
    assert 'status' in result or 'data' in result, "Result should have status or data key"
    print("✓ get_holdings structure test passed")

def test_auth_token_parsing():
    """Test authentication token parsing"""
    print("\nTesting auth token parsing...")

    # Test with string token
    result1 = get_positions("simple_string_token")
    assert isinstance(result1, dict), "Should handle string token"

    # Test with JSON string
    json_token = json.dumps({'token': 'test_token'})
    result2 = get_positions(json_token)
    assert isinstance(result2, dict), "Should handle JSON string token"

    # Test with dict
    dict_token = {'token': 'test_token'}
    result3 = get_positions(dict_token)
    assert isinstance(result3, dict), "Should handle dict token"

    print("✓ Auth token parsing test passed")

if __name__ == "__main__":
    print("=" * 60)
    print("Jainam Prop - Positions and Holdings Function Tests")
    print("=" * 60)

    try:
        test_positions()
        test_holdings()
        test_auth_token_parsing()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        print("\nNote: These are structure tests. Full integration testing")
        print("requires valid Jainam API credentials.")

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
