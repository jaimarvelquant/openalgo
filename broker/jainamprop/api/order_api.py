import json
import os
import re
from tokenize import Token

import httpx

from broker.jainamprop.baseurl import BASE_URL, INTERACTIVE_URL
from broker.jainamprop.mapping.transform_data import (
    map_product_type,
    reverse_map_product_type,
    transform_data,
    transform_modify_order_data,
)


def _get_client_id(auth_token=None):
    """
    Robustly extract clientID for XTS requests.
    1. Environment variable (highest priority)
    2. Database/Session lookup
    3. JWT extraction (fallback)
    """
    client_id = os.getenv("JAINAMPROP_USER_ID")
    if client_id:
        logger.info(f"Using JAINAMPROP_USER_ID from env: {client_id}")
        return client_id

    try:
        from flask import session
        from database.auth_db import get_user_id as _get_uid
        login_username = session.get("user")
        if login_username:
            raw_uid = _get_uid(login_username)
            if raw_uid and isinstance(raw_uid, str):
                return raw_uid.split("_")[0]
    except Exception:
        pass

    if auth_token:
        try:
            import base64
            parts = auth_token.split(".")
            if len(parts) >= 2:
                payload_b64 = parts[1]
                payload_b64 += "=" * ((4 - len(payload_b64) % 4) % 4)
                jwt_payload = json.loads(base64.urlsafe_b64decode(payload_b64).decode("utf-8"))
                raw_uid = (
                    jwt_payload.get("userID")
                    or jwt_payload.get("userId")
                    or jwt_payload.get("userid")
                )
                if raw_uid and isinstance(raw_uid, str):
                    return raw_uid.split("_")[0]
        except Exception:
            pass

    return None


from database.auth_db import get_auth_token
from database.token_db import get_br_symbol, get_symbol, get_token
from utils.httpx_client import get_httpx_client
from utils.logging import get_logger
from database.apilog_db import async_log_order, init_db

logger = get_logger(__name__)


def get_api_response(endpoint, auth, method="GET", payload=""):
    AUTH_TOKEN = auth

    if not AUTH_TOKEN:
        logger.error("Auth token is empty or None - cannot make API request")
        return {
            "type": "error",
            "code": "e-auth-token-missing",
            "description": "Authentication token is missing or expired. Please reconnect your broker.",
        }

    api_key = os.getenv("BROKER_API_KEY")

    # Get the shared httpx client with connection pooling
    client = get_httpx_client()

    headers = {
        "authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
    }

    # Extract clientID for XTS requests
    client_id = _get_client_id(AUTH_TOKEN)

    # Gateway Mapping: All PRO accounts must use "PRO" in order payload data,
    # but the actual sub-account ID (e.g. PRO1489) should be used in GET query URLs.
    api_client_id = client_id
    # Note: We don't map to "PRO" here anymore for GET, as per user request.

    def _derive_cluster_base():
        try:
            from flask import session
            cb = session.get("JAINAMPROP_CLUSTER_BASE")
            if isinstance(cb, str) and cb:
                return cb.rstrip("/")
        except Exception:
            pass
        try:
            lookup_url = f"{BASE_URL}/hostlookup"
            versions = ["interactive_1.0.1", "interactive_1.0.2", "interactiveapi_1.0.1", "interactive_2.0"]
            for ver in versions:
                r = client.post(lookup_url, json={"accesspassword": "2021HostLookUpAccess", "version": ver}, timeout=10.0)
                if r.status_code == 200:
                    j = r.json()
                    ok = j.get("type") in (True, "success") or j.get("code") == "hostlookup"
                    if ok and isinstance(j.get("result"), dict):
                        cs = j["result"].get("connectionString")
                        if cs:
                            cs = cs.strip().strip("`").strip()
                            return re.sub(r"/([^/]+)hostlookup/?$", r"/\1interactive", cs)
        except Exception:
            pass
        return INTERACTIVE_URL

    cluster_base_url = _derive_cluster_base()
    url = f"{cluster_base_url}{endpoint}"
    
    logger.info(f"API Request URL: {url}")
    # Log headers with masked token
    log_headers = {**headers, "authorization": "***"}
    logger.info(f"API Headers: {log_headers}")

    if method == "GET":

        def fetch_json(url_to_get: str) -> dict:
            def _needs_bearer_retry(res_data, status_code):
                # Retry if HTTP 401 OR if JSON body contains session error
                if status_code == 401:
                    return True
                if isinstance(res_data, dict):
                    code = res_data.get("code")
                    if code in ("e-session-0005", "e-token-0001"):
                        return True
                return False

            try:
                r = client.get(url_to_get, headers=headers, timeout=15.0)
                data = r.json() if r.status_code == 200 else {}
                
                if _needs_bearer_retry(data, r.status_code) and not headers["authorization"].startswith("Bearer "):
                    logger.info(f"Detected session error ({data.get('code')}), retrying with Bearer prefix...")
                    bearer_headers = {**headers, "authorization": f"Bearer {headers['authorization']}"}
                    r = client.get(url_to_get, headers=bearer_headers, timeout=15.0)
                    data = r.json()
                
                r.status = r.status_code
                return data
            except Exception as e:
                try:
                    # Retry with HTTP/1.1 for older Symphony gateways
                    client_h1 = httpx.Client(http2=False, http1=True, timeout=15.0)
                    r2 = client_h1.get(url_to_get, headers=headers)
                    data2 = r2.json()
                    if _needs_bearer_retry(data2, r2.status_code) and not headers["authorization"].startswith("Bearer "):
                        bearer_headers = {**headers, "authorization": f"Bearer {headers['authorization']}"}
                        r2 = client_h1.get(url_to_get, headers=bearer_headers)
                        data2 = r2.json()
                    return data2
                except Exception:
                    return {}

        # Multi-ID reasoning: Some Prop firm clusters tag orders as 'PRO' at the gateway, 
        # but store them under the specific sub-account ID in the OMS. 
        # Querying both and merging ensures the user sees all their orders.
        ids_to_try = []
        if client_id:
            ids_to_try.append(client_id)
            if client_id.upper().startswith("PRO") or ("PRO" in client_id.upper()):
                ids_to_try.append("PRO")
        
        # Explicitly add ZZJ17038 as requested by user to ensure coverage
        ids_to_try.append("ZZJ17038")
        
        # Also try to extract the user ID from current session or JWT fallback
        try:
            from flask import session
            from database.auth_db import get_user_id as _get_uid
            login_username = session.get("user")
            if login_username:
                u_id = _get_uid(login_username)
                if u_id and isinstance(u_id, str):
                    ids_to_try.append(u_id.split("_")[0])
        except Exception:
            pass
            
        if not ids_to_try:
            ids_to_try.append("PRO")
            
        # Deduplicate IDs
        ids_to_try = list(dict.fromkeys(ids_to_try))
        
        # Scrub any pre-existing clientID from the base url to prevent duplication
        clean_url = re.sub(r"([?&])clientID=[^&]*", "", url)
        clean_url = clean_url.replace("?&", "?").replace("&&", "&").rstrip("?").rstrip("&")

        merged_result = []
        final_type = "success"
        
        for cid in ids_to_try:
            separator = "&" if "?" in clean_url else "?"
            q_url = f"{clean_url}{separator}clientID={cid}"
            
            logger.info(f"Multi-ID search for cid={cid} -> {q_url}")
            data = fetch_json(q_url)
            
            # Fallback to Cluster 0 if Cluster 10/2/etc fails for this ID
            if (not isinstance(data, dict)) or data.get("type") == "error":
                if cluster_base_url != INTERACTIVE_URL:
                    fb_url = f"{INTERACTIVE_URL}{endpoint}"
                    fb_url = re.sub(r"([?&])clientID=[^&]*", "", fb_url)
                    fb_url = fb_url.replace("?&", "?").replace("&&", "&").rstrip("?").rstrip("&")
                    fb_separator = "&" if "?" in fb_url else "?"
                    fb_url = f"{fb_url}{fb_separator}clientID={cid}"
                    logger.info(f"Primary cluster mapping failed for {cid}, falling back to: {fb_url}")
                    data = fetch_json(fb_url)
            
            if data and data.get("type") == "success" and isinstance(data.get("result"), list):
                merged_result.extend(data["result"])
            elif data and data.get("type") == "error":
                final_type = "error" if not merged_result else final_type

        # Use a dictionary to deduplicate orders by AppOrderID (common in multi-ID queries)
        dedup_orders = {str(o.get("AppOrderID")): o for o in merged_result if isinstance(o, dict) and o.get("AppOrderID")}
        
        final_data = {
            "type": final_type,
            "code": "s-orders-0001",
            "description": f"Retrieved merged order book for IDs: {ids_to_try}",
            "result": list(dedup_orders.values())
        }

        try:
            logger.info(f"Merged API Response (httpx): {len(final_data['result'])} items found for {ids_to_try}")
        except Exception:
            pass
            
        try:
            from database.apilog_db import executor, async_log_order
            executor.submit(
                async_log_order, "jainamprop_order_api", {"url": url, "endpoint": endpoint, "ids": ids_to_try}, final_data
            )
        except Exception:
            pass
            
        return final_data

    elif method == "POST":
        response = client.post(url, headers=headers, json=payload)
    else:
        response = client.request(method, url, headers=headers, json=payload)

    # Add status attribute for compatibility with the existing codebase
    response.status = response.status_code
    logger.info(f"API Response (httpx): {response.text}")
    return response.json()


def get_order_book(auth):
    return get_api_response("/orders", auth)


def get_trade_book(auth):
    return get_api_response("/orders/trades", auth)


def get_positions(auth):
    return get_api_response("/portfolio/positions?dayOrNet=DayWise", auth)


def get_holdings(auth):
    return get_api_response("/portfolio/holdings", auth)


def get_open_position(tradingsymbol, exchange, producttype, auth):
    # Convert Trading Symbol from OpenAlgo Format to Broker Format Before Search in OpenPosition
    tradingsymbol = get_br_symbol(tradingsymbol, exchange)
    positions_data = get_positions(auth)

    # Map exchange from OpenAlgo format to XTS format
    exchange_mapping = {
        "NSE": "NSECM",
        "BSE": "BSECM",
        "NFO": "NSEFO",
        "BFO": "BSEFO",
        "MCX": "MCXFO",
        "CDS": "NSECD",
    }
    xts_exchange = exchange_mapping.get(exchange, exchange)

    net_qty = "0"

    logger.info(
        f"Looking for position: symbol={tradingsymbol}, exchange={xts_exchange}, product={producttype}"
    )
    logger.info(f"Positions data: {positions_data}")

    # XTS returns {"type": "success", "result": {"positionList": [...]}}
    if positions_data and positions_data.get("type") == "success":
        position_list = positions_data.get("result", {}).get("positionList", [])
        for position in position_list:
            pos_symbol = position.get("TradingSymbol", "")
            pos_exchange = position.get("ExchangeSegment", "")
            pos_product = position.get("ProductType", "")
            logger.info(
                f"Checking position: symbol={pos_symbol}, exchange={pos_exchange}, product={pos_product}"
            )
            if (
                pos_symbol == tradingsymbol
                and pos_exchange == xts_exchange
                and pos_product == producttype
            ):
                net_qty = str(position.get("Quantity", 0))
                logger.info(f"Found matching position. Net Quantity: {net_qty}")
                break

    return net_qty


def place_order_api(data, auth):
    AUTH_TOKEN = auth

    # Check if this is a direct instrument ID payload or needs transformation
    if all(
        key in data
        for key in ["exchangeSegment", "exchangeInstrumentID", "productType", "orderType"]
    ):
        newdata = data
    else:
        # Traditional symbol-based payload that needs transformation
        token = get_token(data["symbol"], data["exchange"])
        newdata = transform_data(data, token)

    # XTS requires clientID in the order payload
    client_id = _get_client_id(AUTH_TOKEN)

    if client_id:
        if client_id.upper().startswith("PRO"):
            # The XTS Gateway explicitly requires PRO as the clientID mapped for Proprietary OMS
            newdata["clientID"] = "PRO"
        else:
            newdata["clientID"] = client_id
    if "apiOrderSource" not in newdata:
        newdata["apiOrderSource"] = "WebAPI"

    headers = {
        "authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
    }

    # Get the shared httpx client with connection pooling
    client = get_httpx_client()

    # Use derived cluster base if available for better reliability
    def _derive_cluster_base():
        try:
            from flask import session
            cb = session.get("JAINAMPROP_CLUSTER_BASE")
            if isinstance(cb, str) and cb:
                return cb.rstrip("/")
        except Exception:
            pass
        return INTERACTIVE_URL

    cluster_base_url = _derive_cluster_base()
    url = f"{cluster_base_url}/orders"

    def _needs_bearer_retry(res_data, status_code):
        if status_code == 401: return True
        if isinstance(res_data, dict):
            code = res_data.get("code")
            if code in ("e-session-0005", "e-token-0001"): return True
        return False

    # Make the request using the shared client
    try:
        response = client.post(url, headers=headers, json=newdata)
        try:
            res_json = response.json()
        except:
            res_json = {}

        if _needs_bearer_retry(res_json, response.status_code) and not headers["authorization"].startswith("Bearer "):
            logger.info(f"Detected session error in placement, retrying with Bearer prefix...")
            bearer_headers = {**headers, "authorization": f"Bearer {headers['authorization']}"}
            response = client.post(url, headers=bearer_headers, json=newdata)
    except Exception as e:
        logger.error(f"Order placement connection error: {str(e)}")
        # Simple fallback for connection issues
        response = httpx.post(url, headers=headers, json=newdata, timeout=15)

    # Add status attribute for compatibility
    response.status = response.status_code
    logger.info(f"Place Order Raw Response: {response.text}")

    # Parse the JSON response
    try:
        response_data = response.json()
    except json.JSONDecodeError:
        response_data = {
            "error": "Invalid JSON response from server",
            "raw_response": response.text,
        }

    orderid = (
        response_data.get("result", {}).get("AppOrderID")
        if response_data.get("type") == "success"
        else None
    )

    return response, response_data, orderid


def place_smartorder_api(data, auth):
    AUTH_TOKEN = auth

    # If no API call is made in this function then res will return None
    res = None

    # Extract necessary info from data
    symbol = data.get("symbol")
    exchange = data.get("exchange")
    product = data.get("product")
    position_size = int(data.get("position_size", "0"))

    # Get current open position for the symbol
    current_position = int(
        get_open_position(symbol, exchange, map_product_type(product), AUTH_TOKEN)
    )

    logger.info(f"position_size : {position_size}")
    logger.info(f"Open Position : {current_position}")

    # Determine action based on position_size and current_position
    action = None
    quantity = 0

    # If both position_size and current_position are 0, do nothing
    if position_size == 0 and current_position == 0 and int(data["quantity"]) != 0:
        action = data["action"]
        quantity = data["quantity"]
        # logger.info(f"action : {action}")
        # logger.info(f"Quantity : {quantity}")
        res, response, orderid = place_order_api(data, AUTH_TOKEN)
        # logger.info(f"{res}")
        # logger.info(f"{response}")

        return res, response, orderid

    elif position_size == current_position:
        if int(data["quantity"]) == 0:
            response = {
                "status": "success",
                "message": "No OpenPosition Found. Not placing Exit order.",
            }
        else:
            response = {
                "status": "success",
                "message": "No action needed. Position size matches current position",
            }
        orderid = None
        return res, response, orderid  # res remains None as no API call was mad

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
            # logger.info(f"smart buy quantity : {quantity}")
        elif position_size < current_position:
            action = "SELL"
            quantity = current_position - position_size
            # logger.info(f"smart sell quantity : {quantity}")

    if action:
        # Prepare data for placing the order
        order_data = data.copy()
        order_data["action"] = action
        order_data["quantity"] = str(quantity)

        # logger.info(f"{order_data}")
        # Place the order
        res, response, orderid = place_order_api(order_data, auth)
        # logger.info(f"{res}")
        logger.debug(f"Placing order with payload: {order_data}")
        logger.debug(f"API Response: {response}")
        logger.info(f"Order ID: {orderid}")

        return res, response, orderid


def close_all_positions(current_api_key, auth):
    # Fetch the current open positions
    AUTH_TOKEN = auth

    positions_response = get_positions(AUTH_TOKEN)
    logger.info(f"Open_positions : {positions_response}")

    positions_list = positions_response.get("result", {}).get("positionList", [])
    if not positions_list:
        return {"message": "No Open Positions Found"}, 200

    # If response has positions
    for position in positions_list:
        # Skip if net quantity is zero
        if int(position["Quantity"]) == 0:
            continue

        # Determine action based on net quantity
        action = "SELL" if int(position["Quantity"]) > 0 else "BUY"
        quantity = abs(int(position["Quantity"]))

        exchange_segment = position["ExchangeSegment"]
        instrument_id = position["ExchangeInstrumentId"]

        logger.info(f"Exchange Segment: {exchange_segment}")
        logger.info(f"Exchange Instrument ID: {instrument_id}")

        # Prepare the order payload
        place_order_payload = {
            "exchangeSegment": exchange_segment,
            "exchangeInstrumentID": instrument_id,
            "productType": position["ProductType"],
            "orderType": "MARKET",
            "orderSide": action,
            "timeInForce": "DAY",
            "disclosedQuantity": "0",
            "orderQuantity": str(quantity),
            "limitPrice": "0",
            "stopPrice": "0",
            "orderUniqueIdentifier": "openalgo",
        }

        # Place the order to close the position
        res, response, orderid = place_order_api(place_order_payload, auth)

        # logger.info(f"{res}")
        # logger.info(f"{response}")
        # logger.info(f"{orderid}")

        # Note: Ensure place_order_api handles any errors and logs accordingly

    return {"status": "success", "message": "All Open Positions SquaredOff"}, 200


def cancel_order(orderid, auth):
    # Assuming you have a function to get the authentication token
    AUTH_TOKEN = auth

    # Get the shared httpx client with connection pooling
    client = get_httpx_client()
    # logger.info(f"{orderid}")
    # Set up the request headers
    headers = {
        "authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
    }

    # Prepare the payload
    client_id = _get_client_id(AUTH_TOKEN)

    url = f"{INTERACTIVE_URL}/orders?appOrderID={orderid}"
    if client_id:
        # Use actual client_id for cancel (consistent with GET requests)
        url += f"&clientID={client_id}"
    # Make the request using the shared client
    response = client.delete(url, headers=headers)
    # Add status attribute for compatibility with the existing codebase
    response.status = response.status_code

    data = json.loads(response.text)

    # Check if the request was successful
    if data.get("status"):
        # Return a success response
        return {"status": "success", "orderid": orderid}, 200
    else:
        # Return an error response
        return {
            "status": "error",
            "message": data.get("message", "Failed to cancel order"),
        }, response.status


def modify_order(data, auth):
    # Assuming you have a function to get the authentication token
    AUTH_TOKEN = auth

    # Get the shared httpx client with connection pooling
    client = get_httpx_client()

    token = get_token(data["symbol"], data["exchange"])
    data["symbol"] = get_br_symbol(data["symbol"], data["exchange"])

    transformed_data = transform_modify_order_data(data, token)

    # XTS requires clientID in the modify order payload
    client_id = _get_client_id(AUTH_TOKEN)

    if client_id:
        if client_id.upper().startswith("PRO"):
            transformed_data["clientID"] = "PRO"
        else:
            transformed_data["clientID"] = client_id

    if "apiOrderSource" not in transformed_data:
        transformed_data["apiOrderSource"] = "WebAPI"

    # Set up the request headers
    headers = {
        "authorization": AUTH_TOKEN,
        "Content-Type": "application/json",
    }
    payload = json.dumps(transformed_data)

    # Make the request using the shared client
    response = client.put(f"{INTERACTIVE_URL}/orders", headers=headers, content=payload)

    # Add status attribute for compatibility with the existing codebase
    response.status = response.status_code
    logger.info(f"Response of modify order :{response.status}")
    data = json.loads(response.text)

    if data.get("status") == "true" or data.get("message") == "SUCCESS":
        return {"status": "success", "orderid": data["data"]["orderid"]}, 200
    else:
        return {
            "status": "error",
            "message": data.get("message", "Failed to modify order"),
        }, response.status


def cancel_all_orders_api(data, auth):
    # Get the order book

    AUTH_TOKEN = auth

    order_book_response = get_order_book(AUTH_TOKEN)
    logger.debug(f"Order book response: {order_book_response}")
    if order_book_response.get("type") != "success":
        return [], []  # Return empty lists indicating failure to retrieve the order book

    orders = order_book_response.get("result", [])

    # Filter orders that are in 'open' or 'trigger_pending' state
    # logger.info(f"Orders: {orders}")
    orders_to_cancel = [
        order for order in orders if order["OrderStatus"] in ["New", "Trigger Pending"]
    ]
    logger.info(f"Orders to cancel: {orders_to_cancel}")
    canceled_orders = []
    failed_cancellations = []

    # Cancel the filtered orders
    for order in orders_to_cancel:
        orderid = order["AppOrderID"]
        cancel_response, status_code = cancel_order(orderid, auth)
        if status_code == 200:
            logger.info(f"Order {orderid} canceled successfully")
            canceled_orders.append(orderid)
        else:
            logger.error(f"Failed to cancel order {orderid}")
            failed_cancellations.append(orderid)

    return canceled_orders, failed_cancellations
