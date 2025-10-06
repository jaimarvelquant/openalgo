import os
import json
from database.auth_db import upsert_broker_token
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

logger = get_logger(__name__)

def authenticate_broker(request_token):
    """
    Authenticate with Jainam XTS Connect API

    Args:
        request_token (str): Request token from OAuth flow

    Returns:
        tuple: (access_token, error_message)
    """
    try:
        # Fetching the necessary credentials from environment variables
        interactive_api_key = os.getenv('BROKER_API_KEY')  # Interactive API Key
        interactive_api_secret = os.getenv('BROKER_API_SECRET')  # Interactive API Secret

        # Jainam XTS Connect root URL
        root_url = "http://ctrade.jainam.in:3000"

        # Generate checksum for authentication
        import hashlib
        checksum_input = f"{interactive_api_key}{request_token}{interactive_api_secret}"
        checksum = hashlib.sha256(checksum_input.encode()).hexdigest()

        # Authentication payload
        data = {
            'api_key': interactive_api_key,
            'request_token': request_token,
            'checksum': checksum
        }

        # Get the shared httpx client
        client = get_httpx_client()

        # Authentication endpoint
        url = f"{root_url}/interactive/user/session"
        headers = {'X-Kite-Version': '3'}

        try:
            response = client.post(url, headers=headers, data=data)
            response.raise_for_status()

            response_data = response.json()
            if 'data' in response_data and 'access_token' in response_data['data']:
                access_token = response_data['data']['access_token']
                logger.info("Jainam authentication successful")
                return access_token, None
            else:
                return None, "Authentication succeeded but no access token was returned"
        except Exception as e:
            error_message = str(e)
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_detail = e.response.json()
                    error_message = error_detail.get('message', str(e))
            except:
                pass
            return None, f"API error: {error_message}"
    except Exception as e:
        return None, f"An exception occurred: {str(e)}"

def authenticate_market_data():
    """
    Authenticate market data session with Jainam

    Returns:
        tuple: (market_token, error_message)
    """
    try:
        # Fetching market data credentials
        market_api_key = os.getenv('BROKER_API_KEY_MARKET')
        market_api_secret = os.getenv('BROKER_API_SECRET_MARKET')

        root_url = "http://ctrade.jainam.in:3000"

        # Get the shared httpx client
        client = get_httpx_client()

        # Market data authentication endpoint
        url = f"{root_url}/apimarketdata/auth/login"
        data = {
            'appKey': market_api_key,
            'secretKey': market_api_secret,
            'source': 'WEBAPI'
        }

        try:
            response = client.post(url, json=data)
            response.raise_for_status()

            response_data = response.json()
            if 'result' in response_data and 'token' in response_data['result']:
                market_token = response_data['result']['token']
                logger.info("Jainam market data authentication successful")
                return market_token, None
            else:
                return None, "Market data authentication succeeded but no token was returned"
        except Exception as e:
            error_message = str(e)
            try:
                if hasattr(e, 'response') and e.response is not None:
                    error_detail = e.response.json()
                    error_message = error_detail.get('message', str(e))
            except:
                pass
            return None, f"Market data API error: {error_message}"
    except Exception as e:
        return None, f"An exception occurred: {str(e)}"
