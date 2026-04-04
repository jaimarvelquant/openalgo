from flask import Flask, request, jsonify, render_template
import datetime, sqlite3

DB_PATH = r"D:\Github\openalgo\db\openalgo.db"

app = Flask(__name__)

def db_connect():
    return sqlite3.connect(DB_PATH, timeout=30)

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
                instance_name, symbol, leg1, leg2, straddle_width,
                start_time, squareoff_time, end_time, expiry, status, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get("instance_name"), data.get("symbol"), data.get("leg1"), data.get("leg2"),
            float(data.get("straddle_width",0.0)), data.get("start_time"), data.get("squareoff_time"),
            data.get("end_time"), data.get("expiry"), "PENDING",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))
        conn.commit()
    return jsonify({"status":"success","message":"Strategy uploaded"})

@app.route("/edit_strategy/<int:strategy_id>", methods=["PUT"])
def edit_strategy(strategy_id):
    data = request.json
    if not data:
        return jsonify({"status":"error","message":"No JSON received"}), 400
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE strategy_status
            SET instance_name=?, symbol=?, leg1=?, leg2=?, straddle_width=?,
                start_time=?, squareoff_time=?, end_time=?, expiry=?, updated_at=?
            WHERE id=?
        """, (
            data.get("instance_name"), data.get("symbol"), data.get("leg1"), data.get("leg2"),
            float(data.get("straddle_width",0.0)), data.get("start_time"), data.get("squareoff_time"),
            data.get("end_time"), data.get("expiry"),
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), strategy_id
        ))
        conn.commit()
    return jsonify({"status":"success","message":"Strategy updated"})
@app.route("/toggle_strategy/<int:strategy_id>", methods=["PUT"])
def toggle_strategy(strategy_id):
    data = request.json
    enabled = int(data.get("enabled",0))
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE strategy_status SET enabled=? WHERE id=?", (enabled, strategy_id))
        conn.commit()
    return jsonify({"status":"success","message":"Strategy toggled","enabled":enabled})


import threading
from runner import scheduler_loop

if __name__ == "__main__":
    # Start scheduler in background
    threading.Thread(target=scheduler_loop, daemon=True).start()
    app.run(port=5050, debug=True)

