from broker.deltaex.api.order_api import _get_base_url, _get_api_creds
import requests
from utils.logging import get_logger

logger = get_logger(__name__)

def get_ticker(symbol, auth_token):
    """Fetch live ticker data from Delta Exchange"""
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    
    # Delta usually uses "/" in tickers but OpenAlgo usually uses "_" or just symbol.
    # Convert "BTC-USDT" to "BTC" etc. if needed
    symbol = symbol.upper()
    
    path = f"/v2/tickers/{symbol}"
    url = f"{_get_base_url(is_testnet, is_india, is_demo, is_india_testnet)}{path}"
    
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            ticker = data.get('result', {})
            return {
                "symbol": ticker.get('symbol', symbol),
                "last_price": float(ticker.get('last_price', 0)),
                "change": float(ticker.get('close_24h', 0)),
                "high": float(ticker.get('high_24h', 0)),
                "low": float(ticker.get('low_24h', 0)),
                "volume": float(ticker.get('volume_24h', 0))
            }
        else:
            logger.error(f"Delta Ticker Error: HTTP {response.status_code}")
            return {}
    except Exception as e:
        logger.error(f"Delta Ticker Exception: {e}")
        return {}

def get_market_data(symbols, auth_token):
    """Fetch multiple tickers for the dashboard"""
    if not isinstance(symbols, list): symbols = [symbols]
    data_list = []
    for s in symbols:
        ticker = get_ticker(s, auth_token)
        if ticker: data_list.append(ticker)
    return data_list
