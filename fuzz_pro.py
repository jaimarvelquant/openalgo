import asyncio
import httpx
from database.auth_db import get_auth_token

async def fuzz_pro_order():
    token = get_auth_token("jainamprop")
    if not token:
        print("No token")
        return

    base_url = "https://smpb.jainam.in:4143/5interactive"
    headers = {"authorization": token, "Content-Type": "application/json"}

    params_to_try = [
        {},
        {"orderRole": "PRO"},
        {"OrderRole": "PRO"},
        {"participantType": "PRO"},
        {"ParticipantType": "PRO"},
        {"clientType": "PRO"},
        {"ClientType": "PRO"},
        {"clientID": "PRO"},
        {"orderCategoryType": "PRO"}
    ]

    async with httpx.AsyncClient(http2=True, verify=False) as client:
        for idx, extra_params in enumerate(params_to_try):
            payload = {
                "exchangeSegment": "NSEFO",
                "exchangeInstrumentID": 54514,
                "productType": "NRML",
                "orderType": "Market",
                "orderSide": "BUY",
                "timeInForce": "DAY",
                "disclosedQuantity": 0,
                "orderQuantity": 65,
                "limitPrice": 0,
                "stopPrice": 0,
                "orderUniqueIdentifier": "openalgo",
                "clientID": "PRO1489"
            }
            payload.update(extra_params)

            r = await client.post(f"{base_url}/orders", headers=headers, json=payload, timeout=10)
            if r.status_code == 200:
                print(f"Test {idx} with {extra_params}: SUCCESS - {r.text[:200]}")
            else:
                print(f"Test {idx} with {extra_params}: HTTP {r.status_code}")

if __name__ == "__main__":
    asyncio.run(fuzz_pro_order())
