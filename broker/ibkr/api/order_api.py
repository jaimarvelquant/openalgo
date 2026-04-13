import os
import json
import asyncio
import random
import math
from datetime import datetime
from utils.logging import get_logger
from broker.ibkr.mapping.transform_data import transform_data, map_product_type

logger = get_logger(__name__)

def safe_float(val, d=4):
    try:
        f = float(val)
        if math.isnan(f) or math.isinf(f): return 0.0
        return round(f, d)
    except: return 0.0

def get_ib_connection(auth, offset=0, specific_cid=None):
    try:
        import asyncio
        import nest_asyncio
        
        # THREAD-SPECIFIC LOOP (Flask Helper): Ensure current thread has an active loop
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Apply nested policy to the thread-local loop
        nest_asyncio.apply(loop)
        
        from ib_insync import IB
            
        cid_str, port_str = auth.split(":::")
        bcid = int(cid_str); port = int(port_str); host = os.getenv("IBKR_HOST", "127.0.0.1")
        ib = IB()
        
        # DYNAMIC LANE DISCOVERY: Use a randomized base to prevent collision in concurrent API envs
        tid = specific_cid if specific_cid is not None else random.randint(1000, 9999)
        
        for attempt in range(5):
            try:
                # Use a stable incremental shift for lane discovery
                current_id = (tid + (attempt * 10)) % 65535
                if current_id == 0: current_id = random.randint(1, 1000)
                
                print(f"[SERVICE PULSE] IBKR Connect Attempt {attempt+1}: cid={current_id} on port {port}")
                # Increased timeout to 10s for more stability
                ib.connect(host, port, clientId=current_id, timeout=10)
                if ib.isConnected(): 
                    print(f"[SERVICE PULSE] IBKR Connected Successfully (cid={current_id})")
                    # Wait for API to be ready
                    ib.sleep(0.5)
                    return ib
            except Exception as e:
                print(f"[SERVICE PULSE] IBKR Connect Failed (cid={current_id}): {e}")
                if ib.isConnected(): ib.disconnect()
                # Random jittered sleep between attempts
                ib.sleep(0.2 + random.random() * 0.3)
                continue
        return None
    except Exception as e:
        logger.error(f"Connect fail: {e}"); return None

def place_order_api(data, auth):
    # USE MASTER ID (0) for all orders if possible to ensure priority
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: ib = get_ib_connection(auth, offset=0)
    if not ib: return None, {"s": "error", "message": "Conn Fail"}, None
    try:
        from ib_insync import MarketOrder, LimitOrder
        payload = transform_data(data); contract = payload['contract']; order = payload['order']
        
        # DYNAMIC HIJACK: Match exact contract from live portfolio
        ib.reqPositions(); ib.sleep(1)
        target_sym = str(data.get("symbol", "")).strip()
        for p in ib.positions():
            psym = str(p.contract.localSymbol or p.contract.symbol).strip()
            if psym == target_sym:
                contract = p.contract
                if contract.symbol == 'CL': contract.multiplier = '1000' # CL GUARD
                break
        
        ib.qualifyContracts(contract)
        if order.orderType == 'MKT':
            # 1% slippage for Safety instead of 10%
            tickers = ib.reqTickers(contract); ib.sleep(1)
            t = tickers[0] if tickers else None
            p = (t.marketPrice() or t.last or t.close) if t else None
            if not (p is None or p <= 0 or math.isnan(p)):
                limit_p = round((p * 0.99 if order.action == 'SELL' else p * 1.01) * 20) / 20
                order = LimitOrder(order.action, order.totalQuantity, limit_p)
        
        trade = ib.placeOrder(contract, order)
        # FORCE SYNC: Wait for TWS to return the REAL PermID (max 3 seconds)
        for i in range(30):
            ib.waitOnUpdate(0.1)
            if trade.order.permId and trade.order.permId != 0:
                break
        
        orderid = str(trade.order.permId)
        
        # MOCK response object with .status = 200 to satisfy the service layer
        from types import SimpleNamespace
        mock_res = SimpleNamespace(status=200)
        
        return mock_res, {"s": "ok", "orderid": orderid, "id": orderid, "status": "success"}, orderid
    finally:
        if ib: ib.disconnect()

def get_order_book(auth):
    cache_path = os.path.join("db", "ibkr_orders_cache.json")
    ib = get_ib_connection(auth, offset=15)
    cl = []
    if not ib: return {"s": "ok", "status": "success", "orderBook": cl}
    try:
        ib.reqAllOpenOrders(); ib.reqCompletedOrders(apiOnly=False); ib.reqExecutions(); ib.sleep(8) 
        ft = []; seen = set()
        for t in ib.openTrades() + ib.trades():
            if t.order.permId not in seen: ft.append(t); seen.add(t.order.permId)
        ol = []
        for trade in ft:
            pids = str(trade.order.permId); st = str(trade.orderStatus.status or "submitted").lower()
            tq = safe_float(trade.order.totalQuantity, 1); fq = safe_float(trade.orderStatus.filled, 1)
            tp = str(trade.order.orderType or "LMT")
            t_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for ln in reversed(trade.log):
                if ln.time: t_str = ln.time.strftime("%Y-%m-%d %H:%M:%S"); break
            ol.append({
                "id": pids, "orderId": pids, "symbol": str(trade.contract.localSymbol or trade.contract.symbol),
                "exchange": str(trade.contract.exchange or "IDEALPRO"),
                "action": 'BUY' if trade.order.action in ('BUY', 'BOT') else 'SELL',
                "quantity": tq, "qty": tq, "status": st,
                "price": safe_float(trade.order.lmtPrice or 0.0),
                "trigger_price": safe_float(trade.order.auxPrice or 0.0),
                "type": tp, "pricetype": tp, "product": "NRML", "productType": "NRML",
                "filled_quantity": fq, "avg_price": safe_float(trade.orderStatus.avgFillPrice),
                "timestamp": t_str, "time": t_str, "currency": "USD"
            })
        ol.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        try:
            with open(cache_path, "w") as f:
                json.dump({"orderBook": ol}, f)
        except:
            pass
        return {"s": "ok", "status": "success", "orderBook": ol, "data": ol, "orders": ol}
    finally:
        if ib: ib.disconnect()

def get_positions(auth):
    cache_path = os.path.join("db", "ibkr_positions_cache.json")
    cl = []
    if os.path.exists(cache_path):
        try:
            with open(cache_path, "r") as f: cl = json.load(f).get("netPositions", [])
        except: pass
    ib = get_ib_connection(auth) 
    if not ib: return {"s": "ok", "status": "success", "netPositions": cl, "positions": cl, "data": cl}
    try:
        # Step 1: Deep Sync - Request fresh data across ALL discovered accounts
        ib.reqPositions()
        
        # Financial Advisor / Managed Account Guard: Explicitly request updates for every ID
        managed = ib.managedAccounts()
        print(f"[SERVICE PULSE] IBKR Discovery: Searching {len(managed)} managed accounts: {managed}")
        if not managed:
            ib.client.reqAccountUpdates(True, "")
        else:
            for acc in managed:
                ib.client.reqAccountUpdates(True, acc)
            
        # Reactive Soak: Wait for the wrapper to populate
        for _ in range(15):
            ib.waitOnUpdate(0.2)
            if ib.positions() or ib.portfolio():
                break
        
        # Merge Positions and Portfolio
        raw_pos = ib.positions()
        raw_port = ib.portfolio()
        
        # Deduplicated map using (conId, account) as key
        merged = {}
        for p in raw_pos:
            merged[f"{p.contract.conId}_{p.account}"] = {"contract": p.contract, "qty": p.position, "avg_p": p.avgCost, "account": p.account}
        
        for p in raw_port:
            key = f"{p.contract.conId}_{p.account}"
            if key not in merged or merged[key]["qty"] == 0:
                merged[key] = {"contract": p.contract, "qty": p.position, "avg_p": p.averageCost, "account": p.account}

        if not merged:
             return {"s": "ok", "status": "success", "netPositions": [], "positions": [], "data": []}

        # 2. Optimized Loop: Skip expensive network calls (qualify/tickers)
        # Use info already in the portfolio object for speed
        p_items = {f"{it.contract.conId}_{it.account}": it for it in raw_port}
        
        pl = []
        for key, p_data in merged.items():
            qty = safe_float(p_data["qty"], 1)
            # if qty == 0: continue # REMOVED: Show all even if zero
            
            contract = p_data["contract"]
            account = p_data["account"]
            raw_avg = safe_float(p_data["avg_p"])
            sym = str(contract.localSymbol or contract.symbol)
            
            # Use Portfolio market price directly (Very fast, no extra request)
            it = p_items.get(f"{contract.conId}_{account}")
            ltp = safe_float(it.marketPrice) if it else 0.0
            
            # Unit Price logic (Screen Price vs Contract Value)
            mult = safe_float(getattr(contract, 'multiplier', 1) or 1)
            
            # Divide by multiplier to get the 'Screen Price' (e.g. 0.15 instead of 150)
            avg_p = raw_avg / mult if mult > 0 else raw_avg
            
            # P&L and Account
            pnl = safe_float(it.unrealizedPNL, 2) if it else 0.0
            
            # EXCHANGE IDENTIFICATION
            exch = str(contract.exchange or contract.primaryExchange or "IBKR")
            if "IDEALPRO" in exch.upper(): exch = "IDEALPRO"
            if "NYMEX" in exch.upper(): exch = "NYMEX"

            pl.append({
                "tradingsymbol": sym, "symbol": sym, 
                "exchange": exch, 
                "productType": "NRML", "product": "NRML", "producttype": "NRML",
                "quantity": qty, "netqty": qty, "qty": qty,
                "average_price": safe_float(avg_p, 4), "averagePrice": safe_float(avg_p, 4),
                "account": str(account), 
                "ltp": safe_float(ltp, 4),
                "pnl": safe_float(pnl, 2), "unrealized_pnl": safe_float(pnl, 2), "currency": "USD"
            })

        print(f"[SERVICE PULSE] >>> IBKR SYNC: {len(pl)} positions matched to contract currency. <<<")
            
        # Final Processing
        final_pl = pl
        
        # WE NO LONGER FALLBACK TO 'cl' (old cache) if we found nothing - this prevents old positions from lingering
        try:
            with open(cache_path, "w") as f:
                json.dump({"netPositions": final_pl}, f)
        except Exception as e:
            logger.error(f"Failed to write IBKR cache: {e}")

        # logger.debug(f"[SERVICE PULSE] >>> IBKR SYNC: Sending {len(final_pl)} LIVE active items to Dashboard. <<<")
        return {"s": "ok", "status": "success", "netPositions": final_pl, "positions": final_pl, "data": final_pl}
    except Exception as e:
        logger.error(f"IBKR Get Positions Error: {e}")
        # Only return cache as a last resort on CONNECTION CRASH
        return {"s": "ok", "status": "success", "netPositions": cl, "positions": cl, "data": cl}
    finally:
        if ib: ib.disconnect()

def get_trade_book(auth):
    ib = get_ib_connection(auth, offset=35)
    if not ib: return {"s": "error", "message": "Conn Fail"}
    try:
        ib.reqExecutions(); ib.sleep(8)
        tl = []
        for fl in ib.fills():
            q = safe_float(fl.execution.shares, 1); p = safe_float(fl.execution.avgPrice); val = safe_float(q * p, 2)
            tl.append({
                "orderId": str(fl.execution.permId), "order_id": str(fl.execution.permId),
                "symbol": str(fl.contract.localSymbol or fl.contract.symbol),
                "exchange": str(fl.contract.exchange or "IBKR"), 
                "action": 'BUY' if fl.execution.side == 'BOT' else 'SELL',
                "quantity": q, "qty": q, "price": p, "fillprice": p, "averageprice": p, "avg_price": p, "avgprice": p,
                "trade_value": val, "value": val, "trade_val": val, "tradevalue": val,
                "product": "NRML", "productType": "NRML", "product_type": "NRML",
                "tradeId": str(fl.execution.execId), "trade_id": str(fl.execution.execId),
                "timestamp": fl.execution.time.strftime("%Y-%m-%d %H:%M:%S") if fl.execution.time else datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "time": fl.execution.time.strftime("%H:%M:%S") if fl.execution.time else "", "currency": "USD"
            })
        tl.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return {"s": "ok", "status": "success", "tradebook": tl, "trades": tl, "data": tl}
    finally:
        if ib: ib.disconnect()

def cancel_order(orderid, auth):
    """Cancel an existing order by reconnecting as the original owner (Robust)"""
    # Step 1: DISCOVER owner via Master (0)
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: return {"s": "error", "message": "Conn Fail"}, 500
    
    found_cid = None
    try:
        oids = str(orderid).strip()
        ib.reqAllOpenOrders(); ib.sleep(2)
        target_trade = next((t for t in ib.openTrades() if str(t.order.permId) == oids), None)
        if not target_trade:
             return {"s": "error", "message": f"Order {oids} not found"}, 404
        found_cid = target_trade.order.clientId
    finally:
        ib.disconnect()

    # Step 2: RECONNECT as Owner to perform cancellation
    logger.info(f"[SERVICE PULSE] Cancelling Order {oids} via original Owner CID {found_cid}")
    ib = get_ib_connection(auth, specific_cid=found_cid)
    if not ib: return {"s": "error", "message": f"Could not connect as Owner CID {found_cid}"}, 500
    
    try:
        ib.reqAllOpenOrders(); ib.sleep(1.5)
        for t in ib.openTrades():
            if str(t.order.permId) == oids:
                ib.cancelOrder(t.order)
                ib.sleep(2) # Soak for TWS state change
                return {"s": "ok", "status": "success", "orderid": oids, "message": "Cancellation sent as session owner"}, 200
        return {"s": "error", "message": "Order lost during reconnection"}, 404
    finally:
        if ib: ib.disconnect()

def modify_order(data, auth):
    """Modify an existing order by reconnecting as the original owner clientId (Robust)"""
    # Step 1: DISCOVER owner via Master (0)
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: return {"s": "error", "message": "Conn Fail"}, 500
    
    found_info = None
    try:
        oid = str(data.get('orderid') or data.get('order_id', '')).strip()
        ib.reqAllOpenOrders(); ib.sleep(2)
        for t in ib.openTrades():
            if str(t.order.permId) == oid:
                found_info = {"cid": t.order.clientId, "oid": t.order.orderId}
                break
        if not found_info:
            return {"s": "error", "message": f"Order {oid} not found in open trades"}, 404
    finally:
        ib.disconnect()

    # Step 2: RECONNECT as Owner to perform modification
    target_cid = found_info["cid"]
    logger.info(f"[SERVICE PULSE] Modifying Order {oid} via original Owner CID {target_cid}")
    
    ib = get_ib_connection(auth, specific_cid=target_cid)
    if not ib: return {"s": "error", "message": f"Could not connect as Owner CID {target_cid}"}, 500
    
    try:
        # Re-fetch to confirm state on the owner connection
        ib.reqAllOpenOrders(); ib.sleep(1.5)
        target_trade = next((t for t in ib.openTrades() if str(t.order.permId) == oid), None)
        
        if not target_trade:
             return {"s": "error", "message": "Order lost during reconnection"}, 404
             
        o = target_trade.order; contract = target_trade.contract
        
        # Hardened Modification
        modified = False
        if 'price' in data and data['price'] is not None:
            o.lmtPrice = float(data['price']); modified = True
        if 'trigger_price' in data and data['trigger_price'] is not None:
             if hasattr(o, 'auxPrice'): o.auxPrice = float(data['trigger_price']); modified = True
        if 'quantity' in data and data['quantity'] is not None:
            o.totalQuantity = int(float(data['quantity'])); modified = True
            
        if modified:
            # IMPORTANT: NO orderId reset! We are the owner.
            ib.placeOrder(contract, o)
            ib.sleep(2) # Final soak for TWS flush
            return {"s": "ok", "status": "success", "orderid": oid, "message": "Modification saved as session owner"}, 200
        else:
            return {"s": "error", "message": "No modification fields provided"}, 400
    finally:
        if ib: ib.disconnect()

def get_funds(auth):
    ib = get_ib_connection(auth, offset=45)
    if not ib: return {"s": "error", "status": "error", "message": "Conn Fail"}
    try:
        acc_summ = ib.accountSummary(); funds_list = []
        for it in acc_summ:
            if it.tag in ('NetLiquidation', 'AvailableFunds', 'BuyingPower', 'CashBalance'):
                funds_list.append({"title": it.tag, "value": it.value})
        return {"s": "ok", "status": "success", "funds": funds_list, "data": funds_list}
    finally:
        if ib: ib.disconnect()

def get_margins(auth): return get_funds(auth)
def get_balance(auth): return get_funds(auth)

def get_open_position(tradingsymbol, exchange, product, auth):
    pd = get_positions(auth)
    if pd and pd.get("s") == "ok":
        ts = str(tradingsymbol).strip().upper()
        for p in pd.get("data", []):
            ps = str(p.get("symbol", "")).strip().upper()
            if ts == ps or ts in ps or ps in ts: return p.get("netQty", "0")
    return "0"

def close_position_api(data, auth):
    """Square off a specific symbol using a counter order"""
    sym = str(data.get("symbol") or "").strip()
    if not sym: return {"s": "error", "message": "Symbol missing"}, 400
    
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: return {"s": "error", "message": "Conn Fail"}, 500
    
    try:
        from ib_insync import MarketOrder
        
        # 1. DEEP DISCOVERY: Probe managed accounts to fill the cache
        managed = ib.managedAccounts()
        if not managed: ib.client.reqAccountUpdates(True, "")
        else:
            for acc in managed: ib.client.reqAccountUpdates(True, acc)
            
        # 2. REACTIVE SOAK
        for _ in range(15):
            ib.waitOnUpdate(0.1)
            if ib.positions() or ib.portfolio(): break
            
        # 3. FUZZY MATCHING: Check Positions and Portfolio
        ib_pos_list = ib.positions() + [p for p in ib.portfolio()]
        
        for p in ib_pos_list:
            # Strip multiple spaces and normalize for matching
            psym_raw = str(getattr(p.contract, 'localSymbol', '') or getattr(p.contract, 'symbol', ''))
            psym = " ".join(psym_raw.split()).upper()
            target = " ".join(sym.split()).upper()
            
            # Match by symbol OR localSymbol
            if psym == target or target in psym or psym in target:
                qty = p.position
                if qty == 0: continue
                
                action = "SELL" if qty > 0 else "BUY"
                abs_qty = abs(qty)
                
                logger.info(f"[SERVICE PULSE] Closing {psym}: Side={action}, Qty={abs_qty}")
                ib.qualifyContracts(p.contract)
                trade = ib.placeOrder(p.contract, MarketOrder(action, abs_qty))
                return {"s": "ok", "status": "success", "message": f"Closed {sym}"}, 200
                
        return {"s": "error", "message": f"Position {sym} not found in active portfolio"}, 404
    finally:
        if ib: ib.disconnect()

def cancel_all_orders_api(data, auth):
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: return [], ["Conn Error"]
    try:
        ib.reqGlobalCancel(); return ["ALL"], [] 
    finally:
        if ib: ib.disconnect()

def close_all_positions(api_key, auth):
    """Square off the entire portfolio using counter orders"""
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: return {"s": "error", "status": "error", "message": "Conn Error"}, 500
    try:
        from ib_insync import MarketOrder
        
        # 1. DEEP DISCOVERY
        managed = ib.managedAccounts()
        if not managed: ib.client.reqAccountUpdates(True, "")
        else:
            for acc in managed: ib.client.reqAccountUpdates(True, acc)
            
        # 2. REACTIVE SOAK
        for _ in range(25):
            ib.waitOnUpdate(0.1)
            if ib.positions() or ib.portfolio(): break
            
        # 3. GLOBAL SQUARE OFF
        c = 0
        seen_conids = set()
        # Merge positions and portfolio for the most complete list
        all_items = ib.positions() + [p for p in ib.portfolio()]
        
        for p in all_items:
            if p.contract.conId in seen_conids: continue
            if p.position == 0: continue
            
            seen_conids.add(p.contract.conId)
            action = "SELL" if p.position > 0 else "BUY"
            abs_qty = abs(p.position)
            
            print(f"[SERVICE PULSE] Global Closing: {p.contract.localSymbol} Qty={abs_qty}")
            ib.qualifyContracts(p.contract)
            ib.placeOrder(p.contract, MarketOrder(action, abs_qty))
            c += 1
            
        return {"s": "ok", "status": "success", "message": f"Squared off {c} positions"}, 200
    finally:
        if ib: ib.disconnect()

def place_smartorder_api(data, auth):
    """Sync position to a specific size using reactive discovery"""
    sym = str(data.get("symbol") or "").strip()
    target_size = int(float(data.get("position_size", 0)))
    
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: return None, {"status": "error", "message": "Conn Fail"}, None
    
    try:
        from ib_insync import MarketOrder
        
        # 1. DEEP DISCOVERY
        managed = ib.managedAccounts()
        if not managed: ib.client.reqAccountUpdates(True, "")
        else:
            for acc in managed: ib.client.reqAccountUpdates(True, acc)
            
        # 2. REACTIVE SOAK
        for _ in range(15):
            ib.waitOnUpdate(0.1)
            if ib.positions() or ib.portfolio(): break
            
        # 3. FUZZY MATCHING
        ib_pos_list = ib.positions() + [p for p in ib.portfolio()]
        current_qty = 0
        target_norm = " ".join(sym.split()).upper()
        found_contract = None
        
        for p in ib_pos_list:
            psym_raw = str(getattr(p.contract, 'localSymbol', '') or getattr(p.contract, 'symbol', ''))
            psym_norm = " ".join(psym_raw.split()).upper()
            
            if psym_norm == target_norm or target_norm in psym_norm or psym_norm in target_norm:
                if p.position != 0:
                    current_qty = int(p.position)
                    found_contract = p.contract
                    break
        
        # 4. EXECUTION LOGIC
        if current_qty == target_size:
            return None, {"status": "success", "message": "Position matches target"}, None
            
        action = "BUY" if target_size > current_qty else "SELL"
        diff_qty = abs(target_size - current_qty)
        
        # If no contract found (new position), we need to create one
        if not found_contract:
            # Fallback to creating a contract from data (less ideal, but necessary for new entries)
            # For IBKR, we usually need a conId or specific params
            return None, {"status": "error", "message": f"Contract for {sym} not found in active positions."}, None
            
        logger.info(f"[SERVICE PULSE] Smart Order Synchronization: {sym} ({current_qty} -> {target_size})")
        ib.qualifyContracts(found_contract)
        trade = ib.placeOrder(found_contract, MarketOrder(action, diff_qty))
        return trade, {"status": "success", "message": f"Smart order placed: {action} {diff_qty}"}, trade.order.permId
        
    finally:
        if ib: ib.disconnect()
