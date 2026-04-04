from flask import Flask, request, jsonify, render_template
import datetime, sqlite3, threading, time, os
from openalgo import api
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENALGO_API_KEY")
API_HOST = os.getenv("OPENALGO_HOST")

client = api(api_key=API_KEY, host=API_HOST)

DB_PATH = r"D:\Github\openalgo\db\openalgo.db"

app = Flask(__name__)

# ------------------------------------------
# DB helper
# ------------------------------------------
def db_connect():
    return sqlite3.connect(DB_PATH, timeout=30)

# ------------------------------------------
# Web routes
# ------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view_strategies")
def view_strategies():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_status")
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return jsonify([dict(zip(cols, r)) for r in rows])

@app.route("/view_leg_status")
def view_leg_status():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leg_status")
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return jsonify([dict(zip(cols, r)) for r in rows])

@app.route("/upload_strategy", methods=["POST"])
def upload_strategy():
    data = request.json
    if not data:
        return jsonify({"status":"error","message":"No JSON received"}), 400

    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO strategy_status (
                instance_name, symbol, straddle_width,
                start_time, squareoff_time, end_time, expiry, status, updated_at, enabled
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("instance_name"), data.get("symbol"),
            float(data.get("straddle_width",0.0)), data.get("start_time"),
            data.get("squareoff_time"), data.get("end_time"), data.get("expiry"),
            "PENDING", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0
        ))
        strategy_id = cursor.lastrowid

        # Insert N legs
        legs = data.get("legs", [])
        for idx, leg_str in enumerate(legs, start=1):
            cursor.execute("""
                INSERT INTO strategy_legs (strategy_id, leg_id, leg_str)
                VALUES (?, ?, ?)
            """, (strategy_id, idx, leg_str))

        conn.commit()

    return jsonify({"status":"success","message":"Strategy uploaded"})
@app.route("/duplicate_strategy/<int:strategy_id>", methods=["POST"])
@app.route("/duplicate_strategy/<int:strategy_id>", methods=["POST"])
def duplicate_strategy(strategy_id):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_status WHERE id=?", (strategy_id,))
        strat = cursor.fetchone()
        if not strat:
            return jsonify({"status":"error","message":"Strategy not found"}), 404
        cols = [d[0] for d in cursor.description]
        strat_dict = dict(zip(cols, strat))

        # Create new instance name
        base_name = strat_dict["instance_name"]
        new_name = base_name + "_copy"

        cursor.execute("""
            INSERT INTO strategy_status (
                instance_name, symbol, straddle_width,
                start_time, squareoff_time, end_time, expiry,
                status, updated_at, enabled
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            new_name,
            strat_dict["symbol"],
            strat_dict["straddle_width"],
            strat_dict["start_time"],
            strat_dict["squareoff_time"],
            strat_dict["end_time"],
            strat_dict["expiry"],
            "PENDING",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            0
        ))
        new_id = cursor.lastrowid

        # Duplicate legs with fresh leg_id sequence
        cursor.execute("SELECT leg_str FROM strategy_legs WHERE strategy_id=?", (strategy_id,))
        legs = cursor.fetchall()
        for idx, (leg_str,) in enumerate(legs, start=1):
            cursor.execute("INSERT INTO strategy_legs (strategy_id, leg_id, leg_str) VALUES (?, ?, ?)",
                           (new_id, idx, leg_str))
        conn.commit()

    return jsonify({"status":"success","message":"Strategy duplicated","new_id":new_id})

@app.route("/view_strategy_legs")
def view_strategy_legs():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_legs")
        rows = cursor.fetchall()
        cols = [d[0] for d in cursor.description]
        return jsonify([dict(zip(cols, r)) for r in rows])

# ------------------------------------------
# Runner logic
# ------------------------------------------
def normalize_expiry(expiry_str: str) -> str:
    parts = expiry_str.split("-")
    if len(parts) == 3:
        day, mon, year = parts
        if len(year) == 4:
            year = year[-2:]
        return f"{day}{mon}{year}"
    return expiry_str.replace("-", "")
    
def get_freeze_qty(exchange, symbol):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT freeze_qty FROM qty_freeze WHERE exchange=? AND symbol=?", (exchange, symbol))
        row = cursor.fetchone()
        return row[0] if row else 0
def extract_strike(trading_symbol):
    import re
    m = re.search(r'(\d{4,5})(CE|PE)', trading_symbol)
    return int(m.group(1)) if m else None

       
        
def map_exchange_for_freeze(symbol_exchange):
    """
    Map payload exchange to freeze table exchange.
    """
    if symbol_exchange == "NSE_INDEX":
        return "NFO"
    elif symbol_exchange == "BSE_INDEX":
        return "BFO"
    return symbol_exchange  # fallback
    

def parse_strike(symbol: str) -> str:
    if symbol:
        digits = "".join([c for c in symbol if c.isdigit()])
        if digits:
            return digits[-5:]
    return None

def save_leg_response(strategy_id, leg_id, leg, response, expiry):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leg_status (
                strategy_id, leg_id, trading_symbol, underlying, strike, expiry, offset,
                option_type, action, quantity, stoploss_pct, order_id, status,
                entry_time, sl_order_id, stoploss_price, sl_hit, profit_hit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy_id, leg_id,
            response.get("symbol"), response.get("underlying"),
            parse_strike(response.get("symbol")), normalize_expiry(expiry),
            response.get("offset"), response.get("option_type"),
            leg["action"], leg["quantity"], leg["stoploss"],
            response.get("orderid"), response.get("status","ERROR"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            None, None, 0, 0
        ))
        conn.commit()

def fetch_avg_price(orderid, strategy_name):
    time.sleep(1)
    resp = client.orderstatus(strategy=strategy_name, order_id=orderid)
    data = resp.get("data", {})
    if data.get("order_status") == "complete":
        return float(data.get("average_price", 0))
    return 0.0

def calculate_sl_price(avg_price, stoploss_pct, action):
    if avg_price <= 0:
        return None
    if action == "BUY":
        return avg_price * (1 - stoploss_pct/100.0)
    else:
        return avg_price * (1 + stoploss_pct/100.0)

def place_slm_order(strategy, leg, entry_resp, avg_price, leg_id):
    try:
        sl_pct = leg["stoploss_pct"]
        if sl_pct <= 0:
            print(f"[WARN] No stoploss defined for leg {leg_id}")
            return

        # Calculate SL trigger price
        if leg["action"].upper() == "SELL":
            sl_price = avg_price * (1 + sl_pct/100.0)
            sl_action = "BUY"
        else:
            sl_price = avg_price * (1 - sl_pct/100.0)
            sl_action = "SELL"

        sl_price = max(1, round(sl_price, 2))

        sl_payload = {
            "apikey": API_KEY,
            "strategy": strategy["instance_name"],
            "underlying": strategy["symbol"],
            "exchange": "BSE_INDEX" if strategy["symbol"].upper()=="SENSEX" else "NSE_INDEX",
            "expiry_date": normalize_expiry(strategy["expiry"]),
            "offset": leg["offset"],
            "option_type": leg["option_type"],
            "action": sl_action,
            "quantity": leg["quantity"],
            "pricetype": "SL-M",
            "product": "NRML",
            "trigger_price": sl_price,
        }

        print(f"[SL-M] Placing SL order for leg {leg_id}: {sl_payload}")
        sl_resp = client.optionsorder(**sl_payload)
        print(f"[SL-M] Response: {sl_resp}")

        sl_order_id = sl_resp.get("orderid")
        sl_status = sl_resp.get("status", "UNKNOWN")

        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE leg_status
                SET sl_order_id=?, stoploss_price=?, sl_hit=0, status=?, entry_time=?, avg_price=?, sl_error=?
                WHERE strategy_id=? AND leg_id=?
            """, (
                sl_order_id,
                sl_price,
                sl_status,
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                avg_price,
                None if sl_order_id else str(sl_resp),
                strategy["id"],
                leg_id
            ))
            conn.commit()

        if not sl_order_id:
            print(f"[ERROR] SL order not placed for leg {leg_id}, response={sl_resp}")

    except Exception as e:
        print(f"[EXCEPTION] SL placement failed for leg {leg_id}: {e}")
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE leg_status
                SET sl_order_id=NULL, stoploss_price=?, sl_hit=0, status='ERROR', avg_price=?, sl_error=?
                WHERE strategy_id=? AND leg_id=?
            """, (
                avg_price,
                avg_price,
                str(e),
                strategy["id"],
                leg_id
            ))
            conn.commit()



def parse_leg(leg_str, symbol):
    parts = leg_str.split("|")
    multiplier = int(parts[3]) if len(parts) >= 4 else 1
    lot_sizes = {"NIFTY": 65, "SENSEX": 20}
    lot_size = lot_sizes.get(symbol.upper(), 1)

    return {
        "offset": parts[0],
        "option_type": "CE" if parts[1] == "C" else "PE",
        "action": "BUY" if parts[2] == "B" else "SELL",
        "multiplier": multiplier,
        "quantity": multiplier * lot_size,
        "stoploss_pct": int(parts[4].replace("SL#","")) if len(parts) >= 5 else 0,
        "strike": None  # will be filled later from trading_symbol
    }


def place_leg_workflow(strategy, leg_str, leg_id):
    try:
        leg = parse_leg(leg_str, strategy["symbol"])

        # Map exchange for payload vs freeze table
        exchange_payload = "BSE_INDEX" if strategy["symbol"].upper() == "SENSEX" else "NSE_INDEX"
        exchange_freeze = "BFO" if exchange_payload == "BSE_INDEX" else "NFO"

        # Lot size mapping
        lot_sizes = {"NIFTY": 65, "SENSEX": 20}
        lot_size = lot_sizes.get(strategy["symbol"].upper(), 1)

        # Normalize leg quantity
        leg_qty = (leg["quantity"] // lot_size) * lot_size
        leg["quantity"] = leg_qty

        # Normalize splitsize
        freeze_qty = get_freeze_qty(exchange_freeze, strategy["symbol"])
        splitsize = (freeze_qty // lot_size) * lot_size
        if splitsize <= 0:
            splitsize = leg_qty  # fallback: no split

        # Ensure remainder is valid
        if leg_qty % splitsize != 0:
            remainder = leg_qty % splitsize
            if remainder % lot_size != 0:
                adjusted_qty = (leg_qty // splitsize) * splitsize
                print(f"[WARN] Adjusted total qty from {leg_qty} to {adjusted_qty} to fit splitsize {splitsize}")
                leg_qty = adjusted_qty
                leg["quantity"] = leg_qty

        # Build entry order payload
        payload = {
            "apikey": API_KEY,
            "strategy": strategy["instance_name"],
            "underlying": strategy["symbol"],
            "exchange": exchange_payload,
            "expiry_date": normalize_expiry(strategy["expiry"]),
            "offset": leg["offset"],
            "option_type": leg["option_type"],
            "action": leg["action"],
            "quantity": leg["quantity"],
            "pricetype": "MARKET",
            "product": "NRML",
            "splitsize": splitsize,
        }

        print(f"[ENTRY] Placing entry order for leg {leg_id}: {payload}")
        resp = client.optionsorder(**payload)
        print(f"[ENTRY] Response: {resp}")

        # Collect all order IDs from split results
        # Collect all order IDs from split results
        order_ids = [r.get("orderid") for r in resp.get("results", []) if r.get("orderid")]
        order_ids_str = ",".join(order_ids) if order_ids else resp.get("orderid","")

        strike_val = extract_strike(resp.get("symbol",""))

        # Save entry order in DB
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO leg_status
                (strategy_id, leg_id, trading_symbol, underlying, strike, expiry, offset,
                 option_type, action, quantity, stoploss_pct, order_id, status, entry_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                strategy["id"], leg_id,
                resp.get("symbol", ""),
                strategy["symbol"],
                strike_val,
                strategy["expiry"],
                leg["offset"],
                leg["option_type"],
                leg["action"],
                leg["quantity"],
                leg["stoploss_pct"],
                order_ids_str,
                resp.get("status","UNKNOWN"),
                datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()

        # Poll for average price
        avg_price = 0
        for oid in order_ids or [order_ids_str]:
            for _ in range(10):
                avg_price = fetch_avg_price(oid, strategy["instance_name"])
                if avg_price > 0:
                    break
                time.sleep(3)
            if avg_price > 0:
                break

        if avg_price > 0:
            place_slm_order(strategy, leg, resp, avg_price, leg_id)
        else:
            entry_price = resp.get("price", 0)
            print(f"[WARN] avg_price not found for leg {leg_id}, using entry_price={entry_price}")
            place_slm_order(strategy, leg, resp, entry_price, leg_id)

    except Exception as e:
        print(f"[EXCEPTION] Workflow failed for leg {leg_id}: {e}")
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE leg_status
                SET status='ERROR', sl_error=?
                WHERE strategy_id=? AND leg_id=?
            """, (str(e), strategy["id"], leg_id))
            conn.commit()



def place_initial_orders(strategy):
    # Load all legs from strategy_legs table
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT leg_id, leg_str FROM strategy_legs WHERE strategy_id=?", (strategy["id"],))
        rows = cursor.fetchall()

    # Spawn independent threads for each leg
    for leg_id, leg_str in rows:
        threading.Thread(target=place_leg_workflow, args=(strategy, leg_str, leg_id), daemon=True).start()

    # Mark strategy RUNNING once launched
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE strategy_status SET status=?, started_at=? WHERE id=?",
                       ("RUNNING", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), strategy["id"]))
        conn.commit()


def scheduler_loop():
    while True:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM strategy_status WHERE enabled=1 AND status='PENDING'")
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]
            strategies = [dict(zip(cols, r)) for r in rows]

        for strat in strategies:
            if strat["start_time"]:
                start_time = datetime.datetime.strptime(strat["start_time"], "%H:%M:%S").time()
                now = datetime.datetime.now().time()
                if now >= start_time and now <= datetime.datetime.strptime(strat["end_time"], "%H:%M:%S").time():
                    print(f"[START] Launching {strat['instance_name']}")
                    place_initial_orders(strat)
        time.sleep(30)

# ------------------------------------------
# Main
# ------------------------------------------
if __name__ == "__main__":
    threading.Thread(target=scheduler_loop, daemon=True).start()
    app.run(port=5050, debug=True)
