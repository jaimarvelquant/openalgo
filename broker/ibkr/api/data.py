import pandas as pd
from datetime import datetime
from utils.logging import get_logger
from broker.ibkr.api.order_api import get_ib_connection
from broker.ibkr.mapping.transform_data import transform_data

logger = get_logger(__name__)

class BrokerData:
    def __init__(self, auth_token):
        self.auth_token = auth_token

    def get_quotes(self, symbol: str, exchange: str) -> dict:
        ib = get_ib_connection(self.auth_token)
        if not ib:
            raise Exception("Failed to connect to IBKR TWS")
        
        try:
            # Use centralized transform_data for intelligent contract discovery
            payload = transform_data({"symbol": symbol})
            contract = payload['contract']
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
            # Use centralized transform_data for intelligent contract discovery
            payload = transform_data({"symbol": symbol, "exchange": exchange})
            contract = payload['contract']
            ib.qualifyContracts(contract)

            # Map interval to IBKR duration/barSize
            # Map interval to IBKR duration/barSize
            bar_mapping = {"1m": "1 min", "5m": "5 mins", "15m": "15 mins", "1h": "1 hour", "D": "1 day"}
            bar_size = bar_mapping.get(interval, "1 min")

            # Calculate duration string
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            # Format endDateTime correctly for IBKR (YYYYMMDD HH:mm:ss)
            end_dt_str = end.strftime("%Y%m%d 23:59:59")
            
            if interval == "D":
                # For Daily data, use standard buckets for better stability
                if diff_days <= 30:
                    duration = "1 M"
                elif diff_days <= 365:
                    duration = "1 Y"
                else:
                    duration = f"{(diff_days // 365) + 1} Y"
            else:
                # Intraday duration logic
                if diff_days <= 1:
                    duration = "1 D"
                elif diff_days <= 7:
                    duration = f"{diff_days} D"
                elif diff_days <= 30:
                    duration = "1 M"
                else:
                    duration = f"{(diff_days // 30) + 1} M"

            bars = ib.reqHistoricalData(
                contract,
                endDateTime=end_dt_str,
                durationStr=duration,
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
