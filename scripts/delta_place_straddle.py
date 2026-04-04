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
AUTH_TOKEN = f"INDIA_TESTNET:::{API_KEY}:::{API_SECRET}"

def run_straddle():
    print(f"\n--- DELTA: PLACE BTC STRADDLE ---")
    
    if not API_KEY or not API_SECRET:
        print("[ERROR] No credentials found in .env!")
        return

    # Symbols for 04-April-2026 Expiry at 67,000 Strike
    call_sym = "C-BTC-67000-040426"
    put_sym = "P-BTC-67000-040426"

    print(f"\n>>> Leg 1: Buying Call {call_sym} (Size: 1) <<<")
    res1, s1 = place_order(AUTH_TOKEN, call_sym, "DELTA", 1, "BUY", "MARKET", "NRML")
    if res1.get('status') == 'success':
         print(f"[SUCCESS] Call Placed! ID: {res1.get('order_id')}")
    else:
         print(f"[FAILED] Call failed: {res1.get('message')}")

    time.sleep(1)

    print(f"\n>>> Leg 2: Buying Put {put_sym} (Size: 1) <<<")
    res2, s2 = place_order(AUTH_TOKEN, put_sym, "DELTA", 1, "BUY", "MARKET", "NRML")
    if res2.get('status') == 'success':
         print(f"[SUCCESS] Put Placed! ID: {res2.get('order_id')}")
    else:
         print(f"[FAILED] Put failed: {res2.get('message')}")

    print(f"\n--- STRADDLE TEST COMPLETE ---")
    print(f"Check your dashboard. You should now have 2 active Option positions (1 Call, 1 Put).")

if __name__ == "__main__":
    run_straddle()
