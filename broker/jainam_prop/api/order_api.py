import json
import time
from decimal import Decimal, InvalidOperation
import httpx
from types import SimpleNamespace
from database.auth_db import get_auth_token
from broker.jainam_prop.mapping.transform_data import transform_data, transform_response
from broker.jainam_prop.api.config import get_jainam_base_url
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

logger = get_logger(__name__)

SMART_ORDER_LATENCY_THRESHOLD_SECONDS = 10.0

class JainamAPI:
    """Jainam XTS Connect API wrapper"""

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
    Place order with Jainam

    Args:
        data: OpenAlgo order data
        auth_token: Authentication token

    Returns:
        (response_object, response_data, order_id)
    """
    try:
        # Parse auth_token to get API credentials
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'token': auth_token}
        else:
            credentials = auth_token

        # Initialize Jainam API
        jainam_api = JainamAPI()
        jainam_api.interactive_token = credentials.get('token', auth_token)

        # Transform data to Jainam format
        jainam_order = transform_data(data)

        # Add client ID from user profile (this should be passed or retrieved)
        jainam_order['clientID'] = credentials.get('client_id', 'DEFAULT_USER')

        # API endpoint
        url = f"{jainam_api.root_url}/interactive/orders"

        # Make API request
        response = jainam_api.client.post(
            url,
            headers=jainam_api._get_headers(),
            json=jainam_order
        )

        response_data = response.json()

        # Transform response to OpenAlgo format
        openalgo_response = transform_response(response_data)

        # Create response object
        response_obj = SimpleNamespace(status=response.status_code)

        order_id = openalgo_response.get('orderid', '')

        logger.info(f"Jainam order placed: {order_id}")
        return response_obj, openalgo_response, order_id

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
    Modify existing order with Jainam

    Args:
        order_id: Order ID to modify
        data: Modified order data
        auth_token: Authentication token

    Returns:
        (response_object, response_data, order_id)
    """
    try:
        # Parse auth_token
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'token': auth_token}
        else:
            credentials = auth_token

        jainam_api = JainamAPI()
        jainam_api.interactive_token = credentials.get('token', auth_token)

        # Transform data to Jainam format
        jainam_order = transform_data(data)
        jainam_order['appOrderID'] = int(order_id)
        jainam_order['clientID'] = credentials.get('client_id', 'DEFAULT_USER')

        # Remove fields not needed for modification
        jainam_order.pop('exchangeSegment', None)
        jainam_order.pop('exchangeInstrumentID', None)
        jainam_order.pop('orderSide', None)

        # API endpoint
        url = f"{jainam_api.root_url}/interactive/orders"

        # Make PUT request for modification
        response = jainam_api.client.put(
            url,
            headers=jainam_api._get_headers(),
            json=jainam_order
        )

        response_data = response.json()
        openalgo_response = transform_response(response_data)

        response_obj = SimpleNamespace(status=response.status_code)

        logger.info(f"Jainam order modified: {order_id}")
        return response_obj, openalgo_response, order_id

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
    Cancel order with Jainam

    Args:
        order_id: Order ID to cancel
        auth_token: Authentication token

    Returns:
        (response_object, response_data)
    """
    try:
        # Parse auth_token
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'token': auth_token}
        else:
            credentials = auth_token

        jainam_api = JainamAPI()
        jainam_api.interactive_token = credentials.get('token', auth_token)

        # API endpoint
        url = f"{jainam_api.root_url}/interactive/orders"

        # Request data
        cancel_data = {
            'appOrderID': int(order_id),
            'orderUniqueIdentifier': 'OPENALGO_PLATFORM'
        }

        # Make DELETE request
        response = jainam_api.client.request(
            'DELETE',
            url,
            headers=jainam_api._get_headers(),
            json=cancel_data
        )

        response_data = response.json()
        openalgo_response = transform_response(response_data)

        response_obj = SimpleNamespace(status=response.status_code)

        logger.info(f"Jainam order cancelled: {order_id}")
        return response_obj, openalgo_response

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
        Order book data
    """
    try:
        # Parse auth_token
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'token': auth_token}
        else:
            credentials = auth_token

        jainam_api = JainamAPI()
        jainam_api.interactive_token = credentials.get('token', auth_token)

        # API endpoint
        url = f"{jainam_api.root_url}/interactive/orders"

        # Make GET request
        response = jainam_api.client.get(
            url,
            headers=jainam_api._get_headers()
        )

        return response.json()

    except Exception as e:
        logger.error(f"Error getting Jainam order book: {e}")
        return {'status': 'error', 'message': str(e)}

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
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'token': auth_token}
        else:
            credentials = auth_token

        # Initialize Jainam API
        jainam_api = JainamAPI()
        jainam_api.interactive_token = credentials.get('token', auth_token)

        # API endpoint with NetWise parameter (as per XTS API and story requirements)
        url = f"{jainam_api.root_url}/interactive/portfolio/positions?dayOrNet=NetWise"

        logger.info(f"Fetching positions from Jainam: {url}")

        # Make GET request with 10-second timeout
        response = jainam_api.client.get(
            url,
            headers=jainam_api._get_headers(),
            timeout=10.0
        )

        response.raise_for_status()
        response_data = response.json()

        logger.info(f"Positions retrieved successfully")
        return response_data

    except httpx.HTTPStatusError as e:
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
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'token': auth_token}
        else:
            credentials = auth_token

        # Initialize Jainam API
        jainam_api = JainamAPI()
        jainam_api.interactive_token = credentials.get('token', auth_token)

        # API endpoint (as per XTS API)
        url = f"{jainam_api.root_url}/interactive/portfolio/holdings"

        logger.info(f"Fetching holdings from Jainam: {url}")

        # Make GET request with 10-second timeout
        response = jainam_api.client.get(
            url,
            headers=jainam_api._get_headers(),
            timeout=10.0
        )

        response.raise_for_status()
        response_data = response.json()

        logger.info(f"Holdings retrieved successfully")
        return response_data

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error getting Jainam holdings: {e.response.status_code} - {e.response.text}")
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
        dict: Trade book data transformed to OpenAlgo format using transform_trade_book()

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
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'token': auth_token}
        else:
            credentials = auth_token

        # Initialize Jainam API
        jainam_api = JainamAPI()
        jainam_api.interactive_token = credentials.get('token', auth_token)

        # API endpoint for trade book (as per XTS API pattern)
        url = f"{jainam_api.root_url}/interactive/trades"

        logger.info(f"Fetching trade book from Jainam: {url}")

        # Make GET request with 10-second timeout
        response = jainam_api.client.get(
            url,
            headers=jainam_api._get_headers(),
            timeout=10.0
        )

        response.raise_for_status()
        response_data = response.json()

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

        # Handle empty trade book (return empty list)
        if not response_data or not trade_data:
            logger.info("Trade book is empty")
            return {
                'status': 'success',
                'trades': []
            }

        # Transform response using transform_trade_book from mapping/order_data.py
        from broker.jainam_prop.mapping.order_data import transform_trade_book
        transformed_data = transform_trade_book(trade_data)

        logger.info(f"Trade book retrieved successfully with {len(transformed_data.get('trades', []))} trades")
        return transformed_data

    except httpx.HTTPStatusError as e:
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
        tradingsymbol (str): Trading symbol in OpenAlgo format (e.g., 'SBIN-EQ')
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
