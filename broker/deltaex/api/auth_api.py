import hashlib
import hmac
import time
import requests
import email.utils
from utils.logging import get_logger

logger = get_logger(__name__)

def get_signature(api_secret, method, timestamp, path, query_string="", body=""):
    """
    Generate HMAC-SHA256 signature for Delta Exchange API.
    Pre-hash string MUST be: METHOD + TIMESTAMP + PATH + QUERY_STRING + BODY
    All parts must be strings with no extra spaces.
    """
    # Ensure all components are strings and cleaned
    method = str(method).upper()
    timestamp = str(timestamp)
    path = str(path)
    query_string = str(query_string)
    body = str(body)

    # Delta India v2 node expects the '?' in the signature payload if query exists
    q = f"?{query_string}" if query_string else ""
    payload = method + timestamp + path + q + body
    
    signature = hmac.new(
        api_secret.encode('utf-8'), 
        payload.encode('utf-8'), 
        hashlib.sha256
    ).hexdigest()
    
    return signature

def deep_clean(s):
    """Ensure no quotes or weird whitespace survive the .env loading"""
    if not s: return ""
    return str(s).strip().strip("'").strip('"')

def sync_time(base_url=None):
    """Fetch live server time from Delta via HTTP Date (Forces Origin sync to avoid CDN Cache)"""
    if not base_url:
        base_url = "https://api.delta.exchange"
    try:
        # CDN Cache-Buster: Delta India node often returns cached headers.
        # We append a random query parameter to force a fresh 'Date' header from origin.
        import random
        cb = f"{int(time.time())}{random.randint(100,999)}"
        res = requests.get(f"{base_url}/v2/products?page_size=1&cb={cb}", timeout=5)
        server_date = res.headers.get('Date')
        if server_date:
            # High-precision RFC date parsing to Unix timestamp
            timestamp = int(email.utils.parsedate_to_datetime(server_date).timestamp())
            return str(timestamp)
    except:
        pass
    return str(int(time.time()))

def authenticate_broker(api_key, api_secret):
    """
    Verify Delta Exchange credentials by trying regional and paper-trading endpoints.
    """
    api_key = deep_clean(api_key)
    api_secret = deep_clean(api_secret)
    
    # Official UTC seconds (Perfectly synced to Delta's internal clock)
    timestamp = sync_time()
    path = "/v2/profile"
    method = "GET"
    query_string = ""
    body = ""
    
    def get_headers(sig, ts, key):
        return {
            'api-key': key,
            'x-api-key': key,
            'signature': sig,
            'timestamp': ts,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'delta-rest-client-v2.0.0'
        }

    # Priority URLs for all global regions and account types
    urls = [
        "https://cdn-ind.testnet.deltaex.org",     # India Partner Testnet (Verified API)
        "https://api.india.delta.exchange",        # India Mainnet
        "https://api-ind.testnet.delta.exchange",  # India Testnet Fallback
        "https://testnet-api.delta.exchange",      # Global Testnet
        "https://demo-api.delta.exchange",         # Global Demo
        "https://api.delta.exchange"               # Global Mainnet
    ]

    try:
        for base_url in urls:
            try:
                # IMPORTANT: Sync time for EACH server to avoid regional drift failures during discovery
                ts = sync_time(base_url)
                signature = get_signature(api_secret, method, ts, path, query_string, body)
                
                full_url = base_url + path
                logger.info(f"Checking Delta environment: {base_url}")
                response = requests.get(full_url, headers=get_headers(signature, ts, api_key), timeout=10)
                
                if response.status_code == 200:
                    # Detect and stamp the environment
                    if "deltaex.org" in base_url: prefix = "INDIA_TESTNET:::"
                    elif "api-ind.testnet" in base_url: prefix = "INDIA_TESTNET:::"
                    elif "india" in base_url: prefix = "INDIA:::"
                    elif "demo-api" in base_url: prefix = "DEMO:::"
                    elif "testnet" in base_url: prefix = "TESTNET:::"
                    else: prefix = ""
                    
                    logger.info(f"Delta Auth SUCCESS on {base_url}")
                    return f"{prefix}{api_key}:::{api_secret}", None
                
                # Check error reason to help debug
                try:
                    data = response.json()
                    err_code = data.get('error', {}).get('code', 'unknown')
                    if err_code == 'expired_signature':
                        logger.error(f"Delta server {base_url} confirmed the key but rejected the time sync (Drift detected).")
                    else:
                        logger.warning(f"Delta server {base_url} rejected key: {err_code}")
                except:
                    logger.warning(f"Delta server {base_url} rejected request: HTTP {response.status_code}")
                
            except Exception as e:
                logger.warning(f"Delta server {base_url} unreachable: {str(e)}")
                continue

        return None, "Delta Error: API key unrecognized. Please verify Mainnet vs Testnet on your dashboard."
            
    except Exception as e:
        logger.exception(f"Delta Smart Auth Exception: {str(e)}")
        return None, f"Connection Error: {str(e)}"
