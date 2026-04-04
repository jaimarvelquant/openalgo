# Mapping OpenAlgo API Request to IBKR TWS API
from utils.logging import get_logger

logger = get_logger(__name__)

def transform_data(data):
    """
    Transforms the OpenAlgo Platform API request structure to the format expected by the IBKR TWS API.
    Returns a dictionary with 'contract' and 'order' objects.
    """
    from ib_insync import Contract, MarketOrder, LimitOrder, StopOrder
    
    symbol_full = data["symbol"]
    # OpenAlgo symbols sometimes have colon separators. For IBKR, we can use it to pass extra info.
    # Format: SYMBOL:CURRENCY:EXCH:SEC_TYPE
    # Example: AAPL:USD:SMART:STK
    parts = symbol_full.split(':')
    symbol = parts[0]
    currency = parts[1] if len(parts) > 1 else "USD"
    exchange = parts[2] if len(parts) > 2 else "SMART"
    sec_type = parts[3] if len(parts) > 3 else "STK"

    contract = Contract()
    contract.symbol = symbol
    contract.secType = sec_type
    contract.exchange = exchange
    contract.currency = currency

    quantity = int(data["quantity"])
    action = data["action"].upper() # BUY or SELL
    
    price_type = data.get("pricetype", "MARKET").upper()
    price = float(data.get("price", 0))
    trigger_price = float(data.get("trigger_price", 0))

    if price_type == "LIMIT":
        order = LimitOrder(action, quantity, price)
    elif price_type == "STOP" or price_type == "SL-M":
        order = StopOrder(action, quantity, trigger_price)
    elif price_type == "MARKET":
        order = MarketOrder(action, quantity)
    else:
        # Default to Market
        logger.warning(f"Unknown pricetype {price_type}, defaulting to Market")
        order = MarketOrder(action, quantity)

    return {
        "contract": contract,
        "order": order
    }

def map_product_type(product):
    """
    In IBKR, product type usually maps to account types or IBKR's own routing.
    For now, return as is or map to common ones.
    """
    return product

def reverse_map_product_type(product):
    return product
