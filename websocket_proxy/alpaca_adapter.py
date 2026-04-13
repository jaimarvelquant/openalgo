import asyncio
import threading
import time
from datetime import datetime
from alpaca.data.live import StockDataStream, CryptoDataStream
from utils.logging import get_logger
from .base_adapter import BaseBrokerWebSocketAdapter

class AlpacaWebSocketAdapter(BaseBrokerWebSocketAdapter):
    """
    Alpaca WebSocket Adapter for Real-time Quotes.
    Supports both Stocks and Crypto via Alpaca SDK.
    """

    def __init__(self):
        super().__init__()
        self.stock_stream = None
        self.crypto_stream = None
        self.user_id = None
        self._loop = None
        self._thread = None
        self.logger = get_logger("alpaca_streaming")
        self.active_subscriptions = set()

    def initialize(self, broker_name, user_id, auth_data=None):
        self.user_id = user_id
        # Use provided auth_data or fetch from database (Issue #765 pattern)
        if auth_data:
            self.auth_data = auth_data
        else:
            self.logger.info(f"Fetching auth token from DB for {user_id}")
            self.auth_data = self.get_auth_token_for_user(user_id)
            
        self.logger.info(f"Initialized Alpaca Streaming for {user_id}")
        return self._create_success_response("Initialized")

    def connect(self):
        if self.connected:
            return self._create_success_response("Already connected")
        
        try:
            # auth: MODE:::API_KEY:::SECRET_KEY
            auth_str = str(self.auth_data)
            self.logger.debug(f"Auth Data available (length: {len(auth_str)})")
            
            parts = auth_str.split(":::")
            if len(parts) < 3:
                self.logger.error(f"Invalid Auth Format. Expected 3 parts, got {len(parts)} from credentials")
                return self._create_error_response("AUTH_FAIL", f"Invalid Auth Format (parts={len(parts)})")
            
            mode = parts[0]
            api_key = parts[1]
            secret_key = parts[2]
            # Use SIP for Live, IEX for Paper (SDK handles this often)
            
            self._thread = threading.Thread(target=self._run_loop, args=(api_key, secret_key), daemon=True)
            self._thread.start()
            
            # Wait for loop to be ready
            timeout = 10
            while self._loop is None and timeout > 0:
                time.sleep(0.5)
                timeout -= 0.5
            
            self.connected = True
            self.logger.info("Alpaca Streaming Thread Started")
            return self._create_success_response("Connected")
        except Exception as e:
            self.logger.error(f"Connect Error: {e}")
            return self._create_error_response("ERROR", str(e))

    def _run_loop(self, api_key, secret_key):
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        self.stock_stream = StockDataStream(api_key, secret_key)
        self.crypto_stream = CryptoDataStream(api_key, secret_key)
        
        # Start the streams (this is blocking in the thread)
        # Note: We need to subscribe to something or they might close
        # But run() handles connection and waiting.
        
        async def run_streams():
            await asyncio.gather(
                self.stock_stream._run_forever(),
                self.crypto_stream._run_forever()
            )

        self._loop.run_until_complete(run_streams())

    async def _on_quote(self, data):
        """Callback for stock quotes"""
        try:
            symbol = data.symbol
            topic = f"ALPACA_{symbol}_QUOTE"
            payload = {
                "ltp": float(data.ask_price + data.bid_price) / 2 if hasattr(data, 'ask_price') else 0,
                "bid": float(data.bid_price) if hasattr(data, 'bid_price') else 0,
                "ask": float(data.ask_price) if hasattr(data, 'ask_price') else 0,
                "volume": 0, # Quote data doesn't usually have volume
                "timestamp": int(datetime.now().timestamp()),
                "symbol": symbol,
                "exchange": "ALPACA",
                "mode": 2
            }
            # If it's a trade, better LTP
            if hasattr(data, 'price'):
                payload["ltp"] = float(data.price)
            
            self.publish_market_data(topic, payload)
        except Exception as e:
            self.logger.debug(f"Quote processing error: {e}")

    def subscribe(self, symbol, exchange, mode=2, depth_level=5):
        if not self.connected:
            return self._create_error_response("NOT_CONNECTED", "Adapter not connected")
        
        try:
            is_crypto = "/" in symbol or exchange.upper() == "CRYPTO"
            
            if is_crypto:
                future = asyncio.run_coroutine_threadsafe(
                    self._subscribe_crypto(symbol), self._loop
                )
            else:
                future = asyncio.run_coroutine_threadsafe(
                    self._subscribe_stock(symbol), self._loop
                )
            
            self.active_subscriptions.add(symbol)
            return self._create_success_response(f"Subscribed: {symbol}")
        except Exception as e:
            return self._create_error_response("ERROR", str(e))

    async def _subscribe_stock(self, symbol):
        self.stock_stream.subscribe_quotes(self._on_quote, symbol)
        self.logger.info(f"Subscribed Stock: {symbol}")

    async def _subscribe_crypto(self, symbol):
        self.crypto_stream.subscribe_quotes(self._on_quote, symbol)
        self.logger.info(f"Subscribed Crypto: {symbol}")

    def unsubscribe(self, symbol, exchange, mode=2):
        if symbol in self.active_subscriptions:
            try:
                is_crypto = "/" in symbol
                if is_crypto:
                    asyncio.run_coroutine_threadsafe(self.crypto_stream.unsubscribe_quotes(symbol), self._loop)
                else:
                    asyncio.run_coroutine_threadsafe(self.stock_stream.unsubscribe_quotes(symbol), self._loop)
                
                self.active_subscriptions.remove(symbol)
                return self._create_success_response(f"Unsubscribed: {symbol}")
            except Exception as e:
                return self._create_error_response("ERROR", str(e))
        return self._create_error_response("NOT_FOUND", "Symbol not found")

    def disconnect(self):
        if self._loop:
            try:
                # Stop streams - these are synchronous flag setters in the SDK
                if self.stock_stream:
                    self.stock_stream.stop()
                if self.crypto_stream:
                    self.crypto_stream.stop()
                
                # Request loop to stop
                if self._loop.is_running():
                    self._loop.call_soon_threadsafe(self._loop.stop())
            except Exception as e:
                self.logger.warning(f"Error during Alpaca stream stop: {e}")
        
        self.connected = False
        self.logger.info("Alpaca Streaming Disconnected")
