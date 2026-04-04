import os
import sys
import json
import time

# Mocking OpenAlgo environment
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
print(f"[DEBUG] Project Root: {project_root}")

from broker.deltaex.api.order_api import get_order_book, get_trade_book, get_positions, get_balance
from broker.deltaex.api.auth_api import authenticate_broker

print("\n--- OPENALGO CORE TEST: DELTA EXCHANGE ---")

# 1. Fetch Credentials from .env
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("BROKER_API_KEY")
API_SECRET = os.getenv("BROKER_API_SECRET")
# Force prefix for India Testnet for this test
AUTH_TOKEN = f"INDIA_TESTNET:::{API_KEY}:::{API_SECRET}"

print(f"\n>>> TEST 1: Mapping Logic Verification <<<")
from broker.deltaex.mapping.order_data import transform_trade_book
sample_raw_trade = {
    "id": "test_id",
    "product_symbol": "BTCUSD",
    "side": "buy",
    "size": "1.0",
    "price": "60000.0",
    "created_at": "2024-04-03 10:00:00"
}
mapped = transform_trade_book([sample_raw_trade])
print(f"Mapped Trade: {json.dumps(mapped[0], indent=2)}")
if 'trading_symbol' not in mapped[0]:
    print("[CRITICAL ERROR] Mapping FAILED! Mapped item is missing keys.")

print(f"\n>>> TEST 2: Real Handshake (Fills) <<<")
try:
    fills = get_trade_book(AUTH_TOKEN)
    print(f"Handshake Fills: Found {len(fills)} items.")
    if len(fills) > 0:
        print(f"Sample Fill: {json.dumps(fills[0], indent=2)}")
except Exception as e:
    print(f"Fills failed: {e}")

print(f"\n>>> TEST 3: Real Handshake (Positions) <<<")
try:
    positions = get_positions(AUTH_TOKEN)
    print(f"Handshake Positions: Found {len(positions)} active items.")
    if len(positions) > 0:
        print(f"Sample Position: {json.dumps(positions[0], indent=2)}")
except Exception as e:
    print(f"Positions failed: {e}")

print(f"\n--- TEST COMPLETE ---")
