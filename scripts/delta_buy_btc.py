import os
import sys
from dotenv import load_dotenv

# 1. Path-Agnostic Root Discovery (Automated)
def add_project_root():
    """Automatically find and add the OpenAlgo root folder to sys.path"""
    current = os.path.abspath(os.path.dirname(__file__))
    while current != os.path.dirname(current):
        if os.path.exists(os.path.join(current, "broker")) and os.path.exists(os.path.join(current, "app.py")):
            sys.path.append(current)
            return current
        current = os.path.dirname(current)
    return None

root = add_project_root()
if not root:
    print("[ERROR] Could not find the OpenAlgo root! Please run this script from inside the project folder.")
    sys.exit(1)

from broker.deltaex.api.order_api import place_order

load_dotenv(os.path.join(root, ".env"))
api_key = os.getenv("BROKER_API_KEY")
api_secret = os.getenv("BROKER_API_SECRET")

if not api_key or not api_secret:
    print("[ERROR] Please ensure BROKER_API_KEY and BROKER_API_SECRET are set in your .env file!")
    sys.exit(1)

auth_token = f"INDIA_TESTNET:::{api_key}:::{api_secret}"
symbol = "BTCUSD"
quantity = 1
side = "BUY"
order_type = "MARKET"

print(f"--- DELTA EXCHANGE ORDER TEST ---")
print(f"Symbol:   {symbol}")
print(f"Quantity: {quantity}")
print(f"Side:     {side}")
print(f"Root:     {root}")
print(f"----------------------------------")

print("[1/2] Resolving Product IDs and Syncing Clock...")
result = place_order(
    auth_token=auth_token,
    symbol=symbol,
    exchange="DELTA",
    quantity=quantity,
    side=side,
    order_type=order_type,
    product="NRML"
)

if result.get("status") == "success":
    print(f"[SUCCESS] >>> Order Placed! Order ID: {result.get('order_id')}")
else:
    print(f"[FAILED] Error: {result.get('message')}")
