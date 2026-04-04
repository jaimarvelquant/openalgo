from utils.logging import get_logger

logger = get_logger(__name__)

def map_order_data(order_data):
    """
    Extracts the order list from the IBKR API response.
    """
    if not order_data or order_data.get("s") != "ok":
        return []
    return order_data.get("orderBook", [])

def calculate_order_statistics(order_data):
    """
    Calculates statistics from order data.
    """
    total_buy_orders = 0
    total_sell_orders = 0
    total_completed_orders = 0
    total_open_orders = 0
    total_rejected_orders = 0

    for order in order_data:
        action = order.get("action", "").upper()
        if action == "BUY":
            total_buy_orders += 1
        elif action == "SELL":
            total_sell_orders += 1

        status = order.get("status", "").lower()
        if status in ["filled", "complete"]:
            total_completed_orders += 1
        elif status in ["submitted", "presubmitted", "open"]:
            total_open_orders += 1
        elif status in ["inactive", "rejected"]:
            total_rejected_orders += 1

    return {
        "total_buy_orders": total_buy_orders,
        "total_sell_orders": total_sell_orders,
        "total_completed_orders": total_completed_orders,
        "total_open_orders": total_open_orders,
        "total_rejected_orders": total_rejected_orders,
    }

def transform_order_data(order_data):
    """
    Standardizes IBKR order data for the OpenAlgo frontend.
    """
    import math
    transformed = []
    for order in order_data:
        # Standardize status
        status = order.get("status", "").lower()
        if status in ["filled", "complete"]:
            status = "complete"
        elif status in ["submitted", "presubmitted", "open"]:
            status = "open"
        elif status in ["inactive", "rejected"]:
            status = "rejected"
        elif status in ["cancelled", "api_cancelled"]:
            status = "cancelled"

        qty = float(order.get("quantity", 0))
        filled_qty = float(order.get("filled_quantity", 0))
        price = float(order.get("price", 0.0))
        avg_price = float(order.get("avg_price", 0.0))
        trigger_price = float(order.get("trigger_price", 0.0))

        # NaN safety
        if math.isnan(qty): qty = 0.0
        if math.isnan(filled_qty): filled_qty = 0.0
        if math.isnan(price): price = 0.0
        if math.isnan(avg_price): avg_price = 0.0
        if math.isnan(trigger_price): trigger_price = 0.0

        transformed.append({
            "orderid": order.get("id"),
            "symbol": order.get("symbol"),
            "exchange": order.get("exchange", "IBKR"),
            "action": order.get("action"),
            "quantity": qty,
            "filledqty": filled_qty,
            "price": price,
            "trigger_price": trigger_price,
            "avg_price": avg_price,
            "status": status,
            "order_status": status,
            "pricetype": order.get("pricetype"),
            "product": order.get("product", "NRML"),
            "timestamp": order.get("timestamp", "")
        })
    return transformed

def map_position_data(position_data):
    """
    Extracts positions from IBKR API response.
    """
    if not position_data or position_data.get("s") != "ok":
        return []
    return position_data.get("netPositions", [])

def transform_positions_data(positions_data):
    """
    Standardizes IBKR position data for the OpenAlgo frontend.
    """
    import math
    transformed = []
    for pos in positions_data:
        qty = float(pos.get("netQty", 0))
        avg_price = float(pos.get("avgPrice", 0))
        pnl = float(pos.get("pnl", 0.0))
        ltp = float(pos.get("ltp", 0.0))
        
        # Replace NaN with 0.0 for frontend safety
        if math.isnan(pnl): pnl = 0.0
        if math.isnan(ltp): ltp = 0.0
        if math.isnan(avg_price): avg_price = 0.0
        if math.isnan(qty): qty = 0.0
        
        # Calculate PnL percentage if possible
        pnl_percent = 0.0
        if avg_price > 0 and abs(qty) > 0:
            investment = abs(avg_price * qty)
            pnl_percent = (pnl / investment) * 100
            
        if math.isnan(pnl_percent): pnl_percent = 0.0
            
        transformed.append({
            "symbol": str(pos.get("symbol") or ""),
            "exchange": str(pos.get("exchange") or "IBKR"),
            "product": str(pos.get("productType", "NRML")),
            "quantity": qty,
            "average_price": avg_price,
            "ltp": ltp,
            "pnl": pnl,
            "pnlpercent": pnl_percent
        })
    return transformed

def map_trade_data(trade_data):
    """
    Extracts trade data from IBKR API response.
    """
    if not trade_data or trade_data.get("s") != "ok":
        return []
    return trade_data.get("tradebook", [])

def transform_tradebook_data(trade_data):
    """
    Standardizes IBKR trade data for the OpenAlgo frontend.
    """
    import math
    transformed = []
    for trade in trade_data:
        qty = float(trade.get("quantity", 0))
        price = float(trade.get("price", 0.0))
        
        if math.isnan(qty): qty = 0.0
        if math.isnan(price): price = 0.0

        transformed.append({
            "orderid": trade.get("orderId"),
            "tradeId": trade.get("tradeId"),
            "symbol": trade.get("symbol"),
            "exchange": trade.get("exchange"),
            "action": trade.get("action"),
            "quantity": qty,
            "price": price,
            "timestamp": trade.get("timestamp", "")
        })
    return transformed
