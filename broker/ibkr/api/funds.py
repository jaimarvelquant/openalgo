from utils.logging import get_logger
from broker.ibkr.api.order_api import get_ib_connection

logger = get_logger(__name__)

def get_margin_data(auth):
    # Use offset 2 for margin to avoid connection collision with orders/positions
    ib = get_ib_connection(auth, offset=2)
    if not ib:
        return {
            "availablecash": "0.00",
            "collateral": "0.00",
            "m2munrealized": "0.00",
            "m2mrealized": "0.00",
            "utiliseddebits": "0.00",
        }

    try:
        # Get account values
        acc_vals = ib.accountValues()
        
        available_funds = next((v.value for v in acc_vals if v.tag == 'AvailableFunds'), "0.00")
        excess_liquidity = next((v.value for v in acc_vals if v.tag == 'ExcessLiquidity'), "0.00")
        unrealized_pnl = next((v.value for v in acc_vals if v.tag == 'UnrealizedPnL'), "0.00")
        realized_pnl = next((v.value for v in acc_vals if v.tag == 'RealizedPnL'), "0.00")
        
        return {
            "availablecash": str(available_funds),
            "collateral": str(excess_liquidity),
            "m2munrealized": str(unrealized_pnl),
            "m2mrealized": str(realized_pnl),
            "utiliseddebits": "0.00",
        }
    finally:
        ib.disconnect()
