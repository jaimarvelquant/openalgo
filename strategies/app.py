from flask import Flask, request, jsonify
import sqlite3
import datetime
import threading
import time
from openalgo import api

# --- Config ---
DB_PATH = r"D:\Github\openalgo\db\openalgo.db"
API_KEY = "your_api_key_here"
client = api(api_key=API_KEY, host="http://127.0.0.1:5000")

app = Flask(__name__)

# --- Helpers ---
def db_connect():
    return sqlite3.connect(DB_PATH, timeout=30)

def normalize_expiry(expiry):
    try:
        dt = datetime.datetime.strptime(expiry, "%d-%b-%y")
        return dt.strftime("%d%b%y").upper()
    except Exception:
        return expiry

def map_offset(offset):
    mapping = {
        "0.0": "ATM",
        "1.0": "OTM1",
        "2.0": "OTM2",
        "-1.0": "ITM1",
        "-2.0": "ITM2"
    }
    return mapping.get(str(offset), str(offset))

# --- Strategy Runner ---
def run_strategy(strategy_id):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_status WHERE id=?", (strategy_id,))
        row = cursor.fetchone()
        if not row:
            return
        columns = [desc[0] for desc in cursor.description]
        strat = dict(zip(columns, row))

    print(f"=== Running {strat['instance_name']} ===")

    # Example: place dummy orders
    payload = {
        "strategy": "CSV_STRATEGY",
        "underlying": strat["symbol"],
        "exchange": "NFO",
        "expiry_date": normalize_expiry(strat["expiry"]),
        "offset": map_offset("0.0"),
        "option_type": "CE",
        "action": "SELL",
        "quantity": 65,
        "pricetype": "MARKET",
        "product": "NRML",
        "splitsize": 0,
    }
    resp = client.optionsorder(**payload)
    print(f"[ORDER] {resp}")

    # Monitoring loop (simplified)
    sq_time = datetime.datetime.strptime(strat["squareoff_time"], "%H:%M:%S").time()
    while datetime.datetime.now().time() < sq_time:
        print(f"[RUNNING] Monitoring {strat['instance_name']} at {datetime.datetime.now().strftime('%H:%M:%S')}")
        time.sleep(10)
    print(f"[EXIT] Squareoff reached for {strat['instance_name']}")

# --- Routes ---
@app.route("/upload_strategy", methods=["POST"])
def upload_strategy():
    data = request.json
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO strategy_status (
                instance_name, symbol, leg1, leg2, straddle_width,
                start_time, squareoff_time, end_time, expiry, status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["instance_name"],
            data["symbol"],
            data["leg1"],
            data["leg2"],
            data.get("straddle_width", 0.0),
            data["start_time"],
            data["squareoff_time"],
            data["end_time"],
            data["expiry"],
            "PENDING",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
        return jsonify({"status": "success", "message": "Strategy uploaded"})

@app.route("/run_strategy/<int:strategy_id>", methods=["POST"])
def run_strategy_endpoint(strategy_id):
    thread = threading.Thread(target=run_strategy, args=(strategy_id,))
    thread.start()
    return jsonify({"status": "started", "strategy_id": strategy_id})

@app.route("/view_strategies", methods=["GET"])
def view_strategies():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_status")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        strategies = [dict(zip(columns, row)) for row in rows]
    return jsonify(strategies)

@app.route("/view_leg_status", methods=["GET"])
def view_leg_status():
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM leg_status")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        legs = [dict(zip(columns, row)) for row in rows]
    return jsonify(legs)

# --- Run server ---
if __name__ == "__main__":
    app.run(port=5050, debug=True)
