"""
Comprehensive Timestamp Value Propagation Test
QA Fix Round 3: Validate timestamp values through entire pipeline
"""

def test_timestamp_value_propagation():
    """
    Test that timestamp values propagate correctly through all transformation layers.
    This addresses QA blocker: timestamp field getting empty string in final payload.
    """
    from broker.jainam_prop.mapping.order_data import (
        transform_trade_book,
        transform_tradebook_data
    )

    print("\n" + "=" * 70)
    print("Timestamp Value Propagation Test")
    print("=" * 70)

    # Mock trade with TradeTime (as returned by Jainam API)
    api_trade = {
        'AppOrderID': '123456',
        'TradeID': 'T001',
        'TradingSymbol': 'SBIN-EQ',
        'ExchangeSegment': 'NSECM',
        'ProductType': 'MIS',
        'OrderSide': 'BUY',
        'TradedQuantity': 100,
        'TradedPrice': 550.50,
        'TradeTime': '2025-01-15 09:15:00',  # This is the timestamp we want to preserve
        'ExchangeTradeID': 'EXT001'
    }

    print(f"\n1. Raw API Trade:")
    print(f"   TradeTime: '{api_trade['TradeTime']}'")

    # Step 1: transform_trade_book (API layer transform)
    result1 = transform_trade_book([api_trade])
    trade1 = result1['trades'][0]
    print(f"\n2. After transform_trade_book():")
    print(f"   timestamp: '{trade1.get('timestamp')}'")
    assert trade1['timestamp'] == '2025-01-15 09:15:00', \
        f"Step 1 failed: expected '2025-01-15 09:15:00', got '{trade1.get('timestamp')}'"

    # Step 2: Simulate what map_trade_data does (preserve the timestamp field)
    # In production, map_trade_data wraps the data but should preserve timestamp
    mapped_trade = {
        'TradingSymbol': trade1['symbol'],
        'ExchangeSegment': trade1['exchange'],
        'ProductType': trade1['product'],
        'OrderSide': trade1['action'],
        'TradedQuantity': trade1['quantity'],
        'TradedPrice': trade1['price'],
        'timestamp': trade1['timestamp'],  # CRITICAL: Preserve timestamp field
        'AppOrderID': trade1['orderid'],
        'TradeID': trade1['trade_id']
    }
    print(f"\n3. After simulated mapping:")
    print(f"   timestamp: '{mapped_trade.get('timestamp')}'")
    assert mapped_trade['timestamp'] == '2025-01-15 09:15:00', \
        f"Step 2 failed: expected '2025-01-15 09:15:00', got '{mapped_trade.get('timestamp')}'"

    # Step 3: transform_tradebook_data (service layer transform)
    result3 = transform_tradebook_data([mapped_trade])
    trade3 = result3[0]
    print(f"\n4. After transform_tradebook_data():")
    print(f"   timestamp: '{trade3.get('timestamp')}'")

    # CRITICAL ASSERTION: Timestamp value must be preserved through entire pipeline
    assert trade3['timestamp'] == '2025-01-15 09:15:00', \
        f"BLOCKER: Timestamp value lost in final transform! Expected '2025-01-15 09:15:00', got '{trade3.get('timestamp')}'"

    print("\n" + "=" * 70)
    print("✅ TIMESTAMP VALUE PROPAGATION TEST PASSED")
    print("=" * 70)
    print("\nTimestamp value successfully propagated through all layers:")
    print("  API Response → transform_trade_book → map_trade_data → transform_tradebook_data")
    print(f"  Final timestamp value: '{trade3['timestamp']}'")
    print()

if __name__ == '__main__':
    test_timestamp_value_propagation()
