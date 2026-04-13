from datetime import datetime
from alpaca.trading.enums import OrderStatus

def map_order_data(order_data):
    """
    Map Alpaca SDK Order objects to dictionary format.
    Expects keys: orderid, symbol, exchange, pricetype, action, order_status, quantity, price, trigger_price, timestamp
    """
    if not isinstance(order_data, list):
        return []
        
    mapped_orders = []
    for o in order_data:
        # Normalize status to Dashboard expectations: open, complete, rejected, cancelled, pending
        raw_status = str(o.status).split('.')[-1].lower()
        if raw_status in ["open", "partially_filled", "held"]:
            status = "open"
        elif raw_status in ["new", "accepted", "pending_new", "accepted_for_bidding", "suspended"]:
            status = "pending"
        elif raw_status == "filled":
            status = "complete"
        elif raw_status == "rejected":
            status = "rejected"
        else:
            status = "cancelled"

        mapped_orders.append({
            "orderid": str(o.id),
            "symbol": o.symbol,
            "exchange": "ALPACA",
            "product": "CNC",
            "pricetype": str(o.order_type).split('.')[-1].upper(),
            "action": str(o.side).split('.')[-1].upper(),
            "order_status": status,
            "quantity": float(o.qty) if o.qty else 0.0,
            "filled_quantity": float(o.filled_qty) if o.filled_qty else 0.0,
            "price": float(o.limit_price) if o.limit_price else 0.0,
            "trigger_price": float(o.stop_price) if o.stop_price else 0.0,
            "average_price": float(o.filled_avg_price) if o.filled_avg_price else 0.0,
            "timestamp": o.created_at.isoformat() if hasattr(o.created_at, 'isoformat') else str(o.created_at),
            "tag": o.client_order_id
        })
    return mapped_orders

def calculate_order_statistics(order_data):
    """
    Calculate summary stats for the dashboard.
    """
    stats = {
        "total_orders": len(order_data),
        "total_buy_orders": 0,
        "total_sell_orders": 0,
        "total_open_orders": 0,
        "total_completed_orders": 0,
        "total_rejected_orders": 0,
        "total_cancelled_orders": 0
    }
    
    for o in order_data:
        status = o.get("order_status", "").lower()
        side = o.get("action", "").upper()
        
        if side == "BUY":
            stats["total_buy_orders"] += 1
        elif side == "SELL":
            stats["total_sell_orders"] += 1

        if status in ["open", "pending"]:
            stats["total_open_orders"] += 1
        elif status == "complete":
            stats["total_completed_orders"] += 1
        elif status == "rejected":
            stats["total_rejected_orders"] += 1
        elif status == "cancelled":
            stats["total_cancelled_orders"] += 1
            
    return stats

def transform_order_data(order_data):
    """
    Final field transformation for dashboard display compatibility.
    """
    return order_data

def map_position_data(positions):
    """
    Map Alpaca SDK Position objects to dictionary format.
    """
    if not isinstance(positions, list):
        return []
        
    mapped_positions = []
    for p in positions:
        qty = float(p.qty) if p.qty is not None else 0.0
        mapped_positions.append({
            "symbol": p.symbol,
            "exchange": "ALPACA",
            "product": "CNC",
            "quantity": qty,
            "qty": qty,  # Redundant for compatibility
            "side": "BUY" if qty > 0 else "SELL",
            "average_price": float(p.avg_entry_price) if p.avg_entry_price else 0.0,
            "ltp": float(p.current_price) if p.current_price else 0.0,
            "pnl": float(p.unrealized_pl) if p.unrealized_pl else 0.0,
            "pnlpercent": float(p.unrealized_plpc) * 100 if p.unrealized_plpc else 0.0,
            "market_value": float(p.market_value) if p.market_value else 0.0
        })
    return mapped_positions

def transform_positions_data(positions_data):
    """
    Final field transformation for dashboard display compatibility.
    """
    return positions_data

def map_trade_data(trade_data):
    """
    Map Alpaca filled orders to Trade format.
    """
    if not isinstance(trade_data, list):
        return []
        
    mapped_trades = []
    for t in trade_data:
        avg_price = float(t.filled_avg_price) if t.filled_avg_price else 0.0
        qty = float(t.filled_qty) if t.filled_qty else 0.0
        mapped_trades.append({
            "trade_id": f"TR_{t.id}",
            "orderid": str(t.id),
            "symbol": t.symbol,
            "exchange": "ALPACA",
            "product": "CNC",
            "action": str(t.side).split('.')[-1].upper(),
            "quantity": qty,
            "average_price": avg_price,
            "trade_value": qty * avg_price,
            "timestamp": t.filled_at.isoformat() if t.filled_at else str(t.created_at)
        })
    return mapped_trades

def transform_tradebook_data(trade_data):
    """
    Final field transformation for dashboard display compatibility.
    """
    return trade_data

def map_portfolio_data(positions):
    """
    Map Alpaca positions to Portfolio format (Holdings).
    """
    # Alpaca positions function as holdings in OpenAlgo interface
    return map_position_data(positions)

def calculate_portfolio_statistics(holdings_data):
    """
    Calculate summary statistics for the holdings portfolio.
    """
    total_inv_value = 0.0
    total_holding_value = 0.0
    total_pnl = 0.0
    
    for h in holdings_data:
        qty = h.get("quantity", 0.0)
        avg_price = h.get("average_price", 0.0)
        ltp = h.get("ltp", 0.0)
        pnl = h.get("pnl", 0.0)
        
        # Investment is abs(qty * avg_price) to handle both long and short
        total_inv_value += abs(qty * avg_price)
        total_holding_value += abs(qty * ltp)
        total_pnl += pnl
        
    pnl_percent = (total_pnl / total_inv_value * 100) if total_inv_value != 0 else 0.0
    
    return {
        "totalinvvalue": total_inv_value,
        "totalholdingvalue": total_holding_value,
        "totalprofitandloss": total_pnl,
        "totalpnlpercentage": pnl_percent
    }

def transform_holdings_data(holdings_data):
    """
    Final field transformation for dashboard display compatibility.
    """
    return holdings_data

def map_funds_data(account):
    """
    Map Alpaca account to Margin format.
    """
    if not account:
        return {}
        
    # Account summary usually includes equity, cash, and buying power
    # We calculate today's total profit by comparing equity with the last market close equity
    equity = float(account.equity) if account.equity else 0.0
    last_equity = float(account.last_equity) if account.last_equity else equity
    total_pnl_today = equity - last_equity
    
    return {
        "availablecash": float(account.cash) if account.cash else 0.0,
        "collateral": (float(account.equity) - float(account.cash)) if account.equity and account.cash else 0.0,
        "m2munrealized": total_pnl_today,
        "m2mrealized": 0.0, # Alpaca doesn't split realized/unrealized in account summary for today
        "utiliseddebits": float(account.initial_margin) if account.initial_margin else 0.0
    }
