from ib_insync import IB, Stock, MarketOrder
import time

def place_sbin_order():
    ib = IB()
    try:
        # Connecting to TWS on localhost port 7497 (default for paper trading)
        # Using a unique ClientID to avoid collisions with your dashboard
        print("Connecting to IBKR TWS...")
        ib.connect('127.0.0.1', 7497, clientId=663692)
        
        # Define the SBIN contract on the NSE
        contract = Stock('SBIN', 'NSE', 'INR')
        
        # Qualify the contract to fill in missing details (like conId)
        print("Qualifying SBIN contract...")
        ib.qualifyContracts(contract)
        
        # Create a Market Buy Order for 1 share
        order = MarketOrder('BUY', 1)
        
        # Place the order
        print(f"Placing Market BUY order for 1 share of {contract.localSymbol}...")
        trade = ib.placeOrder(contract, order)
        
        # Wait for a couple of seconds to see the status update
        ib.sleep(2)
        print(f"Order Status: {trade.orderStatus.status}")
        
    except Exception as e:
        print(f"Error placing order: {e}")
    finally:
        # Always disconnect to free up the ClientID
        if ib.isConnected():
            ib.disconnect()
            print("Disconnected from IBKR TWS.")

if __name__ == "__main__":
    place_sbin_order()
