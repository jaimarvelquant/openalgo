import csv
import datetime
import time
import requests

CSV_FILE = r"D:\Github\openalgo\strategies\strategies.csv"
API_KEY = "de31866767c07868eef202e120f83910ff837ec109560dd497f43da2597fd22e"
URL_PLACEORDER = "http://127.0.0.1:5000/api/v1/placeorder"
URL_QUOTES = "http://127.0.0.1:5000/api/v1/quotes"

open_positions = {}

# ------------------------------
# Parse CSV strategies
# ------------------------------
def parse_strategies():
    strategies = []
    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            strategies.append({
                "instance": row["InstanceName"],
                "symbol": row["Symbol"],
                "expiry": row["Expiry"],
                "leg1": row["Leg1Defination"],
                "leg2": row["Leg2Defination"],
                "start": row["StartTime"],
                "squareoff": row["SquareoffTime"],
                "sl": row["CombinedSL"],
                "tgt": row["CombinedTGT"]
            })
    return strategies

# ------------------------------
# Parse leg definition
# ------------------------------
def parse_leg(legdef, atm_price):
    parts = legdef.split("|")
    if len(parts) < 5:
        return None

    # take only first 5 parts
    offset, opttype, action, lotsize, slinfo = parts[:5]

    # derive strike from ATM + offset
    width = float(offset.replace("SW", ""))
    strike = round(atm_price + width * 100)  # adjust scaling

    return {
        "strike": strike,
        "type": "CALL" if opttype == "C" else "PUT",
        "action": "SELL" if action == "S" else "BUY",
        "lotsize": int(lotsize*65),
        "stoploss_pct": int(slinfo.split("#")[1])
    }

# ------------------------------
# Place order
# ------------------------------
def place_leg(leg, symbol, expiry):
    payload = {
        "apikey": API_KEY,
        "strategy": "CSV_STRATEGY",
        "symbol": f"{symbol}{expiry}{leg['strike']}{leg['type'][0]}", # crude symbol format
        "exchange": "NFO",
        "action": leg["action"],
        "quantity": leg["lotsize"],
        "product": "NRML",
        "pricetype": "MARKET"
    }
    resp = requests.post(URL_PLACEORDER, json=payload).json()
    print(f"[ORDER] {leg['action']} {leg['type']} {leg['strike']} -> {resp}")
    if resp.get("status") == "success":
        open_positions[payload["symbol"]] = {
            "entry_time": datetime.datetime.now(),
            "avg_price": 100.0,  # TODO: fetch from tradebook
            "stoploss_pct": leg["stoploss_pct"],
            "active": True
        }
    return resp

# ------------------------------
# Exit straddle (both legs)
# ------------------------------
def exit_straddle(reason="EXIT"):
    for sym in list(open_positions.keys()):
        payload = {
            "apikey": API_KEY,
            "strategy": "CSV_STRATEGY",
            "symbol": sym,
            "exchange": "NFO",
            "action": "BUY",   # opposite of SELL entry
            "quantity": open_positions[sym]["lotsize"] if "lotsize" in open_positions[sym] else 1,
            "product": "NRML",
            "pricetype": "MARKET"
        }
        resp = requests.post(URL_PLACEORDER, json=payload).json()
        print(f"[EXIT] {sym} -> {reason}, {resp}")
        open_positions.pop(sym, None)
    print(f"[INFO] Straddle exited due to {reason}")

# ------------------------------
# Monitor loop
# ------------------------------
def monitor_positions(squareoff_time, tgt_pct=10):
    print("=== Bot Monitoring Started ===")
    while open_positions:
        print(f"[RUNNING] Monitoring at {datetime.datetime.now().strftime('%H:%M:%S')}")
        now = datetime.datetime.now()
        total_entry = sum(pos["avg_price"] for pos in open_positions.values())
        total_pnl = 0
        for sym, pos in list(open_positions.items()):
            resp = requests.post(URL_QUOTES, json={"apikey": API_KEY, "symbol": sym, "exchange": "NFO"}).json()
            if resp.get("status") == "success":
                ltp = resp["data"]["ltp"]
                pnl = (pos["avg_price"] - ltp)  # since entry is SELL
                total_pnl += pnl
                # Stoploss check
                if ltp >= pos["avg_price"] * (1 + pos["stoploss_pct"]/100):
                    exit_straddle("STOPLOSS HIT")
                    return
        # Profit target check
        if total_pnl >= total_entry * (tgt_pct/100):
            exit_straddle("PROFIT TARGET HIT")
            return
        # Time exit
        if now.time() >= squareoff_time:
            exit_straddle("TIME EXIT")
            return
        time.sleep(15)
    print("=== Bot Monitoring Ended ===")

# ------------------------------
# Run strategy
# ------------------------------
def run_strategy(strategy, atm_price):
    print(f"=== Running {strategy['instance']} ===")
    leg1 = parse_leg(strategy["leg1"], atm_price)
    leg2 = parse_leg(strategy["leg2"], atm_price)
    place_leg(leg1, strategy["symbol"], strategy["expiry"])
    place_leg(leg2, strategy["symbol"], strategy["expiry"])
    sq_time = datetime.datetime.strptime(strategy["squareoff"], "%H:%M:%S").time()
    monitor_positions(sq_time)

# ------------------------------
# Main
# ------------------------------
if __name__ == "__main__":
    print(f"=== Strategy Bot Started at {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} IST ===")
    strategies = parse_strategies()
    atm_price = 22000  # TODO: fetch ATM from quotes API
    for strat in strategies:
        start_time = datetime.datetime.strptime(strat["start"], "%H:%M:%S").time()
        while datetime.datetime.now().time() < start_time:
            print(f"[WAIT] Waiting for {strat['instance']} start at {start_time}")
            time.sleep(10)
        run_strategy(strat, atm_price)
