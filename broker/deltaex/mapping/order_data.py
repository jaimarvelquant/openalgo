from datetime import datetime
from utils.logging import get_logger

print("\n[DEBUG] >>> DELTA MAPPING MODULE LOADED <<<\n")

logger = get_logger(__name__)

# --- SMART PROCESSOR HELPER ---
def _process_item_or_list(data, func, key_name=None, **kwargs):
    if data is None:
        data = kwargs.get(key_name) if key_name else None
        if data is None:
             for k in ['order_data', 'trade_data', 'positions_data', 'broker_order', 'fill', 'pos']:
                 if k in kwargs:
                     data = kwargs[k]
                     break
    
    # We must ALWAYS process raw Delta items to ensure all OpenAlgo fields (exchange, action, etc.) are present
    if not data: return [] if isinstance(data, list) else {}

    # SAFETY CHECK: If already mapped (has OpenAlgo unique keys), skip to avoid double-processing
    peek_list = data if isinstance(data, list) else [data]
    if peek_list and isinstance(peek_list[0], dict) and ('trading_symbol' in peek_list[0] and 'exchange' in peek_list[0]):
        return data

    if isinstance(data, dict) and 'result' in data:
        data = data['result']

    if isinstance(data, list):
        return [func(item) for item in data]
    return func(data)

# --- BASE MAPPERS (Single Item Only) ---
def _map_order(o):
    if not o or not isinstance(o, dict): return {}
    order_id = str(o.get('id', ''))
    symbol = o.get('product_symbol') or o.get('product', {}).get('symbol', 'Unknown')
    side = o.get('side', '').upper()
    transaction_type = "BUY" if side == "BUY" else "SELL"
    state = o.get('state', '').lower()
    if state == "filled": 
        status = "COMPLETE"
    elif state == "cancelled":
        status = "CANCELLED"
    elif state == "rejected":
        status = "REJECTED"
    else:
        status = "OPEN"
    quantity = float(o.get('size', 0))
    limit_price = float(o.get('limit_price', 0)) if o.get('limit_price') else 0
    order_time = o.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    order_type = "LIMIT" if limit_price > 0 else "MARKET"
    
    return {
        "order_id": order_id, "orderid": order_id, "exchange_order_id": order_id, 
        "trading_symbol": symbol, "symbol": symbol, "exchange": "DELTA", 
        "transaction_type": transaction_type, "action": transaction_type, 
        "quantity": quantity, "price": limit_price, "order_type": order_type,
        "pricetype": order_type,
        "order_time": order_time, "time": order_time, "timestamp": order_time,
        "product": "NRML", "status": status,
        "order_status": status.lower(),
        "filled_quantity": float(o.get('filled_size', 0)),
        "state": state # Keep state for statistics calculation
    }

def _map_trade(f):
    if not f or not isinstance(f, dict): return {}
    trade_id = str(f.get('id', ''))
    order_id = str(f.get('order_id', ''))
    
    # Delta India Blueprint: Check top-level then nested
    symbol = f.get('product_symbol') or f.get('product', {}).get('symbol', 'Unknown')
    
    side = f.get('side', '').upper()
    transaction_type = "BUY" if side == "BUY" else "SELL"
    
    # Use 'size' or 'quantity'
    quantity = float(f.get('size') or f.get('quantity', 0))
    price = float(f.get('price', 0))
    trade_time = f.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    return {
        "trade_id": trade_id, "tradeid": trade_id, "order_id": order_id, "orderid": order_id,
        "trading_symbol": symbol, "symbol": symbol, "exchange": "DELTA",
        "transaction_type": transaction_type, "action": transaction_type,
        "quantity": quantity, "price": price, "trade_time": trade_time, "time": trade_time,
        "timestamp": trade_time,
        "average_price": price, "trade_value": round(quantity * price, 2)
    }

def _map_pos(p):
    if not p or not isinstance(p, dict): return {}
    
    # Delta India Blueprint: Check top-level then nested
    symbol = p.get('product_symbol') or p.get('product', {}).get('symbol', 'Unknown')
    
    size = float(p.get('size') or 0)
    side = "BUY" if size > 0 else ("SELL" if size < 0 else "NONE")
    
    # Financials
    entry_price = float(p.get('entry_price') or 0)
    mark_price = float(p.get('mark_price') or p.get('mark_price_data', {}).get('price', 0))
    realized_pnl = float(p.get('realized_pnl') or 0)
    unrealized_pnl = float(p.get('unrealized_pnl') or 0)
    
    return {
        "trading_symbol": symbol, "symbol": symbol, "exchange": "DELTA", 
        "transaction_type": side, "action": side, "quantity": abs(size), 
        "product": "NRML", "average_price": entry_price, "avg_price": entry_price,
        "last_price": mark_price, "ltp": mark_price, "pnl": round(realized_pnl + unrealized_pnl, 2),
        "unrealized_pnl": unrealized_pnl, "realized_pnl": realized_pnl
    }

# --- PUBLIC MAPPERS ---
def transform_order_data(data=None, **kwargs):
    return _process_item_or_list(data, _map_order, 'order_data', **kwargs)

def transform_trade_data(data=None, **kwargs):
    return _process_item_or_list(data, _map_trade, 'trade_data', **kwargs)

def transform_positions_data(data=None, **kwargs):
    return _process_item_or_list(data, _map_pos, 'positions_data', **kwargs)

def calculate_order_statistics(orders, **kwargs):
    if isinstance(orders, dict): orders = orders.get('result', [])
    if not orders or not isinstance(orders, list): 
        return {
            "total_buy_orders": 0, "total_sell_orders": 0, 
            "total_completed_orders": 0, "total_open_orders": 0, "total_rejected_orders": 0
        }
    
    total_buy = len([o for o in orders if o.get('transaction_type') == 'BUY'])
    total_sell = len([o for o in orders if o.get('transaction_type') == 'SELL'])
    total_completed = len([o for o in orders if o.get('status') == 'COMPLETE'])
    total_open = len([o for o in orders if o.get('status') == 'OPEN'])
    total_rejected = len([o for o in orders if o.get('status') == 'REJECTED'])
    
    return {
        "total_buy_orders": total_buy,
        "total_sell_orders": total_sell,
        "total_completed_orders": total_completed,
        "total_open_orders": total_open,
        "total_rejected_orders": total_rejected
    }

# --- STABLE ALIASES (RESTORED) ---
map_order_data = transform_order_data
map_trade_data = transform_trade_data
map_position_data = transform_positions_data
transform_order_book = transform_order_data
transform_trade_book = transform_trade_data
transform_tradebook_data = transform_trade_data
map_positions_data = transform_positions_data
map_order_book_data = transform_order_data
map_trade_book_data = transform_trade_data
map_funds_data = lambda data: data # Pass-through for funds
# -----------------------------------------------
