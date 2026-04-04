from broker.deltaex.api.auth_api import get_signature, sync_time
from broker.deltaex.api.order_api import _get_api_creds, _get_base_url
import requests
import json
from utils.logging import get_logger

logger = get_logger(__name__)

def get_funds(auth_token):
    """Fetch wallet balances from Delta Exchange"""
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return []
    
    timestamp = sync_time()
    path = "/v2/wallet/balances"
    signature = get_signature(api_secret, "GET", timestamp, path)
    
    headers = {
        'api-key': api_key, 
        'x-api-key': api_key,
        'signature': signature, 
        'timestamp': timestamp,
        'Content-Type': 'application/json',
        'User-Agent': 'delta-rest-client-v2.0.0'
    }
    
    url = f"{_get_base_url(is_testnet, is_india, is_demo, is_india_testnet)}{path}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            # Map Delta assets to standardized format
            funds = []
            for item in data.get('result', []):
                asset = item.get('asset', {}).get('symbol', 'Unknown')
                balance = float(item.get('balance', 0))
                if balance > 0:
                    funds.append({
                        "asset": asset,
                        "balance": balance,
                        "available": float(item.get('available_balance', 0)),
                        "margin": float(item.get('frozen_balance', 0))
                    })
            return funds
        else:
            logger.error(f"Delta Funds Error: HTTP {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Delta Funds Exception: {e}")
        return []

def get_margin_data(auth_token):
    """Fetch global account margin and P&L from Delta Exchange"""
    api_key, api_secret, is_testnet, is_india, is_demo, is_india_testnet = _get_api_creds(auth_token)
    if not api_key: return {}
    
    timestamp = sync_time()
    path = "/v2/wallet/balances" # We can derive it from here or profile
    signature = get_signature(api_secret, "GET", timestamp, path)
    
    headers = {
        'api-key': api_key, 
        'x-api-key': api_key,
        'signature': signature, 
        'timestamp': timestamp,
        'Content-Type': 'application/json',
        'User-Agent': 'delta-rest-client-v2.0.0'
    }
    
    url = f"{_get_base_url(is_testnet, is_india, is_demo, is_india_testnet)}{path}"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            total_balance = 0
            total_available = 0
            
            # Aggregate across all assets (BTC-USDT, etc.)
            for item in data.get('result', []):
                total_balance += float(item.get('balance', 0))
                total_available += float(item.get('available_balance', 0))
                logger.info(f"Asset: {item.get('asset',{}).get('symbol')}, Available: {item.get('available_balance')}")
            
            res = {
                "availablecash": str(round(total_available, 2)),
                "collateral": str(round(total_balance, 2)),
                "m2munrealized": "0.00",
                "m2mrealized": "0.00",
                "utiliseddebits": "0.00"
            }
            logger.info(f"Delta Margin SUCCESS: {res}")
            return res
        else:
            logger.error(f"Delta Margin FAILED ({response.status_code}): {response.text}")
            return {
                "availablecash": "0.00",
                "collateral": "0.00",
                "m2munrealized": "0.00",
                "m2mrealized": "0.00",
                "utiliseddebits": "0.00"
            }
    except Exception as e:
        logger.error(f"Delta Margin Exception: {str(e)}")
        return {
            "availablecash": "0.00",
            "collateral": "0.00",
            "m2munrealized": "0.00",
            "m2mrealized": "0.00",
            "utiliseddebits": "0.00"
        }
