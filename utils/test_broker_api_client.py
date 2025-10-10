#!/usr/bin/env python3
"""
Unit tests for utils/broker_api_client.py
Tests enterprise-grade resilience patterns: retry logic, circuit breaker, error handling.
"""

from __future__ import annotations

import time
from unittest.mock import MagicMock, patch, PropertyMock

import httpx
import pytest

from utils.broker_api_client import (
    BrokerAPIClient,
    CircuitBreaker,
    CircuitBreakerState,
    ErrorCode,
)


class TestCircuitBreaker:
    """Test circuit breaker pattern implementation."""

    def test_circuit_starts_closed(self):
        """Circuit breaker starts in CLOSED state."""
        cb = CircuitBreaker(failure_threshold=3)
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0

    def test_circuit_opens_after_threshold_failures(self):
        """Circuit opens after threshold failures."""
        cb = CircuitBreaker(failure_threshold=3, expected_exception=ValueError)

        def failing_func():
            raise ValueError("Test error")

        # First 2 failures - circuit stays closed
        for i in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)
            assert cb.state == CircuitBreakerState.CLOSED

        # 3rd failure - circuit opens
        with pytest.raises(ValueError):
            cb.call(failing_func)
        assert cb.state == CircuitBreakerState.OPEN

    def test_circuit_rejects_calls_when_open(self):
        """Circuit rejects calls when OPEN."""
        cb = CircuitBreaker(failure_threshold=1, expected_exception=ValueError)

        def failing_func():
            raise ValueError("Test error")

        # Open the circuit
        with pytest.raises(ValueError):
            cb.call(failing_func)

        assert cb.state == CircuitBreakerState.OPEN

        # Next call should be rejected
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            cb.call(failing_func)

    def test_circuit_resets_on_success(self):
        """Circuit resets to CLOSED after successful call in HALF_OPEN."""
        cb = CircuitBreaker(failure_threshold=2, recovery_timeout=0.1)

        def failing_func():
            raise ValueError("Fail")

        def success_func():
            return "success"

        # Open circuit
        for _ in range(2):
            with pytest.raises(ValueError):
                cb.call(failing_func)

        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        time.sleep(0.15)

        # Next call should enter HALF_OPEN and succeed
        result = cb.call(success_func)
        assert result == "success"
        assert cb.state == CircuitBreakerState.CLOSED
        assert cb.failure_count == 0


class TestBrokerAPIClient:
    """Test enterprise-grade broker API client."""

    def test_client_initialization(self):
        """Client initializes with correct parameters."""
        client = BrokerAPIClient(
            broker_name="test_broker",
            base_url="https://api.test.com",
            max_retries=5,
            timeout=15.0
        )

        assert client.broker_name == "test_broker"
        assert client.base_url == "https://api.test.com"
        assert client.max_retries == 5
        assert client.timeout == 15.0

    def test_create_error_response_structure(self):
        """Error response has standardized structure."""
        client = BrokerAPIClient("test", "https://api.test.com")

        error = client._create_error_response(
            ErrorCode.HTTP_5XX,
            "Server error",
            "/test/endpoint",
            http_status=500,
            details={'key': 'value'},
            correlation_id="abc123"
        )

        assert error['status'] == 'error'
        assert error['error_code'] == 'HTTP_SERVER_ERROR'
        assert error['message'] == 'Server error'
        assert error['endpoint'] == '/test/endpoint'
        assert error['http_status'] == 500
        assert error['details'] == {'key': 'value'}
        assert error['correlation_id'] == 'abc123'
        assert error['broker'] == 'test'
        assert 'timestamp' in error

    @patch('utils.broker_api_client.get_httpx_client')
    def test_successful_get_request(self, mock_get_client):
        """Successful GET request returns parsed JSON."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success', 'data': []}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com")
        result = client.get("/test", "auth_token")

        assert result == {'status': 'success', 'data': []}
        mock_client.get.assert_called_once()

    @patch('utils.broker_api_client.get_httpx_client')
    def test_http_500_retry_and_error_response(self, mock_get_client):
        """HTTP 500 triggers retries and returns error response."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.json.side_effect = Exception("Not JSON")

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com", max_retries=3)
        result = client.get("/test", "auth_token")

        # Should retry 3 times
        assert mock_client.get.call_count == 3

        # Should return standardized error
        assert result['status'] == 'error'
        assert result['error_code'] == 'HTTP_SERVER_ERROR'
        assert result['http_status'] == 500

    @patch('utils.broker_api_client.get_httpx_client')
    def test_http_400_no_retry(self, mock_get_client):
        """HTTP 4xx errors don't trigger retry."""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {'error': 'Invalid input'}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com", max_retries=3)
        result = client.get("/test", "auth_token")

        # Should NOT retry on 4xx
        assert mock_client.get.call_count == 1

        # Should return error response
        assert result['status'] == 'error'
        assert result['error_code'] == 'HTTP_CLIENT_ERROR'
        assert result['http_status'] == 400

    @patch('utils.broker_api_client.get_httpx_client')
    def test_timeout_retry(self, mock_get_client):
        """Timeout errors trigger retry with backoff."""
        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.TimeoutException("Timeout")
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com", max_retries=2)

        with patch('time.sleep') as mock_sleep:
            result = client.get("/test", "auth_token")

        # Should retry
        assert mock_client.get.call_count == 2

        # Should sleep between retries
        assert mock_sleep.call_count == 1

        # Should return timeout error
        assert result['status'] == 'error'
        assert result['error_code'] == 'REQUEST_TIMEOUT'

    @patch('utils.broker_api_client.get_httpx_client')
    def test_connection_error_retry(self, mock_get_client):
        """Connection errors trigger retry."""
        mock_client = MagicMock()
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com", max_retries=2)

        with patch('time.sleep') as mock_sleep:
            result = client.get("/test", "auth_token")

        assert mock_client.get.call_count == 2
        assert result['error_code'] == 'CONNECTION_ERROR'

    @patch('utils.broker_api_client.get_httpx_client')
    def test_circuit_breaker_opens_after_failures(self, mock_get_client):
        """Circuit breaker opens after threshold failures."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Error"
        mock_response.json.side_effect = Exception("Not JSON")

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient(
            "test",
            "https://api.test.com",
            max_retries=1,  # Fail fast
            enable_circuit_breaker=True
        )

        # Make 5 requests to same endpoint to open circuit
        for i in range(5):
            result = client.get("/test", "auth_token")
            assert result['status'] == 'error'

        # Circuit should be open now
        cb = client._get_circuit_breaker("/test")
        assert cb.state == CircuitBreakerState.OPEN

        # Next request should be rejected by circuit breaker
        result = client.get("/test", "auth_token")
        assert result['error_code'] == 'CIRCUIT_BREAKER_OPEN'

    def test_get_metrics(self):
        """Client tracks and reports metrics."""
        client = BrokerAPIClient("test", "https://api.test.com")

        metrics = client.get_metrics()
        assert metrics['broker'] == 'test'
        assert metrics['total_requests'] == 0
        assert metrics['total_errors'] == 0
        assert metrics['error_rate'] == 0

    @patch('utils.broker_api_client.get_httpx_client')
    def test_post_request(self, mock_get_client):
        """POST requests work correctly."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}

        mock_client = MagicMock()
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com")
        result = client.post("/test", "auth_token", json_data={'key': 'value'})

        assert result == {'status': 'success'}
        mock_client.post.assert_called_once()

    @patch('utils.broker_api_client.get_httpx_client')
    def test_exponential_backoff(self, mock_get_client):
        """Retry uses exponential backoff."""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Error"
        mock_response.json.side_effect = Exception("Not JSON")

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient(
            "test",
            "https://api.test.com",
            max_retries=3,
            retry_backoff_factor=1.0
        )

        with patch('time.sleep') as mock_sleep:
            client.get("/test", "auth_token")

        # Should sleep with exponential backoff: 1s, 2s
        assert mock_sleep.call_count == 2
        sleep_calls = [call[0][0] for call in mock_sleep.call_args_list]
        assert sleep_calls[0] == 1.0  # 1.0 * 2^0
        assert sleep_calls[1] == 2.0  # 1.0 * 2^1

    @patch('utils.broker_api_client.get_httpx_client')
    def test_correlation_id_in_headers(self, mock_get_client):
        """Requests include correlation ID in headers."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'status': 'success'}

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com")
        client.get("/test", "auth_token")

        # Check that correlation ID was added to headers
        call_args = mock_client.get.call_args
        headers = call_args[1]['headers']
        assert 'X-Correlation-ID' in headers
        assert len(headers['X-Correlation-ID']) == 8  # UUID prefix

    @patch('utils.broker_api_client.get_httpx_client')
    def test_invalid_json_response_handling(self, mock_get_client):
        """Invalid JSON responses are handled gracefully."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Not JSON"
        mock_response.json.side_effect = Exception("JSON decode error")

        mock_client = MagicMock()
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        client = BrokerAPIClient("test", "https://api.test.com")
        result = client.get("/test", "auth_token")

        assert result['status'] == 'error'
        assert result['error_code'] == 'INVALID_RESPONSE'
        assert 'JSON' in result['message']
