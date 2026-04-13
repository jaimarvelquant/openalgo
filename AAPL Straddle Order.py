from openalgo import api
import sys

# ---------------------------------------------------------------------------
# OpenAlgo - AAPL Option Straddle Order Script
# ---------------------------------------------------------------------------
# This script demonstrates how to place an automated ATM Straddle order 
# (Buy/Sell both Call and Put) for AAPL via the OpenAlgo API.
#
# Prerequisite: Ensure OpenAlgo is running and your broker is connected.
# ---------------------------------------------------------------------------

# 1. Configuration
# Replace with your actual API key from the OpenAlgo dashboard or .env file
API_KEY = "3daa0403ce2501ee7432b75bf100048e3cf510d63d2754f952e93d88bf07ea84" 
HOST = "http://127.0.0.1:5000"

# 2. Initialize the OpenAlgo API Client
client = api(api_key=API_KEY, host=HOST)

def place_aapl_straddle(qty=1, action="BUY", expiry="17APR26"):
    """
    Places an ATM Straddle order for AAPL using the multi-order endpoint.
    
    Args:
        qty (int): Quantity per leg.
        action (str): "BUY" for Long Straddle, "SELL" for Short Straddle.
        expiry (str): Expiry date in DDMMMYY format (e.g., '17APR26').
    """
    print(f"\n🔥 Initiating AAPL {action} Straddle Deployment...")
    print(f"Underlying: AAPL | Expiry: {expiry} | Quantity: {qty}")

    # Use 'ALPACA' or 'IBKR' as the exchange depending on your active broker
    # The API will automatically resolve the correct ATM strike based on LTP
    try:
        response = client.optionsmultiorder(
            strategy="AAPL_Straddle_Bot",
            underlying="AAPL",
            exchange="ALPACA", # Change to 'IBKR' if required
            expiry_date=expiry,
            legs=[
                {
                    "offset": "ATM",
                    "option_type": "CE",
                    "action": action,
                    "quantity": qty,
                    "product": "NRML",
                    "pricetype": "MARKET"
                },
                {
                    "offset": "ATM",
                    "option_type": "PE",
                    "action": action,
                    "quantity": qty,
                    "product": "NRML",
                    "pricetype": "MARKET"
                }
            ]
        )

        if response.get("status") == "success":
            print("\n✅ STRADDLE PLACED SUCCESSFULLY")
            print(f"Underlying LTP: {response.get('underlying_ltp')}")
            for res in response.get("results", []):
                print(f"   - {res['option_type']} Symbol: {res['symbol']} | OrderID: {res['orderid']}")
        else:
            print(f"\n❌ ENTRY FAILED: {response.get('message')}")
            
    except Exception as e:
        print(f"\n⚠️ CONNECTION ERROR: {str(e)}")

if __name__ == "__main__":
    # Change action to "SELL" for a Short Straddle
    # Change expiry to the desired Friday in DDMMMYY format
    place_aapl_straddle(qty=1, action="BUY", expiry="17APR26")
