from alpaca.trading.client import TradingClient
from utils.logging import get_logger

logger = get_logger(__name__)

def get_margin_data(auth_token):
    """
    Fetch account margin and cash details for the Alpaca dashboard.
    auth_token format: MODE:::API_KEY:::SECRET_KEY
    """
    try:
        parts = auth_token.split(":::")
        if len(parts) >= 3:
            mode = parts[0]
            api_key = parts[1]
            secret_key = parts[2]
            is_paper = (mode == "PAPER")
            
            # Initialize Client
            client = TradingClient(api_key, secret_key, paper=is_paper)
            
            # Fetch Account Info
            account = client.get_account()
            
            # Fetch Positions to calculate unrealized P&L
            # Alpaca account object DOES NOT have unrealized_pl directly
            positions = client.get_all_positions()
            
            # Total Unrealized (All Time)
            unrealized_pl_all = sum(float(p.unrealized_pl) for p in positions)
            
            # Today's performance derivation
            # total_today_pnl = current_equity - last_closing_equity
            equity = float(account.equity)
            last_equity = float(account.last_equity)
            total_today_pnl = equity - last_equity
            
            # today_unrealized = sum(p.unrealized_intraday_pl)
            today_unrealized = sum(float(getattr(p, 'unrealized_intraday_pl', 0.0)) for p in positions)
            
            # today_realized = total_today_pnl - today_unrealized
            today_realized = total_today_pnl - today_unrealized
            
            # Map to OpenAlgo dashboard structure
            # Dashboard expectations: availablecash, collateral, m2munrealized, m2mrealized, utiliseddebits
            funds_data = {
                "availablecash": float(account.buying_power),
                "collateral": float(account.equity) - float(account.cash),
                "m2munrealized": unrealized_pl_all,
                "m2mrealized": today_realized, 
                "utiliseddebits": float(account.initial_margin),
                # Keep extra fields for reference or debugging
                "equity": float(account.equity),
                "cash": float(account.cash),
                "currency": account.currency,
                "status": str(account.status)
            }
            
            return funds_data
            
    except Exception as e:
        logger.error(f"Alpaca get_margin_data error: {e}")
        return {}
    
    return {}
