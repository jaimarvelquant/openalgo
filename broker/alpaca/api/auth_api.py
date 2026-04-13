import os
from alpaca.trading.client import TradingClient
from alpaca.common.exceptions import APIError
from utils.logging import get_logger

logger = get_logger(__name__)

def authenticate_broker(api_key, api_secret, is_paper=True):
    """
    Verify Alpaca credentials by attempting to fetch account information.
    """
    api_key = str(api_key).strip()
    api_secret = str(api_secret).strip()
    
    try:
        # Initialize TradingClient to validate keys
        # Use default SDK behavior for Paper/Live URLs
        client = TradingClient(api_key, api_secret, paper=is_paper)
        
        # Attempt to get account info to verify connectivity and credentials
        account = client.get_account()
        
        if account:
            prefix = "PAPER:::" if is_paper else "LIVE:::"
            logger.info(f"Alpaca Auth SUCCESS (Mode: {'Paper' if is_paper else 'Live'})")
            # Returns formatted token for database storage
            return f"{prefix}{api_key}:::{api_secret}", None
            
    except APIError as e:
        logger.error(f"Alpaca API Error: {e}")
        return None, f"Alpaca Error: {str(e)}"
    except Exception as e:
        logger.exception(f"Alpaca Auth Exception: {str(e)}")
        return None, f"Connection Error: {str(e)}"
    
    return None, "Alpaca Error: API key unrecognized or account inactive."
