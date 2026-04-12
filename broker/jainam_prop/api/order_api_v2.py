"""
Enterprise-grade Jainam API implementation using resilient broker client.

This module provides improved error handling, retry logic, and observability
for Jainam API operations.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional, Tuple

from broker.jainam_prop.api.config import get_jainam_base_url
from utils.broker_api_client import BrokerAPIClient
from utils.logging import get_logger

logger = get_logger(__name__)


class JainamAPIClientV2:
    """
    Enterprise-grade Jainam API client with resilience patterns.

    Features:
    - Automatic retry with exponential backoff
    - Circuit breaker for failing endpoints
    - Standardized error responses
    - Comprehensive logging and telemetry
    - Graceful degradation
    """

    def __init__(self):
        """Initialize Jainam API client with resilience features."""
        self.base_url = get_jainam_base_url()

        # Create resilient API client
        self.client = BrokerAPIClient(
            broker_name="jainam",
            base_url=self.base_url,
            max_retries=3,
            retry_backoff_factor=0.5,  # 0.5s, 1s, 2s backoff
            timeout=10.0,
            enable_circuit_breaker=True
        )

    def _parse_auth_token(self, auth_token: Any) -> Dict[str, Any]:
        """
        Parse authentication token into structured credentials.

        Args:
            auth_token: String token or dict with credentials

        Returns:
            Dict with parsed credentials
        """
        if isinstance(auth_token, str):
            try:
                return json.loads(auth_token)
            except json.JSONDecodeError:
                return {'token': auth_token}
        elif isinstance(auth_token, dict):
            return auth_token
        else:
            logger.warning(f"Unexpected auth_token type: {type(auth_token)}")
            return {'token': str(auth_token)}

    def _format_auth_header(self, credentials: Dict[str, Any]) -> str:
        """
        Format authentication header value.

        Args:
            credentials: Parsed credentials dict

        Returns:
            Authorization header value
        """
        # Try different token field names
        token = credentials.get('token') or credentials.get('interactive_token')

        if not token:
            logger.warning("No token found in credentials, using raw string")
            # Fallback to first string value
            for value in credentials.values():
                if isinstance(value, str):
                    token = value
                    break

        return token or ""

    def get_positions(self, auth_token: Any) -> Dict[str, Any]:
        """
        Get net positions from Jainam with enterprise-grade error handling.

        Args:
            auth_token: Authentication token (string or dict)

        Returns:
            Dict with positions data or standardized error response
        """
        try:
            credentials = self._parse_auth_token(auth_token)
            auth_header = self._format_auth_header(credentials)

            response = self.client.get(
                endpoint="/interactive/portfolio/positions",
                auth_token=auth_header
            )

            # Check for error response
            if response.get('status') == 'error':
                logger.error(f"Positions API error: {response.get('message')}")
                return response

            # Success - return raw response (mapping happens at service layer)
            logger.info("Positions retrieved successfully")
            return response

        except Exception as e:
            logger.exception(f"Unexpected error getting positions: {e}")
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'error_code': 'UNKNOWN_ERROR'
            }

    def get_holdings(self, auth_token: Any) -> Dict[str, Any]:
        """
        Get holdings from Jainam with enterprise-grade error handling.

        This method handles the known HTTP 500 issue gracefully:
        - Retries with exponential backoff for transient failures
        - Circuit breaker prevents hammering failing endpoint
        - Returns standardized error format for consistent handling
        - Comprehensive logging for troubleshooting

        Args:
            auth_token: Authentication token (string or dict)

        Returns:
            Dict with holdings data or standardized error response
        """
        try:
            credentials = self._parse_auth_token(auth_token)
            auth_header = self._format_auth_header(credentials)

            response = self.client.get(
                endpoint="/interactive/portfolio/holdings",
                auth_token=auth_header
            )

            # Check for error response
            if response.get('status') == 'error':
                error_code = response.get('error_code')
                message = response.get('message')

                # Special handling for known HTTP 500 issue
                if error_code == 'HTTP_SERVER_ERROR':
                    logger.warning(
                        f"Holdings API returned server error (known Jainam issue): {message}"
                    )
                    return {
                        **response,
                        'known_issue': True,
                        'workaround': 'Contact Jainam support for server-side fix'
                    }

                logger.error(f"Holdings API error: {message}")
                return response

            # Success
            logger.info("Holdings retrieved successfully")
            return response

        except Exception as e:
            logger.exception(f"Unexpected error getting holdings: {e}")
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'error_code': 'UNKNOWN_ERROR'
            }

    def get_trade_book(self, auth_token: Any) -> Dict[str, Any]:
        """
        Get trade book from Jainam with enterprise-grade error handling.

        Args:
            auth_token: Authentication token (string or dict)

        Returns:
            Dict with trade book data or standardized error response
        """
        try:
            credentials = self._parse_auth_token(auth_token)
            auth_header = self._format_auth_header(credentials)

            # Corrected endpoint per XTS documentation
            response = self.client.get(
                endpoint="/interactive/orders/trades",
                auth_token=auth_header
            )

            # Check for error response
            if response.get('status') == 'error':
                logger.error(f"Trade book API error: {response.get('message')}")
                return response

            # Success
            logger.info("Trade book retrieved successfully")
            return response

        except Exception as e:
            logger.exception(f"Unexpected error getting trade book: {e}")
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'error_code': 'UNKNOWN_ERROR'
            }

    def get_order_book(self, auth_token: Any) -> Dict[str, Any]:
        """
        Get order book from Jainam.

        Args:
            auth_token: Authentication token (string or dict)

        Returns:
            Dict with order book data or standardized error response
        """
        try:
            credentials = self._parse_auth_token(auth_token)
            auth_header = self._format_auth_header(credentials)

            response = self.client.get(
                endpoint="/interactive/orders",
                auth_token=auth_header
            )

            if response.get('status') == 'error':
                logger.error(f"Order book API error: {response.get('message')}")
                return response

            logger.info("Order book retrieved successfully")
            return response

        except Exception as e:
            logger.exception(f"Unexpected error getting order book: {e}")
            return {
                'status': 'error',
                'message': f'Unexpected error: {str(e)}',
                'error_code': 'UNKNOWN_ERROR'
            }

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get API client metrics for monitoring and observability.

        Returns:
            Dict with request metrics, error rates, circuit breaker states
        """
        return self.client.get_metrics()


# Convenience functions for backward compatibility
def get_positions_v2(auth_token: Any) -> Dict[str, Any]:
    """Get positions using enterprise-grade client."""
    client = JainamAPIClientV2()
    return client.get_positions(auth_token)


def get_holdings_v2(auth_token: Any) -> Dict[str, Any]:
    """Get holdings using enterprise-grade client."""
    client = JainamAPIClientV2()
    return client.get_holdings(auth_token)


def get_trade_book_v2(auth_token: Any) -> Dict[str, Any]:
    """Get trade book using enterprise-grade client."""
    client = JainamAPIClientV2()
    return client.get_trade_book(auth_token)


def get_order_book_v2(auth_token: Any) -> Dict[str, Any]:
    """Get order book using enterprise-grade client."""
    client = JainamAPIClientV2()
    return client.get_order_book(auth_token)
