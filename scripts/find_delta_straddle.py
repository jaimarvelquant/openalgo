import os
import sys
import requests

# Mocking OpenAlgo environment
project_root = os.getcwd()
sys.path.insert(0, project_root)

def find_straddle():
    print(f"\n--- DELTA: FINDING BTC STRADDLE (Detailed) ---")
    
    base_url = "https://cdn-ind.testnet.deltaex.org"
    res = requests.get(f"{base_url}/v2/products", timeout=10)
    if res.status_code != 200:
        print("[ERROR] Could not fetch products.")
        return

    products = res.json().get('result', [])
    print(f"Total Products: {len(products)}")

    # Filter for BTC Options
    btc_options = [p for p in products if p.get('underlying_asset', {}).get('symbol') == 'BTC' and p.get('product_type') == 'option']
    
    # Sort by strike maybe? Or just see what's there
    print(f"BTC Options Found: {len(btc_options)}")
    
    # Group by expiry
    expiries = {}
    for p in btc_options:
        sym = p.get('symbol')
        # Format C-BTC-66000-050424
        parts = sym.split('-')
        if len(parts) >= 4:
            exp = parts[3]
            strike = parts[2]
            type = parts[0] # C or P
            if exp not in expiries: expiries[exp] = {}
            if strike not in expiries[exp]: expiries[exp][strike] = {}
            expiries[exp][strike][type] = sym

    # Find a strike that has both C and P
    for exp, strikes in expiries.items():
        print(f"\nExpiry: {exp}")
        count = 0
        for strike, types in strikes.items():
            if 'C' in types and 'P' in types:
                print(f"  Strike {strike} Straddle: {types['C']} & {types['P']}")
                count += 1
                if count >= 3: break # Show top 3 per expiry
        if count > 0: break # Use the first expiry that works

if __name__ == "__main__":
    find_straddle()
