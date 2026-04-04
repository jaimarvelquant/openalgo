import os
import time
from utils.logging import get_logger

logger = get_logger(__name__)

def authenticate_broker(code=None):
    """
    Authenticate with IBKR TWS API.
    For IBKR, 'code' is not used in a traditional OAuth way.
    It expects BROKER_API_KEY to be in 'client_id:::port' format.
    Example: '1:::7497' (7497 is default for paper trading, 7496 for live)
    """
    try:
        broker_api_key = os.getenv("BROKER_API_KEY")
        if not broker_api_key or ":::" not in broker_api_key:
            return None, "Invalid BROKER_API_KEY format. Expected 'client_id:::port'"

        parts = broker_api_key.split(":::")
        
        # Determine client_id and port
        if len(parts) >= 2:
            client_id_str = parts[0]
            port_str = parts[1]
        else:
            return None, "Invalid BROKER_API_KEY format. Expected 'client_id:::port'"

        try:
            client_id = int(client_id_str)
        except ValueError:
            logger.warning(f"Non-numeric ClientID '{client_id_str}' in BROKER_API_KEY. Defaulting to ClientID 1.")
            client_id = 1
            
        try:
            port = int(port_str)
        except ValueError:
            return None, f"Invalid port '{port_str}' in BROKER_API_KEY. Port must be a number."
        host = os.getenv("IBKR_HOST", "127.0.0.1")

        logger.info(f"Attempting to connect to IBKR TWS at {host}:{port} with ClientID {client_id}")

        # Import ib_insync here to avoid dependency issues if not installed
        try:
            import asyncio
            
            # Ensure an event loop exists in this thread BEFORE importing ib_insync
            # as ib_insync (and eventkit) may try to get the loop on import.
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            from ib_insync import IB, util
            
            # Apply nest_asyncio if needed
            import nest_asyncio
            nest_asyncio.apply()
            
            ib = IB()
            # Try to connect with a short timeout to verify credentials
            ib.connect(host, port, clientId=client_id, timeout=5, readonly=True)
            ib.disconnect()
            
            logger.info("Successfully verified IBKR TWS connection")
            # For IBKR, we use the client_id:::port as the 'auth_token'
            return broker_api_key, None
        except ImportError:
            return None, "ib_insync library not found. Please install it using 'pip install ib_insync'"
        except Exception as e:
            logger.error(f"Failed to connect to IBKR TWS: {e}")
            return None, f"Connection failed: {str(e)}"

    except Exception as e:
        logger.exception("Unexpected error during IBKR authentication")
        return None, str(e)
