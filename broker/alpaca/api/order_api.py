from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, OrderStatus
from utils.logging import get_logger
from broker.alpaca.mapping.transform_data import transform_data

logger = get_logger(__name__)

def get_alpaca_client(auth):
    """
    Construct Alpaca TradingClient from auth token.
    auth: MODE:::API_KEY:::SECRET_KEY
    """
    try:
        parts = auth.split(":::")
        if len(parts) >= 3:
            mode = parts[0]
            api_key = parts[1]
            secret_key = parts[2]
            is_paper = (mode == "PAPER")
            # Use default SDK behavior for Paper/Live URLs
            return TradingClient(api_key, secret_key, paper=is_paper)
    except Exception as e:
        logger.error(f"Alpaca Client Error: {e}")
    return None

def place_order_api(data, auth):
    """
    Generic order placement for Alpaca (Stocks and Crypto).
    """
    client = get_alpaca_client(auth)
    if not client:
        return None, {"s": "error", "message": "Client Fail"}, None
        
    try:
        # Map OpenAlgo payload to Alpaca request
        payload = transform_data(data)
        req = payload.get('request')
        
        if not req:
            return None, {"s": "error", "message": "Mapping Fail"}, None
            
        # Submit order via Alpaca SDK
        order = client.submit_order(order_data=req)
        
        # Format response compatible with OpenAlgo dashboard
        return str(order.id), {"s": "success", "message": "Order Placed", "id": str(order.id)}, None
        
    except Exception as e:
        logger.error(f"Alpaca Order Exception: {e}")
        return None, {"s": "error", "message": str(e)}, None

def get_positions_api(auth):
    """
    Retrieve all open positions for mapping in the dashboard.
    """
    client = get_alpaca_client(auth)
    if not client: return []
    
    try:
        positions = client.get_all_positions()
        pos_list = []
        for p in positions:
            pos_list.append({
                "symbol": p.symbol,
                "quantity": float(p.qty),
                "avg_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "pnl": float(p.unrealized_pl),
                "pnl_pct": float(p.unrealized_plpc) * 100
            })
        return pos_list
    except Exception as e:
        logger.error(f"Alpaca Get Positions Error: {e}")
        return []

def get_positions(auth_token):
    """
    Service wrapper for retrieving positions.
    """
    client = get_alpaca_client(auth_token)
    if not client: return []
    try:
        return client.get_all_positions()
    except Exception as e:
        logger.error(f"Alpaca get_positions error: {e}")
        return []

def get_orders_api(auth):
    """
    Retrieve recent orders for the dashboard trade/order book.
    """
    client = get_alpaca_client(auth)
    if not client: return []
    
    try:
        # Get all closed and open orders for index
        req = GetOrdersRequest(status="all", limit=50)
        orders = client.get_orders(filter=req)
        
        order_list = []
        for o in orders:
            order_list.append({
                "id": str(o.id),
                "symbol": o.symbol,
                "type": str(o.order_type),
                "side": str(o.side),
                "status": str(o.status),
                "quantity": float(o.qty),
                "filled_qty": float(o.filled_qty) if o.filled_qty else 0.0,
                "price": float(o.limit_price) if o.limit_price else 0.0,
                "avg_price": float(o.filled_avg_price) if o.filled_avg_price else 0.0,
                "timestamp": o.created_at.timestamp()
            })
        return order_list
    except Exception as e:
        logger.error(f"Alpaca Get Orders Error: {e}")
        return []

def get_order_book(auth_token):
    """
    Retrieve raw order book for the dashboard mapping layer.
    """
    client = get_alpaca_client(auth_token)
    if not client: return []
    try:
        req = GetOrdersRequest(status="all", limit=100)
        return client.get_orders(filter=req)
    except Exception as e:
        logger.error(f"Alpaca get_order_book error: {e}")
        return []

def get_trade_book(auth_token):
    """
    Retrieve trades (filled orders) for the dashboard mapping layer.
    """
    client = get_alpaca_client(auth_token)
    if not client: return []
    try:
        # Alpaca filled orders represent the trade history
        req = GetOrdersRequest(status="closed", limit=100)
        orders = client.get_orders(filter=req)
        # Filter only filled or partially filled orders
        return [o for o in orders if o.filled_qty and float(o.filled_qty) > 0]
    except Exception as e:
        logger.error(f"Alpaca get_trade_book error: {e}")
        return []

def cancel_order(orderid, auth_token):
    """
    Cancel a single order by ID.
    """
    client = get_alpaca_client(auth_token)
    if not client:
        return {"status": "error", "message": "Client Fail"}, 500
    try:
        client.cancel_order_by_id(orderid)
        return {"status": "success", "message": f"Order {orderid} cancelled"}, 200
    except Exception as e:
        logger.error(f"Alpaca Cancel Error: {e}")
        return {"status": "error", "message": str(e)}, 400

def cancel_all_orders(order_data, auth_token):
    """
    Cancel all open orders.
    """
    client = get_alpaca_client(auth_token)
    if not client:
        return {"status": "error", "message": "Client Fail"}, 500
    try:
        # Use cancel_orders without filter to cancel all open orders
        client.cancel_orders()
        return {"status": "success", "message": "All orders cancelled"}, 200
    except Exception as e:
        logger.error(f"Alpaca Cancel All Error: {e}")
        return {"status": "error", "message": str(e)}, 400

def modify_order(order_data, auth_token):
    """
    Modify an existing order.
    If order is in 'accepted' status (Alpaca transient state), fall back to Cancel and Replace.
    """
    client = get_alpaca_client(auth_token)
    if not client:
        return {"status": "error", "message": "Client Fail"}, 500
        
    orderid = order_data.get("orderid")
    try:
        from alpaca.trading.requests import ReplaceOrderRequest
        
        # Alpaca allows modifying qty, limit_price, stop_price, time_in_force
        replace_params = {}
        
        if order_data.get("quantity"):
            replace_params["qty"] = int(float(order_data["quantity"]))
        
        if order_data.get("price") and float(order_data["price"]) > 0:
            replace_params["limit_price"] = float(order_data["price"])
            
        if order_data.get("trigger_price") and float(order_data["trigger_price"]) > 0:
            replace_params["stop_price"] = float(order_data["trigger_price"])
            
        req = ReplaceOrderRequest(**replace_params)
        modified_order = client.replace_order_by_id(orderid, req)
        
        return {"status": "success", "message": "Order Modified", "id": str(modified_order.id)}, 200
        
    except Exception as e:
        err_msg = str(e)
        logger.warning(f"Alpaca Modify Attempt Fail: {err_msg}")
        
        # Check for transient 'accepted' status error
        if "cannot replace order in accepted status" in err_msg.lower():
            logger.info(f"Triggering 'Cancel and Replace' for order {orderid}")
            try:
                # 1. Fetch original order details to get current data
                old_order = client.get_order_by_id(orderid)
                
                # 2. Cancel the old order
                client.cancel_order_by_id(orderid)
                
                # 3. Create new order data with modifications
                # We need to map Alpaca order back to OpenAlgo format or use transformed data
                new_data = {
                    "symbol": order_data.get("symbol") or old_order.symbol,
                    "exchange": order_data.get("exchange") or "ALPACA",
                    "action": order_data.get("action") or str(old_order.side).split('.')[-1].upper(),
                    "quantity": order_data.get("quantity") or float(old_order.qty),
                    "product": order_data.get("product") or "CNC",
                    "pricetype": order_data.get("pricetype") or str(old_order.order_type).split('.')[-1].upper(),
                    "price": order_data.get("price") or (float(old_order.limit_price) if old_order.limit_price else 0),
                    "trigger_price": order_data.get("trigger_price") or (float(old_order.stop_price) if old_order.stop_price else 0),
                    "strategy": "System-Modify-Fallback"
                }
                
                # 4. Place new order
                from broker.alpaca.mapping.transform_data import transform_data
                payload = transform_data(new_data)
                new_req = payload.get('request')
                new_order = client.submit_order(order_data=new_req)
                
                return {"status": "success", "message": "Order Replaced (Cancel+New)", "id": str(new_order.id)}, 200
            except Exception as e2:
                logger.error(f"Alpaca Cancel+Replace Fallback Error: {e2}")
                return {"status": "error", "message": f"Modification failed: {err_msg}"}, 400
        
        return {"status": "error", "message": err_msg}, 400

def get_positions(auth_token):
    """
    Retrieve current positions for the dashboard mapping layer.
    """
    client = get_alpaca_client(auth_token)
    if not client: return []
    try:
        return client.get_all_positions()
    except Exception as e:
        logger.error(f"Alpaca get_positions error: {e}")
        return []

def close_position_api(position_data, auth_token):
    """
    Close a single position for a specific symbol.
    """
    client = get_alpaca_client(auth_token)
    if not client:
        return {"status": "error", "message": "Client Authentication Failed"}, 401
        
    symbol = position_data.get("symbol")
    if not symbol:
        return {"status": "error", "message": "Symbol is required"}, 400
        
    try:
        # Alpaca close_position squares off the position for the symbol
        client.close_position(symbol)
        return {"status": "success", "message": f"Position closed for {symbol}"}, 200
    except Exception as e:
        error_msg = str(e)
        if "position does not exist" in error_msg.lower():
            return {"status": "success", "message": "Position already closed"}, 200
        logger.error(f"Alpaca close_position error for {symbol}: {e}")
        return {"status": "error", "message": error_msg}, 500

def close_all_positions(api_key, auth_token):
    """
    Square off all open positions in the portfolio.
    """
    client = get_alpaca_client(auth_token)
    if not client:
        return {"status": "error", "message": "Client Authentication Failed"}, 401
        
    try:
        # Square off everything and cancel pending orders
        client.close_all_positions(cancel_orders=True)
        return {"status": "success", "message": "All positions squared off"}, 200
    except Exception as e:
        logger.error(f"Alpaca close_all_positions error: {e}")
        return {"status": "error", "message": str(e)}, 500

def get_holdings(auth_token):
    """
    Retrieve holdings. For Alpaca, positions are holdings.
    """
    return get_positions(auth_token)

def get_funds(auth_token):
    """
    Retrieve account summary / funds information.
    """
    client = get_alpaca_client(auth_token)
    if not client: return None
    try:
        return client.get_account()
    except Exception as e:
        logger.error(f"Alpaca get_funds error: {e}")
        return None
