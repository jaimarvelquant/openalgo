import json
from broker.jainam_prop.mapping.transform_data import get_token_from_symbol, map_exchange_to_jainam
from broker.jainam_prop.api.config import get_jainam_base_url
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

logger = get_logger(__name__)

def get_quotes(symbol, exchange, auth_token):
    """
    Get quotes for a symbol from Jainam

    Args:
        symbol: Trading symbol (e.g., 'RELIANCE')
        exchange: Exchange (e.g., 'NSE')
        auth_token: Authentication token

    Returns:
        Quote data in OpenAlgo format
    """
    try:
        # Parse auth_token
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'market_token': auth_token}
        else:
            credentials = auth_token

        market_token = credentials.get('market_token', auth_token)
        root_url = get_jainam_base_url()

        # Get token for symbol
        token = get_token_from_symbol(symbol, exchange)
        exchange_segment = map_exchange_to_jainam(exchange)

        # API endpoint for quotes
        url = f"{root_url}/apimarketdata/instruments/quotes"

        # Request payload
        payload = {
            'instruments': [{
                'exchangeSegment': exchange_segment,
                'exchangeInstrumentID': token
            }],
            'xtsMessageCode': 1501,  # Touchline data
            'publishFormat': 'JSON'
        }

        # Headers
        headers = {
            'Content-Type': 'application/json',
            'Authorization': market_token
        }

        # Make request
        client = get_httpx_client()
        response = client.post(url, headers=headers, json=payload)
        response_data = response.json()

        if response_data.get('type') == 'success' and 'result' in response_data:
            quote_data = response_data['result'][0]  # First instrument

            # Transform to OpenAlgo format
            openalgo_quote = {
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

            return openalgo_quote

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
    Get historical data from Jainam

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
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'market_token': auth_token}
        else:
            credentials = auth_token

        market_token = credentials.get('market_token', auth_token)
        root_url = get_jainam_base_url()

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

        # API endpoint
        url = f"{root_url}/apimarketdata/instruments/ohlc"

        # Request parameters
        params = {
            'exchangeSegment': exchange_segment,
            'exchangeInstrumentID': token,
            'startTime': f"{from_date}T09:15:00+05:30",
            'endTime': f"{to_date}T15:30:00+05:30",
            'compressionValue': compression_value
        }

        # Headers
        headers = {
            'Authorization': market_token
        }

        # Make request
        client = get_httpx_client()
        response = client.get(url, headers=headers, params=params)
        response_data = response.json()

        if response_data.get('type') == 'success':
            # Transform OHLC data to OpenAlgo format
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
    Search for instruments by symbol name

    Args:
        search_string: Search query
        auth_token: Authentication token

    Returns:
        List of matching instruments
    """
    try:
        # Parse auth_token
        if isinstance(auth_token, str):
            try:
                credentials = json.loads(auth_token)
            except:
                credentials = {'market_token': auth_token}
        else:
            credentials = auth_token

        market_token = credentials.get('market_token', auth_token)
        root_url = get_jainam_base_url()

        # API endpoint
        url = f"{root_url}/apimarketdata/search/instruments"

        # Request parameters
        params = {
            'searchString': search_string
        }

        # Headers
        headers = {
            'Authorization': market_token
        }

        # Make request
        client = get_httpx_client()
        response = client.get(url, headers=headers, params=params)
        response_data = response.json()

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
