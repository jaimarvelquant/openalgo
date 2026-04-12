"""
Standalone unit tests for get_open_position function (no external dependencies)

Tests core logic without requiring httpx or other dependencies
"""


def simulate_get_open_position(tradingsymbol, exchange, producttype, positions_data):
    """
    Simulated version of get_open_position for testing logic
    """
    try:
        # Handle get_positions() failure (returns error dict)
        if not positions_data:
            return '0'

        if isinstance(positions_data, dict) and positions_data.get('status') == 'error':
            return '0'

        # Extract position list from response
        position_list = []
        if isinstance(positions_data, dict):
            if 'result' in positions_data:
                result = positions_data['result']
                if isinstance(result, list):
                    position_list = result
                elif isinstance(result, dict) and 'positions' in result:
                    position_list = result['positions']
            elif 'data' in positions_data:
                data = positions_data['data']
                if isinstance(data, list):
                    position_list = data
                elif isinstance(data, dict) and 'positions' in data:
                    position_list = data['positions']
        elif isinstance(positions_data, list):
            position_list = positions_data

        if not position_list:
            return '0'

        # Search for matching position
        for position in position_list:
            pos_symbol = position.get('TradingSymbol') or position.get('tradingsymbol') or position.get('symbol', '')
            pos_exchange = position.get('ExchangeSegment') or position.get('exchange') or position.get('exch', '')
            pos_product = position.get('ProductType') or position.get('producttype') or position.get('product', '')

            # Normalize exchange
            exchange_normalized = exchange
            if exchange == 'NSE':
                exchange_normalized = 'NSECM'
            elif exchange == 'BSE':
                exchange_normalized = 'BSECM'
            elif exchange == 'NFO':
                exchange_normalized = 'NSEFO'
            elif exchange == 'MCX':
                exchange_normalized = 'MCXFO'

            # Check for exact match
            if (pos_symbol == tradingsymbol and
                (pos_exchange == exchange or pos_exchange == exchange_normalized) and
                pos_product == producttype):

                # Extract net quantity
                net_qty = (position.get('NetQty') or
                          position.get('netQty') or
                          position.get('netqty') or
                          position.get('Quantity') or
                          position.get('quantity') or
                          '0')

                return str(net_qty)

        return '0'

    except Exception as e:
        return '0'


def run_tests():
    """Run all test cases"""
    print("=" * 70)
    print("GET_OPEN_POSITION STANDALONE TESTS")
    print("=" * 70)

    passed = 0
    failed = 0

    # Test 1: Long position found
    print("\n[Test 1] Long position found")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '100'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '100':
        print("✓ PASSED")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '100', got '{result}'")
        failed += 1

    # Test 2: Short position found
    print("\n[Test 2] Short position found")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'RELIANCE-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '-50'}
        ]
    }
    result = simulate_get_open_position('RELIANCE-EQ', 'NSE', 'MIS', positions)
    if result == '-50':
        print("✓ PASSED")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '-50', got '{result}'")
        failed += 1

    # Test 3: Position not found
    print("\n[Test 3] Position not found")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '100'}
        ]
    }
    result = simulate_get_open_position('INFY-EQ', 'NSE', 'MIS', positions)
    if result == '0':
        print("✓ PASSED")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '0', got '{result}'")
        failed += 1

    # Test 4: Empty positions
    print("\n[Test 4] Empty positions")
    positions = {'type': 'success', 'result': []}
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '0':
        print("✓ PASSED")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '0', got '{result}'")
        failed += 1

    # Test 5: get_positions failure
    print("\n[Test 5] get_positions failure")
    positions = {'status': 'error', 'message': 'Auth failed'}
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '0':
        print("✓ PASSED")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '0', got '{result}'")
        failed += 1

    # Test 6: Exchange normalization (NSE -> NSECM)
    print("\n[Test 6] Exchange normalization (NSE -> NSECM)")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '100'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '100':
        print("✓ PASSED - NSE correctly matched NSECM")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '100', got '{result}'")
        failed += 1

    # Test 7: BSE exchange normalization
    print("\n[Test 7] Exchange normalization (BSE -> BSECM)")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'BSECM', 'ProductType': 'CNC', 'NetQty': '50'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'BSE', 'CNC', positions)
    if result == '50':
        print("✓ PASSED - BSE correctly matched BSECM")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '50', got '{result}'")
        failed += 1

    # Test 8: Product type exact match
    print("\n[Test 8] Product type must match exactly")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'CNC', 'NetQty': '100'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '0':
        print("✓ PASSED - MIS did not match CNC")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '0' (no match), got '{result}'")
        failed += 1

    # Test 9: Multiple positions filtering
    print("\n[Test 9] Multiple positions filtering")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '100'},
            {'TradingSymbol': 'RELIANCE-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '200'},
            {'TradingSymbol': 'INFY-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'CNC', 'NetQty': '50'}
        ]
    }
    result = simulate_get_open_position('RELIANCE-EQ', 'NSE', 'MIS', positions)
    if result == '200':
        print("✓ PASSED - Found correct position among multiple")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '200', got '{result}'")
        failed += 1

    # Test 10: Lowercase field names
    print("\n[Test 10] Lowercase field names")
    positions = {
        'type': 'success',
        'result': [
            {'tradingsymbol': 'SBIN-EQ', 'exchange': 'NSE', 'producttype': 'MIS', 'netqty': '100'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '100':
        print("✓ PASSED - Lowercase fields handled")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '100', got '{result}'")
        failed += 1

    # Test 11: Alternative field names
    print("\n[Test 11] Alternative field names (symbol/exch/product/quantity)")
    positions = {
        'type': 'success',
        'result': [
            {'symbol': 'SBIN-EQ', 'exch': 'NSE', 'product': 'MIS', 'quantity': '100'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '100':
        print("✓ PASSED - Alternative field names handled")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '100', got '{result}'")
        failed += 1

    # Test 12: Direct list response
    print("\n[Test 12] Direct list response (not wrapped in dict)")
    positions = [
        {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSE', 'ProductType': 'MIS', 'NetQty': '100'}
    ]
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '100':
        print("✓ PASSED - Direct list handled")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '100', got '{result}'")
        failed += 1

    # Test 13: Alternative 'data' key
    print("\n[Test 13] Alternative 'data' key response")
    positions = {
        'status': 'success',
        'data': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '100'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '100':
        print("✓ PASSED - 'data' key handled")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '100', got '{result}'")
        failed += 1

    # Test 14: Zero quantity position
    print("\n[Test 14] Zero quantity position")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': '0'}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '0':
        print("✓ PASSED - Zero quantity returned")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '0', got '{result}'")
        failed += 1

    # Test 15: Numeric quantity conversion
    print("\n[Test 15] Numeric quantity conversion to string")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'SBIN-EQ', 'ExchangeSegment': 'NSECM', 'ProductType': 'MIS', 'NetQty': 100}
        ]
    }
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '100' and isinstance(result, str):
        print("✓ PASSED - Integer converted to string")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '100' (string), got '{result}' (type={type(result)})")
        failed += 1

    # Test 16: NFO exchange normalization
    print("\n[Test 16] NFO exchange normalization (NFO -> NSEFO)")
    positions = {
        'type': 'success',
        'result': [
            {'TradingSymbol': 'NIFTY24DECFUT', 'ExchangeSegment': 'NSEFO', 'ProductType': 'NRML', 'NetQty': '50'}
        ]
    }
    result = simulate_get_open_position('NIFTY24DECFUT', 'NFO', 'NRML', positions)
    if result == '50':
        print("✓ PASSED - NFO correctly matched NSEFO")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '50', got '{result}'")
        failed += 1

    # Test 17: None positions
    print("\n[Test 17] None positions (no data)")
    positions = None
    result = simulate_get_open_position('SBIN-EQ', 'NSE', 'MIS', positions)
    if result == '0':
        print("✓ PASSED - None handled gracefully")
        passed += 1
    else:
        print(f"✗ FAILED: Expected '0', got '{result}'")
        failed += 1

    # Summary
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed out of {passed + failed} tests")
    print("=" * 70)

    if failed == 0:
        print("✓ ALL TESTS PASSED!")
        return 0
    else:
        print(f"✗ {failed} TEST(S) FAILED")
        return 1


if __name__ == '__main__':
    exit(run_tests())
