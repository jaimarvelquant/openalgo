import json
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client
from broker.jainam_prop.api.config import get_jainam_base_url

logger = get_logger(__name__)

def get_margin_data(auth_token):
    """
    Get margin/funds data from Jainam

    Args:
        auth_token: Authentication token

    Returns:
        Margin data in OpenAlgo format
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

        interactive_token = credentials.get('token', auth_token)
        root_url = get_jainam_base_url()

        # API endpoint for balance
        url = f"{root_url}/interactive/user/balance"

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': interactive_token
        }

        # Make request
        client = get_httpx_client()
        response = client.get(url, headers=headers)
        response_data = response.json()

        if response_data.get('type') == 'success' and 'result' in response_data:
            balance_data = response_data['result']

            # Transform to OpenAlgo format
            margin_data = {
                'availablecash': float(balance_data.get('AvailableMargin', 0)),
                'collateral': float(balance_data.get('Collateral', 0)),
                'buyingpower': float(balance_data.get('BuyingPower', 0)),
                'usedmargin': float(balance_data.get('UsedMargin', 0)),
                'totalmargin': float(balance_data.get('TotalMargin', 0))
            }

            logger.info("Jainam margin data retrieved successfully")
            return margin_data

        else:
            logger.error(f"Failed to get Jainam margin data: {response_data.get('description', 'Unknown error')}")
            return {
                'status': 'error',
                'message': response_data.get('description', 'Failed to get margin data')
            }

    except Exception as e:
        logger.error(f"Error getting Jainam margin data: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def get_profile(auth_token):
    """
    Get user profile from Jainam

    Args:
        auth_token: Authentication token

    Returns:
        User profile data
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

        interactive_token = credentials.get('token', auth_token)
        root_url = get_jainam_base_url()

        # API endpoint for profile
        url = f"{root_url}/interactive/user/profile"

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': interactive_token
        }

        # Make request
        client = get_httpx_client()
        response = client.get(url, headers=headers)
        response_data = response.json()

        if response_data.get('type') == 'success' and 'result' in response_data:
            profile_data = response_data['result']

            # Transform to OpenAlgo format
            profile = {
                'client_id': profile_data.get('clientID', ''),
                'name': profile_data.get('clientName', ''),
                'email': profile_data.get('email', ''),
                'mobile': profile_data.get('mobile', ''),
                'status': profile_data.get('status', ''),
                'segment': profile_data.get('segment', '')
            }

            return profile

        else:
            return {
                'status': 'error',
                'message': response_data.get('description', 'Failed to get profile')
            }

    except Exception as e:
        logger.error(f"Error getting Jainam profile: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }
