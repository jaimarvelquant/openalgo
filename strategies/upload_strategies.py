import csv
import datetime
import sqlite3

DB_PATH = r"D:\Github\openalgo\db\openalgo.db"
CSV_FILE = r"D:\Github\openalgo\strategies\strategies.csv"

def init_db():
    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        # Clear existing rows
        cursor.execute("DELETE FROM strategy_status")
        cursor.execute("DELETE FROM leg_status")
        conn.commit()

def extract_straddle_width(leg1, leg2):
    """
    Extracts straddle width from leg definitions like SW+0.3 or SW-0.3.
    Looks at the first token before the first '|'.
    """
    for leg in [leg1, leg2]:
        if not leg:
            continue
        first_token = leg.split("|")[0].strip()
        if first_token.startswith("SW"):
            try:
                return float(first_token.replace("SW", ""))
            except ValueError:
                return 0.0
    return 0.0

def upload_strategies():
    with sqlite3.connect(DB_PATH, timeout=30) as conn:
        cursor = conn.cursor()
        with open(CSV_FILE, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Extract straddle width from leg definitions
                straddle_width = extract_straddle_width(row["Leg1Defination"], row["Leg2Defination"])

                cursor.execute("""
                    INSERT INTO strategy_status (
                        instance_name, symbol, expiry, start_time, squareoff_time, end_time,
                        straddle_width, leg1, leg2, status, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    row["InstanceName"],
                    row["Symbol"],
                    row["Expiry"],
                    row["StartTime"],
                    row["SquareoffTime"],
                    row["EndTime"],
                    straddle_width,
                    row["Leg1Defination"],
                    row["Leg2Defination"],
                    "OBSERVING",
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ))
        conn.commit()
    print("✅ Strategies uploaded successfully with leg definitions and straddle width captured.")

if __name__ == "__main__":
    init_db()
    upload_strategies()
