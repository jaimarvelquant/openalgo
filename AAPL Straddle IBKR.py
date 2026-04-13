from ib_insync import IB, Stock, Option, MarketOrder
import math
import time

# ---------------------------------------------------------------------------
# AAPL ATM Straddle Order (Direct IBKR)
# ---------------------------------------------------------------------------
# This script uses the ib_insync library to place a straddle order directly 
# on IBKR. It dynamically fetches the current price and identifies the 
# nearest Friday expiry.
# ---------------------------------------------------------------------------

def place_aapl_straddle(action='BUY', quantity=1):
    ib = IB()
    try:
        print("--- AAPL Direct IBKR Straddle ---")
        print("Connecting to TWS/Gateway...")
        # Using a unique ClientID
        ib.connect('127.0.0.1', 7497, clientId=3344)
        
        # Enable Delayed Market Data if not subscribed
        ib.reqMarketDataType(3)
        
        # 1. Fetch AAPL Contract & Price
        aapl = Stock('AAPL', 'SMART', 'USD')
        ib.qualifyContracts(aapl)
        
        print("Fetching AAPL Spot Price...")
        ticker = ib.reqTickers(aapl)[0]
        ib.sleep(2)
        
        price = ticker.marketPrice() or ticker.last or ticker.close
        if math.isnan(price) or price <= 0:
            print("ERROR: Could not fetch price. Is TWS running and data active?")
            return

        print(f"Current AAPL Price: {price}")
        
        # 2. Calculate ATM Strike (Rounded to nearest 1.0)
        atm_strike = int(round(price))
        print(f"Target ATM Strike: {atm_strike}")
        
        # 3. Find Nearest Expiry Options
        print("Searching for nearest valid expiry...")
        template = Option('AAPL', '', atm_strike, 'C', 'SMART', currency='USD')
        details = ib.reqContractDetails(template)
        
        if not details:
            print(f"ERROR: No options found for AAPL at strike {atm_strike}.")
            return
            
        # Get today's date to filter out past expiries
        today = time.strftime('%Y%m%d')
        valid_expiries = sorted(list(set(
            d.contract.lastTradeDateOrContractMonth 
            for d in details 
            if d.contract.lastTradeDateOrContractMonth >= today
        )))
        
        if not valid_expiries:
            print("ERROR: No active expiries found.")
            return
            
        target_expiry = valid_expiries[0]
        print(f"Selected Expiry: {target_expiry}")
        
        # 4. Define and Qualify the Straddle Legs
        call_leg = Option('AAPL', target_expiry, atm_strike, 'C', 'SMART')
        put_leg = Option('AAPL', target_expiry, atm_strike, 'P', 'SMART')
        
        print("Qualifying legs...")
        ib.qualifyContracts(call_leg, put_leg)
        
        # 5. Execute Orders
        print(f"\nPLACING {action} ORDERS (Qty: {quantity})...")
        
        call_trade = ib.placeOrder(call_leg, MarketOrder(action, quantity))
        put_trade = ib.placeOrder(put_leg, MarketOrder(action, quantity))
        
        print(f"SUBMITTED Call: {call_leg.localSymbol}")
        print(f"SUBMITTED Put:  {put_leg.localSymbol}")
        
        # Wait for status update
        ib.sleep(2)
        print("\nOrder Status:")
        print(f"Call: {call_trade.orderStatus.status}")
        print(f"Put:  {put_trade.orderStatus.status}")
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected.")

if __name__ == "__main__":
    # Change action to 'SELL' for short straddle
    place_aapl_straddle(action='BUY', quantity=1)
