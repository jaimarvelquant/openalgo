import datetime, time
from db import db_connect

def run_strategy(strategy_id):
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM strategy_status WHERE id=?", (strategy_id,))
        row = cursor.fetchone()
        if not row: return
        cols = [d[0] for d in cursor.description]
        strat = dict(zip(cols,row))

    print(f"=== Running {strat['instance_name']} ===")

    # Dummy order placement (replace with broker API)
    print(f"[ORDER] Placing legs for {strat['instance_name']}")

    sq_time = datetime.datetime.strptime(strat["squareoff_time"], "%H:%M:%S").time()
    while datetime.datetime.now().time() < sq_time:
        print(f"[RUNNING] Monitoring {strat['instance_name']} at {datetime.datetime.now().strftime('%H:%M:%S')}")
        time.sleep(10)

    print(f"[EXIT] Squareoff reached for {strat['instance_name']}")


def place_initial_orders(strategy):
    # Replace with broker API calls
    print(f"[ORDER] Placing initial legs for {strategy['instance_name']}")
    # Example: insert into leg_status table
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO leg_status (strategy_id, leg_id, action, status, entry_time, stoploss_pct, underlying, option_type, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy["id"], 1, "SELL", "PLACED",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            50, strategy["symbol"], "CE", 65
        ))
        cursor.execute("""
            INSERT INTO leg_status (strategy_id, leg_id, action, status, entry_time, stoploss_pct, underlying, option_type, quantity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            strategy["id"], 2, "SELL", "PLACED",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            50, strategy["symbol"], "PE", 65
        ))
        conn.commit()

def monitor_strategy(strategy):
    sq_time = datetime.datetime.strptime(strategy["squareoff_time"], "%H:%M:%S").time()
    while datetime.datetime.now().time() < sq_time:
        # Check stoploss/profit triggers here
        print(f"[MONITOR] {strategy['instance_name']} at {datetime.datetime.now().strftime('%H:%M:%S')}")
        time.sleep(10)
    print(f"[EXIT] Squareoff reached for {strategy['instance_name']}")
    with db_connect() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE strategy_status SET status=?, finished_at=? WHERE id=?",
                       ("FINISHED", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), strategy["id"]))
        conn.commit()

def scheduler_loop():
    while True:
        with db_connect() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM strategy_status WHERE enabled=1 AND status='PENDING'")
            rows = cursor.fetchall()
            cols = [d[0] for d in cursor.description]
            strategies = [dict(zip(cols,r)) for r in rows]

        for strat in strategies:
            # Wait until start_time
            if strat["start_time"]:
                start_time = datetime.datetime.strptime(strat["start_time"], "%H:%M:%S").time()
                if datetime.datetime.now().time() >= start_time:
                    print(f"[START] Launching {strat['instance_name']}")
                    place_initial_orders(strat)
                    monitor_strategy(strat)
        time.sleep(30)  # poll every 30s
