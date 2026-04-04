import os
import json
import asyncio
from utils.logging import get_logger
from broker.ibkr.mapping.transform_data import transform_data, map_product_type

logger = get_logger(__name__)

def get_ib_connection(auth, offset=0):
    """
    Establish a connection to IBKR TWS.
    auth should be in 'client_id:::port' format.
    Offset is used to allow concurrent connections (e.g. for different dashboard widgets).
    """
    try:
        import asyncio
        
        # Ensure an event loop exists in this thread BEFORE importing ib_insync
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        from ib_insync import IB, util
        
        # Apply nest_asyncio
        import nest_asyncio
        nest_asyncio.apply()

        ib = IB()
        
        client_id_str, port_str = auth.split(":::")
        client_id = int(client_id_str) + offset
        port = int(port_str)
        host = os.getenv("IBKR_HOST", "127.0.0.1")

        logger.debug(f"Connecting to IBKR TWS at {host}:{port} with ClientID {client_id}")
        ib.connect(host, port, clientId=client_id, timeout=10)
        
        # Give a small delay for synchronization
        ib.sleep(1)
        
        return ib
    except Exception as e:
        logger.error(f"Failed to connect to IBKR TWS (ClientID {client_id if 'client_id' in locals() else 'unknown'}): {e}")
        return None

def place_order_api(data, auth):
    """
    Place a new order on IBKR TWS.
    """
    ib = get_ib_connection(auth)
    if not ib:
        return None, {"s": "error", "message": "Failed to connect to IBKR TWS"}, None

    try:
        from ib_insync import MarketOrder, LimitOrder, StopOrder, Contract
        
        # Transform data
        payload = transform_data(data)
        logger.debug(f"Transformed IBKR order: {payload}")

        contract = payload['contract']
        order = payload['order']

        # Qualify contract
        ib.qualifyContracts(contract)

        # Place trade
        trade = ib.placeOrder(contract, order)
        
        # Wait a bit for status or check synchronously
        # For simplicity, we return the orderId
        orderid = str(trade.order.orderId)
        
        logger.info(f"Order placed successfully on IBKR. Order ID: {orderid}")
        
        response_data = {
            "s": "ok",
            "id": orderid,
            "status": trade.orderStatus.status,
            "message": "Order placed successfully"
        }
        
        # In OpenAlgo, 'response' should be an object with .status property
        class FakeResponse:
            def __init__(self, status):
                self.status = status
            def json(self):
                return response_data

        return FakeResponse(200), response_data, orderid

    except Exception as e:
        logger.error(f"Error during IBKR order placement: {e}")
        return None, {"s": "error", "message": str(e)}, None
    finally:
        ib.disconnect()

def get_order_book(auth):
    ib = get_ib_connection(auth)
    if not ib:
        return {"s": "error", "message": "Failed to connect to IBKR TWS"}

    try:
        # Request ALL orders (Open and Completed) from ALL clients (apiOnly=False)
        ib.reqAllOpenOrders()
        ib.reqCompletedOrders(apiOnly=False)
        ib.reqExecutions() # Refresh execution list to help populate trades
        ib.sleep(2) 
        
        trades = ib.trades()
        logger.info(f"IBKR trades found: {len(trades)}")
        
        # If still empty, try to refresh from executions
        if not trades:
            executions = ib.executions()
            if executions:
                logger.info(f"IBKR found {len(executions)} executions. Trying to recover trades...")
                ib.sleep(1)
                trades = ib.trades()

        orders_list = []
        for trade in trades:
            last_time = ""
            if trade.log:
                last_time = trade.log[-1].time.isoformat() if trade.log[-1].time else ""
            
            # Map action
            action = trade.order.action
            if action == 'BOT': action = 'BUY'
            elif action == 'SLD': action = 'SELL'
            
            orders_list.append({
                "id": str(trade.order.orderId) if trade.order.orderId != 0 else str(trade.order.permId),
                "symbol": trade.contract.localSymbol or trade.contract.symbol,
                "exchange": trade.contract.exchange or "IBKR",
                "action": action,
                "quantity": float(trade.order.totalQuantity),
                "status": trade.orderStatus.status,
                "price": float(trade.order.lmtPrice if trade.order.orderType == 'LMT' else 0.0),
                "trigger_price": float(trade.order.auxPrice if 'STOP' in trade.order.orderType else 0.0),
                "pricetype": trade.order.orderType,
                "product": "NRML",
                "filled_quantity": float(trade.orderStatus.filled),
                "avg_price": float(trade.orderStatus.avgFillPrice),
                "timestamp": last_time
            })
        
        logger.info(f"Retrieved {len(orders_list)} orders from IBKR")
        return {"s": "ok", "orderBook": orders_list}
    finally:
        ib.disconnect()

def get_positions(auth):
    # Use different clientId for positions to avoid collision with orderbook
    ib = get_ib_connection(auth, offset=1)
    if not ib:
        return {"s": "error", "message": "Failed to connect to IBKR TWS"}

    try:
        # IBKR automatically starts account updates upon connection if enabled.
        # We wait for the existing background sync to fill ib.portfolio() and ib.positions().
        ib.sleep(3) # Increase wait for full background synchronization
        
        # Use portfolio items to get more details if available
        portfolio = {f"{item.contract.conId}_{item.account}": item for item in ib.portfolio()}
        
        positions = ib.positions()
        positions_list = []
        for pos in positions:
            symbol = pos.contract.localSymbol or pos.contract.symbol
            
            # Find matching portfolio item if possible
            key = f"{pos.contract.conId}_{pos.account}"
            pf_item = portfolio.get(key)
            
            ltp = float(pf_item.marketPrice) if pf_item else 0.0
            pnl = float(pf_item.unrealizedPNL) if pf_item else 0.0
            
            positions_list.append({
                "symbol": symbol,
                "exchange": pos.contract.exchange,
                "productType": "NRML", 
                "netQty": float(pos.position),
                "avgPrice": float(pos.avgCost),
                "account": pos.account,
                "ltp": ltp,
                "pnl": pnl
            })
        
        logger.info(f"Retrieved {len(positions_list)} positions from IBKR")
        return {"s": "ok", "netPositions": positions_list}
    except Exception as e:
        logger.error(f"Error fetching IBKR positions: {e}")
        return {"s": "error", "message": str(e)}
    finally:
        ib.disconnect()

def get_trade_book(auth):
    ib = get_ib_connection(auth)
    if not ib:
        return {"s": "error", "message": "Failed to connect to IBKR TWS"}

    try:
        fills = ib.fills()
        trades_list = []
        for fill in fills:
            # Map side
            side = fill.execution.side
            if side == 'BOT': side = 'BUY'
            elif side == 'SLD': side = 'SELL'
            
            trades_list.append({
                "orderId": str(fill.execution.orderId),
                "symbol": fill.contract.localSymbol or fill.contract.symbol,
                "exchange": fill.contract.exchange,
                "action": side,
                "quantity": float(fill.execution.shares),
                "price": float(fill.execution.avgPrice),
                "tradeId": fill.execution.execId,
                "timestamp": fill.execution.time.isoformat() if fill.execution.time else ""
            })
        return {"s": "ok", "tradebook": trades_list}
    finally:
        ib.disconnect()

def cancel_order(orderid, auth):
    ib = get_ib_connection(auth)
    if not ib:
        return {"s": "error", "message": "Failed to connect to IBKR TWS"}, 500

    try:
        # Find order in trades
        trades = [t for t in ib.trades() if str(t.order.orderId) == orderid]
        if not trades:
            return {"s": "error", "message": "Order not found"}, 404
        
        trade = trades[0]
        ib.cancelOrder(trade.order)
        
        # Check status
        # ib.sleep(1)
        
        return {"s": "ok", "id": orderid, "status": "cancelled"}, 200
    finally:
        ib.disconnect()

def modify_order(data, auth):
    # For IBKR, modify is just re-placing with same orderId or using modifyOrder
    ib = get_ib_connection(auth)
    if not ib:
        return {"s": "error", "message": "Failed to connect to IBKR TWS"}, 500

    try:
        from ib_insync import LimitOrder, StopOrder
        orderid = int(data.get('order_id'))
        
        # Find trade
        trades = [t for t in ib.trades() if t.order.orderId == orderid]
        if not trades:
            return {"s": "error", "message": "Order not found"}, 404
        
        trade = trades[0]
        order = trade.order
        
        # Update price/qty
        if 'price' in data:
            order.lmtPrice = float(data['price'])
        if 'quantity' in data:
            order.totalQuantity = int(data['quantity'])
            
        ib.placeOrder(trade.contract, order)
        
        return {"s": "ok", "orderid": str(orderid)}, 200
    finally:
        ib.disconnect()

def get_open_position(tradingsymbol, exchange, product, auth):
    positions_data = get_positions(auth)
    net_qty = "0"

    if positions_data and positions_data.get("s") == "ok":
        for position in positions_data.get("netPositions", []):
            if position.get("symbol") == tradingsymbol:
                net_qty = position.get("netQty", "0")
                break

    return net_qty

def cancel_all_orders_api(data, auth):
    ib = get_ib_connection(auth)
    if not ib:
        return [], []
    
    try:
        cancelled = []
        failed = []
        for trade in ib.openTrades():
            try:
                ib.cancelOrder(trade.order)
                cancelled.append(str(trade.order.orderId))
            except:
                failed.append(str(trade.order.orderId))
        return cancelled, failed
    finally:
        ib.disconnect()

def close_all_positions(current_api_key, auth):
    ib = get_ib_connection(auth)
    if not ib:
        return {"s": "error", "message": "Failed to connect to IBKR TWS"}, 500

    try:
        from ib_insync import MarketOrder
        for pos in ib.positions():
            action = "SELL" if pos.position > 0 else "BUY"
            qty = abs(pos.position)
            order = MarketOrder(action, qty)
            ib.placeOrder(pos.contract, order)
        
        return {"status": "success", "message": "All positions closure initiated"}, 200
    finally:
        ib.disconnect()

def place_smartorder_api(data, auth):
    # Follow the pattern from other brokers
    symbol = data.get("symbol")
    exchange = data.get("exchange")
    product = data.get("product")
    position_size = int(data.get("position_size", "0"))

    current_position = int(get_open_position(symbol, exchange, product, auth))

    action = None
    quantity = 0

    if position_size == 0 and current_position == 0 and int(data["quantity"]) != 0:
        action = data["action"]
        quantity = data["quantity"]
        return place_order_api(data, auth)

    elif position_size == current_position:
        return None, {"status": "success", "message": "Position size matches current position"}, None

    if position_size == 0 and current_position > 0:
        action = "SELL"
        quantity = abs(current_position)
    elif position_size == 0 and current_position < 0:
        action = "BUY"
        quantity = abs(current_position)
    elif current_position == 0:
        action = "BUY" if position_size > 0 else "SELL"
        quantity = abs(position_size)
    else:
        if position_size > current_position:
            action = "BUY"
            quantity = position_size - current_position
        elif position_size < current_position:
            action = "SELL"
            quantity = current_position - position_size

    if action:
        order_data = data.copy()
        order_data["action"] = action
        order_data["quantity"] = str(quantity)
        return place_order_api(order_data, auth)
    
    return None, {"status": "error", "message": "No action determined"}, None
