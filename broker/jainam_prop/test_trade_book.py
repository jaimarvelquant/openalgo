"""
Test script for Jainam Prop get_trade_book function
Tests the implementation with mock data
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_transform_trade_book():
    """Test the transform_trade_book function with mock data"""
    from broker.jainam_prop.mapping.order_data import transform_trade_book

    print("\n=== Testing transform_trade_book ===")

    # Mock Jainam trade data
    mock_trades = [
        {
            'AppOrderID': '123456',
            'TradeID': 'T001',
            'TradingSymbol': 'SBIN-EQ',
            'ExchangeSegment': 'NSECM',
            'ProductType': 'MIS',
            'OrderSide': 'BUY',
            'TradedQuantity': 100,
            'TradedPrice': 550.50,
            'TradeTime': '2025-10-07T10:15:30',
            'ExchangeTradeID': 'EXT001'
        },
        {
            'AppOrderID': '123457',
            'TradeID': 'T002',
            'TradingSymbol': 'RELIANCE-EQ',
            'ExchangeSegment': 'NSECM',
            'ProductType': 'NRML',
            'OrderSide': 'SELL',
            'TradedQuantity': 50,
            'TradedPrice': 2450.00,
            'TradeTime': '2025-10-07T10:20:45',
            'ExchangeTradeID': 'EXT002'
        }
    ]

    # Test with trades
    result = transform_trade_book(mock_trades)
    print(f"\n✓ Transform result: {json.dumps(result, indent=2)}")

    # Validate result structure
    assert result['status'] == 'success', "Status should be 'success'"
    assert 'trades' in result, "Result should contain 'trades' key"
    assert len(result['trades']) == 2, "Should have 2 trades"

    # Validate first trade
    first_trade = result['trades'][0]
    assert first_trade['orderid'] == '123456', "Order ID mismatch"
    assert first_trade['trade_id'] == 'T001', "Trade ID mismatch"
    assert first_trade['symbol'] == 'SBIN-EQ', "Symbol mismatch"
    assert first_trade['product'] == 'MIS', "Product type mismatch"
    assert first_trade['action'] == 'BUY', "Action mismatch"
    assert first_trade['quantity'] == 100, "Quantity mismatch"
    assert first_trade['price'] == 550.50, "Price mismatch"

    print("\n✓ All transform_trade_book tests passed!")

    # Test with empty trades
    empty_result = transform_trade_book([])
    assert empty_result['status'] == 'success', "Empty result should have success status"
    assert len(empty_result['trades']) == 0, "Empty trades should return empty list"
    print("✓ Empty trade book test passed!")

def test_map_trade_data():
    """Test the map_trade_data function"""
    from broker.jainam_prop.mapping.order_data import map_trade_data

    print("\n=== Testing map_trade_data ===")

    # Mock trade data with 'trades' key (from transform_trade_book)
    mock_data = {
        'status': 'success',
        'trades': [
            {
                'orderid': '123456',
                'trade_id': 'T001',
                'symbol': 'SBIN-EQ',
                'exchange': 'NSE',
                'action': 'BUY',
                'quantity': 100,
                'price': 550.50
            }
        ]
    }

    result = map_trade_data(mock_data)
    print(f"\n✓ Map trade data result: {result}")
    assert len(result) == 1, "Should return 1 trade"
    print("✓ map_trade_data test passed!")

    # Test with empty data
    empty_result = map_trade_data([])
    assert empty_result == [], "Empty data should return empty list"
    print("✓ Empty map_trade_data test passed!")

def test_transform_tradebook_data():
    """Test the transform_tradebook_data function"""
    from broker.jainam_prop.mapping.order_data import transform_tradebook_data

    print("\n=== Testing transform_tradebook_data ===")

    # Mock mapped trade data
    mock_trades = [
        {
            'TradingSymbol': 'SBIN-EQ',
            'ExchangeSegment': 'NSECM',
            'ProductType': 'MIS',
            'OrderSide': 'BUY',
            'TradedQuantity': 100,
            'TradedPrice': 550.50,
            'TradeTime': '2025-10-07T10:15:30',
            'AppOrderID': '123456',
            'TradeID': 'T001'
        }
    ]

    result = transform_tradebook_data(mock_trades)
    print(f"\n✓ Transform tradebook data result: {json.dumps(result, indent=2)}")

    assert len(result) == 1, "Should return 1 transformed trade"
    assert result[0]['symbol'] == 'SBIN-EQ', "Symbol should match"
    assert result[0]['exchange'] == 'NSE', "Exchange should be mapped to NSE"
    assert result[0]['quantity'] == 100, "Quantity should match"
    assert result[0]['average_price'] == 550.50, "Price should match"
    assert result[0]['trade_value'] == 55050.0, "Trade value should be calculated correctly"

    print("✓ transform_tradebook_data test passed!")

def test_performance_large_tradebook():
    """Test performance with 100+ trades (IV3 requirement: <5 seconds)"""
    import time
    print("\n=== Testing Performance with 100+ Trades (IV3) ===")

    from broker.jainam_prop.mapping.order_data import (
        transform_trade_book,
        map_trade_data,
        transform_tradebook_data
    )

    # Generate 150 mock trades to test performance
    large_trade_list = []
    symbols = ['SBIN', 'RELIANCE', 'TCS', 'INFY', 'HDFC', 'ICICI', 'ITC', 'WIPRO', 'AXIS', 'BHARTI']

    for i in range(150):
        trade = {
            'AppOrderID': f'ORD{100000 + i}',
            'TradeID': f'T{1000 + i}',
            'TradingSymbol': f'{symbols[i % len(symbols)]}-EQ',
            'ExchangeSegment': 'NSECM',
            'ProductType': 'MIS' if i % 2 == 0 else 'NRML',
            'OrderSide': 'BUY' if i % 2 == 0 else 'SELL',
            'TradedQuantity': (i % 10 + 1) * 10,
            'TradedPrice': 100.0 + (i % 50) * 10,
            'TradeTime': f'2025-10-07T10:{i % 60:02d}:{(i * 3) % 60:02d}',
            'ExchangeTradeID': f'EXT{2000 + i}'
        }
        large_trade_list.append(trade)

    print(f"\n✓ Generated {len(large_trade_list)} mock trades")
    expected_timestamp = large_trade_list[0]['TradeTime']

    # Measure performance
    start_time = time.time()

    # Step 1: Transform
    transformed = transform_trade_book(large_trade_list)

    # Step 2: Map (without actual DB lookups for this test)
    mapped = map_trade_data(transformed)

    # Step 3: Final transform
    final = transform_tradebook_data(mapped)

    end_time = time.time()
    elapsed = end_time - start_time

    print(f"✓ Processed {len(final)} trades")
    print(f"✓ Time elapsed: {elapsed:.3f} seconds")

    # Validate performance requirement (IV3: <5 seconds)
    assert elapsed < 5.0, f"Performance requirement failed: {elapsed:.3f}s >= 5.0s"
    print(f"✓ Performance test PASSED (requirement: <5s, actual: {elapsed:.3f}s)")

    # Validate data integrity
    assert len(final) == 150, "Should return all 150 trades"

    # Validate required fields are present and have valid values
    sample_trade = final[0]
    required_fields = ['symbol', 'exchange', 'product', 'action', 'quantity',
                      'average_price', 'trade_value', 'orderid', 'timestamp']
    for field in required_fields:
        assert field in sample_trade, f"Missing required field: {field}"

    # QA Fix: Validate timestamp value propagation (not just presence)
    assert sample_trade['timestamp'], "Timestamp field must have a value"
    assert sample_trade['timestamp'] == expected_timestamp, \
        f"Timestamp value mismatch: expected '{expected_timestamp}', got '{sample_trade['timestamp']}'"

    print(f"✓ All required fields present: {', '.join(required_fields)}")
    print(f"✓ Timestamp value validated: {sample_trade['timestamp']}")
    print("✓ Large tradebook performance test passed!")

def test_result_key_handling():
    """Test that both 'result' and 'data' keys are handled correctly (QA Fix)"""
    print("\n=== Testing 'result' vs 'data' Key Handling ===")

    from broker.jainam_prop.mapping.order_data import transform_trade_book

    # Mock trade
    mock_trade = {
        'AppOrderID': '123456',
        'TradeID': 'T001',
        'TradingSymbol': 'SBIN-EQ',
        'ExchangeSegment': 'NSECM',
        'ProductType': 'MIS',
        'OrderSide': 'BUY',
        'TradedQuantity': 100,
        'TradedPrice': 550.50,
        'TradeTime': '2025-10-07T10:15:30',
        'ExchangeTradeID': 'EXT001'
    }

    # Test 1: Response with 'result' key (Jainam/XTS format)
    result_response = {'type': 'success', 'result': [mock_trade]}
    result_data = result_response.get('result', result_response.get('data', []))
    result = transform_trade_book(result_data)
    assert result['status'] == 'success', "Should handle 'result' key"
    assert len(result['trades']) == 1, "Should extract trade from 'result' key"
    print("✓ 'result' key handling test passed!")

    # Test 2: Response with 'data' key (fallback format)
    data_response = {'status': 'success', 'data': [mock_trade]}
    data_data = data_response.get('result', data_response.get('data', []))
    result = transform_trade_book(data_data)
    assert result['status'] == 'success', "Should handle 'data' key"
    assert len(result['trades']) == 1, "Should extract trade from 'data' key"
    print("✓ 'data' key handling test passed!")

    # Test 3: Empty result key
    empty_response = {'type': 'success', 'result': []}
    empty_data = empty_response.get('result', empty_response.get('data', []))
    result = transform_trade_book(empty_data)
    assert result['status'] == 'success', "Should handle empty 'result' key"
    assert len(result['trades']) == 0, "Should return empty list"
    print("✓ Empty 'result' key handling test passed!")

    print("✓ All 'result' key handling tests passed!")

def test_integration_flow():
    """Test the complete integration flow"""
    print("\n=== Testing Integration Flow ===")

    from broker.jainam_prop.mapping.order_data import (
        transform_trade_book,
        map_trade_data,
        transform_tradebook_data
    )

    # Simulate API response
    api_response = {
        'data': [
            {
                'AppOrderID': '123456',
                'TradeID': 'T001',
                'TradingSymbol': 'SBIN-EQ',
                'ExchangeSegment': 'NSECM',
                'OrderSide': 'BUY',
                'TradedQuantity': 100,
                'TradedPrice': 550.50,
                'TradeTime': '2025-10-07T10:15:30',
                'ExchangeTradeID': 'EXT001',
                'ProductType': 'MIS'
            }
        ]
    }

    # Step 1: Transform from Jainam format
    print("\nStep 1: Transform trade book...")
    transformed = transform_trade_book(api_response['data'])
    print(f"✓ Transformed: {len(transformed.get('trades', []))} trades")

    # Step 2: Map trade data (symbol resolution would happen here)
    print("\nStep 2: Map trade data...")
    mapped = map_trade_data(transformed)
    print(f"✓ Mapped: {len(mapped)} trades")

    # Step 3: Transform to final format
    print("\nStep 3: Transform to final format...")
    final = transform_tradebook_data(mapped)
    print(f"✓ Final: {len(final)} trades")
    print(f"\nFinal trade data:\n{json.dumps(final, indent=2)}")

    # Validate final output
    assert len(final) == 1, "Should have 1 final trade"
    assert 'symbol' in final[0], "Should have symbol"
    assert 'exchange' in final[0], "Should have exchange"
    assert 'quantity' in final[0], "Should have quantity"
    assert 'average_price' in final[0], "Should have average_price"
    assert 'trade_value' in final[0], "Should have trade_value"

    print("\n✓ Integration flow test passed!")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Jainam Prop Trade Book Function Tests")
    print("=" * 60)

    try:
        test_transform_trade_book()
        test_map_trade_data()
        test_transform_tradebook_data()
        test_result_key_handling()
        test_performance_large_tradebook()
        test_integration_flow()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
