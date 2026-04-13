import asyncio
import os
import math
from ib_insync import IB, MarketOrder, LimitOrder, Contract
from broker.ibkr.api.order_api import get_ib_connection

def close_ibkr_position(symbol, auth="0:::7497"):
    """
    Bulletproof function to close a specific IBKR position by symbol.
    Can be called from any Python strategy.
    
    Args:
        symbol (str): The localSymbol or symbol to close (e.g., 'EUR.USD' or 'WL2J6 C11500')
        auth (str): The 'clientId:::port' string.
    """
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib:
        return False, "Failed to connect to TWS Master ID"
    
    try:
        print(f"Scanning portfolio for {symbol}...")
        ib.reqPositions()
        ib.sleep(2)
        
        target_pos = None
        for p in ib.positions():
            psym = str(p.contract.localSymbol or p.contract.symbol).strip()
            if symbol.strip() in psym:
                target_pos = p
                break
        
        if not target_pos:
            return False, f"No active position found for {symbol}"
        
        print(f"Position Found: {target_pos.contract.localSymbol} | Qty: {target_pos.position}")
        
        action = "SELL" if target_pos.position > 0 else "BUY"
        qty = abs(target_pos.position)
        
        # Guard for Crude Oil Multiplier
        if target_pos.contract.symbol == 'CL':
            target_pos.contract.multiplier = '1000'
            
        print(f"Executing {action} for {qty} units...")
        
        # Qualify before sending
        ib.qualifyContracts(target_pos.contract)
        
        # Use Marketable Limit for better fills on options
        trade = ib.placeOrder(target_pos.contract, MarketOrder(action, qty))
        
        # Wait for acceptance
        for i in range(10):
            ib.waitOnUpdate(0.2)
            if trade.orderStatus.status in ('Submitted', 'Filled', 'PreSubmitted'):
                break
                
        return True, f"Close order placed: {trade.orderStatus.status}"
        
    except Exception as e:
        return False, str(e)
    finally:
        ib.disconnect()

def close_all_ibkr_positions(auth="0:::7497"):
    """Closes EVERY open position in the TWS account."""
    ib = get_ib_connection(auth, specific_cid=0)
    if not ib: return False, "Conn Fail"
    try:
        ib.reqPositions(); ib.sleep(2); count = 0
        for p in ib.positions():
            if p.position == 0: continue
            action = "SELL" if p.position > 0 else "BUY"
            if p.contract.symbol == 'CL': p.contract.multiplier = '1000'
            ib.qualifyContracts(p.contract)
            ib.placeOrder(p.contract, MarketOrder(action, abs(p.position)))
            count += 1
        return True, f"Closed {count} positions"
    finally:
        ib.disconnect()
