#!/usr/bin/env python3
"""
Unit tests for broker/jainam_prop/api/order_api_v2.py
Tests enterprise-grade Jainam implementation with resilience patterns.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from broker.jainam_prop.api.order_api_v2 import (
    JainamAPIClientV2,
    get_holdings_v2,
    get_positions_v2,
    get_trade_book_v2,
)


class TestJainamAPIClientV2:
    """Test enterprise-grade Jainam API client."""

    def test_client_initialization(self):
        """Client initializes with Jainam configuration."""
        with patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url') as mock_url:
            mock_url.return_value = "https://api.jainam.com"

            client = JainamAPIClientV2()

            assert client.base_url == "https://api.jainam.com"
            assert client.client.broker_name == "jainam"
            assert client.client.max_retries == 3
            assert client.client.enable_circuit_breaker is True

    def test_parse_auth_token_from_string(self):
        """Parse auth token from plain string."""
        client = JainamAPIClientV2()

        result = client._parse_auth_token("simple_token")
        assert result == {'token': 'simple_token'}

    def test_parse_auth_token_from_json_string(self):
        """Parse auth token from JSON string."""
        client = JainamAPIClientV2()

        auth_json = json.dumps({'token': 'abc123', 'client_id': 'user456'})
        result = client._parse_auth_token(auth_json)

        assert result['token'] == 'abc123'
        assert result['client_id'] == 'user456'

    def test_parse_auth_token_from_dict(self):
        """Parse auth token from dict."""
        client = JainamAPIClientV2()

        result = client._parse_auth_token({'token': 'xyz789', 'extra': 'data'})
        assert result['token'] == 'xyz789'
        assert result['extra'] == 'data'

    def test_format_auth_header(self):
        """Format authorization header from credentials."""
        client = JainamAPIClientV2()

        # With 'token' key
        result = client._format_auth_header({'token': 'my_token'})
        assert result == 'my_token'

        # With 'interactive_token' key
        result = client._format_auth_header({'interactive_token': 'int_token'})
        assert result == 'int_token'

        # Fallback to first string value
        result = client._format_auth_header({'some_key': 'fallback_token'})
        assert result == 'fallback_token'

    @patch('broker.jainam_prop.api.order_api_v2.BrokerAPIClient')
    @patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url')
    def test_get_positions_success(self, mock_url, mock_client_class):
        """Get positions successfully."""
        mock_url.return_value = "https://api.jainam.com"

        mock_api_client = MagicMock()
        mock_api_client.get.return_value = {
            'status': 'success',
            'data': [{'symbol': 'RELIANCE', 'quantity': 10}]
        }
        mock_client_class.return_value = mock_api_client

        client = JainamAPIClientV2()
        result = client.get_positions("test_token")

        assert result['status'] == 'success'
        assert len(result['data']) == 1
        mock_api_client.get.assert_called_once_with(
            endpoint="/interactive/portfolio/positions",
            auth_token="test_token"
        )

    @patch('broker.jainam_prop.api.order_api_v2.BrokerAPIClient')
    @patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url')
    def test_get_holdings_http_500_error(self, mock_url, mock_client_class):
        """Get holdings handles HTTP 500 gracefully."""
        mock_url.return_value = "https://api.jainam.com"

        mock_api_client = MagicMock()
        mock_api_client.get.return_value = {
            'status': 'error',
            'error_code': 'HTTP_SERVER_ERROR',
            'message': 'Server error: HTTP 500',
            'http_status': 500
        }
        mock_client_class.return_value = mock_api_client

        client = JainamAPIClientV2()
        result = client.get_holdings("test_token")

        # Should return error with known_issue flag
        assert result['status'] == 'error'
        assert result['error_code'] == 'HTTP_SERVER_ERROR'
        assert result['known_issue'] is True
        assert 'workaround' in result

    @patch('broker.jainam_prop.api.order_api_v2.BrokerAPIClient')
    @patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url')
    def test_get_holdings_success(self, mock_url, mock_client_class):
        """Get holdings successfully when API works."""
        mock_url.return_value = "https://api.jainam.com"

        mock_api_client = MagicMock()
        mock_api_client.get.return_value = {
            'status': 'success',
            'data': [{'symbol': 'TCS', 'quantity': 5, 'pnl': 1000}]
        }
        mock_client_class.return_value = mock_api_client

        client = JainamAPIClientV2()
        result = client.get_holdings("test_token")

        assert result['status'] == 'success'
        assert len(result['data']) == 1
        mock_api_client.get.assert_called_once_with(
            endpoint="/interactive/portfolio/holdings",
            auth_token="test_token"
        )

    @patch('broker.jainam_prop.api.order_api_v2.BrokerAPIClient')
    @patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url')
    def test_get_trade_book_corrected_endpoint(self, mock_url, mock_client_class):
        """Get trade book uses corrected endpoint."""
        mock_url.return_value = "https://api.jainam.com"

        mock_api_client = MagicMock()
        mock_api_client.get.return_value = {'status': 'success', 'trades': []}
        mock_client_class.return_value = mock_api_client

        client = JainamAPIClientV2()
        result = client.get_trade_book("test_token")

        # Should use corrected endpoint
        mock_api_client.get.assert_called_once_with(
            endpoint="/interactive/orders/trades",
            auth_token="test_token"
        )
        assert result['status'] == 'success'

    @patch('broker.jainam_prop.api.order_api_v2.BrokerAPIClient')
    @patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url')
    def test_get_order_book(self, mock_url, mock_client_class):
        """Get order book works correctly."""
        mock_url.return_value = "https://api.jainam.com"

        mock_api_client = MagicMock()
        mock_api_client.get.return_value = {'status': 'success', 'orders': []}
        mock_client_class.return_value = mock_api_client

        client = JainamAPIClientV2()
        result = client.get_order_book("test_token")

        mock_api_client.get.assert_called_once_with(
            endpoint="/interactive/orders",
            auth_token="test_token"
        )
        assert result['status'] == 'success'

    @patch('broker.jainam_prop.api.order_api_v2.BrokerAPIClient')
    @patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url')
    def test_get_metrics(self, mock_url, mock_client_class):
        """Get metrics from API client."""
        mock_url.return_value = "https://api.jainam.com"

        mock_api_client = MagicMock()
        mock_api_client.get_metrics.return_value = {
            'broker': 'jainam',
            'total_requests': 10,
            'total_errors': 2,
            'error_rate': 0.2
        }
        mock_client_class.return_value = mock_api_client

        client = JainamAPIClientV2()
        metrics = client.get_metrics()

        assert metrics['broker'] == 'jainam'
        assert metrics['total_requests'] == 10
        assert metrics['error_rate'] == 0.2

    @patch('broker.jainam_prop.api.order_api_v2.BrokerAPIClient')
    @patch('broker.jainam_prop.api.order_api_v2.get_jainam_base_url')
    def test_unexpected_exception_handling(self, mock_url, mock_client_class):
        """Unexpected exceptions are caught and returned as errors."""
        mock_url.return_value = "https://api.jainam.com"

        mock_api_client = MagicMock()
        mock_api_client.get.side_effect = RuntimeError("Unexpected error")
        mock_client_class.return_value = mock_api_client

        client = JainamAPIClientV2()
        result = client.get_positions("test_token")

        assert result['status'] == 'error'
        assert result['error_code'] == 'UNKNOWN_ERROR'
        assert 'Unexpected error' in result['message']


class TestConvenienceFunctions:
    """Test convenience wrapper functions."""

    @patch('broker.jainam_prop.api.order_api_v2.JainamAPIClientV2')
    def test_get_positions_v2_convenience(self, mock_client_class):
        """get_positions_v2 creates client and calls method."""
        mock_client = MagicMock()
        mock_client.get_positions.return_value = {'status': 'success'}
        mock_client_class.return_value = mock_client

        result = get_positions_v2("test_token")

        assert result['status'] == 'success'
        mock_client.get_positions.assert_called_once_with("test_token")

    @patch('broker.jainam_prop.api.order_api_v2.JainamAPIClientV2')
    def test_get_holdings_v2_convenience(self, mock_client_class):
        """get_holdings_v2 creates client and calls method."""
        mock_client = MagicMock()
        mock_client.get_holdings.return_value = {'status': 'success'}
        mock_client_class.return_value = mock_client

        result = get_holdings_v2("test_token")

        assert result['status'] == 'success'
        mock_client.get_holdings.assert_called_once_with("test_token")

    @patch('broker.jainam_prop.api.order_api_v2.JainamAPIClientV2')
    def test_get_trade_book_v2_convenience(self, mock_client_class):
        """get_trade_book_v2 creates client and calls method."""
        mock_client = MagicMock()
        mock_client.get_trade_book.return_value = {'status': 'success'}
        mock_client_class.return_value = mock_client

        result = get_trade_book_v2("test_token")

        assert result['status'] == 'success'
        mock_client.get_trade_book.assert_called_once_with("test_token")
