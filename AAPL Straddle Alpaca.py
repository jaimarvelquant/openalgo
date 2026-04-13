import sys
import os
import math
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient, OptionHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest, OptionLatestQuoteRequest

# ---------------------------------------------------------------------------
# AAPL ATM Straddle Order (Alpaca Direct)
# ---------------------------------------------------------------------------
# This script uses the alpaca-py library to place a straddle order on Alpaca.
# It identifies the ATM strike and formats the option symbols using the 
# Options Symbology Standard (OSI).
# ---------------------------------------------------------------------------

# Reconfigure stdout for UTF-8 to handle any special characters in Windows
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older python versions if needed
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1. Configuration (Paper Trading by default)
API_KEY = "PKYHQBIL63VIJGVVXLC2RBY6MQ"
SECRET_KEY = "8JVdEMKYbwZk65m9GKfhfKDRFWe9k8jHLfK8UNwvv7V5"
PAPER = True 

def get_next_friday():
    """Returns the date of the upcoming Friday."""
    d = datetime.now()
    # If today is Friday, it will pick today. Adjust logic if same-day is too late.
    while d.weekday() != 4: # 4 is Friday
        d += timedelta(days=1)
    return d

def format_alpaca_option_symbol(underlying, expiry_dt, strike, option_type):
    """
    Formats an OSI compliant option symbol for Alpaca.
    Format: [Symbol][YYMMDD][C/P][Strike Price cents]
    Example: AAPL250417C00185000 (AAPL 185 Call expiring April 17, 2025)
    """
    expiry_str = expiry_dt.strftime('%y%m%d')
    # Strike is multiplied by 1000 and zero-padded to 8 digits
    strike_fixed = int(strike * 1000)
    strike_str = f"{strike_fixed:08d}"
    return f"{underlying.upper():<6}{expiry_str}{option_type}{strike_str}".replace(" ", "")

def place_alpaca_straddle(action=OrderSide.BUY, qty=1):
    trading_client = TradingClient(API_KEY, SECRET_KEY, paper=PAPER)
    stock_data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    option_data_client = OptionHistoricalDataClient(API_KEY, SECRET_KEY)
    
    print(f"--- AAPL Alpaca ATM Straddle - LIMIT Order ({'Paper' if PAPER else 'Live'}) ---")
    
    try:
        # 1. Fetch AAPL Latest Price
        print("Fetching AAPL latest price...")
        quote_req = StockLatestQuoteRequest(symbol_or_symbols="AAPL")
        quote = stock_data_client.get_stock_latest_quote(quote_req)
        
        # Calculate Mid-price
        price = (quote["AAPL"].ask_price + quote["AAPL"].bid_price) / 2
        print(f"Current AAPL Price: {price:.2f}")
        
        # 2. Calculate ATM Strike
        # US Options typically have 1.0 or 0.5 intervals. We'll round to nearest integer.
        atm_strike = round(price)
        print(f"Target ATM Strike: {atm_strike}")
        
        # 3. Identify Target Expiry (Next Friday)
        expiry_dt = get_next_friday()
        print(f"Target Expiry: {expiry_dt.strftime('%Y-%m-%d')}")
        
        # 4. Generate Option Symbols (OSI Standard)
        call_sym = format_alpaca_option_symbol("AAPL", expiry_dt, atm_strike, "C")
        put_sym = format_alpaca_option_symbol("AAPL", expiry_dt, atm_strike, "P")
        
        print(f"Generated Call Symbol: {call_sym}")
        print(f"Generated Put Symbol:  {put_sym}")
        
        # 5. Submit Limit Orders
        print("\nFetching option quotes for Limit prices...")
        for sym in [call_sym, put_sym]:
            try:
                # Fetch Mid-price for the option
                opt_quote_req = OptionLatestQuoteRequest(symbol_or_symbols=sym)
                opt_quote = option_data_client.get_option_latest_quote(opt_quote_req)
                
                bid = opt_quote[sym].bid_price
                ask = opt_quote[sym].ask_price
                mid_price = round((bid + ask) / 2, 2)
                
                if mid_price <= 0:
                    print(f"Warning: Mid-price for {sym} is 0. Using small default or skipping.")
                    continue
                    
                print(f"Targeting {sym} at Limit Price: {mid_price} (Bid: {bid}, Ask: {ask})")
                
                order_data = LimitOrderRequest(
                    symbol=sym,
                    qty=qty,
                    side=action,
                    limit_price=mid_price,
                    time_in_force=TimeInForce.GTC
                )
                
                order = trading_client.submit_order(order_data=order_data)
                print(f"SUCCESS: Limit Order placed for {sym}. ID: {order.id}")
            except Exception as e:
                print(f"FAILED: Order error for {sym}: {str(e)}")

    except Exception as e:
        print(f"CRITICAL ERROR: {str(e)}")

if __name__ == "__main__":
    # Change to OrderSide.SELL for short straddle
    place_alpaca_straddle(action=OrderSide.BUY, qty=1)
