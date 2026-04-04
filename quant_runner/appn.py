import os
import datetime
import sqlite3
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("OPENALGO_API_KEY")
API_HOST = os.getenv("OPENALGO_HOST")

# --- Helpers ---
def db_connect():
    return sqlite3.connect("quant_runner.db")

def normalize_expiry(expiry_str: str) -> str:
    """Normalize expiry date to DDMMMYY format."""
    parts = expiry_str.split("-")
    if len(parts) == 3:
        day, mon, year = parts
        if len(year) == 4:
            year = year[-2:]
        return f"{day}{mon}{year}"
    return expiry_str.replace("-", "")

def parse_strike(symbol: str) -> str:
    """Extract strike price from option symbol like NIFTY24MAR2623100PE."""
    if symbol:
        digits = "".join([c for c in symbol if c.isdigit()])
        if digits:
            return digits[-5:]  # last 5 digits usually strike
    return None

# --- Save response into leg_status ---
def save_leg_response(strategy_id, leg_id, leg, response, expiry):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE leg_status
            SET trading_symbol=?, strike=?, expiry=?, offset=?, option_type=?,
                action=?, quantity=?, stoploss_pct=?, order_id=?, status=?,
                entry_time=?, sl_hit=?, profit_hit=?
            WHERE strategy_id=? AND leg_id=? AND status='PLACED'
        """, (
            response.get("symbol"),
            parse_strike(response.get("symbol")),
            normalize_expiry(expiry),
            response.get("offset"),
            response.get("option_type"),
            leg["action"],
            65,
            leg["stoploss"],
            response.get("orderid"),
            response.get("status","ERROR"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            0,
            0,
            strategy_id,
            leg_id
        ))
        conn.commit()

# --- Place initial orders ---
def place_initial_orders(strategy):
    def parse_leg(leg_str):
        parts = leg_str.split("|")
        return {
            "offset": parts[0],
            "option_type": "CE" if parts[1] == "C" else "PE",
            "action": "BUY" if parts[2] == "B" else "SELL",
            "stoploss": int(parts[4].replace("SL#","")) if len(parts) >= 5 else 0
        }

    leg1 = parse_leg(strategy["leg1"])
    leg2 = parse_leg(strategy["leg2"])

    payload1 = {
        "apikey": API_KEY,
        "strategy": strategy["instance_name"],
        "underlying": strategy["symbol"],
        "exchange": "NSE_INDEX",
        "expiry_date": normalize_expiry(strategy["expiry"]),
        "offset": leg1["offset"],
        "option_type": leg1["option_type"],
        "action": leg1["action"],
        "quantity": 65,
        "pricetype": "MARKET",
        "product": "NRML",
        "splitsize": 0,
    }
    leg1_resp = client.optionsorder(**payload1)
    print("⬅️ Leg1 Response:", leg1_resp)

    payload2 = payload1.copy()
    payload2.update({
        "offset": leg2["offset"],
        "option_type": leg2["option_type"],
        "action": leg2["action"],
    })
    leg2_resp = client.optionsorder(**payload2)
    print("⬅️ Leg2 Response:", leg2_resp)

    # ✅ Update leg_status rows
    save_leg_response(strategy["id"], 1, leg1, leg1_resp, strategy["expiry"])
    save_leg_response(strategy["id"], 2, leg2, leg2_resp, strategy["expiry"])
