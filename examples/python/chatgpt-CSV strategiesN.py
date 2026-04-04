import csv
import datetime
import time
import sqlite3
from openalgo import api

# ------------------------------------------
# Config
# ------------------------------------------
CSV_FILE = r"D:\Github\openalgo\strategies\strategies.csv"
DB_PATH = r"D:\Github\openalgo\db\openalgo.db"

client = api(
    api_key="de31866767c07868eef202e120f83910ff837ec109560dd497f43da2597fd22e",
    host="http://127.0.0.1:5000",
)

# ------------------------------------------
# DB: Get nearest active expiry
# ------------------------------------------
def get_active_expiry(underlying="NIFTY"):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT expiry 
        FROM symtoken
        WHERE instrumenttype='CE'
          AND symbol LIKE ? || '%'
        ORDER BY expiry ASC
    """, (underlying,))
    rows = cursor.fetchall()
    conn.close()
    if rows:
        expiry = rows[0][0]
        print(f"[OK] Found expiry {expiry} for {underlying}")
        return expiry
    else:
        print("[ERR] No expiry found in DB")
        return None

# ------------------------------------------
# Parse CSV strategies
# ------------------------------------------
def parse_strategies():
    strategies = []
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            strategies.append({
                "instance": row["InstanceName"],
                "symbol": row["Symbol"],
                "expiry": row["Expiry"],  # e.g. CW, but we’ll override with DB
                "leg1": row["Leg1Defination"],
                "leg2": row["Leg2Defination"],
                "start": row["StartTime"],
                "squareoff": row["SquareoffTime"],
            })
    return strategies

# ------------------------------------------
# Parse leg definition
# ------------------------------------------
def parse_leg(legdef):
    parts = legdef.split("|")
    if len(parts) < 5:
        return None
    offset, opttype, action, lotsize, slinfo = parts[:5]
    return {
        "offset": offset,  # e.g. SW+0.3
        "type": "CE" if opttype == "C" else "PE",
        "action": "SELL" if action == "S" else "BUY",
        "lotsize": int(lotsize*65),
        "stoploss_pct": int(slinfo.split("#")[1])
    }

# ------------------------------------------
# Place order via optionsorder API
# ------------------------------------------
def place_leg(leg, underlying, expiry_date):
    response = client.optionsorder(
        strategy="CSV_STRATEGY",
        underlying=underlying,
        exchange="NFO",
        expiry_date=expiry_date,
        offset=leg["offset"],       # e.g. SW+0.3 or SW-0.3
        option_type=leg["type"],    # CE or PE
        action=leg["action"],       # BUY or SELL
        quantity=leg["lotsize"],
        pricetype="MARKET",
        product="NRML",
        splitsize=0,
    )
    print(f"[ORDER] {leg['action']} {leg['type']} {leg['offset']} -> {response}")
    return response

# ------------------------------------------
# Run one strategy
# ------------------------------------------
def run_strategy(strategy):
    print(f"=== Running {strategy['instance']} ===")
    expiry_date = get_active_expiry(strategy["symbol"])
    if not expiry_date:
        return

    leg1 = parse_leg(strategy["leg1"])
    leg2 = parse_leg(strategy["leg2"])

    place_leg(leg1, strategy["symbol"], expiry_date)
    place_leg(leg2, strategy["symbol"], expiry_date)

    # Monitoring loop (simplified)
    sq_time = datetime.datetime.strptime(strategy["squareoff"], "%H:%M:%S").time()
    while datetime.datetime.now().time() < sq_time:
        print(f"[RUNNING] Monitoring {strategy['instance']} at {datetime.datetime.now().strftime('%H:%M:%S')}")
        time.sleep(15)
    print(f"[EXIT] Squareoff time reached for {strategy['instance']}")

# ------------------------------------------
# Main
# ------------------------------------------
if __name__ == "__main__":
    print(f"=== Strategy Bot Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST ===")
    strategies = parse_strategies()
    for strat in strategies:
        start_time = datetime.datetime.strptime(strat["start"], "%H:%M:%S").time()
        while datetime.datetime.now().time() < start_time:
            print(f"[WAIT] Waiting for {strat['instance']} start at {start_time}")
            time.sleep(10)
        run_strategy(strat)
