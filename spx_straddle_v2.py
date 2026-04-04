from ib_insync import IB, Index, Option, MarketOrder
import math
import time

def sell_spx_atm_straddle():
    ib = IB()
    try:
        print("--- SPX ATM Straddle Sell Strategy (v2.1 - Multi-Expiry Fix) ---")
        print("Connecting to IBKR TWS...")
        # Using a unique ClientID
        ib.connect('127.0.0.1', 7497, clientId=634991)
        
        # Enable Delayed Market Data (Type 3) to bypass subscription errors
        print("Enabling Delayed Market Data (Type 3)...")
        ib.reqMarketDataType(3)
        
        # 1. Define the SPX Index contract
        spx_index = Index('SPX', 'CBOE', 'USD')
        ib.qualifyContracts(spx_index)
        
        # 2. Fetch the SPX Index LTP
        print("Requesting SPX Spot Price from TWS (please wait)...")
        ticker = ib.reqTickers(spx_index)[0]
        ib.sleep(3) # Wait for data arrival over the network
        
        # Check both real-time AND delayed data fields
        spx_ltp = ticker.marketPrice()
        if math.isnan(spx_ltp) or spx_ltp <= 1.0:
            spx_ltp = ticker.last # Try last price
        if math.isnan(spx_ltp) or spx_ltp <= 1.0:
            spx_ltp = ticker.close # Fallback to yesterday's close
            
        # 3. Final Fallback: Manual Input if TWS returns NaN
        if math.isnan(spx_ltp) or spx_ltp <= 1.0:
            print("\nWARNING: TWS returned 'NaN' for SPX price (Market data missing).")
            try:
                user_input = input("Please enter the current SPX index price manually (e.g. 5235): ")
                spx_ltp = float(user_input)
            except ValueError:
                print("Error: Invalid number entered. Aborting strategy.")
                return
        
        print(f"Captured SPX Price: {spx_ltp}")
        
        # 4. Calculate ATM Strike (Rounded to nearest 5 points)
        atm_strike = int(round(spx_ltp / 5) * 5)
        print(f"Target ATM Strike: {atm_strike}")
        
        # 5. Define near-expiry Options
        print("Searching for ALL available SPX Option Expiries for Strike {}...".format(atm_strike))
        # Templates with empty expiry and tradingClass to find everything
        call_template = Option('SPX', '', atm_strike, 'C', 'CBOE', currency='USD')
        put_template = Option('SPX', '', atm_strike, 'P', 'CBOE', currency='USD')
        
        # Fetch all contract details to resolve ambiguity
        call_details = ib.reqContractDetails(call_template)
        put_details = ib.reqContractDetails(put_template)
        
        if not call_details or not put_details:
            print(f"Error: Could not find ANY SPX options for strike {atm_strike}. Check TWS connection.")
            return

        # Sort by Expiry Date (nearest first) to pick the front-month/0-DTE option
        call_details.sort(key=lambda x: x.contract.lastTradeDateOrContractMonth)
        put_details.sort(key=lambda x: x.contract.lastTradeDateOrContractMonth)
        
        # Select the nearest expiry contract and its specific ID
        call_contract = call_details[0].contract
        put_contract = put_details[0].contract
        
        print(f"Selected Expiry: {call_contract.lastTradeDateOrContractMonth} ({call_contract.tradingClass})")

        # 6. Place Sell Market Orders (1 Lot Each)
        print("\n--- PLACING SELL ORDERS ---")
        call_order = MarketOrder('SELL', 1)
        put_order = MarketOrder('SELL', 1)
        
        print(f"Selling: {call_contract.localSymbol}")
        call_trade = ib.placeOrder(call_contract, call_order)
        
        print(f"Selling: {put_contract.localSymbol}")
        put_trade = ib.placeOrder(put_contract, put_order)
        
        # Monitor the execution for 3 seconds
        ib.sleep(3)
        print("\n--- Trading Summary ---")
        print(f"Call Order ({call_contract.localSymbol}): {call_trade.orderStatus.status}")
        print(f"Put Order  ({put_contract.localSymbol}): {put_trade.orderStatus.status}")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected from IBKR TWS.")

if __name__ == "__main__":
    sell_spx_atm_straddle()
