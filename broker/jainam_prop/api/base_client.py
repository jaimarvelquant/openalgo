"""
Base API client for Jainam XTS API interactions.

Provides centralized request handling, error management, and logging
for all API modules (auth, orders, data, funds).

Based on reference: _sample_strategy/xts_connect.py lines 1070-1089
Modified to use httpx library instead of requests for async compatibility.
"""

import logging
import httpx
from typing import Dict, Any, Optional, Union

from .routes import get_route
from .config import get_jainam_base_url

logger = logging.getLogger(__name__)


class BaseAPIClient:
    """
    Base class for Jainam XTS API clients.
    
    Provides centralized:
    - HTTP request handling (GET, POST, PUT, DELETE)
    - Authentication header management
    - Error handling (HTTP errors, timeouts, connection errors)
    - Logging
    - Route resolution
    
    Usage:
        class OrderAPIClient(BaseAPIClient):
            def place_order(self, order_data):
                return self._post('order.place', json_data=order_data)
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: float = 10.0
    ):
        """
        Initialize base API client.
        
        Args:
            base_url: Jainam API base URL (defaults to config value)
            auth_token: Authentication token (interactive or market data)
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url or get_jainam_base_url()
        self.auth_token = auth_token
        self.default_timeout = timeout
        self._client = None
    
    def _get_client(self) -> httpx.Client:
        """
        Get or create httpx client instance.
        
        Uses shared client from existing implementation for connection pooling.
        
        Returns:
            httpx.Client instance
        """
        if self._client is None:
            # Import here to avoid circular dependency
            try:
                from .order_api import get_httpx_client
                self._client = get_httpx_client()
            except ImportError:
                # Fallback: create new client if import fails
                self._client = httpx.Client(timeout=self.default_timeout)
        
        return self._client
    
    def set_auth_token(self, token: str) -> None:
        """
        Set or update authentication token.
        
        Args:
            token: Authentication token
        """
        self.auth_token = token
    
    def _build_headers(
        self,
        additional_headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, str]:
        """
        Build request headers with authentication.
        
        Args:
            additional_headers: Optional additional headers to include
        
        Returns:
            Complete headers dictionary
        """
        headers = {
            'Content-Type': 'application/json'
        }
        
        if self.auth_token:
            headers['Authorization'] = self.auth_token
        
        if additional_headers:
            headers.update(additional_headers)
        
        return headers
    
    def _request(
        self,
        route_key: str,
        method: str = 'GET',
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        content: Optional[Union[str, bytes]] = None,
        timeout: Optional[float] = None,
        use_standard_marketdata: bool = False,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Jainam API.
        
        Based on reference: _sample_strategy/xts_connect.py lines 1070-1089
        
        Args:
            route_key: Route key from JAINAM_ROUTES (e.g., 'user.login')
            method: HTTP method (GET, POST, PUT, DELETE)
            params: Query parameters (for GET/DELETE)
            json_data: JSON body (for POST/PUT) - will be serialized automatically
            content: Raw content (for POST/PUT) - use for pre-serialized JSON
            timeout: Request timeout in seconds (uses default if not specified)
            use_standard_marketdata: Use standard market data API instead of binary
            **kwargs: Additional arguments to pass to httpx
        
        Returns:
            Response JSON as dictionary
        
        Raises:
            httpx.HTTPStatusError: For HTTP error responses
            httpx.TimeoutException: For timeout errors
            httpx.ConnectError: For connection errors
            KeyError: If route_key not found in routes dictionary
        
        Examples:
            >>> client = BaseAPIClient(auth_token="token123")
            >>> response = client._request('user.login', 'POST', json_data={'appKey': 'key'})
            >>> response = client._get('user.balance', params={'clientID': 'user123'})
        """
        # Get route path from dictionary
        route_path = get_route(route_key, use_standard_marketdata=use_standard_marketdata)
        url = f"{self.base_url}{route_path}"
        
        # Build headers
        headers = self._build_headers(kwargs.pop('headers', None))
        
        # Get httpx client
        client = self._get_client()
        
        # Use default timeout if not specified
        if timeout is None:
            timeout = self.default_timeout
        
        # Log request (DEBUG level)
        logger.debug(f"{method} {url}")
        if json_data:
            logger.debug(f"Request JSON: {json_data}")
        elif content:
            logger.debug(f"Request content (first 200 chars): {str(content)[:200]}")
        
        try:
            # Make request based on method
            if method.upper() in ['GET', 'DELETE']:
                response = client.request(
                    method,
                    url,
                    params=params,
                    headers=headers,
                    timeout=timeout,
                    **kwargs
                )
            else:  # POST, PUT
                # Use either json_data or content, not both
                if content is not None:
                    response = client.request(
                        method,
                        url,
                        content=content,
                        headers=headers,
                        timeout=timeout,
                        **kwargs
                    )
                else:
                    response = client.request(
                        method,
                        url,
                        json=json_data,
                        headers=headers,
                        timeout=timeout,
                        **kwargs
                    )
            
            # Log response status
            logger.debug(f"Response status: {response.status_code}")
            
            # Raise for HTTP errors
            response.raise_for_status()
            
            # Parse and return JSON
            response_json = response.json()
            logger.debug(f"Response type: {response_json.get('type', 'unknown')}")
            
            return response_json
        
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            # Special handling for HTTP 400 errors - check if it's an expected "Data Not Available" response
            if status_code == 400:
                try:
                    error_data = e.response.json()
                    error_code = error_data.get('code', '')
                    description = error_data.get('description', '').lower()

                    # Known "Data Not Available" error codes from Jainam API
                    # These are expected when no data exists (empty orderbook, tradebook, positions, etc.)
                    # Pattern: e-{endpoint}-0005
                    no_data_error_codes = [
                        'e-orders-0005',        # No order data available (empty orderbook)
                        'e-tradebook-0005',     # No trade data available (empty tradebook)
                        'e-portfolio-0005',     # No position data available (empty positions)
                        'e-holdings-0005',      # No holdings data available (empty holdings)
                        'e-funds-0005',         # No funds data available
                        'e-balance-0005',       # No balance data available
                    ]

                    # Check if this is a "Data Not Available" error
                    # Match by error code OR by description containing "data not available"
                    is_no_data_error = (
                        error_code.lower() in [code.lower() for code in no_data_error_codes] or
                        'data not available' in description
                    )

                    if is_no_data_error:
                        # Log at DEBUG level - this is expected when no data exists
                        # The calling function will handle this appropriately (return empty data)
                        logger.debug(
                            f"HTTP 400 for {route_key}: Data Not Available "
                            f"(code: {error_code}) - Expected when no data exists"
                        )
                        raise  # Re-raise for caller to handle
                    else:
                        # Log other HTTP 400 errors at ERROR level (actual errors)
                        logger.error(
                            f"HTTP {status_code} error for {route_key}: "
                            f"{e.response.text[:500]}"
                        )
                        raise
                except (ValueError, KeyError, AttributeError):
                    # If we can't parse the response JSON, log as ERROR
                    logger.error(
                        f"HTTP {status_code} error for {route_key}: "
                        f"{e.response.text[:500]}"
                    )
                    raise
            else:
                # Log all non-400 HTTP errors at ERROR level
                logger.error(
                    f"HTTP {status_code} error for {route_key}: "
                    f"{e.response.text[:500]}"
                )
                raise
        
        except httpx.TimeoutException as e:
            logger.error(f"Timeout error for {route_key}: {e}")
            raise
        
        except httpx.ConnectError as e:
            logger.error(f"Connection error for {route_key}: {e}")
            raise
        
        except Exception as e:
            logger.error(f"Unexpected error for {route_key}: {e}")
            raise
    
    def _get(
        self,
        route_key: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for GET requests.
        
        Args:
            route_key: Route key from JAINAM_ROUTES
            params: Query parameters
            **kwargs: Additional arguments
        
        Returns:
            Response JSON as dictionary
        """
        return self._request(route_key, 'GET', params=params, **kwargs)
    
    def _post(
        self,
        route_key: str,
        json_data: Optional[Dict[str, Any]] = None,
        content: Optional[Union[str, bytes]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for POST requests.
        
        Args:
            route_key: Route key from JAINAM_ROUTES
            json_data: JSON body (will be serialized automatically)
            content: Raw content (for pre-serialized JSON)
            **kwargs: Additional arguments
        
        Returns:
            Response JSON as dictionary
        """
        return self._request(route_key, 'POST', json_data=json_data, content=content, **kwargs)
    
    def _put(
        self,
        route_key: str,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for PUT requests.
        
        Args:
            route_key: Route key from JAINAM_ROUTES
            json_data: JSON body
            **kwargs: Additional arguments
        
        Returns:
            Response JSON as dictionary
        """
        return self._request(route_key, 'PUT', json_data=json_data, **kwargs)
    
    def _delete(
        self,
        route_key: str,
        params: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for DELETE requests.
        
        Args:
            route_key: Route key from JAINAM_ROUTES
            params: Query parameters
            **kwargs: Additional arguments
        
        Returns:
            Response JSON as dictionary
        """
        return self._request(route_key, 'DELETE', params=params, **kwargs)
    
    def close(self) -> None:
        """Close the HTTP client connection."""
        if self._client is not None:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close client."""
        self.close()

