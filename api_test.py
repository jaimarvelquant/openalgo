import requests

BASE_URL = "http://localhost:5000/api/v1"
API_KEY = "de31866767c07868eef202e120f83910ff837ec109560dd497f43da2597fd22e"

class OpenAlgoClient:
    def __init__(self, base_url=BASE_URL, api_key=API_KEY):
        self.base_url = base_url
        self.api_key = api_key

    def _post(self, endpoint, payload):
        payload["apikey"] = self.api_key
        url = f"{self.base_url}/{endpoint}"
        try:
            r = requests.post(url, json=payload)
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _get(self, endpoint):
        url = f"{self.base_url}/{endpoint}"
        try:
            r = requests.get(url, params={"apikey": self.api_key})
            return r.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}

    # --- Order Management ---
    def place_order(self):
        return self._post("placeorder", {
            "symbol": "SBIN", "exchange": "NSE",
            "action": "BUY", "quantity": 1,
            "product": "MIS", "pricetype": "MARKET",
            "strategy": "demo"
        })

    def smart_order(self):
        return self._post("placesmartorder", {
            "symbol": "SBIN", "exchange": "NSE",
            "action": "BUY", "quantity": 1,
            "product": "MIS", "pricetype": "MARKET",
            "position_size": 5, "strategy": "demo"
        })

    # --- Market Data ---
    def get_quote(self):
        return self._post("quotes", {"symbol": "SBIN", "exchange": "NSE"})

    def get_history(self):
        return self._post("history", {
            "symbol": "SBIN", "exchange": "NSE",
            "interval": "D",  # daily candles
            "start_date": "2026-01-01",
            "end_date": "2026-03-13"
        })

    def option_chain(self):
        return self._post("optionchain", {
            "underlying": "NIFTY", "exchange": "NFO",
            "expiry_date": "2026-03-17"
        })

    # --- Account Info ---
    def funds(self):
        return self._post("funds", {})

    def holdings(self):
        return self._post("holdings", {})

    # --- Symbol & Search ---
    def instruments(self):
        return self._get("instruments?exchange=NSE")

    def search_symbol(self, query="SBIN"):
        return self._post("search", {"query": query})

    # --- Utilities ---
    def ping(self):
        return self._post("ping", {})

    def market_timings(self):
        return self._post("markettimings", {"exchange": "NSE"})

    def market_holidays(self):
        return self._post("marketholidays", {"exchange": "NSE"})


if __name__ == "__main__":
    client = OpenAlgoClient()

    print("Ping:", client.ping())
    print("Place Order:", client.place_order())
    print("Smart Order:", client.smart_order())
    print("Quote:", client.get_quote())
    print("History:", client.get_history())
    print("Option Chain:", client.option_chain())
    print("Funds:", client.funds())
    print("Holdings:", client.holdings())
    # print("Instruments:", client.instruments())
    print("Search Symbol:", client.search_symbol())
    print("Market Timings:", client.market_timings())
    print("Market Holidays:", client.market_holidays())
