import requests
import sqlite3
import datetime
import time

# ==============================
# Parameters
# ==============================
url_quotes = "http://127.0.0.1:5000/api/v1/quotes"
url_placeorder = "http://127.0.0.1:5000/api/v1/placeorder"
url_tradebook = "http://127.0.0.1:5000/api/v1/tradebook"

apikey = "de31866767c07868eef202e120f83910ff837ec109560dd497f43da2597fd22e"
strategy = "CRUDEOIL_STRADDLE"
exchange = "MCX"
product = "NRML"
pricetype = "MARKET"
quantity = 100
limit_price = 0.0
DB_PATH = r"D:\Github\openalgo\db\openalgo.db"

# Track positions
open_positions = {}

# ==============================
# Utility functions
# ==============================
def square_off(symbol, reason="MANUAL EXIT"):
    payload = {
        "apikey": apikey,
        "strategy": strategy,
        "symbol": symbol,
        "exchange": exchange,
        "action": "BUY",   # opposite of SELL entry
        "quantity": quantity,
        "product": product,
        "pricetype": "MARKET"
    }
    resp = requests.post(url_placeorder, json=payload).json()
    print(f"[EXIT] {symbol} -> {reason}, {resp}")
    open_positions.pop(symbol, None)

def get_trade_avg_price(orderid, symbol, retries=10, delay=15):
    for attempt in range(retries):
        resp = requests.post(url_tradebook, json={"apikey": apikey}).json()
        if resp.get("status") == "success":
            trades = resp["data"]
            total_qty, total_value = 0, 0
            for trade in trades:
                if trade["orderid"] == orderid and trade["symbol"] == symbol:
                    qty = trade.get("quantity", 0)
                    avg_price = trade.get("average_price", 0)
                    total_qty += qty
                    total_value += qty * avg_price
            if total_qty > 0:
                weighted_avg = round(total_value / total_qty, 2)
                print(f"[OK] Trade found: {symbol}, Weighted Avg Price={weighted_avg}")
                return weighted_avg
        print(f"[WAIT] Trade not found yet for {symbol}, retry {attempt+1}/{retries}...")
        time.sleep(delay)
    print(f"[ERR] No trade found for {symbol} with orderid {orderid} after {retries} retries")
    return None

# ==============================
# Order placement
# ==============================
def place_order(symbol, action, expiry):
    payload = {
        "apikey": apikey,
        "strategy": strategy,
        "symbol": symbol,
        "exchange": exchange,
        "action": action,
        "quantity": quantity,
        "product": product,
        "pricetype": pricetype,
        "price": limit_price
    }
    resp = requests.post(url_placeorder, json=payload).json()
    print(f"{action} {symbol} -> {resp}")

    if resp.get("status") == "success":
        orderid = resp.get("orderid")
        if orderid:
            avg_price = get_trade_avg_price(orderid, symbol)
            if avg_price:
                stop_price = round(avg_price * 1.5, 2)
                target_price = round(avg_price * 0.9, 2)  # 10% profit
                open_positions[symbol] = {
                    "entry_time": datetime.datetime.now(),
                    "avg_price": avg_price,
                    "stop_price": stop_price,
                    "target_price": target_price,
                    "active": True
                }
                print(f"[OK] {symbol} StopLoss={stop_price}, Target={target_price}")
    return resp

def place_straddle(ce_symbol, pe_symbol, expiry):
    place_order(ce_symbol, "SELL", expiry)
    place_order(pe_symbol, "SELL", expiry)

# ==============================
# Monitoring loop
# ==============================
def monitor_positions():
    print("=== Bot Monitoring Started ===")
    while open_positions:
        print(f"[RUNNING] Bot monitoring at {datetime.datetime.now().strftime('%H:%M:%S')}")
        now = datetime.datetime.now()
        for symbol, pos in list(open_positions.items()):
            if not pos["active"]:
                continue
            # Square off after 1 hour
            if (now - pos["entry_time"]).seconds >= 3600:
                square_off(symbol, "TIME EXIT")
                continue
            # Check LTP
            resp = requests.post(url_quotes, json={"apikey": apikey, "symbol": symbol, "exchange": exchange}).json()
            if resp.get("status") == "success":
                ltp = resp["data"]["ltp"]
                if ltp >= pos["stop_price"]:
                    square_off(symbol, "STOPLOSS HIT")
                elif ltp <= pos["target_price"]:
                    square_off(symbol, "PROFIT TARGET HIT")
        time.sleep(15)
    print("=== Bot Monitoring Ended ===")

# ==============================
# Run workflow
# ==============================
if __name__ == "__main__":
    print(f"=== Strategy Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST ===")
    print("=== Platform: windows ===")

    # Example: replace with your futures/options lookup
    ce_symbol = "CRUDEOIL17MAR268300CE"
    pe_symbol = "CRUDEOILM17MAR268300PE"
    expiry = "17-MAR-26"

    place_straddle(ce_symbol, pe_symbol, expiry)
    monitor_positions()
