import os
import sys
import requests
import json
import time
import hmac
import hashlib
import email.utils
from dotenv import load_dotenv

load_dotenv()

# 1. Credentials
API_KEY = os.getenv("BROKER_API_KEY")
API_SECRET = os.getenv("BROKER_API_SECRET")

# 2. Server Rooms
SERVERS = {
    "India Testnet": "https://cdn-ind.testnet.deltaex.org",
    "Global Mainnet": "https://api.delta.exchange"
}

def get_signature(secret, method, ts, path, query_string=""):
    # Pre-hash string MUST include the '?' for Delta v2
    q = f"?{query_string}" if query_string else ""
    payload = method + str(ts) + path + q + ""
    return hmac.new(secret.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()

def sync_time(base_url):
    """Fetch live origin time with Cache-Buster"""
    try:
        cb = int(time.time() * 1000)
        res = requests.get(f"{base_url}/v2/products?page_size=1&cb={cb}", timeout=5)
        server_date = res.headers.get('Date')
        if server_date:
            timestamp = int(email.utils.parsedate_to_datetime(server_date).timestamp())
            return str(timestamp)
    except:
        pass
    return str(int(time.time()))

def run_probe():
    print(f"\n--- DELTA TRUTH REVEALER: START ---")
    
    if not API_KEY or not API_SECRET:
        print("[ERROR] No credentials found in .env!")
        return

    for name, base_url in SERVERS.items():
        print(f"\n{'-'*60}\nSERVER: {name} ({base_url})\n{'-'*60}")
        
        # Test 1: FILLS (Trade History) - Discovery not required
        print(f"\n>>> TEST 1: Fills Discovery (Global query) <<<")
        ts = sync_time(base_url)
        path = "/v2/fills"; query = "page_size=5"
        sig = get_signature(API_SECRET, "GET", ts, path, query)
        h = { 'api-key': API_KEY, 'x-api-key': API_KEY, 'signature': sig, 'timestamp': ts }
        
        discovered_assets = []
        try:
            r = requests.get(f"{base_url}{path}?{query}", headers=h, timeout=10)
            if r.status_code == 200:
                data = r.json().get('result', [])
                print(f"[SUCCESS] Found {len(data)} trades.")
                for item in data:
                    asset = item.get('product', {}).get('underlying_asset', {}).get('symbol')
                    if asset and asset not in discovered_assets: discovered_assets.append(asset)
                    # Snapshot
                    print(f"    - ID: {item.get('id')} | Sym: {item.get('product', {}).get('symbol')} | Size: {item.get('size')}")
            else:
                print(f"[ERROR] Fills failed (HTTP {r.status_code}): {r.text[:100]}...")
        except:
            pass

        # Test 2: POSITIONS with Discovered Assets
        if not discovered_assets: discovered_assets = ['BTC', 'ETH']
        print(f"\n>>> TEST 2: Positions for Assets: {discovered_assets} <<<")
        for asset in discovered_assets[:2]:
            ts = sync_time(base_url)
            path = "/v2/positions"; query = f"underlying_asset_symbol={asset}"
            sig = get_signature(API_SECRET, "GET", ts, path, query)
            h['signature'] = sig; h['timestamp'] = ts
            
            try:
                r = requests.get(f"{base_url}{path}?{query}", headers=h, timeout=10)
                if r.status_code == 200:
                    data = r.json().get('result', [])
                    active = [p for p in data if abs(float(p.get('size') or 0)) > 0]
                    print(f"[SUCCESS] {asset} Items found: {len(data)} (Active: {len(active)})")
                    for p in active:
                        print(f"    - Sym: {p.get('product_symbol')} | Entry: {p.get('entry_price')} | Size: {p.get('size')}")
                else:
                    print(f"[ERROR] {asset} Positions failed: {r.status_code}")
            except:
                pass

        # Test 3: ORDERS for Discovered Assets
        print(f"\n>>> TEST 3: Orders for Assets: {discovered_assets} (Global list) <<<")
        for asset in discovered_assets[:2]:
            ts = sync_time(base_url)
            path = "/v2/orders"; query = f"underlying_asset_symbol={asset}&state=open,filled,cancelled,rejected&page_size=5"
            sig = get_signature(API_SECRET, "GET", ts, path, query)
            h['signature'] = sig; h['timestamp'] = ts
            
            try:
                r = requests.get(f"{base_url}{path}?{query}", headers=h, timeout=10)
                if r.status_code == 200:
                    data = r.json().get('result', [])
                    print(f"[SUCCESS] {asset} Orders found: {len(data)}")
                    for o in data[:3]:
                        print(f"    - ID: {o.get('id')} | Sym: {o.get('product', {}).get('symbol')} | State: {o.get('state')}")
                else:
                    print(f"[ERROR] {asset} Orders failed: {r.status_code}")
            except:
                pass

    print(f"\n--- TRUTH REVEALER COMPLETE ---")

if __name__ == "__main__":
    run_probe()
