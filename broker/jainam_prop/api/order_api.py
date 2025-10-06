import json
import os
from types import SimpleNamespace
from database.auth_db import get_auth_token
from broker.jainam_prop.mapping.transform_data import transform_data, transform_response
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

logger = get_logger(__name__)

class JainamAPI:
    """Jainam XTS Connect API wrapper"""

    def __init__(self):
        self.root_url = "http://ctrade.jainam.in:3000"
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
            from broker.jainam_prop.api.auth_api import authenticate_broker, authenticate_market_data

            # Authenticate interactive session
            interactive_token, error = authenticate_broker("dummy_request_token")  # This needs proper OAuth flow
            if error:
                logger.error(f"Interactive authentication failed: {error}")
                return False

            # Authenticate market data session
            market_token, error = authenticate_market_data()
            if error:
                logger.error(f"Market data authentication failed: {error}")
                return False

            self.interactive_token = interactive_token
            self.market_token = market_token
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
