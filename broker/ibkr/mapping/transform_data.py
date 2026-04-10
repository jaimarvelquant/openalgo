# Mapping OpenAlgo API Request to IBKR TWS API
from utils.logging import get_logger

logger = get_logger(__name__)

def transform_data(data):
    """
    Transforms the OpenAlgo Platform API request structure to the format expected by the IBKR TWS API.
    Returns a dictionary with 'contract' and 'order' objects.
    """
    from ib_insync import Contract, MarketOrder, LimitOrder, StopOrder
    import re
    
    symbol_full = data["symbol"]
    # OpenAlgo symbols sometimes have colon separators. For IBKR, we can use it to pass extra info.
    # Format: SYMBOL:CURRENCY:EXCH:SEC_TYPE
    # Example: AAPL:USD:SMART:STK
    parts = symbol_full.split(':')
    symbol = parts[0]
    
    contract = Contract()
    
    if len(parts) > 1:
        # Use explicit parts if provided via colons
        contract.symbol = symbol
        contract.currency = parts[1] if len(parts) > 1 else "USD"
        contract.exchange = parts[2] if len(parts) > 2 else "SMART"
        contract.secType = parts[3].upper() if len(parts) > 3 else "STK"
    else:
        # Auto-detect if it's an option local symbol
        # Pattern: underlying [multiple spaces] YYMMDD[C/P]STRIKE
        # Example: 'SPXW 260406P06580000' or 'SPX   260417C06570000'
        option_pattern = r'^[A-Z0-9.\s]+\s+\d{6}[CP]\d+$'
        
        # Auto-detect if it's an option symbol (Strict YYMMDD format OR localSymbol fragment)
        option_detected = re.match(option_pattern, symbol.strip()) or \
                         (' C' in symbol or ' P' in symbol) and any(char.isdigit() for char in symbol)
        
        if option_detected:
            contract.localSymbol = symbol.strip()
            # For Future Options (CL/WL/XL/LO2/SO2), secType must be 'FOP', not 'OPT'
            is_crude = any(x in symbol for x in ['CL', 'WL', 'XL', 'LO2', 'SO2'])
            contract.secType = 'FOP' if is_crude else 'OPT'
            contract.symbol = 'CL' if is_crude else ''
            contract.exchange = 'NYMEX' if is_crude else 'SMART'
            contract.currency = 'USD'
            contract.multiplier = '1000' if is_crude else '100'
        elif symbol.strip() == 'CL': # Specifically handle Crude Future
            contract.symbol = 'CL'
            contract.secType = 'FUT'
            contract.exchange = 'NYMEX'
            contract.currency = 'USD'
        elif '.' in symbol and len(symbol) == 7: # Likely Forex: EUR.USD
            contract.symbol = symbol.split('.')[0]
            contract.currency = symbol.split('.')[1]
            contract.secType = 'CASH'
            contract.exchange = 'IDEALPRO'
        elif symbol.startswith('CL') and len(symbol) > 2: # Potential Future/FOP
             contract.symbol = 'CL'
             contract.secType = 'FUT' # Default to FUT, hijacking logic handles FOP
             contract.exchange = 'NYMEX'
             contract.currency = 'USD'
        else:
            # Default to STK
            contract.symbol = symbol
            contract.secType = 'STK'
            contract.exchange = 'SMART'
            contract.currency = 'USD'

    # If exchange is provided in data (not common for IBKR orders in OA but can happen)
    if data.get("exchange") and data.get("exchange") != "IBKR":
        contract.exchange = data["exchange"]

    # FORCE CASH for Forex like symbols
    if contract.exchange == 'IDEALPRO' or ('.' in symbol and len(symbol) == 7):
        contract.secType = 'CASH'
        contract.exchange = 'IDEALPRO'
        if '.' in symbol:
            contract.symbol = symbol.split('.')[0]
            contract.currency = symbol.split('.')[1]
        else:
            contract.symbol = symbol
            contract.currency = "USD" if symbol != "USD" else "EUR"

    # Special handling for SPX/SPXW which might need specific exchange
    if "SPX" in symbol:
        contract.exchange = "CBOE" if not len(parts) > 2 else parts[2]
        contract.currency = "USD"
        contract.multiplier = "100"

    quantity = int(float(data.get("quantity", 0)))
    action = data.get("action", "BUY").upper()
    
    price_type = str(data.get("pricetype") or data.get("order_type", "MARKET")).upper()
    price = float(data.get("price", 0))
    trigger_price = float(data.get("trigger_price", 0))

    if price_type == "LIMIT":
        order = LimitOrder(action, quantity, price)
    elif price_type in ["STOP", "STP", "SL-M"]:
        order = StopOrder(action, quantity, trigger_price)
    elif price_type == "MARKET":
        order = MarketOrder(action, quantity)
    else:
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
