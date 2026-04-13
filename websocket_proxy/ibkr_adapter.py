import json
import threading
import time
import asyncio
import math
from datetime import datetime
from ib_insync import IB, util, Contract, MarketOrder
import nest_asyncio

from utils.logging import get_logger
from .base_adapter import BaseBrokerWebSocketAdapter
from broker.ibkr.mapping.transform_data import transform_data

class IbkrWebSocketAdapter(BaseBrokerWebSocketAdapter):
    """
    Stabilized IBKR WebSocket Adapter (Ver 6.0)
    Uses Event-Driven approach to avoid ZMQ flooding.
    """

    def __init__(self):
        super().__init__()
        self.ib = None
        self.user_id = None
        self._streaming_thread = None
        self._stop_event = threading.Event()
        self.active_tickers = {}
        self.logger = get_logger("ibkr_streaming")
        nest_asyncio.apply()

    def initialize(self, broker_name, user_id, auth_data=None):
        self.user_id = user_id
        self.auth_data = auth_data
        self.logger.info(f"Initializing IBKR Streaming for {user_id}")
        return self._create_success_response("Initialized")

    def connect(self):
        if self.connected:
            return self._create_success_response("Already connected")
        try:
            auth = self.auth_data or "663789:::7497"
            cid_str, port_str = str(auth).split(":::")
            bcid = int(cid_str); port = int(port_str); host = "127.0.0.1"

            self.ib = IB()
            # Use Stable Offset for Streaming
            self.ib.connect(host, port, clientId=bcid + 99, timeout=10)
            
            if self.ib.isConnected():
                # Enable Delayed Data (Type 3) for users without live subscriptions
                self.ib.reqMarketDataType(3)
                self.connected = True
                self._stop_event.clear()
                self._streaming_thread = threading.Thread(target=self._run_ib_loop, daemon=True)
                self._streaming_thread.start()
                self.logger.info("IBKR Streaming Connected (Event-Driven)")
                return self._create_success_response("Connected")
            return self._create_error_response("CONN_FAIL", "Check TWS Connection")
        except Exception as e:
            return self._create_error_response("ERROR", str(e))

    def _run_ib_loop(self):
        while not self._stop_event.is_set():
            try:
                self.ib.waitOnUpdate(timeout=0.5)
            except:
                time.sleep(1)
        if self.ib: self.ib.disconnect()

    def _on_ticker_update(self, ticker):
        """Callback for LIVE ticker updates only"""
        try:
            # Use marketPrice() for most accurate quote
            ltp = ticker.marketPrice()
            if not ltp or math.isnan(ltp) or ltp <= 0: return

            symbol = ticker.contract.localSymbol or ticker.contract.symbol
            # Official OpenAlgo topic format: EXCHANGE_SYMBOL_MODE
            topic = f"IBKR_{symbol}_QUOTE"
            
            close_p = ticker.close or ltp
            vol = int(ticker.volume) if ticker.volume and not math.isnan(ticker.volume) else 0

            # Standard flat payload logic (server.py wraps this in a "data" key)
            payload = {
                "ltp": float(ltp),
                "close": float(close_p),
                "volume": vol,
                "timestamp": int(datetime.now().timestamp()),
                "symbol": symbol,
                "exchange": "IBKR",
                "mode": 2
            }
            self.publish_market_data(topic, payload)
        except Exception as e:
            self.logger.debug(f"Ticker processing error: {e}")

    def subscribe(self, symbol, exchange, mode=2, depth_level=5):
        if not self.connected or not self.ib:
            return self._create_error_response("NOT_CONNECTED", "Adapter not connected")
        try:
            payload = transform_data({"symbol": symbol, "action": "BUY", "quantity": "1"})
            contract = payload['contract']
            self.ib.qualifyContracts(contract)
            
            # Subscribe and attach EVENT callback (No more polling loops!)
            ticker = self.ib.reqMktData(contract, "", False, False)
            ticker.updateEvent += self._on_ticker_update
            
            self.active_tickers[symbol] = ticker
            self.logger.info(f"Subscribed: {symbol} (Callback Active)")
            return self._create_success_response(f"Subscribed to {symbol}")
        except Exception as e:
            return self._create_error_response("ERROR", str(e))

    def unsubscribe(self, symbol, exchange, mode=2):
        if symbol in self.active_tickers:
            ticker = self.active_tickers.pop(symbol)
            ticker.updateEvent -= self._on_ticker_update # Detach
            if self.ib: self.ib.cancelMktData(ticker.contract)
            return self._create_success_response(f"Unsubscribed: {symbol}")
        return self._create_error_response("NOT_FOUND", "Symbol not found")

    def disconnect(self):
        self._stop_event.set()
        if self._streaming_thread: self._streaming_thread.join(timeout=2)
        self.connected = False
        self.logger.info("IBKR Streaming Disconnected")
