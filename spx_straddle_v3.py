from ib_insync import IB, Index, Option, MarketOrder, LimitOrder, StopOrder, Stock
import math
import time
import requests

def sell_spx_atm_bracket_straddle():
    ib = IB()
    try:
        print("--- SPX ATM Straddle SELL (v3.3 - Expiry Guard & TIF Sync) ---")
        print("Connecting to IBKR TWS...")
        # Using a unique ClientID
        ib.connect('127.0.0.1', 7497, clientId=634991)
        
        # 0. Set Data Type 
        ib.reqMarketDataType(3) 

        # 1. Fetch SPX LTP & Calculate ATM Strike
        spx_index = Index('SPX', 'CBOE', 'USD')
        ib.qualifyContracts(spx_index)
        
        print("Step 1: Attempting to fetch SPX price from IBKR...")
        ticker = ib.reqTickers(spx_index)[0]
        ib.sleep(3) 
        spx_ltp = ticker.marketPrice() or ticker.last or ticker.close
        
        # 1.1 SPY Fallback for users without SPX index data 
        if math.isnan(spx_ltp) or spx_ltp <= 1.0:
            print("   - Direct SPX price NOT found. Trying SPY ETF...")
            spy_contract = Stock('SPY', 'SMART', 'USD')
            ib.qualifyContracts(spy_contract)
            spy_ticker = ib.reqTickers(spy_contract)[0]
            ib.sleep(2)
            spy_price = spy_ticker.marketPrice() or spy_ticker.last or spy_ticker.close
            if not math.isnan(spy_price) and spy_price > 0:
                spx_ltp = spy_price * 10
                print(f"   - Estimated SPX Index Price using SPY ETF: {round(spx_ltp, 2)}")

        # 1.2 Public Web Fallback 
        if math.isnan(spx_ltp) or spx_ltp <= 1.0:
            print("   - IBKR Data API is BLOCKED. Requesting Public Market Price...")
            try:
                headers = {'User-Agent': 'Mozilla/5.0'}
                url = "https://query1.finance.yahoo.com/v8/finance/chart/%5EGSPC"
                response = requests.get(url, headers=headers, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    spx_ltp = data['chart']['result'][0]['meta']['regularMarketPrice']
                    print(f"   - Captured SPX Index Price from Public Web: {round(spx_ltp, 2)}")
            except Exception as e:
                print(f"   - Public fallback failed: {e}")

        # 1.3 Manual Input Fallback
        if math.isnan(spx_ltp) or spx_ltp <= 1.0:
            user_input = input("\nCRITICAL: All price sources failed. Enter current SPX Index Price manually: ")
            try:
                spx_ltp = float(user_input)
            except ValueError:
                print("Error: Invalid input. Strategy Aborted.")
                return
        
        atm_strike = int(round(spx_ltp / 5) * 5)
        print(f"Target ATM Strike: {atm_strike} (At Index: {round(spx_ltp, 2)})")
        
        # 2. Find Nearest Expiry Options
        print("Searching for nearest AVAILABLE SPX Option Expiry for Strike {}...".format(atm_strike))
        call_template = Option('SPX', '', atm_strike, 'C', 'CBOE', currency='USD')
        put_template = Option('SPX', '', atm_strike, 'P', 'CBOE', currency='USD')
        
        # Fetch all contract details
        call_details = ib.reqContractDetails(call_template)
        put_details = ib.reqContractDetails(put_template)
        
        # Get today's date YYYYMMDD to filter out expired contracts
        today_str = time.strftime('%Y%m%d')
        
        # Filter: Only keep contracts that expire TODAY or LATER
        valid_calls = [d for d in call_details if d.contract.lastTradeDateOrContractMonth >= today_str]
        valid_puts = [d for d in put_details if d.contract.lastTradeDateOrContractMonth >= today_str]

        if not valid_calls or not valid_puts:
            print(f"Error: No ACTIVE SPX options found for {atm_strike}. Check TWS connection.")
            return

        # Sort by Expiry Date (nearest first)
        valid_calls.sort(key=lambda x: x.contract.lastTradeDateOrContractMonth)
        valid_puts.sort(key=lambda x: x.contract.lastTradeDateOrContractMonth)
        
        # Select the nearest expiry contract
        call_contract = valid_calls[0].contract
        put_contract = valid_puts[0].contract
        print(f"Selected Expiry: {call_contract.lastTradeDateOrContractMonth} ({call_contract.tradingClass})")

        # 3. Place Market Sell Orders
        print("\n--- PLACING ENTRY SELL ORDERS ---")
        # Explicitly set tif='DAY' to avoid Market Preset warnings
        call_trade = ib.placeOrder(call_contract, MarketOrder('SELL', 1, tif='DAY'))
        put_trade = ib.placeOrder(put_contract, MarketOrder('SELL', 1, tif='DAY'))
        
        print("Waiting for orders to fill...")
        # Wait up to 10 seconds for fills
        for _ in range(10):
            if call_trade.isDone() and put_trade.isDone():
                break
            ib.sleep(1)

        # 4. Define and Place Exit Brackets (TP 50% / SL 150%)
        # Note: Since we SOLD, our exit is a BUY back
        for leg_name, trade in [("CALL", call_trade), ("PUT", put_trade)]:
            entry_price = trade.orderStatus.avgFillPrice or trade.orderStatus.lastFillPrice or 0.0
            
            if entry_price <= 0:
                print(f"Warning: Leg {leg_name} not confirmed/filled. Auto-bracket skipped.")
                continue
                
            qty = trade.order.totalQuantity
            contract = trade.contract
            
            # Risk Levels (Rounded to nearest tick size 0.05 for SPX)
            tp_buy_price = round((entry_price * 0.50) * 20) / 20
            sl_stop_price = round((entry_price * 1.50) * 20) / 20
            
            print(f"\nLeg {leg_name} filled at {entry_price}")
            print(f"   Take-Profit Buy Limit: {tp_buy_price}")
            print(f"   Stop-Loss Buy Stop:    {sl_stop_price}")

            # OCA (One-Cancels-All) Group: Linked risk management
            oca_group = f"SPX_EXIT_{trade.order.permId}"
            
            # TP Limit Buy
            tp_order = LimitOrder('BUY', qty, tp_buy_price, ocaGroup=oca_group, ocaType=1, tif='GTC')
            ib.placeOrder(contract, tp_order)
            
            # SL Stop Buy
            sl_order = StopOrder('BUY', qty, sl_stop_price, ocaGroup=oca_group, ocaType=1, tif='GTC')
            ib.placeOrder(contract, sl_order)
            
            print(f"Risk Brackets placed for {leg_name}")

        print("\n--- ALL TASKS COMPLETED ---")
        ib.sleep(2)

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
    finally:
        if ib.isConnected():
            ib.disconnect()
            print("\nDisconnected.")

if __name__ == "__main__":
    sell_spx_atm_bracket_straddle()
