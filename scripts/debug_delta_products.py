import requests
import json

base_url = "https://cdn-ind.testnet.deltaex.org"
res = requests.get(f"{base_url}/v2/products", timeout=10)
products = res.json().get('result', [])
for p in products[:50]:
    print(f"Sym: {p.get('symbol')} | Type: {p.get('product_type')} | Under: {p.get('underlying_asset', {}).get('symbol')}")
