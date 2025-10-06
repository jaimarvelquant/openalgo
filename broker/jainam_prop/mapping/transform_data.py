"""
Data transformation module for Jainam broker
Converts between OpenAlgo format and Jainam XTS Connect API format
"""

def transform_data(data):
    """
    Transform OpenAlgo request to Jainam format

    OpenAlgo Input:
    {
        "symbol": "RELIANCE-EQ",
        "exchange": "NSE",
        "action": "BUY",
        "quantity": 10,
        "pricetype": "LIMIT",
        "product": "MIS",
        "price": 2500.50,
        "trigger_price": 2490.00
    }

    Jainam Output:
    {
        "exchangeSegment": "NSECM",
        "exchangeInstrumentID": 738561,
        "productType": "MIS",
        "orderType": "LIMIT",
        "orderSide": "BUY",
        "timeInForce": "DAY",
        "disclosedQuantity": 0,
        "orderQuantity": 10,
        "limitPrice": 2500.50,
        "stopPrice": 2490.00,
        "orderUniqueIdentifier": "WEB_EXE_PLATFORM",
        "clientID": "user_id"
    }
    """

    # Extract base symbol (remove -EQ suffix if present)
    symbol = data['symbol'].replace('-EQ', '').replace('-', '')

    # Map action to Jainam format
    action_mapping = {
        'BUY': 'BUY',
        'SELL': 'SELL'
    }

    # Map price type to Jainam order types
    pricetype_mapping = {
        'MARKET': 'MARKET',
        'LIMIT': 'LIMIT',
        'SL': 'STOPMARKET',
        'SL-M': 'STOPLIMIT'
    }

    # Map product type to Jainam product types
    product_mapping = {
        'CNC': 'CNC',
        'MIS': 'MIS',
        'NRML': 'NRML'
    }

    # Map exchange to Jainam exchange segments
    exchange_mapping = {
        'NSE': 'NSECM',
        'NFO': 'NSEFO',
        'BSE': 'BSECM',
        'MCX': 'MCXFO'
    }

    # Get exchange segment
    exchange = data.get('exchange', 'NSE')
    exchange_segment = exchange_mapping.get(exchange, 'NSECM')

    # Get token from symbol (this would need to be implemented)
    # For now, we'll use a placeholder - in real implementation,
    # this should lookup from master contract database
    token = get_token_from_symbol(symbol, exchange)

    # Build Jainam order structure
    jainam_order = {
        "exchangeSegment": exchange_segment,
        "exchangeInstrumentID": token,
        "productType": product_mapping.get(data.get('product', 'MIS'), 'MIS'),
        "orderType": pricetype_mapping.get(data.get('pricetype', 'MARKET'), 'MARKET'),
        "orderSide": action_mapping.get(data.get('action', 'BUY'), 'BUY'),
        "timeInForce": "DAY",  # Jainam uses DAY as default
        "disclosedQuantity": 0,
        "orderQuantity": int(data.get('quantity', 1)),
        "limitPrice": float(data.get('price', 0)),
        "stopPrice": float(data.get('trigger_price', 0)),
        "orderUniqueIdentifier": "OPENALGO_PLATFORM"
    }

    # Handle special cases for stop orders
    if data.get('pricetype') == 'SL':
        jainam_order['stopPrice'] = float(data.get('trigger_price', 0))
        jainam_order['limitPrice'] = 0
    elif data.get('pricetype') == 'SL-M':
        jainam_order['stopPrice'] = float(data.get('trigger_price', 0))
        jainam_order['limitPrice'] = float(data.get('price', 0))

    return jainam_order

def transform_response(jainam_response):
    """
    Transform Jainam response to OpenAlgo format

    Jainam Response:
    {
        "type": "success",
        "result": {
            "AppOrderID": "12345678",
            "OrderUniqueIdentifier": "OPENALGO_PLATFORM"
        }
    }

    OpenAlgo Response:
    {
        "status": "success",
        "orderid": "12345678",
        "message": "Order placed successfully"
    }
    """
    if jainam_response.get('type') == 'success':
        return {
            'status': 'success',
            'orderid': str(jainam_response.get('result', {}).get('AppOrderID', '')),
            'message': 'Order placed successfully'
        }
    else:
        return {
            'status': 'error',
            'message': jainam_response.get('description', 'Unknown error')
        }

def get_token_from_symbol(symbol, exchange):
    """
    Get instrument token from symbol and exchange
    This should lookup from master contract database
    """
    # Placeholder implementation - in real scenario,
    # this should query the database
    # For now, return a dummy token
    return 123456  # This should be replaced with actual lookup

def map_exchange_to_jainam(exchange):
    """Map OpenAlgo exchange to Jainam exchange segment"""
    mapping = {
        'NSE': 'NSECM',
        'NFO': 'NSEFO',
        'BSE': 'BSECM',
        'MCX': 'MCXFO'
    }
    return mapping.get(exchange, 'NSECM')

def map_jainam_to_exchange(exchange_segment):
    """Map Jainam exchange segment to OpenAlgo exchange"""
    mapping = {
        'NSECM': 'NSE',
        'NSEFO': 'NFO',
        'BSECM': 'BSE',
        'MCXFO': 'MCX'
    }
    return mapping.get(exchange_segment, 'NSE')
