"""
Unit tests for Jainam Prop positions and holdings with field validation
Tests AC6 requirements: symbol, exchange, product, quantity, price, P&L
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from broker.jainam_prop.mapping.order_data import (
    map_position_data,
    transform_positions_data,
    map_portfolio_data,
    calculate_portfolio_statistics,
    transform_holdings_data
)
from services.auth_payload import build_broker_auth_payload

class TestPositionMapping:
    """Test suite for position mapping functions"""

    def test_map_position_data_with_valid_data(self):
        """Test map_position_data with valid position data"""
        position_data = {
            'result': {
                'positionList': [
                    {
                        'ExchangeInstrumentId': 12345,
                        'ExchangeSegment': 'NSECM',
                        'TradingSymbol': '',
                        'Quantity': 100,
                        'BuyAveragePrice': 550.50,
                        'SellAveragePrice': 0,
                        'LastTradedPrice': 552.00,
                        'RealizedProfitLoss': 150.00,
                        'ProductType': 'MIS'
                    }
                ]
            }
        }

        with patch('database.token_db.get_symbol', return_value='SBIN-EQ'):
            result = map_position_data(position_data)

        assert isinstance(result, dict)
        assert 'positionList' in result
        assert isinstance(result['positionList'], list)
        assert len(result['positionList']) == 1
        assert result['positionList'][0]['TradingSymbol'] == 'SBIN-EQ'

    def test_map_position_data_empty_result(self):
        """Test map_position_data with empty result"""
        position_data = {'result': []}
        with patch('database.token_db.get_symbol', return_value=None):
            result = map_position_data(position_data)
        assert result == {'positionList': []}

    def test_map_position_data_no_result_key(self):
        """Test map_position_data with missing result key"""
        position_data = {}
        with patch('database.token_db.get_symbol', return_value=None):
            result = map_position_data(position_data)
        assert result == {'positionList': []}

    def test_map_position_data_legacy_list_payload(self):
        """Ensure legacy list payloads are normalised correctly"""
        position_data = {
            'result': [
                {
                    'ExchangeInstrumentId': 67890,
                    'ExchangeSegment': 'BSECM',
                    'TradingSymbol': '',
                    'Quantity': 10,
                    'BuyAveragePrice': 100.00,
                    'SellAveragePrice': 0,
                    'LastTradedPrice': 105.00,
                    'RealizedProfitLoss': 50.00,
                    'ProductType': 'CNC'
                }
            ]
        }

        with patch('database.token_db.get_symbol', return_value='TEST-BSE'):
            result = map_position_data(position_data)

        assert result['positionList'][0]['TradingSymbol'] == 'TEST-BSE'

    def test_transform_positions_data_with_valid_data(self):
        """Test transform_positions_data validates all AC6 required fields"""
        positions_data = {
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

        result = transform_positions_data(positions_data)

        # Validate all AC6 required fields exist
        assert isinstance(result, list)
        assert len(result) == 1

        position = result[0]
        # AC6: symbol, exchange, product, quantity, price, P&L
        assert 'symbol' in position
        assert 'exchange' in position
        assert 'product' in position
        assert 'quantity' in position
        assert 'average_price' in position
        assert 'ltp' in position
        assert 'pnl' in position

        # Verify values
        assert position['symbol'] == 'SBIN-EQ'
        assert position['exchange'] == 'NSE'
        assert position['product'] == 'MIS'
        assert position['quantity'] == 100
        assert position['average_price'] == '550.50'
        assert position['ltp'] == 552.00
        assert position['pnl'] == 150.00

    def test_transform_positions_data_negative_quantity(self):
        """Test transform_positions_data with negative quantity (short position)"""
        positions_data = {
            'positionList': [
                {
                    'TradingSymbol': 'RELIANCE-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'MIS',
                    'Quantity': -50,
                    'BuyAveragePrice': 0,
                    'SellAveragePrice': 2500.00,
                    'LastTradedPrice': 2480.00,
                    'RealizedProfitLoss': 1000.00
                }
            ]
        }

        result = transform_positions_data(positions_data)

        assert len(result) == 1
        position = result[0]
        assert position['quantity'] == -50
        assert position['average_price'] == '2500.00'

    def test_transform_positions_data_empty_list(self):
        """Test transform_positions_data with empty position list"""
        positions_data = {'positionList': []}
        result = transform_positions_data(positions_data)
        assert result == []

    def test_transform_positions_data_no_positionlist_key(self):
        """Test transform_positions_data with missing positionList key"""
        positions_data = {}
        result = transform_positions_data(positions_data)
        assert result == []

    def test_transform_positions_data_invalid_position(self):
        """Test transform_positions_data skips invalid position entries"""
        positions_data = {
            'positionList': [
                'invalid_string',
                {
                    'TradingSymbol': 'VALID-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'CNC',
                    'Quantity': 10,
                    'BuyAveragePrice': 100.00,
                    'LastTradedPrice': 105.00,
                    'RealizedProfitLoss': 50.00
                }
            ]
        }

        result = transform_positions_data(positions_data)
        assert len(result) == 1  # Only valid position processed
        assert result[0]['symbol'] == 'VALID-EQ'


class TestHoldingsMapping:
    """Test suite for holdings mapping functions"""

    def test_map_portfolio_data_with_valid_data(self):
        """Test map_portfolio_data with valid holdings data"""
        portfolio_data = {
            'type': 'success',
            'result': {
                'RMSHoldings': {
                    'Holdings': {
                        'INE123A01012': {
                            'ExchangeNSEInstrumentId': 11536,
                            'HoldingQuantity': 50,
                            'BuyAvgPrice': 500.00,
                            'MarketRate': 520.00
                        }
                    }
                }
            }
        }

        with patch('database.token_db.get_symbol', return_value='RELIANCE-EQ'):
            result = map_portfolio_data(portfolio_data)

        assert 'holdings' in result
        assert 'totalholding' in result
        assert len(result['holdings']) == 1

        holding = result['holdings'][0]
        # AC6: symbol, exchange, product, quantity, price, P&L
        assert holding['tradingsymbol'] == 'RELIANCE-EQ'
        assert holding['exchange'] == 'NSE'
        assert holding['quantity'] == 50
        assert holding['product'] == 'CNC'
        assert holding['buy_price'] == 500.00
        assert holding['current_price'] == 520.00
        assert holding['profitandloss'] == pytest.approx((520.00 - 500.00) * 50)
        assert holding['pnlpercentage'] == pytest.approx(((520.00 - 500.00) / 500.00) * 100)

    def test_map_portfolio_data_enriches_price_with_market_quote(self):
        """Ensure we fetch live quotes when holdings payload lacks MTM values"""
        portfolio_data = {
            'type': 'success',
            'result': {
                'RMSHoldings': {
                    'Holdings': {
                        'INE654C01010': {
                            'ExchangeNSEInstrumentId': 225412,
                            'HoldingQuantity': 10,
                            'BuyAvgPrice': 100.0,
                            # No market price/value fields present
                        }
                    }
                }
            }
        }

        with patch('database.token_db.get_symbol', return_value='FAKESYM-EQ'):
            with patch('broker.jainam_prop.mapping.order_data.get_quotes') as mock_get_quotes:
                mock_get_quotes.return_value = {'ltp': 112.5}

                result = map_portfolio_data(
                    portfolio_data,
                    auth_token={'market_token': 'market-token-123'}
                )

        holding = result['holdings'][0]
        assert holding['current_price'] == pytest.approx(112.5)
        assert holding['profitandloss'] == pytest.approx((112.5 - 100.0) * 10)
        assert holding['pnlpercentage'] == pytest.approx(12.5)
        # Quote should be fetched exactly once and cached
        mock_get_quotes.assert_called_once_with(
            'FAKESYM-EQ',
            'NSE',
            {'market_token': 'market-token-123'}
        )

    def test_map_portfolio_data_no_success_type(self):
        """Test map_portfolio_data with non-success type"""
        portfolio_data = {'type': 'error'}
        with patch('database.token_db.get_symbol', return_value=None):
            result = map_portfolio_data(portfolio_data)

        assert result['holdings'] == []
        assert result['totalholding'] is None

    def test_map_portfolio_data_empty_holdings(self):
        """Test map_portfolio_data with empty holdings"""
        portfolio_data = {
            'type': 'success',
            'result': {
                'RMSHoldings': {
                    'Holdings': {}
                }
            }
        }

        with patch('database.token_db.get_symbol', return_value=None):
            result = map_portfolio_data(portfolio_data)

        assert result['holdings'] == []
        assert result['totalholding']['totalholdingvalue'] == 0
        assert result['totalholding']['totalinvvalue'] == 0

    def test_calculate_portfolio_statistics_with_valid_data(self):
        """Test calculate_portfolio_statistics with valid holdings data"""
        holdings_data = {
            'holdings': [],
            'totalholding': {
                'totalholdingvalue': 50000.00,
                'totalinvvalue': 45000.00,
                'totalprofitandloss': 5000.00,
                'totalpnlpercentage': 11.11
            }
        }

        result = calculate_portfolio_statistics(holdings_data)

        assert result['totalholdingvalue'] == 50000.00
        assert result['totalinvvalue'] == 45000.00
        assert result['totalprofitandloss'] == 5000.00
        assert result['totalpnlpercentage'] == 11.11

    def test_calculate_portfolio_statistics_no_totalholding(self):
        """Test calculate_portfolio_statistics with missing totalholding"""
        holdings_data = {'holdings': []}

        result = calculate_portfolio_statistics(holdings_data)

        assert result['totalholdingvalue'] == 0
        assert result['totalinvvalue'] == 0
        assert result['totalprofitandloss'] == 0
        assert result['totalpnlpercentage'] == 0

    def test_transform_holdings_data_with_valid_data(self):
        """Test transform_holdings_data validates all AC6 required fields"""
        holdings_data = {
            'holdings': [
                {
                    'tradingsymbol': 'INFY-EQ',
                    'exchange': 'NSE',
                    'quantity': 100,
                    'product': 'CNC',
                    'buy_price': 1450.00,
                    'current_price': 1500.00,
                    'profitandloss': 2500.00,
                    'pnlpercentage': 5.5
                }
            ]
        }

        result = transform_holdings_data(holdings_data)

        # Validate all AC6 required fields exist
        assert isinstance(result, list)
        assert len(result) == 1

        holding = result[0]
        # AC6: symbol, exchange, product, quantity, price, P&L
        assert 'symbol' in holding
        assert 'exchange' in holding
        assert 'quantity' in holding
        assert 'product' in holding
        assert 'price' in holding  # AC6 CRITICAL
        assert 'pnl' in holding
        assert 'pnlpercent' in holding

        # Verify values
        assert holding['symbol'] == 'INFY-EQ'
        assert holding['exchange'] == 'NSE'
        assert holding['quantity'] == 100
        assert holding['product'] == 'CNC'
        assert holding['price'] == 1500.00  # AC6 price field now reflects current price when available
        assert holding['pnl'] == 2500.00
        assert holding['pnlpercent'] == 5.5

    def test_transform_holdings_data_empty_holdings(self):
        """Test transform_holdings_data with empty holdings"""
        holdings_data = {'holdings': []}
        result = transform_holdings_data(holdings_data)
        assert result == []

    def test_transform_holdings_data_no_holdings_key(self):
        """Test transform_holdings_data with missing holdings key"""
        holdings_data = {}
        result = transform_holdings_data(holdings_data)
        assert result == []


class TestFieldValidation:
    """Test suite specifically for AC6 field validation"""

    def test_positions_all_ac6_fields_present(self):
        """Comprehensive test that ALL AC6 fields are present in positions"""
        positions_data = {
            'positionList': [
                {
                    'TradingSymbol': 'TCS-EQ',
                    'ExchangeSegment': 'NSECM',
                    'ProductType': 'CNC',
                    'Quantity': 25,
                    'BuyAveragePrice': 3500.00,
                    'SellAveragePrice': 0,
                    'LastTradedPrice': 3550.00,
                    'RealizedProfitLoss': 1250.00
                }
            ]
        }

        result = transform_positions_data(positions_data)
        position = result[0]

        # AC6 CRITICAL VALIDATION: symbol, exchange, product, quantity, price, P&L
        required_fields = ['symbol', 'exchange', 'product', 'quantity', 'average_price', 'ltp', 'pnl']

        for field in required_fields:
            assert field in position, f"Missing required AC6 field: {field}"
            assert position[field] is not None, f"AC6 field {field} is None"

        # Verify field types
        assert isinstance(position['symbol'], str)
        assert isinstance(position['exchange'], str)
        assert isinstance(position['product'], str)
        assert isinstance(position['quantity'], (int, float))
        assert isinstance(position['average_price'], str)  # Formatted as string
        assert isinstance(position['ltp'], float)
        assert isinstance(position['pnl'], float)

    def test_holdings_all_ac6_fields_present(self):
        """Comprehensive test that ALL AC6 fields are present in holdings"""
        holdings_data = {
            'holdings': [
                {
                    'tradingsymbol': 'HDFC-EQ',
                    'exchange': 'NSE',
                    'quantity': 10,
                    'product': 'CNC',
                    'buy_price': 1580.00,
                    'profitandloss': 500.00,
                    'pnlpercentage': 3.2
                }
            ]
        }

        result = transform_holdings_data(holdings_data)
        holding = result[0]

        # AC6 CRITICAL VALIDATION: symbol, exchange, product, quantity, price, P&L
        required_fields = ['symbol', 'exchange', 'product', 'quantity', 'price', 'pnl', 'pnlpercent']

        for field in required_fields:
            assert field in holding, f"Missing required AC6 field: {field}"
            assert holding[field] is not None, f"AC6 field {field} is None"

        # Verify field types
        assert isinstance(holding['symbol'], str)
        assert isinstance(holding['exchange'], str)
        assert isinstance(holding['product'], str)
        assert isinstance(holding['quantity'], (int, float))
        assert isinstance(holding['price'], float)  # AC6 price field
        assert isinstance(holding['pnl'], float)
        assert isinstance(holding['pnlpercent'], float)


class TestIntegrationMappingChain:
    """Integration tests for full mapping chain: API response → map → transform"""

    def test_positions_full_chain(self):
        """Test complete positions pipeline: map_position_data → transform_positions_data

        Uses actual Jainam XTS API response structure: {'result': {'positionList': [...]}}
        """
        # Sample API response from Jainam XTS (actual structure)
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
                    },
                    {
                        'ExchangeInstrumentId': 2885,
                        'ExchangeSegment': 'NSECM',
                        'ProductType': 'CNC',
                        'Quantity': -50,
                        'BuyAveragePrice': 0,
                        'SellAveragePrice': 2500.00,
                        'LastTradedPrice': 2480.00,
                        'RealizedProfitLoss': 1000.00
                    }
                ]
            }
        }

        with patch('database.token_db.get_symbol') as mock_get_symbol:
            # Mock symbol resolution
            mock_get_symbol.side_effect = lambda token, exch: {
                (11536, 'NSE'): 'SBIN-EQ',
                (2885, 'NSE'): 'RELIANCE-EQ'
            }.get((token, exch), None)

            # Execute full chain
            mapped_data = map_position_data(api_response)
            transformed_data = transform_positions_data(mapped_data)

        # Validate output structure
        assert isinstance(transformed_data, list)
        assert len(transformed_data) == 2

        # Validate first position (long)
        pos1 = transformed_data[0]
        assert pos1['symbol'] == 'SBIN-EQ'
        assert pos1['exchange'] == 'NSE'
        assert pos1['product'] == 'MIS'
        assert pos1['quantity'] == 100
        assert pos1['average_price'] == '550.50'
        assert pos1['ltp'] == 552.00
        assert pos1['pnl'] == 150.00

        # Validate second position (short)
        pos2 = transformed_data[1]
        assert pos2['symbol'] == 'RELIANCE-EQ'
        assert pos2['quantity'] == -50
        assert pos2['average_price'] == '2500.00'

    def test_holdings_full_chain(self):
        """Test complete holdings pipeline: map_portfolio_data → transform_holdings_data"""
        # Sample API response from Jainam
        api_response = {
            'type': 'success',
            'result': {
                'RMSHoldings': {
                        'Holdings': {
                            'INE123A01012': {
                                'ExchangeNSEInstrumentId': 11536,
                                'HoldingQuantity': 50,
                                'BuyAvgPrice': 500.00,
                                'MarketRate': 520.00
                            },
                            'INE456B02023': {
                                'ExchangeNSEInstrumentId': 2885,
                                'HoldingQuantity': 25,
                                'BuyAvgPrice': 2400.00,
                                'MarketRate': 2455.00
                            }
                        }
                    }
                }
            }

        with patch('database.token_db.get_symbol') as mock_get_symbol:
            # Mock symbol resolution
            mock_get_symbol.side_effect = lambda token, exch: {
                (11536, 'NSE'): 'RELIANCE-EQ',
                (2885, 'NSE'): 'INFY-EQ'
            }.get((token, exch), None)

            # Execute full chain
            mapped_data = map_portfolio_data(api_response)
            stats = calculate_portfolio_statistics(mapped_data)
            transformed_data = transform_holdings_data(mapped_data)

        # Validate output structure
        assert isinstance(transformed_data, list)
        assert len(transformed_data) == 2

        # Validate portfolio statistics
        assert stats['totalinvvalue'] == 85000.00  # (50*500) + (25*2400)
        assert stats['totalprofitandloss'] == pytest.approx((20.0 * 50) + (55.0 * 25))

        # Validate first holding
        hold1 = transformed_data[0]
        assert 'symbol' in hold1
        assert 'exchange' in hold1
        assert 'quantity' in hold1
        assert 'product' in hold1
        assert 'price' in hold1  # AC6 CRITICAL
        assert 'pnl' in hold1
        assert 'pnlpercent' in hold1

        # Verify data integrity
        assert hold1['exchange'] == 'NSE'
        assert hold1['product'] == 'CNC'
        assert hold1['price'] == pytest.approx(520.00)
        assert hold1['pnl'] == pytest.approx(1000.0)


class TestAuthPayloadHelper:
    """Unit tests for broker auth payload helper."""

    def test_build_payload_with_feed_token(self):
        payload = build_broker_auth_payload('interactive-token', 'feed-token')

        assert isinstance(payload, dict)
        assert payload['token'] == 'interactive-token'
        assert payload['market_token'] == 'feed-token'
        assert payload['marketAuthToken'] == 'feed-token'
        assert payload['feed_token'] == 'feed-token'

    def test_build_payload_without_feed_token(self):
        payload = build_broker_auth_payload('interactive-only', None)
        assert payload == 'interactive-only'

    def test_build_payload_missing_interactive_token(self):
        payload = build_broker_auth_payload(None, 'feed-token')
        assert payload is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
