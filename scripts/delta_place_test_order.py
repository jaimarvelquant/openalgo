import os
import sys
import json
import time

# Mocking OpenAlgo environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from broker.deltaex.api.order_api import place_order
from dotenv import load_dotenv

load_dotenv()

# 1. Credentials
API_KEY = os.getenv("BROKER_API_KEY")
API_SECRET = os.getenv("BROKER_API_SECRET")
# Force prefix for India Testnet for this test
AUTH_TOKEN = f"INDIA_TESTNET:::{API_KEY}:::{API_SECRET}"

def run_test():
    print(f"\n--- DELTA: PLACE TEST ORDER ---")
    
    if not API_KEY or not API_SECRET:
        print("[ERROR] No credentials found in .env!")
        return

    # STEP: PLACE LIMIT BUY ORDER (BTCUSD @ $50,000)
    print(f"\n>>> Placing a LIMIT BUY Order: BTCUSD @ $50,000 (Size: 1) <<<")
    # This price is safely below current market price ($66k+)
    res, status = place_order(AUTH_TOKEN, "BTCUSD", "DELTA", 1, "BUY", "LIMIT", "NRML", price=50000)
    
    if res.get('status') == 'success':
        order_id = res.get('order_id')
        print(f"\n[SUCCESS] Order Placed! ID: {order_id}")
        print(f"Check your dashboard now. The Order Book should show 1 active item.")
    else:
        print(f"\n[FAILED] Could not place order: {res.get('message')}")

    print(f"\n--- TEST COMPLETE ---")

if __name__ == "__main__":
    run_test()
