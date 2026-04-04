import sqlite3

def get_active_futures_ltp():
    # Connect to your SQLite DB
    conn = sqlite3.connect("openalgo.db")
    cursor = conn.cursor()

    # Try March expiry first
    fut_symbol = "CRUDEOIL19MAR26FUT"
    fut_quote = client.quotes(symbol=fut_symbol, exchange="MCX")

    if fut_quote.get("status") == "success":
        spot = fut_quote["data"]["ltp"]
        if spot and spot > 0:
            print(f"Futures LTP ({fut_symbol}): {spot}")
            conn.close()
            return spot, fut_symbol

    print(f"{fut_symbol} returned LTP=0. Looking for next expiry...")

    # Query DB for next available crude oil futures contract
    cursor.execute("""
        SELECT symbol FROM symtoken
        WHERE symbol LIKE 'CRUDEOIL%FUT'
        ORDER BY expiry_date ASC
    """)
    rows = cursor.fetchall()

    for row in rows:
        alt_symbol = row[0]
        alt_quote = client.quotes(symbol=alt_symbol, exchange="MCX")
        if alt_quote.get("status") == "success":
            alt_spot = alt_quote["data"]["ltp"]
            if alt_spot and alt_spot > 0:
                print(f"Futures LTP ({alt_symbol}): {alt_spot}")
                conn.close()
                return alt_spot, alt_symbol

    conn.close()
    print("No active futures contract found.")
    return None, None
