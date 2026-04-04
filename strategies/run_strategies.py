import os
import datetime
import time
import sqlite3
import logging
from dotenv import load_dotenv
from openalgo import api

# --- Logging setup ---
logging.basicConfig(
    filename="strategy_runner.log",
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- Environment setup ---
load_dotenv()
DB_PATH = r"D:\Github\openalgo\db\openalgo.db"
API_KEY = os.getenv("API_KEY")

client = api(
    api_key=API_KEY,
    host="http://127.0.0.1:5000",
)

# --- Helpers ---
def normalize_expiry(expiry):
    """Convert expiry from symtoken (e.g. 29-JUN-27) to broker format (e.g. 27JUN29)."""
    try:
        dt = datetime.datetime.strptime(expiry, "%d-%b-%y")
        return dt.strftime("%d%b%y").upper()
    except Exception:
        return expiry  # fallback

def map_offset(offset):
    """Map numeric offsets to broker strings."""
    mapping = {
        "0.0": "ATM",
        "1.0": "OTM1",
        "2.0": "OTM2",
        "-1.0": "ITM1",
        "-2.0": "ITM2"
    }
    return mapping.get(str(offset), str(offset))

def parse_leg(legdef, symbol, straddle_width=0.0):
    parts = legdef.split("|")
    if len(parts) < 5:
        return None
    offset, opttype, action, multiplier, slinfo = parts[:5]

    base_lot = 65 if symbol.upper() == "NIFTY" else 20 if symbol.upper() == "SENSEX" else 1
    lotsize = int(multiplier) * base_lot

    if offset.startswith("SW"):
        try:
            adj = float(offset.replace("SW", ""))
        except ValueError:
            adj = 0.0
        resolved_offset = straddle_width + adj
    else:
        resolved_offset = offset

    return {
        "offset": resolved_offset,
        "type": "CE" if opttype == "C" else "PE",
        "action": "SELL" if action == "S" else "BUY",
        "lotsize": lotsize,
        "stoploss_pct": int(slinfo.split("#")[1]),
        "symbol": symbol
    }

# --- Core functions ---
def place_leg(strategy_id, leg_id, leg, expiry_date):
    expiry_date = normalize_expiry(expiry_date)
    offset_value = map_offset(leg["offset"])

    payload = {
        "strategy": "CSV_STRATEGY",
        "underlying": leg["symbol"],
        "exchange": "NFO",
        "expiry_date": expiry_date,
        "offset": offset_value,
        "option_type": leg["type"],
        "action": leg["action"],
        "quantity": leg["lotsize"],
        "pricetype": "MARKET",
        "product": "NRML",
        "splitsize": 0,
    }

    try:
        logging.info(f"Placing leg {leg_id} for strategy {strategy_id} with payload: {payload}")
        response = client.optionsorder(**payload)
        logging.info(f"Response for leg {leg_id}: {response}")
        print(f"[ORDER] {leg['action']} {leg['type']} {offset_value} -> {response}")
    except Exception as e:
        logging.error(f"Exception while placing leg {leg_id}: {e}", exc_info=True)
        response = {"status": "error", "message": str(e)}

    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leg_status (
                strategy_id, leg_id, underlying, expiry, offset, option_type,
                action, quantity, stoploss_pct, order_id, status, entry_time
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy_id,
            leg_id,
            leg["symbol"],
            expiry_date,
            offset_value,
            leg["type"],
            leg["action"],
            leg["lotsize"],
            leg["stoploss_pct"],
            response.get("order_id",""),
            response.get("status","error"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    return response

def squareoff_strategy(strategy_id):
    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, leg_id, underlying, expiry, offset, option_type, action, quantity
            FROM leg_status
            WHERE strategy_id=? AND status='PLACED'
        """, (strategy_id,))
        rows = cursor.fetchall()

        for leg_db_id, leg_id, underlying, expiry, offset, opttype, action, qty in rows:
            exit_action = "BUY" if action == "SELL" else "SELL"
            payload = {
                "strategy": "CSV_STRATEGY_EXIT",
                "underlying": underlying,
                "exchange": "NFO",
                "expiry_date": expiry,
                "offset": offset,
                "option_type": opttype,
                "action": exit_action,
                "quantity": qty,
                "pricetype": "MARKET",
                "product": "NRML",
                "splitsize": 0,
            }
            try:
                logging.info(f"Squareoff leg {leg_id} for strategy {strategy_id} with payload: {payload}")
                resp = client.optionsorder(**payload)
                logging.info(f"Squareoff response: {resp}")
                print(f"[SQUAREOFF] Strategy {strategy_id} Leg {leg_id}: {exit_action} {opttype} -> {resp}")
            except Exception as e:
                logging.error(f"Exception while squareoff leg {leg_id}: {e}", exc_info=True)
                resp = {"status": "error", "message": str(e)}

            cursor.execute("""
                UPDATE leg_status
                SET status='SQUARED_OFF', exit_time=?
                WHERE id=?
            """, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), leg_db_id))

        cursor.execute("""
            UPDATE strategy_status
            SET status='SQUARED_OFF', updated_at=?
            WHERE id=?
        """, (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), strategy_id))
        conn.commit()

def run_strategy(strategy):
    print(f"=== Running {strategy['instance_name']} ===")
    strategy_id = strategy["id"]

    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE strategy_status SET status='STARTED', updated_at=? WHERE id=?",
                       (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), strategy_id))
        conn.commit()

    leg1 = parse_leg(strategy["leg1"], strategy["symbol"], strategy["straddle_width"])
    leg2 = parse_leg(strategy["leg2"], strategy["symbol"], strategy["straddle_width"])

    place_leg(strategy_id, 1, leg1, strategy["expiry"])
    place_leg(strategy_id, 2, leg2, strategy["expiry"])

    sq_time = datetime.datetime.strptime(strategy["squareoff_time"], "%H:%M:%S").time()
    end_time = datetime.datetime.strptime(strategy["end_time"], "%H:%M:%S").time()

    while datetime.datetime.now().time() < sq_time:
        print(f"[RUNNING] Monitoring {strategy['instance_name']} at {datetime.datetime.now().strftime('%H:%M:%S')}")
        time.sleep(15)

    print(f"[EXIT] Squareoff time reached for {strategy['instance_name']}")
    squareoff_strategy(strategy_id)

    while datetime.datetime.now().time() < end_time:
        time.sleep(15)

    print(f"[EXIT] EndTime reached for {strategy['instance_name']}")
    squareoff_strategy(strategy_id)

if __name__ == "__main__":
    print(f"=== Strategy Runner Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST ===")
    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_status")
        strategies = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]

        for row in strategies:
            strat = dict(zip(columns, row))
            start_time = datetime.datetime.strptime(strat["start_time"], "%H:%M:%S").time()
            end_time = datetime.datetime.strptime(strat["end_time"], "%H:%M:%S").time()

            if datetime.datetime.now().time() > end_time:
                print(f"[SKIP] {strat['instance_name']} skipped because EndTime {end_time} has passed.")
