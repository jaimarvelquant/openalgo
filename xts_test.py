import asyncio
import httpx
import sys
from dotenv import load_dotenv
load_dotenv()

async def test_xts_orders():
    # User's token from the recent logs
    from database.auth_db import get_auth_token
    AUTH_TOKEN = get_auth_token("jainamprop")
    if not AUTH_TOKEN:
        print("Please log into Jainamprop to generate a token first.")
        return

    headers = {
        "authorization": AUTH_TOKEN,
        "content-type": "application/json"
    }

    base_url = "https://smpb.jainam.in:4143"
    endpoints = [
        f"{base_url}/interactive/orders",
        f"{base_url}/interactive/orders?clientID=PRO1489",
        f"{base_url}/interactive/orders?clientID=ZZJ17038",
        f"{base_url}/9interactive/orders",
        f"{base_url}/9interactive/orders?clientID=PRO1489"
    ]

    async with httpx.AsyncClient(http2=True, verify=False) as client:
        for url in endpoints:
            print(f"\n--- Testing: {url} ---")
            try:
                r = await client.get(url, headers=headers, timeout=10)
                print(f"Status: {r.status_code}")
                print(f"Response: {r.text}")
            except Exception as e:
                print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_xts_orders())
