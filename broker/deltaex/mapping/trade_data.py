from datetime import datetime

def map_trade_data(fill):
    """
    Standardize Delta Exchange fill (trade) data for the OpenAlgo trades table.
    """
    trade_id = str(fill.get('id', ''))
    order_id = str(fill.get('order_id', ''))
    
    # Delta format: {'id': 123, 'side': 'buy', 'size': '0.1', 'price': '50000'}
    symbol = fill.get('product', {}).get('symbol', 'Unknown')
    
    side = fill.get('side', '').upper()
    transaction_type = "BUY" if side == "BUY" else "SELL"
    
    quantity = float(fill.get('size', 0))
    price = float(fill.get('price', 0))
    
    trade_time = fill.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    return {
        "trade_id": trade_id,
        "order_id": order_id,
        "trading_symbol": symbol,
        "exchange": "DELTA",
        "transaction_type": transaction_type,
        "quantity": quantity,
        "price": price,
        "trade_time": trade_time
    }

def map_trade_book_data(fills):
    """Map a list of Delta fills to OpenAlgo format"""
    if not fills: return []
    if isinstance(fills, list):
         return [map_trade_data(f) for f in fills]
    elif isinstance(fills, dict) and 'result' in fills:
         return [map_trade_data(f) for f in fills.get('result', [])]
    return []
