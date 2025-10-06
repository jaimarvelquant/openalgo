"""
Order data transformation module for Jainam
Handles order-specific data conversions between OpenAlgo and Jainam formats
"""

def transform_order_request(order_data):
    """
    Transform OpenAlgo order request to Jainam format

    Args:
        order_data: OpenAlgo order data

    Returns:
        Jainam order data
    """
    # This is similar to transform_data.py but focused on orders
    # For now, delegate to the main transform_data module
    from broker.jainam_prop.mapping.transform_data import transform_data
    return transform_data(order_data)

def transform_order_response(jainam_response):
    """
    Transform Jainam order response to OpenAlgo format

    Args:
        jainam_response: Jainam API response

    Returns:
        OpenAlgo order response
    """
    from broker.jainam_prop.mapping.transform_data import transform_response
    return transform_response(jainam_response)

def transform_order_status(jainam_order_status):
    """
    Transform Jainam order status to OpenAlgo format

    Args:
        jainam_order_status: Order status from Jainam

    Returns:
        Order status in OpenAlgo format
    """
    # Status mapping
    status_mapping = {
        'NEW': 'open',
        'OPEN': 'open',
        'FILLED': 'complete',
        'CANCELLED': 'cancelled',
        'REJECTED': 'rejected',
        'PARTIALLYFILLED': 'partial'
    }

    # Product type mapping
    product_mapping = {
        'MIS': 'MIS',
        'NRML': 'NRML',
        'CNC': 'CNC'
    }

    # Order type mapping
    order_type_mapping = {
        'MARKET': 'MARKET',
        'LIMIT': 'LIMIT',
        'STOPMARKET': 'SL',
        'STOPLIMIT': 'SL-M'
    }

    try:
        openalgo_status = {
            'orderid': str(jainam_order_status.get('AppOrderID', '')),
            'status': status_mapping.get(jainam_order_status.get('OrderStatus', ''), 'unknown'),
            'symbol': jainam_order_status.get('TradingSymbol', ''),
            'exchange': jainam_order_status.get('ExchangeSegment', ''),
            'action': jainam_order_status.get('OrderSide', ''),
            'quantity': int(jainam_order_status.get('OrderQuantity', 0)),
            'price': float(jainam_order_status.get('OrderPrice', 0)),
            'pricetype': order_type_mapping.get(jainam_order_status.get('OrderType', ''), 'MARKET'),
            'product': product_mapping.get(jainam_order_status.get('ProductType', ''), 'MIS'),
            'filled_quantity': int(jainam_order_status.get('Cumulativetradedquantity', 0)),
            'pending_quantity': int(jainam_order_status.get('pendingQuantity', 0)),
            'average_price': float(jainam_order_status.get('AverageTradedPrice', 0)),
            'order_timestamp': jainam_order_status.get('OrderTime', ''),
            'exchange_order_id': str(jainam_order_status.get('ExchangeOrderID', ''))
        }

        return openalgo_status

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error transforming order status: {str(e)}'
        }

def transform_trade_book(jainam_trades):
    """
    Transform Jainam trade book to OpenAlgo format

    Args:
        jainam_trades: Trade data from Jainam

    Returns:
        Trade data in OpenAlgo format
    """
    try:
        openalgo_trades = []

        for trade in jainam_trades:
            openalgo_trade = {
                'orderid': str(trade.get('AppOrderID', '')),
                'trade_id': str(trade.get('TradeID', '')),
                'symbol': trade.get('TradingSymbol', ''),
                'exchange': trade.get('ExchangeSegment', ''),
                'action': trade.get('OrderSide', ''),
                'quantity': int(trade.get('TradedQuantity', 0)),
                'price': float(trade.get('TradedPrice', 0)),
                'trade_timestamp': trade.get('TradeTime', ''),
                'exchange_trade_id': str(trade.get('ExchangeTradeID', ''))
            }
            openalgo_trades.append(openalgo_trade)

        return {
            'status': 'success',
            'trades': openalgo_trades
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error transforming trade book: {str(e)}'
        }

def validate_order_data(order_data):
    """
    Validate order data before sending to Jainam

    Args:
        order_data: Order data to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['symbol', 'exchange', 'action', 'quantity', 'pricetype']

    # Check required fields
    for field in required_fields:
        if field not in order_data or not order_data[field]:
            return False, f"Missing required field: {field}"

    # Validate action
    valid_actions = ['BUY', 'SELL']
    if order_data['action'].upper() not in valid_actions:
        return False, f"Invalid action: {order_data['action']}. Must be one of {valid_actions}"

    # Validate exchange
    valid_exchanges = ['NSE', 'BSE', 'NFO', 'MCX']
    if order_data['exchange'].upper() not in valid_exchanges:
        return False, f"Invalid exchange: {order_data['exchange']}. Must be one of {valid_exchanges}"

    # Validate price type
    valid_pricetypes = ['MARKET', 'LIMIT', 'SL', 'SL-M']
    if order_data['pricetype'].upper() not in valid_pricetypes:
        return False, f"Invalid pricetype: {order_data['pricetype']}. Must be one of {valid_pricetypes}"

    # Validate quantity
    try:
        quantity = int(order_data['quantity'])
        if quantity <= 0:
            return False, "Quantity must be positive"
    except (ValueError, TypeError):
        return False, "Invalid quantity format"

    # Validate price for limit orders
    if order_data['pricetype'].upper() in ['LIMIT', 'SL-M']:
        try:
            price = float(order_data.get('price', 0))
            if price <= 0:
                return False, "Price must be positive for limit orders"
        except (ValueError, TypeError):
            return False, "Invalid price format"

    # Validate trigger price for stop orders
    if order_data['pricetype'].upper() in ['SL', 'SL-M']:
        try:
            trigger_price = float(order_data.get('trigger_price', 0))
            if trigger_price <= 0:
                return False, "Trigger price must be positive for stop orders"
        except (ValueError, TypeError):
            return False, "Invalid trigger price format"

    return True, None

def get_order_history_transform(jainam_history):
    """
    Transform Jainam order history to OpenAlgo format

    Args:
        jainam_history: Order history from Jainam

    Returns:
        Order history in OpenAlgo format
    """
    try:
        # Similar to order status transformation but for historical data
        return transform_order_status(jainam_history)

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error transforming order history: {str(e)}'
        }
