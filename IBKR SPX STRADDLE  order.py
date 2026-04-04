from ib_insync import IB, Index, Option, MarketOrder
import math
import time

def sell_spx_atm_straddle():
    ib = IB()
    try:
        print("--- SPX ATM Straddle Sell Strategy ---")
        print("Connecting to IBKR TWS...")
        # Using a new ClientID to keep things separate
        ib.connect('127.0.0.1', 7497, clientId=663692)
        
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
        print("Searching for nearest SPX Option Expiry for Strike {}...".format(atm_strike))
        call_option = Option('SPX', '', atm_strike, 'C', 'CBOE', currency='USD')
        put_option = Option('SPX', '', atm_strike, 'P', 'CBOE', currency='USD')
        
        # Identify valid expiry dates on CBOE
        qualified = ib.qualifyContracts(call_option, put_option)
        
        if not qualified:
            print("Error: Could not find valid SPX options. Check TWS Symbol search.")
            return

        print(f"Contract Found: {call_option.localSymbol} (Expiry: {call_option.lastTradeDateOrContractMonth})")

        # 6. Place Sell Market Orders (1 Lot Each)
        print("\nPLACING SELL ORDERS...")
        call_order = MarketOrder('SELL', 1)
        put_order = MarketOrder('SELL', 1)
        
        call_trade = ib.placeOrder(call_option, call_order)
        print(f"SUBMITTED: Call Sell order for {call_option.localSymbol}")
        
        put_trade = ib.placeOrder(put_option, put_order)
        print(f"SUBMITTED: Put Sell order for {put_option.localSymbol}")
        
        # Monitor the execution for 3 seconds
        ib.sleep(3)
        print("\nTrading Summary:")
        print(f"Call Order Status: {call_trade.orderStatus.status}")
        print(f"Put Order Status: {put_trade.orderStatus.status}")
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected from IBKR TWS.")

if __name__ == "__main__":
    sell_spx_atm_straddle()
