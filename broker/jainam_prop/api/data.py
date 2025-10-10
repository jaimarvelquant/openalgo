import json
from broker.jainam_prop.mapping.transform_data import get_token_from_symbol, map_exchange_to_jainam
from broker.jainam_prop.api.config import get_jainam_base_url
from broker.jainam_prop.api.base_client import BaseAPIClient
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

logger = get_logger(__name__)


# ============================================================================
# API Client Class (Task 24.1 - Refactored to use BaseAPIClient)
# ============================================================================

class MarketDataClient(BaseAPIClient):
    """
    Client for Jainam Market Data API operations.

    Refactored to use BaseAPIClient (Task 24.1).
    """

    def __init__(self, auth_token: str, base_url: str = None):
        """
        Initialize Market Data API client.

        Args:
            auth_token: Market Data API token
            base_url: Jainam API base URL (optional)
        """
        super().__init__(base_url=base_url, auth_token=auth_token)

    def get_quotes(self, payload: dict) -> dict:
        """Get quotes for instruments."""
        return self._post('market.instruments.quotes', json_data=payload, timeout=10.0)

    def get_ohlc(self, params: dict) -> dict:
        """Get OHLC/historical data."""
        return self._get('market.instruments.ohlc', params=params, timeout=10.0)

    def search_instruments(self, params: dict) -> dict:
        """Search for instruments."""
        return self._get('market.search.instrumentsbystring', params=params, timeout=10.0)


# ============================================================================
# Helper Functions
# ============================================================================

def _parse_market_auth_token(auth_token):
    """
    Parse auth_token to extract market_token.

    Args:
        auth_token: JSON string or dict containing credentials

    Returns:
        str: market_token
    """
    if isinstance(auth_token, str):
        try:
            credentials = json.loads(auth_token)
        except:
            credentials = {'market_token': auth_token}
    else:
        credentials = auth_token

    return credentials.get('market_token', auth_token)

def get_quotes(symbol, exchange, auth_token):
    """
    Get quotes for a symbol from Jainam.

    Refactored to use MarketDataClient (Task 24.1).

    Args:
        symbol: Trading symbol (e.g., 'RELIANCE')
        exchange: Exchange (e.g., 'NSE')
        auth_token: Authentication token

    Returns:
        Quote data in MarvelQuant format
    """
    try:
        # Parse auth_token
        market_token = _parse_market_auth_token(auth_token)

        # Get token for symbol
        token = get_token_from_symbol(symbol, exchange)
        exchange_segment = map_exchange_to_jainam(exchange)

        # Request payload
        payload = {
            'instruments': [{
                'exchangeSegment': exchange_segment,
                'exchangeInstrumentID': token
            }],
            'xtsMessageCode': 1501,  # Touchline data
            'publishFormat': 'JSON'
        }

        # Use MarketDataClient
        client = MarketDataClient(auth_token=market_token)
        response_data = client.get_quotes(payload)

        if response_data.get('type') == 'success' and 'result' in response_data:
            quote_data = response_data['result'][0]  # First instrument

            # Transform to MarvelQuant format
            marvelquant_quote = {
                'symbol': symbol,
                'exchange': exchange,
                'ltp': float(quote_data.get('LastTradedPrice', 0)),
                'open': float(quote_data.get('Open', 0)),
                'high': float(quote_data.get('High', 0)),
                'low': float(quote_data.get('Low', 0)),
                'close': float(quote_data.get('Close', 0)),
                'volume': int(quote_data.get('TotalTradedQuantity', 0)),
                'timestamp': quote_data.get('LastTradedTime', '')
            }

            return marvelquant_quote

        else:
            return {
                'status': 'error',
                'message': response_data.get('description', 'Failed to get quotes')
            }

    except Exception as e:
        logger.error(f"Error getting Jainam quotes: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def get_historical_data(symbol, exchange, from_date, to_date, interval, auth_token):
    """
    Get historical data from Jainam.

    Refactored to use MarketDataClient (Task 24.1).

    Args:
        symbol: Trading symbol
        exchange: Exchange
        from_date: Start date (YYYY-MM-DD)
        to_date: End date (YYYY-MM-DD)
        interval: Interval (1m, 5m, 1d, etc.)
        auth_token: Authentication token

    Returns:
        Historical data
    """
    try:
        # Parse auth_token
        market_token = _parse_market_auth_token(auth_token)

        # Get token for symbol
        token = get_token_from_symbol(symbol, exchange)
        exchange_segment = map_exchange_to_jainam(exchange)

        # Map interval to Jainam compression value
        interval_mapping = {
            '1m': 1,
            '5m': 5,
            '15m': 15,
            '1h': 60,
            '1d': 1440
        }
        compression_value = interval_mapping.get(interval, 1440)

        # Request parameters
        params = {
            'exchangeSegment': exchange_segment,
            'exchangeInstrumentID': token,
            'startTime': f"{from_date}T09:15:00+05:30",
            'endTime': f"{to_date}T15:30:00+05:30",
            'compressionValue': compression_value
        }

        # Use MarketDataClient
        client = MarketDataClient(auth_token=market_token)
        response_data = client.get_ohlc(params)

        if response_data.get('type') == 'success':
            # Transform OHLC data to MarvelQuant format
            candles = []
            for candle in response_data.get('result', []):
                candles.append({
                    'timestamp': candle.get('timestamp'),
                    'open': float(candle.get('open', 0)),
                    'high': float(candle.get('high', 0)),
                    'low': float(candle.get('low', 0)),
                    'close': float(candle.get('close', 0)),
                    'volume': int(candle.get('volume', 0))
                })

            return {
                'status': 'success',
                'symbol': symbol,
                'exchange': exchange,
                'interval': interval,
                'data': candles
            }
        else:
            return {
                'status': 'error',
                'message': response_data.get('description', 'Failed to get historical data')
            }

    except Exception as e:
        logger.error(f"Error getting Jainam historical data: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def search_instruments(search_string, auth_token):
    """
    Search for instruments by symbol name.

    Refactored to use MarketDataClient (Task 24.1).

    Args:
        search_string: Search query
        auth_token: Authentication token

    Returns:
        List of matching instruments
    """
    try:
        # Parse auth_token
        market_token = _parse_market_auth_token(auth_token)

        # Request parameters
        params = {
            'searchString': search_string
        }

        # Use MarketDataClient
        client = MarketDataClient(auth_token=market_token)
        response_data = client.search_instruments(params)

        if response_data.get('type') == 'success':
            instruments = []
            for instrument in response_data.get('result', []):
                instruments.append({
                    'symbol': instrument.get('DisplayName', ''),
                    'token': instrument.get('ExchangeInstrumentID', 0),
                    'exchange': instrument.get('ExchangeSegment', ''),
                    'instrument_type': instrument.get('Series', ''),
                    'name': instrument.get('Name', '')
                })

            return {
                'status': 'success',
                'instruments': instruments
            }
        else:
            return {
                'status': 'error',
                'message': response_data.get('description', 'Search failed')
            }

    except Exception as e:
        logger.error(f"Error searching Jainam instruments: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }
