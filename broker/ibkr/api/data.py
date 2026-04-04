import pandas as pd
from utils.logging import get_logger
from broker.ibkr.api.order_api import get_ib_connection

logger = get_logger(__name__)

class BrokerData:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def get_quotes(self, symbol: str, exchange: str) -> dict:
        ib = get_ib_connection(self.auth_token)
        if not ib:
            raise Exception("Failed to connect to IBKR TWS")
        
        try:
            from ib_insync import Contract
            parts = symbol.split(':')
            symbol_only = parts[0]
            currency = parts[1] if len(parts) > 1 else "USD"
            exch = parts[2] if len(parts) > 2 else "SMART"
            sec_type = parts[3] if len(parts) > 3 else "STK"

            contract = Contract(symbol=symbol_only, secType=sec_type, exchange=exch, currency=currency)
            ib.qualifyContracts(contract)
            
            ticker = ib.reqTickers(contract)[0]
            
            return {
                "bid": ticker.bid,
                "ask": ticker.ask,
                "open": ticker.open,
                "high": ticker.high,
                "low": ticker.low,
                "ltp": ticker.last,
                "prev_close": ticker.prevBidPrice, # Rough estimate
                "volume": ticker.volume,
                "oi": 0
            }
        finally:
            ib.disconnect()

    def get_history(self, symbol: str, exchange: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        ib = get_ib_connection(self.auth_token)
        if not ib:
            raise Exception("Failed to connect to IBKR TWS")

        try:
            from ib_insync import Contract
            parts = symbol.split(':')
            symbol_only = parts[0]
            currency = parts[1] if len(parts) > 1 else "USD"
            exch = parts[2] if len(parts) > 2 else "SMART"
            sec_type = parts[3] if len(parts) > 3 else "STK"

            contract = Contract(symbol=symbol_only, secType=sec_type, exchange=exch, currency=currency)
            ib.qualifyContracts(contract)

            # Map interval to IBKR duration/barSize
            # Simple mapping for now
            bar_size = "1 min"
            if interval == "1m": bar_size = "1 min"
            elif interval == "5m": bar_size = "5 mins"
            elif interval == "15m": bar_size = "15 mins"
            elif interval == "1h": bar_size = "1 hour"
            elif interval == "D": bar_size = "1 day"

            bars = ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr='1 D',
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True
            )
            
            df = pd.DataFrame(bars)
            if not df.empty:
                df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
                df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
                df['timestamp'] = pd.to_datetime(df['timestamp']).view('int64') // 10**9
            
            return df
        finally:
            ib.disconnect()
