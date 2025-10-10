"""Jainam Prop data transformation helpers.

This module is responsible for translating between MarvelQuant's canonical
order structure and the Jainam XTS Connect API requirements. It now also
provides a database-backed symbol → token lookup that satisfies story 1.1-1
acceptance criteria by resolving tokens from the shared ``symbol_token``
table instead of returning placeholder values.

The token lookup implementation keeps a small in-memory cache to meet the
<100ms performance requirement for successive requests while remaining easy
to invalidate after master contract refreshes.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from broker.jainam_prop._ensure_database import ensure_database_package

ensure_database_package()
from database.symbol import engine
from utils.logging import get_logger

logger = get_logger(__name__)

# Broker identifier used in the symbol_token table
_BROKER_CODE = "jainam_prop"

# Cache size can be tuned via env var if needed; defaults chosen for 100k+ rows
_TOKEN_CACHE_CAPACITY = 10_000


def _normalise_symbol(symbol: str) -> str:
    """Return the canonical representation used for database lookups."""

    if symbol is None:
        return ""
    return symbol.strip().upper()


@lru_cache(maxsize=_TOKEN_CACHE_CAPACITY)
def _lookup_token_cached(symbol: str, exchange: str) -> int:
    """Fetch instrument token for *symbol*/*exchange* from the database."""

    query = text(
        """
        SELECT token
          FROM symbol_token
         WHERE broker = :broker
           AND symbol = :symbol
           AND exchange = :exchange
         LIMIT 1
        """
    )

    try:
        with engine.connect() as connection:
            result: Optional[str] = connection.execute(
                query,
                {
                    "broker": _BROKER_CODE,
                    "symbol": symbol,
                    "exchange": exchange,
                },
            ).scalar()
    except SQLAlchemyError as exc:  # pragma: no cover - requires DB failures
        logger.error(
            "Database error during Jainam token lookup for %s/%s: %s",
            symbol,
            exchange,
            exc,
        )
        raise RuntimeError("Database error while resolving instrument token") from exc

    if result is None:
        raise ValueError(
            f"Token not found for symbol '{symbol}' on exchange '{exchange}'"
        )

    try:
        return int(result)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Invalid token value '{result}' for symbol '{symbol}' on '{exchange}'"
        ) from exc


def clear_token_lookup_cache() -> None:
    """Expose cache clearing so master contract refreshes can invalidate it."""

    _lookup_token_cached.cache_clear()


def _resolve_token(symbol: str, exchange: str) -> int:
    """Resolve the token, retrying with a fallback normalisation if required."""

    try:
        return _lookup_token_cached(symbol, exchange)
    except ValueError as primary_error:
        fallback_symbol = symbol.replace("-EQ", "").replace("-BE", "").replace("-", "")
        if fallback_symbol != symbol:
            try:
                token = _lookup_token_cached(fallback_symbol, exchange)
                logger.debug(
                    "Resolved token for %s/%s via fallback symbol %s",
                    symbol,
                    exchange,
                    fallback_symbol,
                )
                return token
            except ValueError:
                logger.debug(
                    "Fallback symbol %s also missing for %s/%s",
                    fallback_symbol,
                    symbol,
                    exchange,
                )
        raise primary_error

def transform_data(data):
    """
    Transform MarvelQuant request to Jainam format

    MarvelQuant Input:
    {
        "symbol": "RELIANCE-EQ",
        "exchange": "NSE",
        "action": "BUY",
        "quantity": 10,
        "pricetype": "LIMIT",
        "product": "MIS",
        "price": 2500.50,
        "trigger_price": 2490.00
    }

    Jainam Output:
    {
        "exchangeSegment": "NSECM",
        "exchangeInstrumentID": 738561,
        "productType": "MIS",
        "orderType": "LIMIT",
        "orderSide": "BUY",
        "timeInForce": "DAY",
        "disclosedQuantity": 0,
        "orderQuantity": 10,
        "limitPrice": 2500.50,
        "stopPrice": 2490.00,
        "orderUniqueIdentifier": "WEB_EXE_PLATFORM",
        "clientID": "user_id"
    }
    """

    # Extract and normalise inputs
    input_symbol = data.get('symbol', '')
    exchange = data.get('exchange', 'NSE')
    normalised_symbol = _normalise_symbol(input_symbol)
    normalised_exchange = exchange.strip().upper()

    # Map action to Jainam format
    action_mapping = {
        'BUY': 'BUY',
        'SELL': 'SELL'
    }

    # Map price type to Jainam order types
    pricetype_mapping = {
        'MARKET': 'MARKET',
        'LIMIT': 'LIMIT',
        'SL': 'STOPMARKET',
        'SL-M': 'STOPLIMIT'
    }

    # Map product type to Jainam product types
    product_mapping = {
        'CNC': 'CNC',
        'MIS': 'MIS',
        'NRML': 'NRML'
    }

    # Map exchange to Jainam segment using canonical mapping table. Surface
    # unsupported exchanges to the caller instead of silently defaulting to
    # NSE so that order routing cannot mis-target segments QA flagged.
    try:
        exchange_segment = map_exchange_to_jainam(normalised_exchange)
    except ValueError as exc:
        logger.error(
            "Unsupported exchange '%s' for Jainam order transform",
            normalised_exchange,
        )
        raise ValueError(
            f"Unsupported exchange '{normalised_exchange}' for Jainam"
        ) from exc

    # Resolve instrument token via database-backed lookup
    token = get_token_from_symbol(normalised_symbol, normalised_exchange)

    # Build Jainam order structure
    jainam_order = {
        "exchangeSegment": exchange_segment,
        "exchangeInstrumentID": token,
        "productType": product_mapping.get(data.get('product', 'MIS'), 'MIS'),
        "orderType": pricetype_mapping.get(data.get('pricetype', 'MARKET'), 'MARKET'),
        "orderSide": action_mapping.get(data.get('action', 'BUY'), 'BUY'),
        "timeInForce": "DAY",  # Jainam uses DAY as default
        "disclosedQuantity": 0,
        "orderQuantity": int(data.get('quantity', 1)),
        "limitPrice": float(data.get('price', 0)),
        "stopPrice": float(data.get('trigger_price', 0)),
        "orderUniqueIdentifier": "OPENALGO_PLATFORM"
    }

    # Handle special cases for stop orders
    if data.get('pricetype') == 'SL':
        jainam_order['stopPrice'] = float(data.get('trigger_price', 0))
        jainam_order['limitPrice'] = 0
    elif data.get('pricetype') == 'SL-M':
        jainam_order['stopPrice'] = float(data.get('trigger_price', 0))
        jainam_order['limitPrice'] = float(data.get('price', 0))

    return jainam_order

def transform_response(jainam_response):
    """
    Transform Jainam response to MarvelQuant format

    Jainam Response:
    {
        "type": "success",
        "result": {
            "AppOrderID": "12345678",
            "OrderUniqueIdentifier": "OPENALGO_PLATFORM"
        }
    }

    MarvelQuant Response:
    {
        "status": "success",
        "orderid": "12345678",
        "message": "Order placed successfully"
    }
    """
    if jainam_response.get('type') == 'success':
        return {
            'status': 'success',
            'orderid': str(jainam_response.get('result', {}).get('AppOrderID', '')),
            'message': 'Order placed successfully'
        }
    else:
        return {
            'status': 'error',
            'message': jainam_response.get('description', 'Unknown error')
        }

def get_token_from_symbol(symbol: str, exchange: str) -> int:
    """Retrieve Jainam instrument token for the supplied symbol/exchange.

    Args:
        symbol: MarvelQuant symbol (case insensitive). Examples: ``RELIANCE-EQ``,
            ``NIFTY24OCTFUT``.
        exchange: MarvelQuant exchange code (``NSE``, ``BSE``, ``NFO``...).

    Returns:
        Integer instrument token as stored in ``symbol_token``.

    Raises:
        ValueError: If the symbol cannot be found in the master contract, or if
            the stored token value is invalid.
        RuntimeError: If the underlying database query fails.
    """

    if not symbol or not exchange:
        raise ValueError("Symbol and exchange are required for token lookup")

    normalised_symbol = _normalise_symbol(symbol)
    normalised_exchange = exchange.strip().upper()

    token = _resolve_token(normalised_symbol, normalised_exchange)
    logger.debug(
        "Resolved Jainam token %s for %s/%s",
        token,
        normalised_symbol,
        normalised_exchange,
    )
    return token

_OPENALGO_TO_JAINAM_EXCHANGE = {
    "NSE": "NSECM",
    "NFO": "NSEFO",
    "CDS": "NSECD",
    "BSE": "BSECM",
    "BFO": "BSEFO",
    "MCX": "MCXFO",
}

_JAINAM_TO_OPENALGO_EXCHANGE = {
    "NSECM": "NSE",
    "NSEFO": "NFO",
    "NSECD": "CDS",
    "BSECM": "BSE",
    "BSEFO": "BFO",
    "MCXFO": "MCX",
}


def map_exchange_to_jainam(exchange: str) -> str:
    """Map MarvelQuant exchange code to Jainam exchange segment.

    Raises ``ValueError`` if the exchange is not supported by the Jainam XTS
    integration so that calling code can surface configuration issues early.
    """

    if not exchange:
        raise ValueError("Exchange is required for Jainam segment mapping")

    normalised = exchange.strip().upper()
    if normalised in _OPENALGO_TO_JAINAM_EXCHANGE:
        return _OPENALGO_TO_JAINAM_EXCHANGE[normalised]

    if normalised in _JAINAM_TO_OPENALGO_EXCHANGE:
        # Already a Jainam segment – return as-is so callers can round-trip.
        return normalised

    raise ValueError(f"Unsupported exchange '{exchange}' for Jainam")


def map_jainam_to_exchange(exchange_segment: str) -> str:
    """Map Jainam exchange segment back to MarvelQuant exchange code."""

    if not exchange_segment:
        return ""

    normalised = exchange_segment.strip().upper()
    return _JAINAM_TO_OPENALGO_EXCHANGE.get(normalised, normalised)
