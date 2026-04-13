from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, AssetClass
from utils.logging import get_logger

logger = get_logger(__name__)

def transform_data(data):
    """
    Transform OpenAlgo trade data into Alpaca request objects.
    """
    symbol = str(data.get("symbol", "")).upper()
    action = str(data.get("action", "BUY")).upper()
    order_type = str(data.get("order_type", "MARKET")).upper()
    quantity = float(data.get("quantity", 0))
    limit_price = float(data.get("price", 0))
    
    # Determine side
    side = OrderSide.BUY if action == "BUY" else OrderSide.SELL
    
    # Handle Crypto symbol mapping (OpenAlgo BTC-USD -> Alpaca BTC/USD or BTCUSD)
    # Alpaca expects the pair for crypto, often with a slash or without for bars.
    # For orders, usually the ticker is fine (e.g. BTCUSD)
    is_crypto = "/" in symbol or "-" in symbol
    if is_crypto:
        symbol = symbol.replace("-", "/") # Standardize to BTC/USD
    
    # Map TimeInForce (standard GTC for most OpenAlgo strategies)
    tif = TimeInForce.GTC
    
    try:
        if order_type == "LIMIT":
            request = LimitOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=tif,
                limit_price=limit_price
            )
        else:
            request = MarketOrderRequest(
                symbol=symbol,
                qty=quantity,
                side=side,
                time_in_force=tif
            )
            
        return {
            "request": request,
            "is_crypto": is_crypto
        }
        
    except Exception as e:
        logger.error(f"Alpaca Mapping Error: {e}")
        return {}
