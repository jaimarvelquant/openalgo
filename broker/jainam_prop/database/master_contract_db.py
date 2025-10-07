"""
Master contract database module for Jainam
Handles downloading and managing symbol database
"""

import os
import time
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from database.symbol import engine
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

from broker.jainam_prop.mapping.transform_data import (
    clear_token_lookup_cache,
    map_jainam_to_exchange,
)

logger = get_logger(__name__)

_BROKER_CODE = "jainam_prop"
_INSERT_BATCH_SIZE = 5_000

def get_master_contract():
    """
    Download or update master contract from Jainam

    Returns:
        dict: Status and message
    """
    try:
        # Check if we need to authenticate first
        from broker.jainam_prop.api.auth_api import authenticate_market_data

        market_token, error = authenticate_market_data()
        if error:
            return {
                'status': 'error',
                'message': f'Authentication failed: {error}'
            }

        root_url = "http://ctrade.jainam.in:3000"

        # Define exchanges to download
        exchanges = [
            "NSECM",  # NSE Cash Market
            "NSEFO",  # NSE Futures & Options
            "NSECD",  # NSE Currency Derivatives
            "BSECM",  # BSE Cash Market
            "BSEFO",  # BSE Futures & Options
            "MCXFO"   # MCX Futures & Options
        ]

        # Headers for API request
        headers = {
            'Content-Type': 'application/json',
            'Authorization': market_token
        }

        # Download data for each exchange
        all_instruments = []

        for exchange in exchanges:
            try:
                logger.info(f"Downloading master contract for {exchange}")

                # API endpoint
                url = f"{root_url}/apimarketdata/instruments/master"

                # Request payload
                payload = {
                    "exchangeSegmentList": [exchange]
                }

                # Make request
                client = get_httpx_client()
                response = client.post(url, headers=headers, json=payload)
                response_data = response.json()

                if response_data.get('type') == 'success' and 'result' in response_data:
                    # Parse the result (it's usually a pipe-separated string)
                    raw_data = response_data['result']

                    # Split by newlines and then by pipes
                    rows = [row.split('|') for row in raw_data.split('\n') if row.strip()]

                    # Convert to DataFrame for processing
                    columns = [
                        'exchange', 'sec_id', 'InstrumentType', 'symbol', 'sec_description',
                        'instrument_type', 'NameWithSeries', 'InstrumentID', 'PriceBand.High',
                        'PriceBand.Low', 'FreezeQty', 'TickSize', 'lot_size', 'Multiplier',
                        'UnderlyingInstrumentId', 'UnderlyingIndexName', 'expiry_date',
                        'strike_price', 'option_type', 'displayName', 'PriceNumerator',
                        'PriceDenominator', 'Extra'
                    ]

                    df = pd.DataFrame(rows, columns=columns)

                    # Add exchange column
                    df['exchange'] = exchange

                    # Process option types
                    df = _process_option_types(df)

                    # Process expiry dates
                    df = _process_expiry_dates(df)

                    # Convert data types
                    df = _convert_data_types(df)

                    # Add to all instruments
                    all_instruments.append(df)

                    logger.info(f"Downloaded {len(df)} instruments for {exchange}")

                else:
                    logger.error(f"Failed to download {exchange}: {response_data.get('description', 'Unknown error')}")

            except Exception as e:
                logger.error(f"Error downloading {exchange}: {e}")
                continue

        # Combine all exchanges
        if all_instruments:
            master_df = pd.concat(all_instruments, ignore_index=True)

            # Save to database (this should be implemented)
            save_master_contract_to_db(master_df)

            logger.info(f"Master contract updated with {len(master_df)} instruments")
            return {
                'status': 'success',
                'message': f'Master contract updated with {len(master_df)} instruments',
                'total_instruments': len(master_df)
            }
        else:
            return {
                'status': 'error',
                'message': 'No instruments downloaded from any exchange'
            }

    except Exception as e:
        logger.error(f"Error in get_master_contract: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def _process_option_types(df):
    """
    Process and standardize option types

    Args:
        df: DataFrame with instrument data

    Returns:
        DataFrame with processed option types
    """
    def transform_option_type(row):
        instrument_type = row.get('InstrumentType', '')
        display_name = row.get('displayName', '')

        if instrument_type == 'FUTSTK':
            return 'FUT'
        elif instrument_type == 'OPTSTK':
            # Extract option type from display name (usually last part)
            parts = display_name.split()
            if len(parts) >= 3:
                option_part = parts[-1]  # Usually 'CE' or 'PE'
                if option_part in ['CE', 'PE']:
                    return option_part
        elif instrument_type == 'OPTIDX':
            # Similar logic for index options
            parts = display_name.split()
            if len(parts) >= 3:
                option_part = parts[-1]
                if option_part in ['CE', 'PE']:
                    return option_part

        return instrument_type  # Default return

    df['option_type'] = df.apply(transform_option_type, axis=1)
    return df

def _process_expiry_dates(df):
    """
    Process and standardize expiry dates

    Args:
        df: DataFrame with instrument data

    Returns:
        DataFrame with processed expiry dates
    """
    # Convert expiry_date column to datetime
    df['expiry_date'] = pd.to_datetime(df['expiry_date'], errors='coerce').dt.date

    # Handle invalid dates
    df['expiry_date'] = df['expiry_date'].fillna(pd.Timestamp('1900-01-01').date())

    return df

def _convert_data_types(df):
    """
    Convert columns to appropriate data types

    Args:
        df: DataFrame with instrument data

    Returns:
        DataFrame with converted data types
    """
    # Numeric columns
    numeric_columns = [
        'sec_id', 'PriceBand.High', 'PriceBand.Low', 'FreezeQty',
        'TickSize', 'lot_size', 'Multiplier', 'strike_price',
        'PriceNumerator', 'PriceDenominator'
    ]

    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Integer columns
    int_columns = ['sec_id', 'FreezeQty', 'lot_size', 'Multiplier']
    for col in int_columns:
        if col in df.columns:
            df[col] = df[col].astype(int)

    # Float columns
    float_columns = ['PriceBand.High', 'PriceBand.Low', 'TickSize', 'strike_price']
    for col in float_columns:
        if col in df.columns:
            df[col] = df[col].astype(float)

    return df

def _coerce_int(value: Optional[object], default: int = 0) -> int:
    """Best-effort conversion of *value* to integer."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return default
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return default


def _coerce_float(value: Optional[object]) -> Optional[float]:
    """Convert value to float when possible, otherwise return ``None``."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_expiry(value: Optional[object]) -> Optional[str]:
    """Normalise expiry date representations to ISO-8601 strings."""

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None

    if isinstance(value, pd.Timestamp):
        return value.date().isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()

    text_value = str(value).strip()
    if not text_value:
        return None

    try:
        parsed = pd.to_datetime(text_value, errors="raise")
    except (ValueError, TypeError):
        return text_value.upper()
    return parsed.date().isoformat()


def _normalise_exchange_segment(segment: Optional[str]) -> str:
    if not segment:
        return ""
    return str(segment).strip().upper()


def _prepare_symbol_token_records(df: pd.DataFrame) -> List[Dict[str, object]]:
    """Transform raw master contract dataframe into DB-ready mappings."""

    if df.empty:
        return []

    column_map = {col.lower(): col for col in df.columns}

    def get(row: pd.Series, *candidates: str) -> Optional[object]:
        for candidate in candidates:
            column = column_map.get(candidate.lower())
            if column is None:
                continue
            value = row[column]
            if isinstance(value, str):
                value = value.strip()
            if value is not None and value != "":
                return value
        return None

    prepared: Dict[tuple, Dict[str, object]] = {}

    for _, row in df.iterrows():
        token_value = get(
            row,
            "ExchangeInstrumentID",
            "InstrumentID",
            "sec_id",
            "token",
        )
        if token_value is None:
            continue

        symbol_value = get(
            row,
            "NameWithSeries",
            "symbol",
            "DisplayName",
            "Name",
            "Description",
        )
        if symbol_value is None:
            continue

        brsymbol_value = get(
            row,
            "DisplayName",
            "Description",
            "NameWithSeries",
            "symbol",
        ) or symbol_value

        segment_value = _normalise_exchange_segment(
            get(row, "ExchangeSegment", "exchange")
        )
        exchange_value = _map_segment_to_openalgo_exchange(segment_value)

        lotsize_value = _coerce_int(get(row, "LotSize", "lot_size"), default=1)
        instrument_value = get(
            row,
            "InstrumentType",
            "instrument_type",
            "Series",
        )
        tick_size_value = _coerce_float(get(row, "TickSize", "tick_size"))
        expiry_value = _format_expiry(get(row, "ContractExpiration", "expiry_date"))
        strike_value = _coerce_float(get(row, "StrikePrice", "strike_price"))
        name_value = get(row, "Name", "Description")

        key = (
            str(symbol_value).strip().upper(),
            exchange_value,
            _coerce_int(token_value),
        )

        prepared[key] = {
            "broker": _BROKER_CODE,
            "symbol": key[0],
            "brsymbol": str(brsymbol_value).strip(),
            "token": key[2],
            "exchange": exchange_value,
            "brexchange": segment_value,
            "lotsize": lotsize_value,
            "instrumenttype": str(instrument_value).strip().upper()
            if instrument_value
            else None,
            "expiry": expiry_value,
            "strike": strike_value,
            "name": str(name_value).strip() if name_value else None,
            "tick_size": tick_size_value,
        }

    return list(prepared.values())


def _map_segment_to_openalgo_exchange(segment: str) -> str:
    """Wrapper that reuses existing mapping but ensures uppercase input."""

    if not segment:
        return ""

    normalised_segment = segment.upper()
    mapped_exchange = map_jainam_to_exchange(normalised_segment)

    if not mapped_exchange:
        logger.warning(
            "Unknown Jainam exchange segment '%s'; defaulting to original value",
            normalised_segment,
        )
        return normalised_segment

    return mapped_exchange


def save_master_contract_to_db(df: pd.DataFrame) -> None:
    """Persist Jainam master contract data into the shared database table."""

    if df is None or df.empty:
        logger.warning("Received empty DataFrame while saving master contract")
        return

    records = _prepare_symbol_token_records(df)
    if not records:
        logger.error("No valid Jainam records prepared for persistence")
        raise ValueError("No valid instruments to persist")

    delete_query = text(
        "DELETE FROM symbol_token WHERE broker = :broker"
    )
    insert_query = text(
        """
        INSERT INTO symbol_token (
            broker, symbol, brsymbol, token, exchange, brexchange,
            lotsize, instrumenttype, expiry, strike, name, tick_size
        )
        VALUES (
            :broker, :symbol, :brsymbol, :token, :exchange, :brexchange,
            :lotsize, :instrumenttype, :expiry, :strike, :name, :tick_size
        )
        """
    )
    index_queries = [
        text(
            "CREATE INDEX IF NOT EXISTS idx_symbol_token_broker_symbol_exchange "
            "ON symbol_token (broker, symbol, exchange)"
        ),
        text(
            "CREATE INDEX IF NOT EXISTS idx_symbol_token_broker_token "
            "ON symbol_token (broker, token)"
        ),
    ]

    start = time.perf_counter()

    try:
        with engine.begin() as connection:
            connection.execute(delete_query, {"broker": _BROKER_CODE})

            for chunk_start in range(0, len(records), _INSERT_BATCH_SIZE):
                chunk = records[chunk_start : chunk_start + _INSERT_BATCH_SIZE]
                connection.execute(insert_query, chunk)

            for index_query in index_queries:
                connection.execute(index_query)

    except SQLAlchemyError as exc:  # pragma: no cover - requires DB failures
        logger.error("Failed to persist Jainam master contract: %s", exc)
        raise RuntimeError("Error persisting Jainam master contract") from exc

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        "Persisted %s Jainam instruments in %.2f ms",
        len(records),
        duration_ms,
    )

    clear_token_lookup_cache()
    logger.debug("Cleared Jainam token lookup cache after refresh")

def search_instruments(query, exchange=None, limit=50):
    """
    Search instruments in the master contract

    Args:
        query: Search query (symbol name)
        exchange: Filter by exchange (optional)
        limit: Maximum results to return

    Returns:
        List of matching instruments
    """
    try:
        # This should query the actual database
        # For now, return a placeholder response
        logger.info(f"Searching for instruments matching '{query}' in exchange '{exchange}'")

        # Placeholder response
        return {
            'status': 'success',
            'instruments': [],
            'message': 'Search functionality not yet implemented'
        }

    except Exception as e:
        logger.error(f"Error searching instruments: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }

def get_instrument_by_token(token, exchange):
    """
    Get instrument details by token and exchange

    Args:
        token: Instrument token
        exchange: Exchange

    Returns:
        Instrument details or None
    """
    try:
        # This should query the actual database
        logger.info(f"Looking up instrument token {token} in {exchange}")

        # Placeholder response
        return {
            'status': 'error',
            'message': 'Token lookup not yet implemented'
        }

    except Exception as e:
        logger.error(f"Error getting instrument by token: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }
