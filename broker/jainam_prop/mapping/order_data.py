"""
Order data transformation module for Jainam
Handles order-specific data conversions between OpenAlgo and Jainam formats
"""
import json
from typing import Any, Dict, Optional, Tuple

from utils.logging import get_logger
from broker.jainam_prop.api.data import get_quotes

logger = get_logger(__name__)


def _parse_auth_token(auth_token: Optional[Any]) -> Dict[str, Any]:
    """
    Normalize an auth token payload into a dictionary so we can extract
    market-data credentials when available.
    """
    if not auth_token:
        return {}

    if isinstance(auth_token, dict):
        return auth_token

    if isinstance(auth_token, str):
        try:
            return json.loads(auth_token)
        except json.JSONDecodeError:
            # Treat raw string as both interactive and market token
            return {'token': auth_token, 'market_token': auth_token}

    # Unknown type – best effort cast via str
    return {'token': str(auth_token)}


def _extract_market_token(credentials: Dict[str, Any]) -> Optional[str]:
    """
    Extract the market data token from the credential payload. Different XTS
    brokers surface this with slightly different key names, so handle a small
    matrix of options.
    """
    candidate_keys = (
        'market_token',
        'marketToken',
        'market_auth_token',
        'marketAuthToken',
        'marketAuthorizationToken',
        'market_authorization_token',
    )

    for key in candidate_keys:
        token = credentials.get(key)
        if token:
            return token

    # Fall back to main interactive token if nothing else is available.
    return credentials.get('token')

def transform_order_request(order_data):
    """
    Transform OpenAlgo order request to Jainam format

    Args:
        order_data: OpenAlgo order data

    Returns:
        Jainam order data
    """
    # This is similar to transform_data.py but focused on orders
    # For now, delegate to the main transform_data module
    from broker.jainam_prop.mapping.transform_data import transform_data
    return transform_data(order_data)

def transform_order_response(jainam_response):
    """
    Transform Jainam order response to OpenAlgo format

    Args:
        jainam_response: Jainam API response

    Returns:
        OpenAlgo order response
    """
    from broker.jainam_prop.mapping.transform_data import transform_response
    return transform_response(jainam_response)

def transform_order_status(jainam_order_status):
    """
    Transform Jainam order status to OpenAlgo format

    Args:
        jainam_order_status: Order status from Jainam

    Returns:
        Order status in OpenAlgo format
    """
    # Status mapping
    status_mapping = {
        'NEW': 'open',
        'OPEN': 'open',
        'FILLED': 'complete',
        'CANCELLED': 'cancelled',
        'REJECTED': 'rejected',
        'PARTIALLYFILLED': 'partial'
    }

    # Product type mapping
    product_mapping = {
        'MIS': 'MIS',
        'NRML': 'NRML',
        'CNC': 'CNC'
    }

    # Order type mapping
    order_type_mapping = {
        'MARKET': 'MARKET',
        'LIMIT': 'LIMIT',
        'STOPMARKET': 'SL',
        'STOPLIMIT': 'SL-M'
    }

    try:
        openalgo_status = {
            'orderid': str(jainam_order_status.get('AppOrderID', '')),
            'status': status_mapping.get(jainam_order_status.get('OrderStatus', ''), 'unknown'),
            'symbol': jainam_order_status.get('TradingSymbol', ''),
            'exchange': jainam_order_status.get('ExchangeSegment', ''),
            'action': jainam_order_status.get('OrderSide', ''),
            'quantity': int(jainam_order_status.get('OrderQuantity', 0)),
            'price': float(jainam_order_status.get('OrderPrice', 0)),
            'pricetype': order_type_mapping.get(jainam_order_status.get('OrderType', ''), 'MARKET'),
            'product': product_mapping.get(jainam_order_status.get('ProductType', ''), 'MIS'),
            'filled_quantity': int(jainam_order_status.get('Cumulativetradedquantity', 0)),
            'pending_quantity': int(jainam_order_status.get('pendingQuantity', 0)),
            'average_price': float(jainam_order_status.get('AverageTradedPrice', 0)),
            'order_timestamp': jainam_order_status.get('OrderTime', ''),
            'exchange_order_id': str(jainam_order_status.get('ExchangeOrderID', ''))
        }

        return openalgo_status

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error transforming order status: {str(e)}'
        }

def transform_trade_book(jainam_trades):
    """
    Transform Jainam trade book to OpenAlgo format

    Args:
        jainam_trades: Trade data from Jainam

    Returns:
        Trade data in OpenAlgo format
    """
    try:
        openalgo_trades = []

        for trade in jainam_trades:
            openalgo_trade = {
                'orderid': str(trade.get('AppOrderID', '')),
                'trade_id': str(trade.get('TradeID', '')),
                'symbol': trade.get('TradingSymbol', ''),
                'exchange': trade.get('ExchangeSegment', ''),
                'product': trade.get('ProductType', ''),
                'action': trade.get('OrderSide', ''),
                'quantity': int(trade.get('TradedQuantity', 0)),
                'price': float(trade.get('TradedPrice', 0)),
                'timestamp': trade.get('TradeTime', ''),
                'exchange_trade_id': str(trade.get('ExchangeTradeID', ''))
            }
            openalgo_trades.append(openalgo_trade)

        return {
            'status': 'success',
            'trades': openalgo_trades
        }

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error transforming trade book: {str(e)}'
        }

def validate_order_data(order_data):
    """
    Validate order data before sending to Jainam

    Args:
        order_data: Order data to validate

    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['symbol', 'exchange', 'action', 'quantity', 'pricetype']

    # Check required fields
    for field in required_fields:
        if field not in order_data or not order_data[field]:
            return False, f"Missing required field: {field}"

    # Validate action
    valid_actions = ['BUY', 'SELL']
    if order_data['action'].upper() not in valid_actions:
        return False, f"Invalid action: {order_data['action']}. Must be one of {valid_actions}"

    # Validate exchange
    valid_exchanges = ['NSE', 'BSE', 'NFO', 'MCX']
    if order_data['exchange'].upper() not in valid_exchanges:
        return False, f"Invalid exchange: {order_data['exchange']}. Must be one of {valid_exchanges}"

    # Validate price type
    valid_pricetypes = ['MARKET', 'LIMIT', 'SL', 'SL-M']
    if order_data['pricetype'].upper() not in valid_pricetypes:
        return False, f"Invalid pricetype: {order_data['pricetype']}. Must be one of {valid_pricetypes}"

    # Validate quantity
    try:
        quantity = int(order_data['quantity'])
        if quantity <= 0:
            return False, "Quantity must be positive"
    except (ValueError, TypeError):
        return False, "Invalid quantity format"

    # Validate price for limit orders
    if order_data['pricetype'].upper() in ['LIMIT', 'SL-M']:
        try:
            price = float(order_data.get('price', 0))
            if price <= 0:
                return False, "Price must be positive for limit orders"
        except (ValueError, TypeError):
            return False, "Invalid price format"

    # Validate trigger price for stop orders
    if order_data['pricetype'].upper() in ['SL', 'SL-M']:
        try:
            trigger_price = float(order_data.get('trigger_price', 0))
            if trigger_price <= 0:
                return False, "Trigger price must be positive for stop orders"
        except (ValueError, TypeError):
            return False, "Invalid trigger price format"

    return True, None

def get_order_history_transform(jainam_history):
    """
    Transform Jainam order history to OpenAlgo format

    Args:
        jainam_history: Order history from Jainam

    Returns:
        Order history in OpenAlgo format
    """
    try:
        # Similar to order status transformation but for historical data
        return transform_order_status(jainam_history)

    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error transforming order history: {str(e)}'
        }

def map_trade_data(trade_data):
    """
    Map Jainam trade data by converting instrument tokens to symbols

    Args:
        trade_data: Trade data from Jainam API

    Returns:
        Mapped trade data with symbols resolved
    """
    from database.token_db import get_symbol
    from utils.logging import get_logger

    logger = get_logger(__name__)

    # Check if we have the 'trades' key from transform_trade_book
    if isinstance(trade_data, dict) and 'trades' in trade_data:
        trades_list = trade_data['trades']
    else:
        # Raw data from API
        if not trade_data or not isinstance(trade_data, (list, dict)):
            logger.info("No trade data available")
            return []

        if isinstance(trade_data, dict):
            if 'data' in trade_data:
                trades_list = trade_data['data']
            elif 'result' in trade_data:
                trades_list = trade_data['result']
            else:
                trades_list = []
        else:
            trades_list = trade_data

    if not trades_list:
        return []

    # Map symbol tokens to symbols
    for trade in trades_list:
        # Get instrument token and exchange
        if 'ExchangeInstrumentID' in trade:
            symboltoken = trade['ExchangeInstrumentID']
            exch = trade.get("ExchangeSegment", "")
            exchange = exchange_mapping.get(exch, exch)

            # Fetch symbol from database
            symbol_from_db = get_symbol(symboltoken, exchange)

            if symbol_from_db:
                trade['TradingSymbol'] = symbol_from_db

    logger.info(f"Mapped {len(trades_list)} trades")
    return trades_list

def transform_tradebook_data(tradebook_data):
    """
    Transform trade book data to OpenAlgo standard format

    Args:
        tradebook_data: Mapped trade data

    Returns:
        List of transformed trades in OpenAlgo format
    """
    transformed_data = []

    # Exchange mapping
    exchange_mapping = {
        "NSECM": "NSE",
        "BSECM": "BSE",
        "NSEFO": "NFO",
        "BSEFO": "BFO",
        "MCXFO": "MCX",
        "NSECD": "CDS"
    }

    if not tradebook_data:
        return []

    for trade in tradebook_data:
        # Map exchange
        exchange = trade.get("ExchangeSegment", trade.get("exchange", ""))
        mapped_exchange = exchange_mapping.get(exchange, exchange)

        # Extract and convert quantities and prices
        quantity = int(trade.get('TradedQuantity', trade.get('quantity', 0)))
        price = float(trade.get('TradedPrice', trade.get('price', 0.0)))

        transformed_trade = {
            "symbol": trade.get('TradingSymbol', trade.get('symbol', '')),
            "exchange": mapped_exchange,
            "product": trade.get('ProductType', trade.get('product', '')),
            "action": trade.get('OrderSide', trade.get('action', '')),
            "quantity": quantity,
            "average_price": price,
            "trade_value": quantity * price,
            "orderid": str(trade.get('AppOrderID', trade.get('orderid', ''))),
            "timestamp": trade.get('timestamp', trade.get('TradeTime', trade.get('trade_timestamp', ''))),
            "trade_id": str(trade.get('TradeID', trade.get('trade_id', '')))
        }

        transformed_data.append(transformed_trade)

    return transformed_data

def map_position_data(position_data):
    """
    Processes and modifies position data from Jainam API.

    Handles both legacy list payloads and the documented XTS structure:
    {'result': {'positionList': [...]}}.

    Parameters:
    - position_data: A dictionary containing the position information from Jainam API.

    Returns:
    - A dictionary containing the key 'positionList' with enriched position entries.
    """
    from database.token_db import get_symbol

    # Exchange mapping from Jainam format to OpenAlgo format
    exchange_mapping = {
        "NSECM": "NSE",
        "BSECM": "BSE",
        "NSEFO": "NFO",
        "BSEFO": "BFO",
        "MCXFO": "MCX",
        "NSECD": "CDS"
    }

    result_payload = position_data.get('result')

    # Gracefully handle missing/empty result
    if not result_payload:
        logger.info("No position data available.")
        return {'positionList': []}

    # Normalise payload into a dict with `positionList`
    if isinstance(result_payload, dict):
        positions_list = result_payload.get('positionList', [])
        # defensive copy so mutations do not leak to original payload
        normalised_result = dict(result_payload)
    elif isinstance(result_payload, list):
        positions_list = result_payload
        normalised_result = {}
    else:
        logger.warning(f"Unexpected result payload type: {type(result_payload)}")
        return {'positionList': []}

    if not isinstance(positions_list, list):
        logger.warning("positionList payload is not a list – resetting to empty list")
        positions_list = []

    # Process each position to enrich with TradingSymbol from database
    for position in positions_list:
        if not isinstance(position, dict):
            logger.debug(f"Skipping invalid position entry: {position}")
            continue

        # Extract the instrument token and exchange for the current position
        symboltoken = position.get('ExchangeInstrumentId')
        exch = position.get("ExchangeSegment", "")
        exchange = exchange_mapping.get(exch, exch)

        # Use the get_symbol function to fetch the symbol from the database
        symbol_from_db = get_symbol(symboltoken, exchange)

        # Check if a symbol was found; if so, update the TradingSymbol in the current position
        if symbol_from_db:
            position['TradingSymbol'] = symbol_from_db

    # Ensure we always return a dict containing positionList
    normalised_result['positionList'] = positions_list
    return normalised_result

def transform_positions_data(positions_data):
    """
    Transforms positions data into a standardized format for the frontend.

    Parameters:
    - positions_data: A dictionary with 'positionList' key containing a list of positions.

    Returns:
    - A list of transformed positions in a standardized format with required fields:
      symbol, exchange, product, quantity, average_price, ltp, pnl
    """
    logger.info(f"Transforming positions data")

    # Extract position list from the data structure
    positions_list = positions_data.get("positionList", [])

    transformed_data = []

    # Define exchange mappings
    exchange_mapping = {
        "NSECM": "NSE",
        "BSECM": "BSE",
        "NSEFO": "NFO",
        "BSEFO": "BFO",
        "MCXFO": "MCX",
        "NSECD": "CDS"
    }

    if not isinstance(positions_list, list):
        logger.error(f"Error: positions_data is not a list. Received: {type(positions_list)} - {positions_list}")
        return transformed_data

    for position in positions_list:
        if not isinstance(position, dict):  # Ensure it's a dictionary
            logger.info(f"Skipping invalid position: {position}")
            continue

        # Map exchange
        exchange = position.get("ExchangeSegment", "")
        mapped_exchange = exchange_mapping.get(exchange, exchange)

        # Calculate net quantity and average price
        netqty = float(position.get('Quantity', 0))
        if netqty > 0:
            net_amount = float(position.get('BuyAveragePrice', 0))
        elif netqty < 0:
            net_amount = float(position.get('SellAveragePrice', 0))
        else:
            net_amount = 0

        average_price = net_amount
        # Ensure average_price is treated as a float, then format to a string with 2 decimal places
        average_price_formatted = "{:.2f}".format(average_price)

        # Extract symbol, ltp, and pnl (AC6 requirement: symbol, exchange, product, quantity, price, P&L)
        transformed_position = {
            "symbol": position.get("TradingSymbol", ""),
            "exchange": mapped_exchange,
            "product": position.get('ProductType', ''),
            "quantity": position.get('Quantity', 0),
            "average_price": average_price_formatted,
            "ltp": float(position.get('LastTradedPrice', position.get('ltp', 0.0))),
            "pnl": float(position.get('RealizedProfitLoss', position.get('pnl', 0.0))),
        }

        transformed_data.append(transformed_position)

    return transformed_data

def _coerce_float(value):
    """Attempt to coerce a value to float, returning None when not possible."""
    if value is None:
        return None
    try:
        # Empty strings should not raise errors but should return None
        if isinstance(value, str) and not value.strip():
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def map_portfolio_data(portfolio_data, auth_token: Optional[Any] = None):
    """
    Processes and modifies portfolio data from Jainam API.

    Parameters:
    - portfolio_data: A dictionary containing the portfolio/holdings information from Jainam API.
    - auth_token: Optional authentication payload used when we need to fetch market quotes.

    Returns:
    - A dictionary with 'holdings' and 'totalholding' keys structured for the OpenAlgo system.
    """
    from database.token_db import get_symbol

    logger.info("Mapping portfolio data")

    # Exchange mapping from Jainam format to OpenAlgo format
    exchange_mapping = {
        "NSECM": "NSE",
        "BSECM": "BSE",
        "NSEFO": "NFO",
        "BSEFO": "BFO",
        "MCXFO": "MCX",
        "NSECD": "CDS"
    }

    # Check if response is valid and contains result data
    if not portfolio_data or portfolio_data.get('type') != 'success' or 'result' not in portfolio_data:
        logger.info("No portfolio data available.")
        return {'holdings': [], 'totalholding': None}

    # Extract the holdings data from the response
    result = portfolio_data['result']
    rms_holdings = result.get('RMSHoldings', {})
    holdings_data = rms_holdings.get('Holdings', {})

    # Normalise auth token to pull market quotes when holdings payload lacks MTM data
    auth_credentials = _parse_auth_token(auth_token)
    market_token = _extract_market_token(auth_credentials)
    quote_auth_payload: Optional[Dict[str, Any]] = None
    if market_token:
        quote_auth_payload = {'market_token': market_token}

    quote_cache: Dict[Tuple[str, str], Optional[Dict[str, Any]]] = {}

    # Create a list to store the transformed holdings
    holdings_list: list = []
    total_holding_value = 0.0
    total_inv_value = 0.0
    total_pnl = 0.0

    # Process each holding
    for isin, holding in holdings_data.items():
        # Extract NSE instrument ID for symbol lookup
        nse_instrument_id = holding.get('ExchangeNSEInstrumentId')
        exchange = 'NSE'  # Default to NSE for equity holdings

        # Get trading symbol from database using instrument ID and exchange
        trading_symbol = get_symbol(nse_instrument_id, exchange) or isin

        # Get quantity and buy price
        quantity = _coerce_float(holding.get('HoldingQuantity')) or 0.0
        buy_avg_price = _coerce_float(holding.get('BuyAvgPrice')) or 0.0

        inv_value = quantity * buy_avg_price

        # Determine current market price/value if available
        price_candidates = [
            holding.get('MarketRate'),
            holding.get('MarketPrice'),
            holding.get('MarketValuePerShare'),
            holding.get('MarkToMarketPrice'),
            holding.get('MTMPrice'),
            holding.get('CurrentMarketPrice'),
            holding.get('LastTradedPrice'),
            holding.get('LastTradePrice'),
            holding.get('ltp'),
            holding.get('LTP'),
        ]
        current_price = next(
            (val for val in (_coerce_float(candidate) for candidate in price_candidates) if val is not None and val > 0),
            None
        )

        value_candidates = [
            holding.get('CurrentValue'),
            holding.get('HoldingValue'),
            holding.get('MarketValue'),
            holding.get('HoldingCurrentValue'),
        ]
        current_value = next(
            (val for val in (_coerce_float(candidate) for candidate in value_candidates) if val is not None),
            None
        )

        if current_price is None and current_value is not None and quantity:
            current_price = current_value / quantity if quantity != 0 else None

        if current_price is None:
            current_price = buy_avg_price

        if current_value is None:
            current_value = current_price * quantity

        profitandloss = current_value - inv_value
        pnl_percentage = (profitandloss / inv_value * 100) if inv_value else 0.0

        needs_quote = (
            quote_auth_payload
            and trading_symbol
            and trading_symbol != isin
            and quantity
            and (
                current_price is None
                or current_price <= 0
                or abs(profitandloss) < 1e-9
            )
        )

        if needs_quote:
            cache_key = (trading_symbol, exchange)
            quote = quote_cache.get(cache_key)
            if quote is None:
                try:
                    quote = get_quotes(trading_symbol, exchange, quote_auth_payload)
                except Exception as exc:  # pragma: no cover - defensive logging
                    logger.warning(f"Failed to fetch quote for {trading_symbol}: {exc}")
                    quote = None
                quote_cache[cache_key] = quote

            if isinstance(quote, dict) and quote.get('status') != 'error':
                quote_ltp = quote.get('ltp')
                if isinstance(quote_ltp, (int, float)) and quote_ltp > 0:
                    current_price = float(quote_ltp)
                    current_value = current_price * quantity
                    profitandloss = current_value - inv_value
                    pnl_percentage = (profitandloss / inv_value * 100) if inv_value else 0.0

        holding_entry = {
            'tradingsymbol': trading_symbol,
            'exchange': exchange,
            'quantity': quantity,
            'product': 'CNC',
            'buy_price': buy_avg_price,
            'current_price': current_price,
            'investment_value': inv_value,
            'current_value': current_value,
            'profitandloss': profitandloss,
            'pnlpercentage': pnl_percentage
        }

        holdings_list.append(holding_entry)

        # Update totals
        total_inv_value += inv_value
        total_holding_value += current_value
        total_pnl += profitandloss

    # Create totalholding summary
    totalholding = {
        'totalholdingvalue': total_holding_value,
        'totalinvvalue': total_inv_value,
        'totalprofitandloss': total_pnl,
        'totalpnlpercentage': 0 if total_inv_value == 0 else (total_pnl / total_inv_value) * 100
    }

    # Return the structured data
    return {
        'holdings': holdings_list,
        'totalholding': totalholding
    }

def calculate_portfolio_statistics(holdings_data):
    """
    Calculates portfolio statistics from holdings data.

    Parameters:
    - holdings_data: A dictionary with 'holdings' and 'totalholding' keys.

    Returns:
    - A dictionary with portfolio statistics.
    """
    logger.info(f"Calculating portfolio statistics")

    # Check if totalholding exists and is not None
    if 'totalholding' not in holdings_data or holdings_data['totalholding'] is None:
        totalholdingvalue = 0
        totalinvvalue = 0
        totalprofitandloss = 0
        totalpnlpercentage = 0
    else:
        # Extract values from totalholding
        totalholdingvalue = holdings_data['totalholding'].get('totalholdingvalue', 0)
        totalinvvalue = holdings_data['totalholding'].get('totalinvvalue', 0)
        totalprofitandloss = holdings_data['totalholding'].get('totalprofitandloss', 0)
        totalpnlpercentage = holdings_data['totalholding'].get('totalpnlpercentage', 0)

    return {
        'totalholdingvalue': totalholdingvalue,
        'totalinvvalue': totalinvvalue,
        'totalprofitandloss': totalprofitandloss,
        'totalpnlpercentage': totalpnlpercentage
    }

def transform_holdings_data(holdings_data):
    """
    Transforms holdings data into a standardized format for the frontend.

    Parameters:
    - holdings_data: A dictionary with 'holdings' key containing a list of holdings.

    Returns:
    - A list of transformed holdings in a standardized format with required fields:
      symbol, exchange, quantity, product, price, pnl, pnlpercent
    """
    logger.info(f"Transforming holdings data")
    transformed_data = []

    # Check if holdings_data has the expected structure
    if not holdings_data or 'holdings' not in holdings_data:
        return transformed_data

    # Process each holding (AC6 requirement: symbol, exchange, product, quantity, price, P&L)
    for holdings in holdings_data['holdings']:
        transformed_position = {
            "symbol": holdings.get('tradingsymbol', ''),
            "exchange": holdings.get('exchange', ''),
            "quantity": holdings.get('quantity', 0),
            "product": holdings.get('product', ''),
            "price": holdings.get('current_price', holdings.get('buy_price', 0.0)),
            "pnl": holdings.get('profitandloss', 0.0),
            "pnlpercent": holdings.get('pnlpercentage', 0.0)
        }
        transformed_data.append(transformed_position)

    return transformed_data
