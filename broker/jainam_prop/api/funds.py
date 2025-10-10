import json
from typing import Optional

import httpx
from flask import session
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client
from broker.jainam_prop.api.config import get_jainam_base_url
from broker.jainam_prop.api.base_client import BaseAPIClient

logger = get_logger(__name__)


# ============================================================================
# API Client Class (Task 24.1 - Refactored to use BaseAPIClient)
# ============================================================================

class FundsAPIClient(BaseAPIClient):
    """
    Client for Jainam Interactive API funds/balance operations.

    Refactored to use BaseAPIClient (Task 24.1).
    """

    def __init__(self, auth_token: str, base_url: str = None):
        """
        Initialize Funds API client.

        Args:
            auth_token: Interactive API token
            base_url: Jainam API base URL (optional)
        """
        super().__init__(base_url=base_url, auth_token=auth_token)

    def get_balance(self, client_id: Optional[str] = None) -> dict:
        """Get balance/funds data."""
        params = {'clientID': client_id} if client_id else {}
        return self._get('user.balance', params=params, timeout=10.0)

    def get_profile(self, client_id: Optional[str] = None) -> dict:
        """Get user profile."""
        params = {'clientID': client_id} if client_id else {}
        return self._get('user.profile', params=params, timeout=10.0)


def _resolve_client_id(credentials: dict) -> Optional[str]:
    """
    Determine the Jainam client ID from credentials, session, or persisted auth.
    """
    candidate = (
        credentials.get('user_id')
        or credentials.get('clientID')
        or credentials.get('client_id')
        or session.get('USER_ID')
    )

    if candidate:
        return candidate

    try:
        user_session_key = session.get('user_session_key')
        if user_session_key:
            from database.auth_db import get_user_id  # Lazy import to avoid circular deps
            stored_user_id = get_user_id(user_session_key)
            if stored_user_id:
                return stored_user_id
    except Exception as exc:  # pragma: no cover - defensive
        logger.debug("Unable to resolve Jainam client ID from database: %s", exc)

    return None

def get_margin_data(auth_token):
    """
    Get margin/funds data from Jainam.

    Refactored to use FundsAPIClient (Task 24.1).

    Args:
        auth_token: Authentication token

    Returns:
        Margin data in MarvelQuant format
    """
    try:
        # Parse auth_token
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'interactive_token': auth_token}
        else:
            credentials = auth_token

        interactive_token = credentials.get('interactive_token', credentials.get('token', auth_token))
        client_id = _resolve_client_id(credentials)

        # Use FundsAPIClient
        client = FundsAPIClient(auth_token=interactive_token)

        # Track if we got a 400 error
        got_400_error = False

        try:
            response_data = client.get_balance(client_id)
        except httpx.HTTPStatusError as exc:
            # Handle HTTP errors
            got_400_error = (exc.response.status_code == 400)
            response_data = {}
            # Check if it's a 400 error with specific messages
            if got_400_error:
                try:
                    error_data = exc.response.json()
                    response_data = error_data
                except:
                    pass
        except Exception as exc:
            # Handle other errors
            logger.error(f"Error getting Jainam margin data: {exc}")
            response_data = {}

        # Handle 400 errors with specific messages
        if got_400_error:
            description = (response_data.get('description') or '').lower()
            if 'data not available' in description:
                logger.info("Jainam reported no balance data available.")
                return {
                    'availablecash': 0.0,
                    'collateral': 0.0,
                    'buyingpower': 0.0,
                    'usedmargin': 0.0,
                    'totalmargin': 0.0,
                }
            if 'clientid' in description and not client_id:
                logger.error("Jainam balance API requires clientID but none was resolved.")
                return {
                    'status': 'error',
                    'message': 'Client ID required for Jainam balance API. Please re-authenticate.'
                }

        if response_data.get('type') == 'success' and 'result' in response_data:
            balance_data = response_data['result']

            # Transform to MarvelQuant format
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
    Get user profile from Jainam.

    Refactored to use FundsAPIClient (Task 24.1).

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
                credentials = {'interactive_token': auth_token}
        else:
            credentials = auth_token

        interactive_token = credentials.get('interactive_token', credentials.get('token', auth_token))
        client_id = _resolve_client_id(credentials)

        # Use FundsAPIClient
        client = FundsAPIClient(auth_token=interactive_token)
        response_data = client.get_profile(client_id)

        if response_data.get('type') == 'success' and 'result' in response_data:
            profile_data = response_data['result']

            # Transform to MarvelQuant format
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
