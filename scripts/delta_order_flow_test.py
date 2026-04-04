import os
import sys
import json
import time

# Mocking OpenAlgo environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from broker.deltaex.api.order_api import place_order, modify_order, cancel_order, get_order_book
from dotenv import load_dotenv

load_dotenv()

# 1. Credentials
API_KEY = os.getenv("BROKER_API_KEY")
API_SECRET = os.getenv("BROKER_API_SECRET")
# Force prefix for India Testnet for this test
AUTH_TOKEN = f"INDIA_TESTNET:::{API_KEY}:::{API_SECRET}"

def run_flow_test():
    print(f"\n--- DELTA ORDER FLOW TEST: RE-IGNITED ---")
    
    if not API_KEY or not API_SECRET:
        print("[ERROR] No credentials found in .env!")
        return

    # TEST A: PLACE LIMIT ORDER
    print(f"\n>>> STEP 1: Placing a LIMIT BUY Order (Far from price) <<<")
    # Placing a buy @ $40,000 (Safe to place and cancel)
    res, status = place_order(AUTH_TOKEN, "BTCUSD", "DELTA", 1, "BUY", "LIMIT", "NRML", price=40000)
    
    if res.get('status') != 'success':
        print(f"[FAILED] Could not place order: {res.get('message')}")
        return
    
    order_id = res.get('order_id')
    print(f"[SUCCESS] Order Placed! ID: {order_id}")
    
    # Wait for the order book to update
    time.sleep(2)

    # TEST B: MODIFY ORDER (Change Size to 2)
    print(f"\n>>> STEP 2: Modifying Order ID: {order_id} (Size -> 2) <<<")
    mod_data = {"order_id": order_id, "quantity": 2, "price": 40100}
    res, status = modify_order(mod_data, AUTH_TOKEN)
    
    if res.get('status') == 'success':
        print(f"[SUCCESS] Order Modified successfully.")
    else:
        print(f"[FAILED] Could not modify: {res.get('message')}")

    time.sleep(2)

    # TEST C: CANCEL ORDER
    print(f"\n>>> STEP 3: Cancelling Order ID: {order_id} <<<")
    res, status = cancel_order(order_id, AUTH_TOKEN)
    
    if res.get('status') == 'success':
        print(f"[SUCCESS] Order Cancelled.")
    else:
        print(f"[FAILED] Could not cancel: {res.get('message')}")

    # TEST D: FINAL VERIFICATION
    print(f"\n>>> STEP 4: Final Order Book Check <<<")
    orders = get_order_book(AUTH_TOKEN)
    found = False
    for o in orders:
        if str(o.get('order_id')) == str(order_id):
            print(f"[ALERT] Order {order_id} STILL EXISTS in order book (State: {o.get('status')})")
            found = True
    if not found:
        print("[SUCCESS] Order is confirmed GONE from the active order book.")

    print(f"\n--- FLOW TEST COMPLETE ---")

if __name__ == "__main__":
    run_flow_test()
