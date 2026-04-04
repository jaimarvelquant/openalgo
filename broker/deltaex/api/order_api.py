import requests
import json
import time
import os

print("\n[DEBUG] >>> DELTA API MODULE LOADED <<<\n")

from broker.deltaex.api.auth_api import get_signature, sync_time
from broker.deltaex.mapping.order_data import (
    transform_positions_data,
    transform_order_book,
    transform_trade_book
)
from utils.logging import get_logger

logger = get_logger(__name__)

# Global cache for product symbols to avoid excessive API calls
_PRODUCT_CACHE = {}

def _get_api_creds(auth_token):
    """Utility to split auth_token into key, secret and environment"""
    # Default selection from .env if prefix is missing
    env_select = os.getenv("DELTA_ENV", "").upper()
    
    is_testnet = (env_select == "GLOBAL_TESTNET" or env_select == "TESTNET")
    is_india = (env_select == "INDIA_MAINNET" or env_select == "INDIA")
    is_demo = (env_select == "GLOBAL_DEMO" or env_select == "DEMO")
    is_india_testnet = (env_select == "INDIA_TESTNET")
    
    # Prefix override (High priority)
    if auth_token.startswith("TESTNET:::"):
        auth_token = auth_token.replace("TESTNET:::", "")
        is_testnet = True; is_india = False; is_demo = False; is_india_testnet = False
    elif auth_token.startswith("INDIA:::"):
        auth_token = auth_token.replace("INDIA:::", "")
        is_india = True; is_testnet = False; is_demo = False; is_india_testnet = False
    elif auth_token.startswith("DEMO:::"):
        auth_token = auth_token.replace("DEMO:::", "")
        is_demo = True; is_testnet = False; is_india = False; is_india_testnet = False
    elif auth_token.startswith("INDIA_TESTNET:::"):
        auth_token = auth_token.replace("INDIA_TESTNET:::", "")
        is_india_testnet = True; is_testnet = False; is_india = False; is_demo = False
        
    if ":::" in auth_token:
        parts = auth_token.split(":::")
        return parts[0], parts[1], is_testnet, is_india, is_demo, is_india_testnet
    return None, None, False, False, False, False

def _get_base_url(is_testnet, is_india=False, is_demo=False, is_india_testnet=False):
    if is_india_testnet:
        return "https://cdn-ind.testnet.deltaex.org"
    if is_india:
        return "https://api.india.delta.exchange"
    if is_demo:
        return "https://demo-api.delta.exchange"
    return "https://testnet-api.delta.exchange" if is_testnet else "https://api.delta.exchange"

def _fetch_products(is_testnet=False, is_india=False, is_demo=False, is_india_testnet=False):
    """Fetch and cache all products from Delta with a strict timeout to prevent thread hangs"""
    global _PRODUCT_CACHE
    base = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    url = f"{base}/v2/products"
    try:
        logger.info(f"Delta: Refreshing coin-list from {base}...")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            products = response.json().get('result', [])
            _PRODUCT_CACHE = {p['symbol'].upper(): p['id'] for p in products}
            logger.info(f"Delta: Successfully cached {len(_PRODUCT_CACHE)} products.")
        else:
            logger.warning(f"Delta: Coin-list fetch failed (HTTP {response.status_code}). Using empty cache.")
    except Exception as e:
        logger.warning(f"Delta: Coin-list fetch timed out or failed: {str(e)}")

def get_product_id(symbol, is_testnet=False, is_india=False, is_demo=False, is_india_testnet=False):
    """Resolve a symbol string to a stable product_id"""
    symbol = symbol.upper()
    if not _PRODUCT_CACHE:
        _fetch_products(is_testnet, is_india, is_demo, is_india_testnet)
    return _PRODUCT_CACHE.get(symbol)

def get_order_book(auth_token):
    """Fetch orders with 'Underlying Discovery' to satisfy Delta India schema"""
    print(f"\n[HANDSHAKE] >>> DELTA: get_order_book requested at {time.strftime('%H:%M:%S')} <<<\n")
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    
    # 1. Discovery: Find relevant assets
    symbols_to_check = ['BTC', 'ETH', 'USDT', 'DETO']
    try:
        fill_path = "/v2/fills"
        query_params = "page_size=10"
        sig = get_signature(api_secret, "GET", timestamp, fill_path, query_params)
        h = {'api-key': api_key, 'x-api-key': api_key, 'signature': sig, 'timestamp': timestamp}
        f_res = requests.get(f"{base_url}{fill_path}?{query_params}", headers=h, timeout=5)
        if f_res.status_code == 200:
            fills = f_res.json().get('result', [])
            for f in fills:
                asset = f.get('product', {}).get('underlying_asset', {}).get('symbol')
                if asset and asset not in symbols_to_check:
                    symbols_to_check.append(asset)
    except:
        pass

    all_raw_orders = []
    # 2. Iterate through discovered assets (Required for India node visibility)
    for asset in symbols_to_check[:10]:
        path = "/v2/orders"
        query_params = f"underlying_asset_symbol={asset}&page_size=50&state=open,filled,cancelled,rejected"
        signature = get_signature(api_secret, "GET", timestamp, path, query_params)
        
        headers = {
            'api-key': api_key, 'x-api-key': api_key,
            'signature': signature, 'timestamp': timestamp,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{base_url}{path}?{query_params}", headers=headers, timeout=5)
            if response.status_code == 200:
                res_list = response.json().get('result', [])
                if isinstance(res_list, list):
                    all_raw_orders.extend(res_list)
        except:
            continue
            
    # Deduplicate orders by ID
    unique_orders = {o.get('id'): o for o in all_raw_orders if o.get('id')}.values()
    logger.info(f"Delta Orders Handshake: Found {len(unique_orders)} items across: {symbols_to_check}")
    return transform_order_book(list(unique_orders))

def get_trade_book(auth_token):
    """Fetch trade history from Delta Exchange"""
    print(f"\n[ACTION CENTER] >>> DELTA: get_trade_book pulse detected! <<<\n")
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return []
    
    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    path = "/v2/fills"
    query_params = "page_size=20"
    signature = get_signature(api_secret, "GET", timestamp, path, query_params)
    
    headers = {
        'api-key': api_key, 'x-api-key': api_key,
        'signature': signature, 'timestamp': timestamp,
        'Content-Type': 'application/json'
    }
    url = f"{base_url}{path}?{query_params}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        res_json = response.json()
        raw_fills = res_json.get('result', [])
        
        # SCREAMING DEBUG: Print the raw trade data to terminal
        if len(raw_fills) > 0:
            print(f"DEBUG: Found {len(raw_fills)} trades. First ID: {raw_fills[0].get('id')}")
            
        if response.status_code == 200:
            return transform_trade_book(raw_fills)
    except Exception as e:
        logger.error(f"Error in Delta Trades Handshake: {e}")
    return []

def get_positions(auth_token):
    """Fetch active positions with 'Underlying Discovery' for Delta India"""
    print(f"\n[ACTION CENTER] >>> DELTA: get_positions pulse detected! <<<\n")
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return []
    
    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    
    # 1. Self-Correction: Find which assets we actually have activity in
    symbols_to_check = ['BTC', 'ETH', 'USDT', 'DETO']
    try:
        # Check fills to find active symbols
        fill_path = "/v2/fills"
        query_params = "page_size=10"
        sig = get_signature(api_secret, "GET", timestamp, fill_path, query_params)
        h = {'api-key': api_key, 'x-api-key': api_key, 'signature': sig, 'timestamp': timestamp}
        f_res = requests.get(f"{base_url}{fill_path}?{query_params}", headers=h, timeout=5)
        if f_res.status_code == 200:
            fills = f_res.json().get('result', [])
            for f in fills:
                asset = f.get('product', {}).get('underlying_asset', {}).get('symbol')
                if asset and asset not in symbols_to_check:
                    symbols_to_check.append(asset)
    except:
        pass

    all_raw_positions = []
    # 2. Iterate through discovered assets to satisfy Delta's "Underlying Required" schema
    for asset in symbols_to_check[:10]: # Limit to top 10 for performance
        path = "/v2/positions"
        query_params = f"underlying_asset_symbol={asset}"
        signature = get_signature(api_secret, "GET", timestamp, path, query_params)
        
        headers = {
            'api-key': api_key, 'x-api-key': api_key,
            'signature': signature, 'timestamp': timestamp,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(f"{base_url}{path}?{query_params}", headers=headers, timeout=5)
            if response.status_code == 200:
                raw_list = response.json().get('result', [])
                if isinstance(raw_list, list):
                    all_raw_positions.extend(raw_list)
        except:
            continue
            
    # Remove duplicates and filter for active sizes
    unique_positions = {p.get('product_id'): p for p in all_raw_positions if abs(float(p.get('size') or 0)) > 0}.values()
    
    logger.info(f"Delta Discovery Handshake: Found {len(unique_positions)} active positions for: {symbols_to_check}")
    return transform_positions_data(list(unique_positions))

def get_balance(auth_token):
    """Retrieve available balance/margin from Delta marginal endpoint"""
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return []
    
    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    path = "/v2/wallet/balances" # Global balance discovery
    sig = get_signature(api_secret, "GET", timestamp, path)
    headers = { 'api-key': api_key, 'x-api-key': api_key, 'signature': sig, 'timestamp': timestamp }
    
    try:
        r = requests.get(f"{base_url}{path}", headers=headers, timeout=5)
        if r.status_code == 200:
            balances = r.json().get('result', [])
            return [{"asset": b.get('asset', {}).get('symbol'), "balance": b.get('balance')} for b in balances]
    except:
        pass
    return []

def get_margin(auth_token):
    """Retrieve marginal account info (Successful on some India nodes)"""
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return {}
    
    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    path = "/v2/positions/marginal" # This often contains account margin info
    sig = get_signature(api_secret, "GET", timestamp, path)
    headers = { 'api-key': api_key, 'x-api-key': api_key, 'signature': sig, 'timestamp': timestamp }
    
    try:
        r = requests.get(f"{base_url}{path}", headers=headers, timeout=5)
        if r.status_code == 200:
            return r.json().get('result', {})
    except:
        pass
    return {}

def place_order(auth_token, symbol, exchange, quantity, side, order_type, product, 
                price=None, trigger_price=None, stop_loss=None, take_profit=None):
    """Place a new order on Delta Exchange"""
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return None
    
    product_id = get_product_id(symbol, is_testnet, is_india, is_demo, is_india_testnet)
    if not product_id:
        return {"status": "error", "message": f"Symbol {symbol} not found on Delta"}
        
    order_data = {
        "product_id": product_id,
        "size": int(quantity),
        "side": side.lower(),
        "order_type": "market_order" if order_type.upper() == "MARKET" else "limit_order"
    }
    
    if order_type.upper() == "LIMIT" and price:
        order_data["limit_price"] = str(price)
        
    # JSON body for signature (no spaces in separators for Delta API signature match)
    body = json.dumps(order_data, separators=(',', ':'))
    
    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    path = "/v2/orders"
    signature = get_signature(api_secret, "POST", timestamp, path, body=body)
    
    headers = {
        'api-key': api_key, 
        'x-api-key': api_key,
        'signature': signature, 
        'timestamp': timestamp,
        'Content-Type': 'application/json',
        'User-Agent': 'delta-rest-client-v2.0.0'
    }
    url = f"{_get_base_url(is_testnet, is_india, is_demo, is_india_testnet)}{path}"
    
    try:
        response = requests.post(url, headers=headers, data=body, timeout=10)
        result = response.json()
        if response.status_code in [200, 201]:
            logger.info(f"Delta Order placed: {result.get('result', {}).get('id')}")
            return {"status": "success", "order_id": str(result.get('result', {}).get('id'))}, 200
        else:
            msg = result.get('message', f"HTTP {response.status_code}")
            return {"status": "error", "message": msg}, response.status_code
    except Exception as e:
        logger.error(f"Delta place_order error: {e}")
        return {"status": "error", "message": str(e)}, 500

def cancel_order(order_id, auth_token):
    """Cancel order with automatic product_id discovery"""
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return {"status": "error", "message": "Invalid token"}, 401
    
    # 1. Discover product_id for this order
    product_id = None
    all_orders = get_order_book(auth_token)
    for o in all_orders:
        if str(o.get('order_id')) == str(order_id):
            # We need to find the raw product_id. 
            # Our mapper doesn't keep it, so we'll fetch products if needed or just re-run discovery
            symbol = o.get('symbol')
            product_id = get_product_id(symbol, is_testnet, is_india, is_demo, is_india_testnet)
            break
            
    if not product_id:
        return {"status": "error", "message": "Order not found or already closed"}, 404
        
    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    path = "/v2/orders"
    
    # Body for Cancel: id and product_id
    body_dict = {"id": int(order_id), "product_id": int(product_id)}
    body = json.dumps(body_dict, separators=(',', ':'))
    
    signature = get_signature(api_secret, "DELETE", timestamp, path, body=body)
    headers = {
        'api-key': api_key, 'x-api-key': api_key,
        'signature': signature, 'timestamp': timestamp,
        'Content-Type': 'application/json'
    }
    
    try:
        r = requests.delete(f"{base_url}{path}", headers=headers, data=body, timeout=10)
        if r.status_code == 200:
            return {"status": "success", "message": "Order cancelled"}, 200
        return r.json(), r.status_code
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def modify_order(data, auth_token):
    """Modify order with automatic product_id discovery"""
    order_id = data.get('orderid') or data.get('order_id')
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    
    # Discover product_id
    product_id = None
    all_orders = get_order_book(auth_token)
    for o in all_orders:
        if str(o.get('order_id')) == str(order_id):
            symbol = o.get('symbol')
            product_id = get_product_id(symbol, is_testnet, is_india, is_demo, is_india_testnet)
            break
            
    if not product_id:
        return {"status": "error", "message": "Order not found"}, 404

    base_url = _get_base_url(is_testnet, is_india, is_demo, is_india_testnet)
    timestamp = sync_time(base_url)
    path = "/v2/orders"
    
    modify_data = {
        "id": int(order_id),
        "product_id": int(product_id),
        "size": int(data.get('quantity'))
    }
    if data.get('price'): modify_data["limit_price"] = str(data.get('price'))
    
    body = json.dumps(modify_data, separators=(',', ':'))
    signature = get_signature(api_secret, "PUT", timestamp, path, body=body)
    
    headers = {
        'api-key': api_key, 'x-api-key': api_key,
        'signature': signature, 'timestamp': timestamp,
        'Content-Type': 'application/json'
    }
    
    try:
        r = requests.put(f"{base_url}{path}", headers=headers, data=body, timeout=10)
        if r.status_code == 200:
            return {"status": "success", "message": "Order modified"}, 200
        return r.json(), r.status_code
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

def get_open_position(tradingsymbol, exchange, product, auth_token):
    """Get net quantity for a specific symbol on Delta"""
    positions = get_positions(auth_token)
    for p in positions:
        if p.get('symbol') == tradingsymbol:
            qty = float(p.get('quantity', 0))
            if p.get('transaction_type') == 'SELL':
                qty = -qty
            return qty
    return 0

def place_smartorder_api(data, auth_token):
    """Place an order to reach a target position size (e.g. square attracting to 0)"""
    symbol = data.get('symbol')
    exchange = data.get('exchange')
    product = data.get('product')
    target_pos = int(data.get('position_size', 0))
    
    current_pos = get_open_position(symbol, exchange, product, auth_token)
    diff = target_pos - current_pos
    
    if diff == 0:
        return None, {"status": "success", "message": "Position already at target"}, None
        
    side = "buy" if diff > 0 else "sell"
    qty = abs(diff)
    
    order_res = place_order(auth_token, symbol, exchange, qty, side, "MARKET", product)
    
    if order_res and order_res.get('status') == 'success':
        return None, order_res, order_res.get('order_id')
    else:
        return None, order_res, None
