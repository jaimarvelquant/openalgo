"""
Unit tests for get_open_position function

Tests all scenarios:
- Long position (positive quantity)
- Short position (negative quantity)
- No position (not found)
- Invalid symbol
- Empty positions
- get_positions() failure
- Various response formats
- Exchange normalization (NSE -> NSECM)
"""
import json
import pytest
from unittest.mock import patch, MagicMock
from broker.jainam_prop.api.order_api import get_open_position


class TestGetOpenPosition:
    """Test suite for get_open_position function"""

    def test_long_position_found(self):
        """Test finding a long position (positive quantity)"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '100'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '100'
            mock_get_pos.assert_called_once_with('test_token')

    def test_short_position_found(self):
        """Test finding a short position (negative quantity)"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'RELIANCE-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '-50'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('RELIANCE-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '-50'

    def test_position_not_found(self):
        """Test when position doesn't exist (returns 0)"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '100'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            # Search for different symbol
            result = get_open_position('INFY-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '0'

    def test_empty_positions(self):
        """Test when position book is empty"""
        mock_positions = {
            'type': 'success',
            'result': []
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '0'

    def test_get_positions_failure(self):
        """Test when get_positions() returns error"""
        mock_positions = {
            'status': 'error',
            'message': 'Authentication failed'
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '0'

    def test_get_positions_returns_none(self):
        """Test when get_positions() returns None"""
        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = None

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '0'

    def test_exchange_normalization(self):
        """Test exchange normalization (NSE -> NSECM)"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',  # XTS format
                    'ProductType': 'MIS',
                    'NetQty': '100'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            # Search with NSE (should match NSECM)
            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '100'

    def test_exchange_normalization_bse(self):
        """Test BSE exchange normalization (BSE -> BSECM)"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'BSECM',
                    'ProductType': 'CNC',
                    'NetQty': '50'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'BSE', 'CNC', 'test_token')

            assert result == '50'

    def test_product_type_exact_match(self):
        """Test that product type must match exactly"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'CNC',
                    'NetQty': '100'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            # Search for MIS (should not match CNC)
            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '0'

    def test_multiple_positions_filter(self):
        """Test filtering through multiple positions"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '100'
                },
                {
                    'TradingSymbol': 'RELIANCE-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '200'
                },
                {
                    'TradingSymbol': 'INFY-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'CNC',
                    'NetQty': '50'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            # Should find RELIANCE
            result = get_open_position('RELIANCE-EQ', 'NSE', 'MIS', 'test_token')
            assert result == '200'

    def test_alternative_field_names_lowercase(self):
        """Test handling of lowercase field names"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'tradingsymbol': 'SBIN-EQ',  # lowercase
                    'exchange': 'NSE',           # direct exchange
                    'producttype': 'MIS',        # lowercase
                    'netqty': '100'              # lowercase
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '100'

    def test_alternative_field_names_mixed(self):
        """Test handling of mixed case field names"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'symbol': 'SBIN-EQ',
                    'exch': 'NSE',
                    'product': 'MIS',
                    'quantity': '100'  # Alternative field name
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '100'

    def test_direct_list_response(self):
        """Test when get_positions returns direct list (not wrapped in dict)"""
        mock_positions = [
            {
                'TradingSymbol': 'SBIN-EQ',
                'ExchangeSegment': 'NSECM',
                'ProductType': 'MIS',
                'NetQty': '100'
            }
        ]

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '100'

    def test_nested_data_key_response(self):
        """Test alternative response format with 'data' key"""
        mock_positions = {
            'status': 'success',
            'data': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '100'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '100'

    def test_zero_quantity_position(self):
        """Test position with zero quantity"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '0'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '0'

    def test_numeric_quantity_conversion(self):
        """Test conversion of numeric quantity to string"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': 100  # Integer instead of string
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '100'
            assert isinstance(result, str)

    def test_exception_handling(self):
        """Test graceful handling of exceptions"""
        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.side_effect = Exception('Network error')

            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'test_token')

            assert result == '0'

    def test_nfo_exchange_normalization(self):
        """Test NFO exchange normalization"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'NIFTY24DECFUT',
                    'ExchangeSegment': 'NSEFO',
                    'ProductType': 'NRML',
                    'NetQty': '50'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            result = get_open_position('NIFTY24DECFUT', 'NFO', 'NRML', 'test_token')

            assert result == '50'

    def test_auth_token_string_format(self):
        """Test with string auth token format"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '100'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            # Pass string token
            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', 'simple_string_token')

            assert result == '100'

    def test_auth_token_dict_format(self):
        """Test with dict auth token format"""
        mock_positions = {
            'type': 'success',
            'result': [
                {
                    'TradingSymbol': 'SBIN-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'NetQty': '100'
                }
            ]
        }

        with patch('broker.jainam_prop.api.order_api.get_positions') as mock_get_pos:
            mock_get_pos.return_value = mock_positions

            # Pass dict token
            result = get_open_position('SBIN-EQ', 'NSE', 'MIS', {'token': 'test_token'})

            assert result == '100'


if __name__ == '__main__':
    # Run tests with pytest
    pytest.main([__file__, '-v', '--tb=short'])
