#!/usr/bin/env python3
"""
QA Fix Validation Test for Story 1.2-1
Tests the critical fix for map_position_data handling {'result': {'positionList': [...]}} payload
"""

import sys
import os
from types import ModuleType
from unittest.mock import patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Provide a lightweight stub for database.token_db so imports succeed
database_module = ModuleType('database')
token_db_module = ModuleType('database.token_db')
symbol_module = ModuleType('database.symbol')

def _default_get_symbol(*args, **kwargs):
    return None

token_db_module.get_symbol = _default_get_symbol
database_module.token_db = token_db_module
symbol_module.engine = None  # Minimal stub to satisfy transform_data imports
database_module.symbol = symbol_module

sys.modules.setdefault('database', database_module)
sys.modules.setdefault('database.token_db', token_db_module)
sys.modules.setdefault('database.symbol', symbol_module)


def test_map_position_data_with_correct_payload():
    """Test that map_position_data correctly handles XTS API payload structure"""

    # Import the function
    from broker.jainam_prop.mapping.order_data import map_position_data

    # Actual Jainam XTS API response structure (as documented by QA)
    api_response = {
        'result': {
            'positionList': [
                {
                    'ExchangeInstrumentId': 11536,
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'Quantity': 100,
                    'BuyAveragePrice': 550.50,
                    'SellAveragePrice': 0,
                    'LastTradedPrice': 552.00,
                    'RealizedProfitLoss': 150.00
                }
            ]
        }
    }

    # Mock the database.token_db.get_symbol function
    with patch('database.token_db.get_symbol') as mock_get_symbol:
        mock_get_symbol.return_value = 'SBIN-EQ'

        # Execute - this should NOT crash
        result = map_position_data(api_response)

    # Validate result structure
    assert isinstance(result, dict), f"Expected dict, got {type(result)}"
    assert 'positionList' in result, f"Expected 'positionList' key in result, got keys: {result.keys()}"
    assert isinstance(result['positionList'], list), f"Expected list, got {type(result['positionList'])}"
    assert len(result['positionList']) == 1, f"Expected 1 position, got {len(result['positionList'])}"

    # Validate TradingSymbol was enriched
    assert result['positionList'][0]['TradingSymbol'] == 'SBIN-EQ', "Symbol enrichment failed"

    print("✅ PASS: map_position_data correctly handles {'result': {'positionList': [...]}} payload")
    return True


def test_transform_positions_data_accepts_result_dict():
    """Test that transform_positions_data correctly extracts positionList from result dict"""

    from broker.jainam_prop.mapping.order_data import transform_positions_data

    # Result dict from map_position_data (containing positionList)
    mapped_data = {
        'positionList': [
            {
                'TradingSymbol': 'SBIN-EQ',
                'ExchangeSegment': 'NSECM',
                'ProductType': 'MIS',
                'Quantity': 100,
                'BuyAveragePrice': 550.50,
                'SellAveragePrice': 0,
                'LastTradedPrice': 552.00,
                'RealizedProfitLoss': 150.00
            }
        ]
    }

    # Execute - this should NOT crash with AttributeError
    result = transform_positions_data(mapped_data)

    # Validate result
    assert isinstance(result, list), f"Expected list, got {type(result)}"
    assert len(result) == 1, f"Expected 1 position, got {len(result)}"

    # Validate AC6 required fields
    position = result[0]
    required_fields = ['symbol', 'exchange', 'product', 'quantity', 'average_price', 'ltp', 'pnl']
    for field in required_fields:
        assert field in position, f"AC6 required field '{field}' missing from output"

    print("✅ PASS: transform_positions_data correctly processes result dict with positionList")
    print("✅ PASS: All AC6 required fields present in output")
    return True


def test_full_pipeline_integration():
    """Test the complete pipeline: API response → map → transform"""

    from broker.jainam_prop.mapping.order_data import map_position_data, transform_positions_data

    # Actual Jainam XTS API response
    api_response = {
        'result': {
            'positionList': [
                {
                    'ExchangeInstrumentId': 11536,
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'Quantity': 100,
                    'BuyAveragePrice': 550.50,
                    'SellAveragePrice': 0,
                    'LastTradedPrice': 552.00,
                    'RealizedProfitLoss': 150.00
                }
            ]
        }
    }

    with patch('database.token_db.get_symbol') as mock_get_symbol:
        mock_get_symbol.return_value = 'SBIN-EQ'

        # Execute full pipeline
        mapped = map_position_data(api_response)
        transformed = transform_positions_data(mapped)

    # Validate final output
    assert isinstance(transformed, list), "Final output should be a list"
    assert len(transformed) == 1, "Should have 1 transformed position"
    assert transformed[0]['symbol'] == 'SBIN-EQ', "Symbol should be enriched"

    print("✅ PASS: Full pipeline (API → map → transform) works without crashes")
    return True


if __name__ == '__main__':
    print("=" * 70)
    print("QA Fix Validation - Story 1.2-1")
    print("Testing Critical Blocker Fix: map_position_data payload handling")
    print("=" * 70)
    print()

    try:
        test_map_position_data_with_correct_payload()
        print()
        test_transform_positions_data_accepts_result_dict()
        print()
        test_full_pipeline_integration()
        print()
        print("=" * 70)
        print("🎉 ALL TESTS PASSED - Critical blocker RESOLVED")
        print("=" * 70)
        sys.exit(0)
    except Exception as e:
        print()
        print("=" * 70)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 70)
        import traceback
        traceback.print_exc()
        sys.exit(1)
