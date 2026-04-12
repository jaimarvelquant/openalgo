"""
Validation test for QA feedback fixes - Story 1.2-2
Tests the field name corrections and ProductType preservation
"""
import json
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_field_names_fix():
    """
    Test that transform_tradebook_data emits correct field names:
    - 'orderid' (not 'order_id')
    - 'timestamp' (not 'trade_date')
    """
    print("\n=== Testing Field Name Fixes (QA Blocker) ===")

    from broker.jainam_prop.mapping.order_data import transform_tradebook_data

    # Mock trade data after mapping
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

    print(f"\nTransformed trade:\n{json.dumps(result[0], indent=2)}")

    # Validate correct field names
    assert 'orderid' in result[0], "Missing 'orderid' field"
    assert 'timestamp' in result[0], "Missing 'timestamp' field"

    # Ensure old incorrect field names are NOT present
    assert 'order_id' not in result[0], "Found deprecated 'order_id' field (should be 'orderid')"
    assert 'trade_date' not in result[0], "Found deprecated 'trade_date' field (should be 'timestamp')"

    # Verify values
    assert result[0]['orderid'] == '123456', "OrderID value mismatch"
    assert result[0]['timestamp'] == '2025-10-07T10:15:30', "Timestamp value mismatch"

    print("\n✓ Field names are correct: 'orderid' and 'timestamp'")
    print("✓ QA Blocker FIXED: Order ID and Fill Time will now render in UI")

def test_transform_trade_book_field_names():
    """
    Test that transform_trade_book emits 'timestamp' (not 'trade_timestamp')
    This validates the QA Concern about consistent field naming at API layer
    """
    print("\n=== Testing transform_trade_book Field Names (QA Concern) ===")

    from broker.jainam_prop.mapping.order_data import transform_trade_book

    mock_jainam_trades = [
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
        }
    ]

    result = transform_trade_book(mock_jainam_trades)
    trade = result['trades'][0]

    print(f"\nAPI-layer transform output:\n{json.dumps(trade, indent=2)}")

    # Validate that transform_trade_book emits 'timestamp' not 'trade_timestamp'
    assert 'timestamp' in trade, "Missing 'timestamp' field in API-layer transform"
    assert 'trade_timestamp' not in trade, "Found deprecated 'trade_timestamp' field (should be 'timestamp')"
    assert trade['timestamp'] == '2025-10-07T10:15:30', "Timestamp value mismatch"

    print("\n✓ transform_trade_book emits 'timestamp' (not 'trade_timestamp')")
    print("✓ QA Concern FIXED: API-layer contract now consistent with other brokers")

def test_product_type_preservation():
    """
    Test that ProductType is preserved through transformation pipeline
    """
    print("\n=== Testing ProductType Preservation (QA Concern) ===")

    from broker.jainam_prop.mapping.order_data import (
        transform_trade_book,
        transform_tradebook_data
    )

    # Test transform_trade_book preserves ProductType
    mock_jainam_trades = [
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
        }
    ]

    # Step 1: transform_trade_book
    step1_result = transform_trade_book(mock_jainam_trades)
    assert 'product' in step1_result['trades'][0], "ProductType not preserved in transform_trade_book"
    assert step1_result['trades'][0]['product'] == 'MIS', "ProductType value lost in transform_trade_book"
    print(f"\n✓ Step 1 (transform_trade_book): ProductType = '{step1_result['trades'][0]['product']}'")

    # Step 2: transform_tradebook_data
    mock_mapped_trades = [
        {
            'TradingSymbol': 'SBIN-EQ',
            'ExchangeSegment': 'NSECM',
            'ProductType': 'NRML',
            'OrderSide': 'SELL',
            'TradedQuantity': 50,
            'TradedPrice': 2450.00,
            'TradeTime': '2025-10-07T11:30:00',
            'AppOrderID': '123457',
            'TradeID': 'T002'
        }
    ]

    step2_result = transform_tradebook_data(mock_mapped_trades)
    assert 'product' in step2_result[0], "ProductType not preserved in transform_tradebook_data"
    assert step2_result[0]['product'] == 'NRML', "ProductType value lost in transform_tradebook_data"
    print(f"✓ Step 2 (transform_tradebook_data): ProductType = '{step2_result[0]['product']}'")

    print("\n✓ QA Concern FIXED: Product column will now populate in trade-book view")

def test_csv_export_compatibility():
    """
    Test that transformed data matches CSV export expectations
    (blueprints/orders.py:95-96)
    """
    print("\n=== Testing CSV Export Compatibility ===")

    from broker.jainam_prop.mapping.order_data import transform_tradebook_data

    mock_trades = [
        {
            'TradingSymbol': 'TCS-EQ',
            'ExchangeSegment': 'NSECM',
            'ProductType': 'CNC',
            'OrderSide': 'BUY',
            'TradedQuantity': 10,
            'TradedPrice': 3500.75,
            'TradeTime': '2025-10-07T14:22:10',
            'AppOrderID': '987654',
            'TradeID': 'T999'
        }
    ]

    result = transform_tradebook_data(mock_trades)
    trade = result[0]

    # CSV export requires these exact field names (from blueprints/orders.py:87-96)
    csv_required_fields = [
        'symbol',      # trade.get('symbol', '')
        'exchange',    # trade.get('exchange', '')
        'product',     # trade.get('product', '')
        'action',      # trade.get('action', '')
        'quantity',    # trade.get('quantity', '')
        'average_price', # trade.get('average_price', '')
        'trade_value', # trade.get('trade_value', '')
        'orderid',     # trade.get('orderid', '')  <-- MUST be 'orderid'
        'timestamp'    # trade.get('timestamp', '') <-- MUST be 'timestamp'
    ]

    print("\nValidating CSV export fields:")
    for field in csv_required_fields:
        assert field in trade, f"Missing required CSV field: {field}"
        print(f"  ✓ {field}: {trade[field]}")

    print("\n✓ All CSV export fields present and correctly named")

def test_orderstatus_service_compatibility():
    """
    Test compatibility with services/orderstatus_service.py:201
    which looks up trades by 'orderid'
    """
    print("\n=== Testing OrderStatus Service Compatibility ===")

    from broker.jainam_prop.mapping.order_data import transform_tradebook_data

    mock_trades = [
        {
            'TradingSymbol': 'INFY-EQ',
            'ExchangeSegment': 'NSECM',
            'ProductType': 'MIS',
            'OrderSide': 'BUY',
            'TradedQuantity': 25,
            'TradedPrice': 1450.00,
            'TradeTime': '2025-10-07T09:45:22',
            'AppOrderID': '555123',
            'TradeID': 'T555'
        }
    ]

    result = transform_tradebook_data(mock_trades)

    # Simulate orderstatus_service.py:201 lookup
    orderid_to_find = '555123'
    matching_trade = None

    for trade in result:
        trade_orderid = str(trade.get('orderid'))
        if trade_orderid == str(orderid_to_find):
            matching_trade = trade
            break

    assert matching_trade is not None, "OrderStatus service would fail to find trade by orderid"
    assert matching_trade['average_price'] == 1450.00, "Average price not accessible"

    print(f"\n✓ OrderStatus service can find trade by orderid: {orderid_to_find}")
    print(f"✓ Average price available: {matching_trade['average_price']}")
    print("✓ QA Blocker FIXED: Order status lookups will now work correctly")

def main():
    """Run QA validation tests"""
    print("=" * 70)
    print("QA Feedback Validation Tests - Story 1.2-2 Trade-Book")
    print("=" * 70)

    try:
        test_field_names_fix()
        test_transform_trade_book_field_names()
        test_product_type_preservation()
        test_csv_export_compatibility()
        test_orderstatus_service_compatibility()

        print("\n" + "=" * 70)
        print("✅ ALL QA FIXES VALIDATED!")
        print("=" * 70)
        print("\nFixed Issues:")
        print("  ✅ BLOCKER: Field naming (orderid/timestamp)")
        print("  ✅ CONCERN: ProductType preservation")
        print("  ✅ CSV Export compatibility")
        print("  ✅ OrderStatus service compatibility")
        print("\nNote: IV3 (performance test) requires running test_trade_book.py")
        return 0

    except AssertionError as e:
        print(f"\n❌ VALIDATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
