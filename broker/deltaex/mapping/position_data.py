def map_position_data(pos):
    """
    Standardize Delta Exchange position data for the OpenAlgo positions table.
    """
    # Delta format: {'symbol': 'BTC-USDT', 'size': 1, 'entry_price': '50000', 'mark_price': '50005'}
    symbol = pos.get('product', {}).get('symbol', 'Unknown')
    
    size = float(pos.get('size', 0))
    side = "BUY" if size > 0 else ("SELL" if size < 0 else "NONE")
    
    entry_price = float(pos.get('entry_price', 0))
    mark_price = float(pos.get('mark_price', 0))
    
    # Calculate P&L if not provided
    realized_pnl = float(pos.get('realized_pnl', 0))
    unrealized_pnl = float(pos.get('unrealized_pnl', 0))

    return {
        "trading_symbol": symbol,
        "exchange": "DELTA",
        "transaction_type": side,
        "quantity": abs(size),
        "product": "NRML",
        "average_price": entry_price,
        "last_price": mark_price,
        "pnl": round(realized_pnl + unrealized_pnl, 2),
        "unrealized_pnl": unrealized_pnl,
        "realized_pnl": realized_pnl
    }

def map_positions_data(positions):
    """Map a list of Delta positions to OpenAlgo format"""
    if not positions: return []
    if isinstance(positions, list):
         return [map_position_data(p) for p in positions]
    elif isinstance(positions, dict) and 'result' in positions:
         return [map_position_data(p) for p in positions.get('result', [])]
    return []
