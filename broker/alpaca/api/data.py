import pandas as pd
from datetime import datetime
from alpaca.data.historical import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, CryptoBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from utils.logging import get_logger

logger = get_logger(__name__)

class BrokerData:
    def __init__(self, auth_token):
        """
        auth_token format: MODE:::API_KEY:::SECRET_KEY
        """
        try:
            parts = auth_token.split(":::")
            if len(parts) >= 3:
                self.mode = parts[0]
                self.api_key = parts[1]
                self.secret_key = parts[2]
            else:
                # Fallback for old/malformed tokens
                self.mode = "LIVE"
                self.api_key = ""
                self.secret_key = ""
                
            self.is_paper = (self.mode == "PAPER")
            self.stock_client = StockHistoricalDataClient(self.api_key, self.secret_key)
            self.crypto_client = CryptoHistoricalDataClient(self.api_key, self.secret_key)
        except Exception as e:
            logger.error(f"Alpaca BrokerData Init Error: {e}")
            raise

    def get_history(self, symbol: str, exchange: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical bars for Stocks or Crypto.
        """
        # Map OpenAlgo interval to Alpaca TimeFrame
        tf_map = {
            "1m": TimeFrame.Minute,
            "5m": TimeFrame(5, TimeFrameUnit.Minute),
            "15m": TimeFrame(15, TimeFrameUnit.Minute),
            "1h": TimeFrame.Hour,
            "D": TimeFrame.Day
        }
        timeframe = tf_map.get(interval, TimeFrame.Minute)
        
        from datetime import timezone
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        
        # Determine if it's Crypto (usually characterized by / in symbol or exchange)
        is_crypto = exchange.upper() in ["CRYPTO", "ALPACA_CRYPTO"] or "/" in symbol
        
        try:
            if is_crypto:
                # Alpaca Crypto Ticker Map: BTCUSD instead of BTC/USD for the request
                clean_symbol = symbol.replace("/", "")
                request_params = CryptoBarsRequest(
                    symbol_or_symbols=clean_symbol,
                    timeframe=timeframe,
                    start=start_dt,
                    end=end_dt
                )
                bars = self.crypto_client.get_crypto_bars(request_params)
            else:
                request_params = StockBarsRequest(
                    symbol_or_symbols=symbol,
                    timeframe=timeframe,
                    start=start_dt,
                    end=end_dt
                )
                bars = self.stock_client.get_stock_bars(request_params)
            
            if not bars or not hasattr(bars, 'df') or bars.df.empty:
                return pd.DataFrame()
            
            df = bars.df.copy()
            
            # Alpaca multi-index df often has (symbol, timestamp)
            if isinstance(df.index, pd.MultiIndex):
                df = df.xs(symbol) if symbol in df.index.levels[0] else df.reset_index(level=0, drop=True)
            
            # Standardize columns to OpenAlgo format
            df.index.name = 'timestamp'
            df = df.reset_index()
            # Convert to unix timestamp (seconds)
            df['timestamp'] = pd.to_datetime(df['timestamp']).view('int64') // 10**9
            
            return df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
            
        except Exception as e:
            logger.error(f"Alpaca get_history Error for {symbol}: {e}")
            return pd.DataFrame()

    def get_quotes(self, symbol: str, exchange: str) -> dict:
        """
        Fetch current market price (LTP).
        """
        # For simple integration, return a compatible dict
        # In a real scenario, use StockQuotesRequest or CryptoQuotesRequest
        try:
            # Quick hack: get last 1m bar to estimate LTP if needed, 
            # but better to use a dedicated quote method if available in SDK
            # For now, let's just return keys and let the dashboard handle it
            return {
                "bid": 0.0,
                "ask": 0.0,
                "ltp": 0.0
            }
        except:
            return {"bid": 0.0, "ask": 0.0, "ltp": 0.0}
