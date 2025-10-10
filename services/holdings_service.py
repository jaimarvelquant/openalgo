import importlib
import inspect
import traceback
from typing import Tuple, Dict, Any, Optional, List, Union
from database.auth_db import get_auth_token_broker
from utils.logging import get_logger
from services.auth_payload import build_broker_auth_payload

# Initialize logger
logger = get_logger(__name__)


def _function_accepts_kwarg(func, kwarg: str) -> bool:
    """
    Return True if the callable `func` can accept the keyword argument `kwarg`.

    Handles explicit keyword parameters as well as **kwargs catch-alls so that we
    can pass optional context (like auth_token) without breaking other brokers.
    """
    try:
        signature = inspect.signature(func)
    except (TypeError, ValueError):
        # Builtins or objects without signatures – assume conservative False
        return False

    for param in signature.parameters.values():
        if param.kind == inspect.Parameter.VAR_KEYWORD:
            return True
        if param.kind in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY) and param.name == kwarg:
            return True
    return False

def format_decimal(value):
    """Format numeric value to 2 decimal places"""
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    return value

def format_holdings_data(holdings_data):
    """Format all numeric values in holdings data to 2 decimal places"""
    if isinstance(holdings_data, list):
        return [
            {
                key: format_decimal(value) if key in ['pnl', 'pnlpercent'] else value
                for key, value in item.items()
            }
            for item in holdings_data
        ]
    return holdings_data

def format_statistics(stats):
    """Format all numeric values in statistics to 2 decimal places"""
    if isinstance(stats, dict):
        return {
            key: format_decimal(value)
            for key, value in stats.items()
        }
    return stats

def import_broker_module(broker_name: str) -> Optional[Dict[str, Any]]:
    """
    Dynamically import the broker-specific holdings modules.

    Args:
        broker_name: Name of the broker

    Returns:
        Dictionary of broker functions or None if import fails
    """
    try:
        # Import API module
        api_module = importlib.import_module(f'broker.{broker_name}.api.order_api')
        # Import mapping module
        mapping_module = importlib.import_module(f'broker.{broker_name}.mapping.order_data')

        # Verify required functions exist
        required_funcs = ['get_holdings', 'map_portfolio_data', 'calculate_portfolio_statistics', 'transform_holdings_data']
        for func_name in required_funcs:
            if func_name.startswith('get_'):
                if not hasattr(api_module, func_name):
                    raise AttributeError(f"API module missing required function: {func_name}")
            else:
                if not hasattr(mapping_module, func_name):
                    raise AttributeError(f"Mapping module missing required function: {func_name}")

        return {
            'get_holdings': getattr(api_module, 'get_holdings'),
            'map_portfolio_data': getattr(mapping_module, 'map_portfolio_data'),
            'calculate_portfolio_statistics': getattr(mapping_module, 'calculate_portfolio_statistics'),
            'transform_holdings_data': getattr(mapping_module, 'transform_holdings_data')
        }
    except (ImportError, AttributeError) as error:
        logger.error(f"Error importing broker modules for {broker_name}: {error}")
        import traceback
        logger.error(traceback.format_exc())
        return None

def get_holdings_with_auth(
    auth_token: Union[str, Dict[str, Any]],
    broker: str,
    original_data: Dict[str, Any] = None
) -> Tuple[bool, Dict[str, Any], int]:
    """
    Get holdings details using provided auth token.

    Args:
        auth_token: Authentication token for the broker API
        broker: Name of the broker
        original_data: Original request data (for sandbox mode, optional for internal calls)

    Returns:
        Tuple containing:
        - Success status (bool)
        - Response data (dict)
        - HTTP status code (int)
    """
    # If in analyze mode AND we have original_data (API call), route to sandbox
    # If original_data is None (internal call), use live broker
    from database.settings_db import get_analyze_mode
    if get_analyze_mode() and original_data:
        from services.sandbox_service import sandbox_get_holdings

        api_key = original_data.get('apikey')
        if not api_key:
            return False, {
                'status': 'error',
                'message': 'API key required for sandbox mode',
                'mode': 'analyze'
            }, 400

        return sandbox_get_holdings(api_key, original_data)

    broker_funcs = import_broker_module(broker)
    if broker_funcs is None:
        return False, {
            'status': 'error',
            'message': 'Broker-specific module not found'
        }, 404

    try:
        # Get holdings using broker functions
        holdings = broker_funcs['get_holdings'](auth_token)
        
        if 'status' in holdings and holdings['status'] == 'error':
            return False, {
                'status': 'error',
                'message': holdings.get('message', 'Error fetching holdings data')
            }, 500

        # Transform data using mapping functions, passing auth_token when supported
        map_portfolio_fn = broker_funcs['map_portfolio_data']
        if _function_accepts_kwarg(map_portfolio_fn, 'auth_token'):
            holdings = map_portfolio_fn(holdings, auth_token=auth_token)
        else:
            holdings = map_portfolio_fn(holdings)
        portfolio_stats = broker_funcs['calculate_portfolio_statistics'](holdings)
        holdings = broker_funcs['transform_holdings_data'](holdings)
        
        # Format numeric values to 2 decimal places
        formatted_holdings = format_holdings_data(holdings)
        formatted_stats = format_statistics(portfolio_stats)
        
        return True, {
            'status': 'success',
            'data': {
                'holdings': formatted_holdings,
                'statistics': formatted_stats
            }
        }, 200
    except Exception as e:
        logger.error(f"Error processing holdings data: {e}")
        traceback.print_exc()
        return False, {
            'status': 'error',
            'message': str(e)
        }, 500

def get_holdings(
    api_key: Optional[str] = None,
    auth_token: Optional[Union[str, Dict[str, Any]]] = None,
    broker: Optional[str] = None,
    feed_token: Optional[str] = None
) -> Tuple[bool, Dict[str, Any], int]:
    """
    Get holdings details.
    Supports both API-based authentication and direct internal calls.
    
    Args:
        api_key: MarvelQuant API key (for API-based calls)
        auth_token: Direct broker authentication token (for internal calls)
        broker: Direct broker name (for internal calls)
        
    Returns:
        Tuple containing:
        - Success status (bool)
        - Response data (dict)
        - HTTP status code (int)
    """
    # Case 1: API-based authentication
    if api_key and not (auth_token and broker):
        AUTH_TOKEN, FEED_TOKEN, broker_name = get_auth_token_broker(
            api_key, include_feed_token=True
        )
        if AUTH_TOKEN is None or broker_name is None:
            return False, {
                'status': 'error',
                'message': 'Invalid marvelquant apikey'
            }, 403
        broker_auth = build_broker_auth_payload(AUTH_TOKEN, FEED_TOKEN)
        if broker_auth is None:
            return False, {
                'status': 'error',
                'message': 'Broker credentials missing interactive session token'
            }, 403
        original_data = {'apikey': api_key}
        return get_holdings_with_auth(broker_auth, broker_name, original_data)

    # Case 2: Direct internal call with auth_token and broker
    elif auth_token and broker:
        effective_auth = auth_token
        if isinstance(auth_token, dict):
            if feed_token:
                # Preserve existing keys while ensuring market token aliases exist
                effective_auth = dict(auth_token)
                for alias in ('market_token', 'marketToken', 'marketAuthToken', 'feed_token'):
                    effective_auth.setdefault(alias, feed_token)
        else:
            effective_auth = build_broker_auth_payload(auth_token, feed_token) or auth_token

        return get_holdings_with_auth(effective_auth, broker, None)
    
    # Case 3: Invalid parameters
    else:
        return False, {
            'status': 'error',
            'message': 'Either api_key or both auth_token and broker must be provided'
        }, 400
