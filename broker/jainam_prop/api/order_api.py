import json
import time
from decimal import Decimal, InvalidOperation
import httpx
from types import SimpleNamespace

from broker.jainam_prop._ensure_database import ensure_database_package

ensure_database_package()
from database.auth_db import get_auth_token
from broker.jainam_prop.mapping.transform_data import transform_data, transform_response
from broker.jainam_prop.api.config import get_jainam_base_url
from broker.jainam_prop.api.base_client import BaseAPIClient
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

logger = get_logger(__name__)

SMART_ORDER_LATENCY_THRESHOLD_SECONDS = 10.0


# ============================================================================
# Helper Functions (Task 24.1)
# ============================================================================

def _parse_auth_token(auth_token):
    """
    Parse auth_token to extract interactive_token and user_id.

    Args:
        auth_token: JSON string or dict containing credentials

    Returns:
        tuple: (interactive_token, user_id)
    """
    if isinstance(auth_token, str):
        try:
            credentials = json.loads(auth_token)
        except:
            credentials = {'interactive_token': auth_token}
    else:
        credentials = auth_token

    interactive_token = credentials.get('interactive_token', credentials.get('token', auth_token))
    user_id = credentials.get('user_id', credentials.get('client_id', 'DEFAULT_USER'))

    return interactive_token, user_id


# ============================================================================
# API Client Class (Task 24.1 - Refactored to use BaseAPIClient)
# ============================================================================

class OrderAPIClient(BaseAPIClient):
    """
    Client for Jainam Interactive API order and portfolio operations.

    Refactored to use BaseAPIClient (Task 24.1).
    """

    def __init__(self, auth_token: str, base_url: str = None):
        """
        Initialize Order API client.

        Args:
            auth_token: Interactive API token
            base_url: Jainam API base URL (optional)
        """
        super().__init__(base_url=base_url, auth_token=auth_token)

    def place_order(self, order_data: dict) -> dict:
        """Place order using Interactive API."""
        return self._post('order.place', json_data=order_data, timeout=15.0)

    def modify_order(self, order_data: dict) -> dict:
        """Modify order using Interactive API."""
        return self._put('order.modify', json_data=order_data, timeout=15.0)

    def cancel_order(self, cancel_data: dict) -> dict:
        """Cancel order using Interactive API."""
        return self._delete('order.cancel', params=cancel_data, timeout=15.0)

    def get_orderbook(self, client_id: str = None) -> dict:
        """
        Get orderbook using regular endpoint.

        CRITICAL: For PRO accounts (isInvestorClient=False), clientID parameter is REQUIRED.
        Reference: xts_connect.py get_order_book() method (line 458-467)

        Endpoint: GET /interactive/orders

        Args:
            client_id: Client ID (REQUIRED for PRO accounts, optional for investor accounts)

        Returns:
            Orderbook data
        """
        params = {}
        if client_id:
            params['clientID'] = client_id
        return self._get('orders', params=params, timeout=15.0)

    def get_tradebook(self, client_id: str = None) -> dict:
        """
        Get tradebook using regular endpoint.

        Works for PRO accounts without dealer privileges.
        This was the original behavior before Task 24.1 refactoring.

        CRITICAL: For PRO accounts (isInvestorClient=False), clientID parameter is REQUIRED.
        Reference: xts_connect.py get_trade() method (line 718-728)

        Endpoint: GET /interactive/orders/trades

        Args:
            client_id: Client ID (REQUIRED for PRO accounts, optional for investor accounts)

        Returns:
            Tradebook data
        """
        params = {}
        if client_id:
            params['clientID'] = client_id
        return self._get('trades', params=params, timeout=15.0)

    def get_positions(self, client_id: str = None, day_or_net: str = "NetWise") -> dict:
        """
        Get positions using regular endpoint.

        CRITICAL: For PRO accounts (isInvestorClient=False), clientID parameter is REQUIRED.
        Reference: xts_connect.py get_position_netwise() method (line 795-803)

        Endpoint: GET /interactive/portfolio/positions

        Args:
            client_id: Client ID (REQUIRED for PRO accounts, optional for investor accounts)
            day_or_net: "DayWise" or "NetWise" (default: "NetWise")

        Returns:
            Positions data
        """
        params = {'dayOrNet': day_or_net}
        if client_id:
            params['clientID'] = client_id
        return self._get('portfolio.positions', params=params, timeout=15.0)

    def get_holdings(self, client_id: str = None) -> dict:
        """
        Get holdings using regular endpoint.

        CRITICAL: For PRO accounts (isInvestorClient=False), clientID parameter is REQUIRED.
        Reference: xts_connect.py get_holding() method (line 742-751)

        Endpoint: GET /interactive/portfolio/holdings

        Args:
            client_id: Client ID (REQUIRED for PRO accounts, optional for investor accounts)

        Returns:
            Holdings data
        """
        params = {}
        if client_id:
            params['clientID'] = client_id
        return self._get('portfolio.holdings', params=params, timeout=15.0)

    # ========================================================================
    # Dealer Endpoints (For Dealer accounts with special privileges)
    # These methods are available but require dealer account configuration
    # ========================================================================

    def get_dealer_orderbook(self, client_id: str) -> dict:
        """
        Get dealer orderbook (requires dealer privileges).

        Endpoint: GET /interactive/orders/dealerorderbook

        Args:
            client_id: Client ID to query

        Returns:
            Dealer orderbook data

        Raises:
            HTTPStatusError: If account doesn't have dealer privileges (HTTP 400)
        """
        return self._get('order.dealer.status', params={'clientID': client_id}, timeout=15.0)

    def get_dealer_tradebook(self, client_id: str) -> dict:
        """
        Get dealer tradebook (requires dealer privileges).

        Endpoint: GET /interactive/orders/dealertradebook

        Args:
            client_id: Client ID to query

        Returns:
            Dealer tradebook data

        Raises:
            HTTPStatusError: If account doesn't have dealer privileges (HTTP 400)
        """
        return self._get('dealer.trades', params={'clientID': client_id}, timeout=15.0)

    def get_dealer_positions(self, client_id: str, day_or_net: str = "NetWise") -> dict:
        """
        Get dealer positions (requires dealer privileges).

        Endpoint: GET /interactive/portfolio/dealerpositions

        Args:
            client_id: Client ID to query
            day_or_net: "DayWise" or "NetWise" (default: "NetWise")

        Returns:
            Dealer positions data

        Raises:
            HTTPStatusError: If account doesn't have dealer privileges (HTTP 400)
        """
        return self._get('portfolio.dealerpositions', params={'clientID': client_id, 'dayOrNet': day_or_net}, timeout=15.0)


# ============================================================================
# Legacy JainamAPI class (kept for backward compatibility)
# ============================================================================

class JainamAPI:
    """
    Jainam XTS Connect API wrapper (Legacy).

    Note: This class is kept for backward compatibility.
    New code should use OrderAPIClient instead.
    """

    def __init__(self):
        self.root_url = get_jainam_base_url()
        self.interactive_token = None
        self.market_token = None
        self.client = get_httpx_client()

    def _get_headers(self):
        """Get headers for API requests"""
        return {
            'Content-Type': 'application/json',
            'Authorization': self.interactive_token
        }

    def authenticate(self):
        """Authenticate with Jainam API"""
        try:
            from broker.jainam_prop.api.auth_api import authenticate_direct

            interactive_token, market_token, user_id, error = authenticate_direct()
            if error:
                logger.error(f"Jainam direct authentication failed: {error}")
                return False

            self.interactive_token = interactive_token
            self.market_token = market_token
            if user_id:
                logger.info(f"Authenticated Jainam session for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False

def place_order_api(data, auth_token):
    """
    Place order with Jainam.

    Refactored to use OrderAPIClient (Task 24.1).

    Args:
        data: MarvelQuant order data
        auth_token: Authentication token (JSON string with interactive_token and user_id)

    Returns:
        (response_object, response_data, order_id)
    """
    try:
        # Parse auth_token
        interactive_token, user_id = _parse_auth_token(auth_token)

        # Transform data to Jainam format
        jainam_order = transform_data(data)

        # Add client ID
        jainam_order['clientID'] = user_id

        # Use OrderAPIClient
        client = OrderAPIClient(auth_token=interactive_token)
        response_data = client.place_order(jainam_order)

        # Transform response to MarvelQuant format
        marvelquant_response = transform_response(response_data)

        # Create response object
        response_obj = SimpleNamespace(status=200)

        order_id = marvelquant_response.get('orderid', '')

        logger.info(f"Jainam order placed: {order_id}")
        return response_obj, marvelquant_response, order_id

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error placing Jainam order: {e}")
        response_obj = SimpleNamespace(status=e.response.status_code)
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return response_obj, response_data, None
    except Exception as e:
        logger.error(f"Error placing Jainam order: {e}")
        response_obj = SimpleNamespace(status=400)
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return response_obj, response_data, None

def modify_order_api(order_id, data, auth_token):
    """
    Modify existing order with Jainam.

    Refactored to use OrderAPIClient (Task 24.1).

    Args:
        order_id: Order ID to modify
        data: Modified order data
        auth_token: Authentication token

    Returns:
        (response_object, response_data, order_id)
    """
    try:
        # Parse auth_token
        interactive_token, user_id = _parse_auth_token(auth_token)

        # Transform data to Jainam format
        jainam_order = transform_data(data)
        jainam_order['appOrderID'] = int(order_id)
        jainam_order['clientID'] = user_id

        # Remove fields not needed for modification
        jainam_order.pop('exchangeSegment', None)
        jainam_order.pop('exchangeInstrumentID', None)
        jainam_order.pop('orderSide', None)

        # Use OrderAPIClient
        client = OrderAPIClient(auth_token=interactive_token)
        response_data = client.modify_order(jainam_order)

        marvelquant_response = transform_response(response_data)
        response_obj = SimpleNamespace(status=200)

        logger.info(f"Jainam order modified: {order_id}")
        return response_obj, marvelquant_response, order_id

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error modifying Jainam order: {e}")
        response_obj = SimpleNamespace(status=e.response.status_code)
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return response_obj, response_data, None
    except Exception as e:
        logger.error(f"Error modifying Jainam order: {e}")
        response_obj = SimpleNamespace(status=400)
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return response_obj, response_data, None

def cancel_order_api(order_id, auth_token):
    """
    Cancel order with Jainam.

    Refactored to use OrderAPIClient (Task 24.1).

    Args:
        order_id: Order ID to cancel
        auth_token: Authentication token

    Returns:
        (response_object, response_data)
    """
    try:
        # Parse auth_token
        interactive_token, user_id = _parse_auth_token(auth_token)

        # Request data
        cancel_data = {
            'appOrderID': int(order_id),
            'orderUniqueIdentifier': 'OPENALGO_PLATFORM'
        }

        # Use OrderAPIClient
        client = OrderAPIClient(auth_token=interactive_token)
        response_data = client.cancel_order(cancel_data)

        marvelquant_response = transform_response(response_data)
        response_obj = SimpleNamespace(status=200)

        logger.info(f"Jainam order cancelled: {order_id}")
        return response_obj, marvelquant_response

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error cancelling Jainam order: {e}")
        response_obj = SimpleNamespace(status=e.response.status_code)
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return response_obj, response_data
    except Exception as e:
        logger.error(f"Error cancelling Jainam order: {e}")
        response_obj = SimpleNamespace(status=400)
        response_data = {
            'status': 'error',
            'message': str(e)
        }
        return response_obj, response_data

def get_order_book(auth_token):
    """
    Get order book from Jainam

    Args:
        auth_token: Authentication token

    Returns:
        Order book data in Jainam format

    Example Response:
        {
            'status': 'success',
            'data': [
                {
                    'orderid': '123456',
                    'symbol': 'SBIN-EQ',
                    'exchange': 'NSE',
                    'action': 'BUY',
                    'quantity': 100,
                    'price': 550.50,
                    'status': 'COMPLETE'
                }
            ]
        }
    """
    try:
        # Parse auth_token
        interactive_token, user_id = _parse_auth_token(auth_token)

        logger.info(f"Fetching order book from Jainam for user {user_id}")

        # Use OrderAPIClient (regular endpoint for PRO accounts)
        # CRITICAL FIX: Do NOT pass clientID parameter for regular PRO accounts
        client = OrderAPIClient(auth_token=interactive_token)
        response_data = client.get_orderbook(client_id=None)

        # Check for error response
        if not isinstance(response_data, dict):
            logger.error("Unexpected response format received from Jainam order book API")
            return {
                'status': 'error',
                'message': 'Unexpected response format from Jainam order book API'
            }

        # Jainam/XTS payloads include a 'type' field to indicate success or error
        response_type = response_data.get('type')
        if response_type and response_type.lower() != 'success':
            error_message = (
                response_data.get('description')
                or response_data.get('message')
                or 'Jainam API reported an error while fetching orders'
            )
            error_code = response_data.get('code') or response_data.get('errorcode')

            # Check if this is a "Data Not Available" error (empty orderbook)
            if error_code and 'e-order' in error_code.lower() and 'data not available' in error_message.lower():
                logger.info("Jainam reported no order data available (empty orderbook)")
                return {
                    'status': 'success',
                    'data': []
                }

            error_payload = {
                'status': 'error',
                'message': error_message
            }
            if error_code:
                error_payload['code'] = error_code
            logger.error(f"Jainam order book returned error payload: {error_message}")
            return error_payload

        # Extract order data from either 'result' or 'data' key
        order_data = response_data.get('result', response_data.get('data', []))

        # Handle empty order book
        if not response_data or not order_data:
            logger.info("Order book is empty")
            return {
                'status': 'success',
                'data': []
            }

        logger.info(f"Order book retrieved successfully with {len(order_data) if isinstance(order_data, list) else 'unknown'} orders")
        return response_data

    except httpx.HTTPStatusError as e:
        # Handle "Data Not Available" as a success case with empty data
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_code = error_data.get('code', '')
                description = error_data.get('description', '').lower()

                # Jainam returns error codes with "Data Not Available" when no orders exist
                if 'data not available' in description:
                    logger.info("Jainam reported no order data available (empty orderbook)")
                    return {
                        'status': 'success',
                        'data': []
                    }
            except:
                pass  # If we can't parse the error, fall through to generic error handling

        logger.error(f"HTTP error getting Jainam order book: {e.response.status_code} - {e.response.text}")
        return {
            'status': 'error',
            'message': f'HTTP error: {e.response.status_code}'
        }
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error getting Jainam order book: {e}")
        return {
            'status': 'error',
            'message': 'Request timeout - please try again'
        }
    except httpx.RequestError as e:
        logger.error(f"Connection error getting Jainam order book: {e}")
        return {
            'status': 'error',
            'message': 'Connection error - please check network'
        }
    except Exception as e:
        logger.error(f"Unexpected error getting Jainam order book: {e}")
        return {
            'status': 'error',
            'message': f'Error retrieving order book: {str(e)}'
        }

def get_positions(auth_token):
    """
    Get current positions from Jainam (NetWise)

    Args:
        auth_token: Authentication token (string or dict)

    Returns:
        dict: Position data in Jainam format

    Example Response:
        {
            'status': 'success',
            'data': [
                {
                    'symbol': 'SBIN-EQ',
                    'exchange': 'NSE',
                    'product': 'MIS',
                    'quantity': 100,
                    'averagePrice': 550.50,
                    'ltp': 552.00,
                    'pnl': 150.00
                }
            ]
        }
    """
    try:
        # Parse auth_token
        interactive_token, user_id = _parse_auth_token(auth_token)

        logger.info(f"Fetching positions from Jainam for user {user_id}")

        # Use OrderAPIClient (regular endpoint for PRO accounts)
        # CRITICAL FIX: Do NOT pass clientID parameter for regular PRO accounts
        client = OrderAPIClient(auth_token=interactive_token)
        response_data = client.get_positions(client_id=None, day_or_net="NetWise")

        logger.info(f"Positions retrieved successfully")
        return response_data

    except httpx.HTTPStatusError as e:
        # Handle "Data Not Available" as a success case with empty data
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_code = error_data.get('code', '')
                description = error_data.get('description', '').lower()

                # Jainam returns "e-portfolio-0005" with "Data Not Available" when no positions exist
                if 'e-portfolio-0005' in error_code.lower() or 'data not available' in description:
                    logger.info("Jainam reported no position data available (empty positions)")
                    return {
                        'status': 'success',
                        'data': []
                    }
            except:
                pass  # If we can't parse the error, fall through to generic error handling

        logger.error(f"HTTP error getting Jainam positions: {e.response.status_code} - {e.response.text}")
        return {
            'status': 'error',
            'message': f'HTTP error: {e.response.status_code}'
        }
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error getting Jainam positions: {e}")
        return {
            'status': 'error',
            'message': 'Request timeout - please try again'
        }
    except httpx.RequestError as e:
        logger.error(f"Connection error getting Jainam positions: {e}")
        return {
            'status': 'error',
            'message': 'Connection error - please check network'
        }
    except Exception as e:
        logger.error(f"Unexpected error getting Jainam positions: {e}")
        return {
            'status': 'error',
            'message': f'Error retrieving positions: {str(e)}'
        }

def get_holdings(auth_token):
    """
    Get long-term holdings from Jainam

    Args:
        auth_token: Authentication token (string or dict)

    Returns:
        dict: Holdings data in Jainam format

    Example Response:
        {
            'status': 'success',
            'data': [
                {
                    'symbol': 'RELIANCE-EQ',
                    'exchange': 'NSE',
                    'quantity': 50,
                    'averagePrice': 2400.00,
                    'ltp': 2450.00,
                    'pnl': 2500.00
                }
            ]
        }
    """
    try:
        # Parse auth_token
        interactive_token, user_id = _parse_auth_token(auth_token)

        logger.info(f"Fetching holdings from Jainam for user {user_id}")

        # Use OrderAPIClient (regular endpoint for PRO accounts)
        # CRITICAL FIX: Do NOT pass clientID parameter for regular PRO accounts
        client = OrderAPIClient(auth_token=interactive_token)
        response_data = client.get_holdings(client_id=None)

        logger.info(f"Holdings retrieved successfully")
        return response_data

    except httpx.HTTPStatusError as e:
        # Handle "Data Not Available" as a success case with empty data
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_code = error_data.get('code', '')
                description = error_data.get('description', '').lower()

                # Jainam returns error codes with "Data Not Available" when no holdings exist
                if 'data not available' in description:
                    logger.info("Jainam reported no holdings data available (empty holdings)")
                    return {
                        'status': 'success',
                        'data': []
                    }
            except:
                pass  # If we can't parse the error, fall through to generic error handling

        # Handle HTTP 500 errors (server-side issues on Jainam's API)
        if e.response.status_code == 500:
            logger.error(f"Jainam holdings API server error (HTTP 500). This is a server-side issue on Jainam's API.")
            logger.error(f"Response body (first 500 chars): {e.response.text[:500]}")
            return {
                'status': 'error',
                'message': 'Jainam API server error. The holdings endpoint is currently unavailable. Please try again later or contact Jainam support.',
                'code': 'JAINAM_SERVER_ERROR'
            }

        logger.error(f"HTTP error getting Jainam holdings: {e.response.status_code} - {e.response.text[:500]}")
        return {
            'status': 'error',
            'message': f'HTTP error: {e.response.status_code}'
        }
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error getting Jainam holdings: {e}")
        return {
            'status': 'error',
            'message': 'Request timeout - please try again'
        }
    except httpx.RequestError as e:
        logger.error(f"Connection error getting Jainam holdings: {e}")
        return {
            'status': 'error',
            'message': 'Connection error - please check network'
        }
    except Exception as e:
        logger.error(f"Unexpected error getting Jainam holdings: {e}")
        return {
            'status': 'error',
            'message': f'Error retrieving holdings: {str(e)}'
        }

def get_trade_book(auth_token):
    """
    Get executed trades from Jainam

    Args:
        auth_token: Authentication token (string or dict)

    Returns:
        dict: Trade book data transformed to MarvelQuant format using transform_trade_book()

    Example Response:
        {
            'status': 'success',
            'trades': [
                {
                    'orderid': '123456',
                    'trade_id': 'T001',
                    'symbol': 'SBIN-EQ',
                    'exchange': 'NSE',
                    'action': 'BUY',
                    'quantity': 100,
                    'price': 550.50,
                    'trade_timestamp': '2025-10-07T10:15:30',
                    'exchange_trade_id': 'EXT001'
                }
            ]
        }
    """
    try:
        # Parse auth_token
        interactive_token, user_id = _parse_auth_token(auth_token)

        logger.info(f"Fetching trade book from Jainam for user {user_id}")

        # Use OrderAPIClient (regular endpoint for PRO accounts)
        # CRITICAL FIX: Do NOT pass clientID parameter for regular PRO accounts
        # The reference implementation is designed for dealer accounts, not regular PRO accounts
        # Passing clientID causes "Supplied client not mapped under dealer" error (e-trade-00002)
        # Without clientID, we get "Data Not Available" (e-tradeBook-0005) when no trades exist - this is correct!
        client = OrderAPIClient(auth_token=interactive_token)
        response_data = client.get_tradebook(client_id=None)

        # DEBUG: Log the actual response to diagnose empty tradebook issue
        logger.info(f"Tradebook API response type: {response_data.get('type') if isinstance(response_data, dict) else type(response_data)}")
        logger.info(f"Tradebook API response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'N/A'}")
        logger.info(f"Tradebook API response (first 500 chars): {str(response_data)[:500]}")

        if not isinstance(response_data, dict):
            logger.error("Unexpected response format received from Jainam trade book API")
            return {
                'status': 'error',
                'message': 'Unexpected response format from Jainam trade book API'
            }

        # Jainam/XTS payloads include a 'type' field to indicate success or error
        response_type = response_data.get('type')
        if response_type and response_type.lower() != 'success':
            error_message = (
                response_data.get('description')
                or response_data.get('message')
                or 'Jainam API reported an error while fetching trades'
            )
            error_payload = {
                'status': 'error',
                'message': error_message
            }
            error_code = response_data.get('code') or response_data.get('errorcode')
            if error_code:
                error_payload['code'] = error_code
            logger.error(f"Jainam trade book returned error payload: {error_message}")
            return error_payload

        # Extract trade data from either 'result' or 'data' key (Jainam/XTS uses 'result')
        trade_data = response_data.get('result', response_data.get('data', []))

        # DEBUG: Log trade data extraction
        logger.info(f"Extracted trade_data type: {type(trade_data)}, length: {len(trade_data) if isinstance(trade_data, (list, dict)) else 'N/A'}")
        if trade_data:
            logger.info(f"First trade data item: {trade_data[0] if isinstance(trade_data, list) and len(trade_data) > 0 else trade_data}")

        # Handle empty trade book (return empty list)
        if not response_data or not trade_data:
            logger.info(f"Trade book is empty - response_data: {bool(response_data)}, trade_data: {bool(trade_data)}")
            return {
                'status': 'success',
                'trades': []
            }

        # Transform response using transform_tradebook_data from mapping/order_data.py
        # Note: Function name is transform_tradebook_data, not transform_trade_book
        from broker.jainam_prop.mapping.order_data import transform_tradebook_data
        transformed_data = transform_tradebook_data(trade_data)

        logger.info(f"Trade book retrieved successfully with {len(transformed_data.get('trades', []))} trades")
        return transformed_data

    except httpx.HTTPStatusError as e:
        # DEBUG: Log the HTTP error details
        logger.info(f"HTTPStatusError caught - Status: {e.response.status_code}, Response: {e.response.text[:500]}")

        # Handle "Data Not Available" as a success case with empty data
        if e.response.status_code == 400:
            try:
                error_data = e.response.json()
                error_code = error_data.get('code', '')
                description = error_data.get('description', '').lower()

                # DEBUG: Log the error details
                logger.info(f"HTTP 400 error - Code: {error_code}, Description: {description}")

                # Jainam returns "e-tradeBook-0005" with "Data Not Available" when no trades exist
                if 'e-tradebook-0005' in error_code.lower() or 'data not available' in description:
                    logger.info("Jainam reported no trade data available (empty tradebook)")
                    return {
                        'status': 'success',
                        'trades': []
                    }
            except Exception as parse_error:
                logger.error(f"Failed to parse HTTP 400 error response: {parse_error}")
                pass  # If we can't parse the error, fall through to generic error handling

        logger.error(f"HTTP error getting Jainam trade book: {e.response.status_code} - {e.response.text}")
        return {
            'status': 'error',
            'message': f'HTTP error: {e.response.status_code}'
        }
    except httpx.TimeoutException as e:
        logger.error(f"Timeout error getting Jainam trade book: {e}")
        return {
            'status': 'error',
            'message': 'Request timeout - please try again'
        }
    except httpx.RequestError as e:
        logger.error(f"Connection error getting Jainam trade book: {e}")
        return {
            'status': 'error',
            'message': 'Connection error - please check network'
        }
    except Exception as e:
        logger.error(f"Unexpected error getting Jainam trade book: {e}")
        return {
            'status': 'error',
            'message': f'Error retrieving trade book: {str(e)}'
        }


def place_smartorder_api(data, auth_token):
    """
    Place a smart order to reach the desired position size.

    Args:
        data (dict): Incoming smart order payload (must contain position_size)
        auth_token: Authentication token for Jainam broker

    Returns:
        tuple: (response_object, response_data, order_id)
    """
    start_time = time.perf_counter()
    symbol_for_logging = data.get('symbol') if isinstance(data, dict) else None

    def _finalize(result_tuple, outcome_label):
        duration = time.perf_counter() - start_time
        latency_status = (
            'within_threshold'
            if duration < SMART_ORDER_LATENCY_THRESHOLD_SECONDS
            else 'exceeded_threshold'
        )
        log_fn = logger.info if latency_status == 'within_threshold' else logger.warning
        log_message = (
            "Smart order %s - symbol=%s duration=%.3fs (threshold=%ss, status=%s)"
            % (
                outcome_label,
                symbol_for_logging or 'UNKNOWN',
                duration,
                SMART_ORDER_LATENCY_THRESHOLD_SECONDS,
                latency_status,
            )
        )
        log_fn(log_message)

        res_obj, response_data, order_id = result_tuple
        if isinstance(response_data, dict):
            response_data.setdefault('latency_seconds', round(duration, 3))
            response_data.setdefault('latency_threshold_seconds', SMART_ORDER_LATENCY_THRESHOLD_SECONDS)
            response_data.setdefault('latency_status', latency_status)
        return res_obj, response_data, order_id

    def _error_response(message, outcome_label):
        logger.error(message)
        return _finalize((None, {'status': 'error', 'message': message}, None), outcome_label)

    def _parse_whole_number(value, field_name):
        try:
            if isinstance(value, int):
                return value
            if isinstance(value, float):
                if value.is_integer():
                    return int(value)
                raise ValueError(f"{field_name} must be a whole number")
            if value is None:
                raise ValueError(f"{field_name} is required")
            decimal_value = Decimal(str(value))
            if decimal_value != decimal_value.to_integral_value():
                raise ValueError(f"{field_name} must be a whole number")
            return int(decimal_value)
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {field_name}: {value}") from exc

    try:
        if not isinstance(data, dict):
            return _error_response('Order payload must be a dictionary', 'invalid_payload')

        required_fields = ['symbol', 'exchange', 'product', 'position_size']
        missing_fields = [field for field in required_fields if field not in data or data[field] in (None, '')]
        if missing_fields:
            error_msg = f"Missing required field(s): {', '.join(missing_fields)}"
            logger.error(error_msg)
            return _finalize((None, {'status': 'error', 'message': error_msg}, None), 'validation_failed')

        symbol = data.get('symbol')
        exchange = data.get('exchange')
        product = data.get('product')
        symbol_for_logging = symbol or symbol_for_logging

        try:
            target_position = _parse_whole_number(data.get('position_size'), 'position_size')
        except ValueError as exc:
            logger.error(f"Invalid position_size provided: {exc}")
            return _finalize((None, {'status': 'error', 'message': str(exc)}, None), 'invalid_target')

        try:
            current_qty_raw = get_open_position(symbol, exchange, product, auth_token)
        except Exception as exc:
            logger.error(f"Failed to retrieve current position for smart order: {exc}", exc_info=True)
            return _finalize((None, {'status': 'error', 'message': 'Failed to fetch current position'}, None), 'position_lookup_failed')

        try:
            current_position = _parse_whole_number(current_qty_raw, 'current position')
        except ValueError as exc:
            logger.error(f"Invalid current position value returned: {exc}")
            return _finalize((None, {'status': 'error', 'message': 'Invalid current position data'}, None), 'invalid_position_data')

        delta = target_position - current_position
        logger.info(
            "Smart order calculation - symbol=%s exchange=%s product=%s target=%d current=%d delta=%d",
            symbol,
            exchange,
            product,
            target_position,
            current_position,
            delta
        )

        if delta == 0:
            message = "No action needed: current position already matches target"
            logger.info("Smart order no-op - %s", message)
            return _finalize((None, {'status': 'success', 'message': message, 'orderid': ''}, ''), 'no_action_needed')

        action = 'BUY' if delta > 0 else 'SELL'
        quantity = abs(delta)

        logger.info(
            "Smart order action - symbol=%s action=%s quantity=%d target=%d current=%d delta=%d",
            symbol,
            action,
            quantity,
            target_position,
            current_position,
            delta
        )

        order_payload = data.copy()
        order_payload['action'] = action
        order_payload['quantity'] = str(quantity)

        # Update the original payload so downstream logging has final action/quantity
        data['action'] = action
        data['quantity'] = str(quantity)

        try:
            res, response_data, order_id = place_order_api(order_payload, auth_token)
        except Exception as exc:
            logger.error(f"Error while placing smart order: {exc}", exc_info=True)
            return _finalize((None, {'status': 'error', 'message': f'Order placement failed: {str(exc)}'}, None), 'order_failed')
        if not isinstance(response_data, dict):
            logger.error(
                "Invalid response type from place_order_api for smart order: %s",
                type(response_data).__name__
            )
            return _finalize((None, {'status': 'error', 'message': 'Invalid response from order placement'}, None), 'invalid_order_response')

        if response_data.get('status') == 'success' and order_id:
            response_data.setdefault('orderid', order_id)

        return _finalize((res, response_data, order_id), 'order_complete')

    except Exception as exc:
        logger.error(f"Unhandled error in place_smartorder_api: {exc}", exc_info=True)
        return _finalize(
            (None, {'status': 'error', 'message': f'Smart order failed: {str(exc)}'}, None),
            'unhandled_exception'
        )

def get_open_position(tradingsymbol, exchange, producttype, auth_token):
    """
    Get the net quantity for a specific symbol from positions

    This function is used by smart order placement to calculate position delta
    and determine order action/quantity. It filters positions by exact symbol,
    exchange, and product type match.

    Args:
        tradingsymbol (str): Trading symbol in MarvelQuant format (e.g., 'SBIN-EQ')
        exchange (str): Exchange code (e.g., 'NSE', 'BSE')
        producttype (str): Product type (e.g., 'CNC', 'MIS', 'NRML')
        auth_token: Authentication token (string or dict)

    Returns:
        str: Net quantity as string (e.g., "100" for long, "-50" for short, "0" for flat/not found)

    Notes:
        - Returns "0" if position not found or if get_positions() fails
        - Matches Jainam/XTS API field names: TradingSymbol, ExchangeSegment, ProductType
        - Logs all lookup attempts for debugging smart order placement
        - Execution time target: <5 seconds (depends on get_positions() API call)
    """
    start_time = time.perf_counter()

    def _finish(value, detail):
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"Position lookup completed in {duration_ms:.2f} ms - {detail}")
        return value

    try:
        # Log position lookup request
        logger.info(f"Position lookup: symbol={tradingsymbol}, exchange={exchange}, product={producttype}")

        # Get all positions from Jainam API
        positions_data = get_positions(auth_token)

        if positions_data is None:
            logger.error("get_positions() returned no data during position lookup")
            return _finish('0', 'no data returned')

        if isinstance(positions_data, dict):
            if positions_data.get('status') == 'error':
                error_msg = positions_data.get('message', 'Unknown error')
                logger.error(f"get_positions() failed during position lookup: {error_msg}")
                return _finish('0', 'error status from get_positions')
        elif not isinstance(positions_data, list):
            payload_type = type(positions_data).__name__
            logger.error(f"get_positions() returned unsupported payload type: {payload_type}")
            return _finish('0', f'unexpected payload type: {payload_type}')

        # Extract position list from response (Jainam/XTS uses 'result' key)
        # Response structure: {'type': 'success', 'result': [position_objects]}
        position_list = []
        if isinstance(positions_data, dict):
            # Check if response has 'result' key (XTS format)
            if 'result' in positions_data:
                result = positions_data['result']
                # Result could be list or dict with nested list
                if isinstance(result, list):
                    position_list = result
                elif isinstance(result, dict) and 'positions' in result:
                    position_list = result['positions']
            # Fallback to 'data' key (alternative format)
            elif 'data' in positions_data:
                data = positions_data['data']
                if isinstance(data, list):
                    position_list = data
                elif isinstance(data, dict) and 'positions' in data:
                    position_list = data['positions']
        elif isinstance(positions_data, list):
            # Direct list response
            position_list = positions_data

        if not position_list:
            logger.info(f"No positions found in position book")
            return _finish('0', 'no positions available')

        logger.info(f"Searching through {len(position_list)} positions for exact match")

        # Search for matching position with exact symbol, exchange, and product type
        for position in position_list:
            # Extract position fields (handle different possible field names)
            pos_symbol = position.get('TradingSymbol') or position.get('tradingsymbol') or position.get('symbol', '')
            pos_exchange = position.get('ExchangeSegment') or position.get('exchange') or position.get('exch', '')
            pos_product = position.get('ProductType') or position.get('producttype') or position.get('product', '')

            # Normalize exchange comparison (XTS uses segments like 'NSECM' for NSE Cash Market)
            # Convert NSE -> NSECM, BSE -> BSECM, etc. for comparison
            exchange_normalized = exchange
            if exchange == 'NSE':
                exchange_normalized = 'NSECM'
            elif exchange == 'BSE':
                exchange_normalized = 'BSECM'
            elif exchange == 'NFO':
                exchange_normalized = 'NSEFO'
            elif exchange == 'MCX':
                exchange_normalized = 'MCXFO'

            # Check for exact match (support both formats)
            if (pos_symbol == tradingsymbol and
                (pos_exchange == exchange or pos_exchange == exchange_normalized) and
                pos_product == producttype):

                # Extract net quantity (try multiple field names)
                net_qty = (position.get('NetQty') or
                          position.get('netQty') or
                          position.get('netqty') or
                          position.get('Quantity') or
                          position.get('quantity') or
                          '0')

                # Ensure return value is string
                net_qty_str = str(net_qty)

                logger.info(f"Position found: symbol={pos_symbol}, exchange={pos_exchange}, product={pos_product}, netqty={net_qty_str}")
                return _finish(net_qty_str, 'position matched')

        # Position not found
        logger.info(f"Position not found for symbol={tradingsymbol}, exchange={exchange}, product={producttype}")
        return _finish('0', 'position not found')

    except Exception as e:
        logger.error(f"Error in get_open_position: {e}", exc_info=True)
        return _finish('0', 'exception encountered')
