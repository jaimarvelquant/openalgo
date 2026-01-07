#Mapping MarvelQuant API Request https://marvelquant.com/docs
#Mapping Angel Broking Parameters https://smartapi.angelbroking.com/docs/Orders

from database.token_db import get_br_symbol

def transform_data(data,token):
    """
    Transforms the new API request structure to the current expected structure.
    """
    from utils.logging import get_logger
    logger = get_logger(__name__)
    
    original_symbol = data.get("symbol", "")
    exchange = data.get("exchange", "")
    
    # Validate that symbol is not a template variable
    if original_symbol and (original_symbol.startswith("{{") and original_symbol.endswith("}}")):
        error_msg = (
            f"Invalid symbol: '{original_symbol}' appears to be a template variable that was not replaced. "
            f"Please ensure the symbol is properly resolved before placing the order."
        )
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    symbol = get_br_symbol(original_symbol, exchange)
    
    # Handle special characters in symbol
    if symbol and '&' in symbol:
        symbol = symbol.replace('&', '%26')
    
    # Ensure symbol is a string (not None) - Flattrade API requires all parameters as strings
    if symbol is None:
        # Check if the original symbol looks like a valid contract symbol
        # Pattern: Base symbol + expiry (YYMON format) + strike + CE/PE (for options)
        # or Base symbol + expiry + FUT (for futures)
        import re
        is_valid_contract = False
        
        # Check for options pattern: e.g., NIFTY24JAN26000CE, BANKNIFTY24JAN50000PE
        option_pattern = r'^[A-Z]+[0-9]{2}[A-Z]{3}[0-9]+(CE|PE)$'
        # Check for futures pattern: e.g., NIFTY24JANFUT, BANKNIFTY24JANFUT
        future_pattern = r'^[A-Z]+[0-9]{2}[A-Z]{3}FUT$'
        # Check for equity (simpler pattern)
        equity_pattern = r'^[A-Z]+(-EQ)?$'
        
        if re.match(option_pattern, original_symbol.upper()) or \
           re.match(future_pattern, original_symbol.upper()) or \
           (exchange in ['NSE', 'BSE'] and re.match(equity_pattern, original_symbol.upper())):
            # Symbol looks like a valid contract - use it directly as broker symbol
            symbol = original_symbol
            is_valid_contract = True
            logger.warning(
                f"Symbol '{original_symbol}' not found in database, but appears to be a valid contract symbol. "
                f"Using it directly as broker symbol. Please update master contracts database for proper mapping."
            )
        
        if not is_valid_contract:
            # Symbol mapping not found and doesn't look like a valid contract
            error_msg = (
                f"Broker symbol mapping not found for symbol '{original_symbol}' on exchange '{exchange}'. "
                f"Please ensure the symbol is added to the master contract database. "
                f"Flattrade requires the full contract symbol (e.g., 'NIFTY24JAN23500CE' for options, not just 'NIFTY'). "
                f"If you believe this is a valid symbol, please download/update the master contracts for Flattrade."
            )
            logger.error(error_msg)
            raise ValueError(error_msg)

    # Basic mapping - ensure all numeric values are strings and no None values
    transformed = {
        "uid": str(data.get("apikey", "")),
        "actid": str(data.get("apikey", "")),
        "exch": str(data.get("exchange", "")),
        "tsym": str(symbol),  # Ensure string, not None
        "qty": str(data.get("quantity", "0")),
        "prc": str(data.get("price", "0")),
        "trgprc": str(data.get("trigger_price", "0")),
        "dscqty": str(data.get("disclosed_quantity", "0")),
        "prd": str(map_product_type(data.get("product", "MIS"))),
        "trantype": 'B' if data.get("action", "BUY").upper() == "BUY" else 'S',
        "prctyp": str(map_order_type(data.get("pricetype", "MARKET"))),
        "mkt_protection": "0",
        "ret": "DAY",
        "ordersource": "API"
    }
    
    # Final validation: ensure no None values and all are strings
    for key, value in transformed.items():
        if value is None:
            raise ValueError(f"Transformed field '{key}' cannot be None. All Flattrade API parameters must be strings.")
        transformed[key] = str(value)  # Ensure it's a string

    return transformed


def transform_modify_order_data(data, token):
    # Handle special characters in symbol
    symbol = data.get("symbol", "")
    if symbol and '&' in symbol:
        symbol = symbol.replace('&', '%26')
    
    # Ensure symbol is a string (not None) - Flattrade API requires all parameters as strings
    if not symbol:
        raise ValueError("Symbol is required for order modification")

    transformed = {
        "uid": str(data.get("apikey", "")),
        "exch": str(data.get("exchange", "")),
        "norenordno": str(data.get("orderid", "")),
        "prctyp": str(map_order_type(data.get("pricetype", "MARKET"))),
        "prc": str(data.get("price", "0")),
        "qty": str(data.get("quantity", "0")),
        "tsym": str(symbol),  # Ensure string, not None
        "ret": "DAY"
    }
    
    # Final validation: ensure no None values and all are strings
    for key, value in transformed.items():
        if value is None:
            raise ValueError(f"Transformed field '{key}' cannot be None. All Flattrade API parameters must be strings.")
        transformed[key] = str(value)  # Ensure it's a string
    
    return transformed



def map_order_type(pricetype):
    """
    Maps the new pricetype to the existing order type.
    """
    order_type_mapping = {
        "MARKET": "MKT",
        "LIMIT": "LMT",
        "SL": "SL-LMT",
        "SL-M": "SL-MKT"
    }
    return order_type_mapping.get(pricetype, "MARKET")  # Default to MARKET if not found

def map_product_type(product):
    """
    Maps the new product type to the existing product type.
    """
    product_type_mapping = {
        "CNC": "C",
        "NRML": "M",
        "MIS": "I",
    }
    return product_type_mapping.get(product, "I")  # Default to DELIVERY if not found



def reverse_map_product_type(product):
    """
    Maps the new product type to the existing product type.
    """
    reverse_product_type_mapping = {
        "C": "CNC",
        "M": "NRML",
        "I": "MIS",
    }
    return reverse_product_type_mapping.get(product)  
