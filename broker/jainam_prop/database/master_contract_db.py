"""
Master contract database module for Jainam
Handles downloading and managing symbol database
"""

import os
import time
import json
from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from broker.jainam_prop._ensure_database import ensure_database_package
from extensions import socketio

ensure_database_package()
from database.symbol import engine
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client
from broker.jainam_prop.api.config import get_jainam_base_url
# NOTE: get_route imported lazily inside functions to avoid circular import
# (Task 24.1 - circular import fix)

from broker.jainam_prop.mapping.transform_data import (
    clear_token_lookup_cache,
    map_jainam_to_exchange,
)

logger = get_logger(__name__)

_BROKER_CODE = "jainam_prop"
_INSERT_BATCH_SIZE = 5_000


def master_contract_download():
    """
    Entry point invoked by the master-contract download service.

    Emits socket events that mirror other broker implementations so the UI
    receives progress updates, and raises an exception when the download fails.
    """
    logger.info("Starting Jainam master contract download")
    try:
        result = get_master_contract()
    except Exception as exc:
        message = f"{exc}"
        socketio.emit('master_contract_download', {
            'status': 'error',
            'message': message,
            'broker': _BROKER_CODE,
        })
        raise

    if not isinstance(result, dict):
        message = "Unknown response from Jainam master contract workflow"
        socketio.emit('master_contract_download', {
            'status': 'error',
            'message': message,
            'broker': _BROKER_CODE,
        })
        raise RuntimeError(message)

    status = result.get('status')
    message = result.get('message') or ''
    payload = {
        'status': status or 'error',
        'message': message or ('Master contract updated with '
                               f"{result.get('total_instruments', 'unknown')} instruments"),
        'broker': _BROKER_CODE,
    }
    socketio.emit('master_contract_download', payload)

    if status != 'success':
        raise RuntimeError(payload['message'])

    return result

def get_master_contract():
    """
    Download or update master contract from Jainam XTS API

    Implementation based on working reference code in:
    broker/jainam_prop/_sample_strategy/xts_connect.py
    - Lines 947-953: get_master() function
    - Lines 119-167: get_master_contract() usage
    - Lines 1070-1089: _request() method showing authentication

    Key implementation details:
    1. Endpoint: POST {root_url}/apimarketdata/instruments/master
    2. Payload: Must use json.dumps() to pre-serialize {"exchangeSegmentList": [...]}
    3. Request: Pass as 'content' parameter (not 'json' parameter) to httpx.post()
    4. Response: Contains pipe-delimited CSV data in 'result' field
    5. Authentication: Market data token in Authorization header

    Returns:
        dict: Status and message

    Example:
        {
            'status': 'success',
            'message': 'Downloaded 50000 instruments from 6 exchanges',
            'total_instruments': 50000
        }
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

        root_url = get_jainam_base_url()

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
                # IMPORTANT: Use centralized route dictionary (Task 24.1)
                # Production uses Binary Market Data API (/apibinarymarketdata/)
                # Route defined in broker/jainam_prop/api/routes.py
                #
                # Lazy import to avoid circular dependency
                from broker.jainam_prop.api.routes import get_route

                # Try both endpoints (binary first, then standard as fallback)
                binary_endpoint = f"{root_url}{get_route('market.instruments.master')}"
                standard_endpoint = f"{root_url}{get_route('market.instruments.master', use_standard_marketdata=True)}"

                endpoints_to_try = [
                    binary_endpoint,    # Binary Market Data API (primary)
                    standard_endpoint,  # Standard Market Data API (fallback)
                ]

                url = endpoints_to_try[0]  # Start with binary endpoint

                # Request payload
                # IMPORTANT: Must use json.dumps() and pass as 'content' parameter, not 'json' parameter
                # This matches the working XTS Connect implementation which uses requests.post(data=json.dumps(params))
                payload = {
                    "exchangeSegmentList": [exchange]
                }
                payload_json = json.dumps(payload)

                # Log complete request details for debugging
                logger.info("=" * 80)
                logger.info(f"MASTER CONTRACT API REQUEST - Exchange: {exchange}")
                logger.info("=" * 80)
                logger.info(f"Base URL (root_url): {root_url}")
                logger.info(f"Full URL: {url}")
                logger.info(f"HTTP Method: POST")
                logger.info(f"Headers: {headers}")
                logger.info(f"Payload (dict): {payload}")
                logger.info(f"Payload (JSON string): {payload_json}")
                logger.info(f"Request timeout: 30.0 seconds")
                logger.info("=" * 80)

                # Make request with retry logic for both endpoints
                # Using 'content' parameter with pre-serialized JSON (not 'json' parameter)
                # This matches the working pattern in xts_connect.py line 1086
                client = get_httpx_client()
                response = None
                last_error = None

                for endpoint_url in endpoints_to_try:
                    try:
                        logger.info(f"Trying endpoint: {endpoint_url}")
                        response = client.post(endpoint_url, headers=headers, content=payload_json, timeout=30.0)

                        # Log response details for debugging
                        logger.info("=" * 80)
                        logger.info(f"MASTER CONTRACT API RESPONSE - Exchange: {exchange}")
                        logger.info("=" * 80)
                        logger.info(f"Endpoint: {endpoint_url}")
                        logger.info(f"HTTP Status Code: {response.status_code}")
                        logger.info(f"Response Headers: {dict(response.headers)}")
                        logger.info(f"Response Content-Type: {response.headers.get('content-type', 'NOT SET')}")
                        logger.info(f"Response Body (first 1000 chars):\n{response.text[:1000]}")
                        logger.info("=" * 80)

                        # If successful, break out of retry loop
                        if response.status_code == 200:
                            logger.info(f"✅ Success with endpoint: {endpoint_url}")
                            break
                        else:
                            last_error = f"HTTP {response.status_code}"
                            logger.warning(f"HTTP {response.status_code} error for {exchange} on {endpoint_url}, trying next endpoint...")

                    except Exception as e:
                        last_error = str(e)
                        logger.warning(f"Error with endpoint {endpoint_url}: {e}, trying next endpoint...")
                        continue

                # Check if we got a successful response from any endpoint
                if not response or response.status_code != 200:
                    logger.error(f"All endpoints failed for {exchange}. Last error: {last_error}")
                    continue

                # Check if response is JSON
                content_type = response.headers.get('content-type', '')
                if 'application/json' not in content_type.lower():
                    logger.error(f"Non-JSON response for {exchange}. Content-Type: {content_type}")
                    logger.error(f"Response body: {response.text[:500]}")
                    continue

                # Parse JSON response
                try:
                    response_data = response.json()
                except json.JSONDecodeError as json_err:
                    logger.error(f"JSON decode error for {exchange}: {json_err}")
                    logger.error(f"Response text: {response.text[:500]}")
                    continue

                if response_data.get('type') == 'success' and 'result' in response_data:
                    # Parse the result (it's usually a pipe-separated string)
                    raw_data = response_data['result']

                    # Split by newlines and then by pipes
                    rows = [row.split('|') for row in raw_data.split('\n') if row.strip()]

                    # IMPORTANT: Handle inconsistent row lengths in API response
                    # Some exchanges (especially BSEFO) may have mixed row lengths
                    # - Index futures: 21 columns
                    # - Stock futures/options: 23 columns (with StrikePrice and OptionType)

                    # Determine the actual column structure from the data
                    if rows:
                        row_lengths = [len(row) for row in rows]
                        min_length = min(row_lengths)
                        max_length = max(row_lengths)

                        logger.info(f"Exchange {exchange}: Detected row lengths - min: {min_length}, max: {max_length}")

                        # If there's inconsistency, log examples
                        # NOTE: This is EXPECTED behavior for F&O exchanges (futures vs options)
                        # - Futures: 21 columns (no StrikePrice/OptionType)
                        # - Options: 23 columns (includes StrikePrice/OptionType)
                        if min_length != max_length:
                            logger.info(f"Exchange {exchange}: Mixed row lengths detected (expected for F&O exchanges)")
                            logger.info(f"  Futures contracts: {min_length} columns (without strike/option type)")
                            logger.info(f"  Options contracts: {max_length} columns (with strike/option type)")
                            # Find examples of each length
                            for target_length in set(row_lengths):
                                example_idx = row_lengths.index(target_length)
                                example_row = rows[example_idx]
                                instrument_name = example_row[4] if len(example_row) > 4 else 'Unknown'
                                logger.info(f"  Example of {target_length}-column row: {instrument_name}")

                        # Pad all rows to match the maximum length
                        padded_rows = []
                        for row in rows:
                            if len(row) < max_length:
                                # Pad with empty strings
                                padded_row = row + [''] * (max_length - len(row))
                                padded_rows.append(padded_row)
                            else:
                                padded_rows.append(row)

                        rows = padded_rows
                        logger.info(f"Exchange {exchange}: Padded all rows to {max_length} columns")

                    # Define columns based on exchange type and detected column count
                    if exchange in ['NSECM', 'BSECM']:
                        # Equity exchanges: 22 columns
                        columns = [
                            'exchange', 'sec_id', 'InstrumentType', 'symbol', 'sec_description',
                            'instrument_type', 'NameWithSeries', 'InstrumentID', 'PriceBand.High',
                            'PriceBand.Low', 'FreezeQty', 'TickSize', 'lot_size', 'Multiplier',
                            'displayName', 'ISIN', 'PriceNumerator', 'PriceDenominator',
                            'DetailedDescription', 'ExtendedSurvIndicator', 'CautionIndicator', 'GSMIndicator'
                        ]
                    else:
                        # F&O exchanges: Use detected max_length to determine column structure
                        if rows and max_length == 23:
                            # 23 columns: Full F&O structure with StrikePrice and OptionType
                            logger.info(f"Exchange {exchange}: Using 23-column F&O structure")
                            columns = [
                                'exchange', 'sec_id', 'InstrumentType', 'symbol', 'sec_description',
                                'instrument_type', 'NameWithSeries', 'InstrumentID', 'PriceBand.High',
                                'PriceBand.Low', 'FreezeQty', 'TickSize', 'lot_size', 'Multiplier',
                                'UnderlyingInstrumentId', 'UnderlyingIndexName', 'expiry_date',
                                'strike_price', 'option_type', 'displayName', 'PriceNumerator',
                                'PriceDenominator', 'DetailedDescription'
                            ]
                        else:
                            # 21 columns: Simplified F&O structure without StrikePrice and OptionType
                            logger.info(f"Exchange {exchange}: Using 21-column F&O structure")
                            columns = [
                                'exchange', 'sec_id', 'InstrumentType', 'symbol', 'sec_description',
                                'instrument_type', 'NameWithSeries', 'InstrumentID', 'PriceBand.High',
                                'PriceBand.Low', 'FreezeQty', 'TickSize', 'lot_size', 'Multiplier',
                                'UnderlyingInstrumentId', 'UnderlyingIndexName', 'expiry_date',
                                'displayName', 'PriceNumerator', 'PriceDenominator', 'DetailedDescription'
                            ]

                    # Verify column count after padding
                    if rows:
                        expected_columns = len(columns)
                        actual_columns = len(rows[0])

                        logger.info(f"Exchange {exchange}: Column count - expected: {expected_columns}, actual: {actual_columns}")

                        if actual_columns != expected_columns:
                            logger.error(f"Column mismatch for {exchange} after padding!")
                            logger.error(f"Expected {expected_columns} columns, got {actual_columns}")
                            logger.error(f"This should not happen after padding - skipping {exchange}")
                            continue

                    # Try to create DataFrame with error handling
                    try:
                        df = pd.DataFrame(rows, columns=columns)
                    except ValueError as ve:
                        logger.error(f"DataFrame creation failed for {exchange}: {ve}")
                        logger.error(f"Attempting to create DataFrame without column names...")
                        # Try creating without column names and then assign them
                        df = pd.DataFrame(rows)
                        if len(df.columns) == len(columns):
                            df.columns = columns
                        else:
                            logger.error(f"Cannot proceed with {exchange}: column count mismatch cannot be resolved")
                            continue

                    # Add exchange column (already in data, but ensure it's set)
                    df['exchange'] = exchange

                    # Process data based on exchange type
                    # Equity exchanges (NSECM, BSECM) don't have derivatives columns
                    # F&O exchanges (NSEFO, BSEFO, NSECD, MCXFO) have derivatives columns
                    if exchange in ['NSECM', 'BSECM']:
                        # Equity exchanges: skip derivatives processing
                        # Add missing columns with default values for consistency
                        df['expiry_date'] = None
                        df['strike_price'] = None
                        df['option_type'] = None

                        # Convert data types for equity
                        df = _convert_data_types(df)
                    else:
                        # F&O exchanges: process derivatives fields
                        df = _process_option_types(df)
                        df = _process_expiry_dates(df)
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
    # Check if expiry_date column exists (F&O exchanges only)
    if 'expiry_date' not in df.columns:
        logger.warning("expiry_date column not found in DataFrame, skipping expiry date processing")
        df['expiry_date'] = None
        return df

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
        exchange_value = _map_segment_to_marvelquant_exchange(segment_value)

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

        # IMPORTANT: Do NOT include 'broker' field - symtoken table doesn't have this column
        # Reference: database/symbol.py line 33-45 (table schema)
        # All brokers share the same symtoken table without broker differentiation
        prepared[key] = {
            "symbol": key[0],
            "brsymbol": str(brsymbol_value).strip(),
            "token": str(key[2]),  # Convert to string for consistency
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


def _map_segment_to_marvelquant_exchange(segment: str) -> str:
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

    # IMPORTANT: Follow the same pattern as other brokers (FivePaisaXTS, Angel, etc.)
    # - Delete entire symtoken table before inserting new data
    # - Use SQLAlchemy ORM bulk_insert_mappings for better performance
    # - No 'broker' column - table is shared across all brokers
    # Reference: broker/fivepaisaxts/database/master_contract_db.py lines 55-80

    start = time.perf_counter()

    try:
        # Import SymToken from database.symbol
        from database.symbol import SymToken, db_session

        # Delete all existing records (same pattern as other brokers)
        logger.info("Deleting existing symtoken table data")
        SymToken.query.delete()
        db_session.commit()

        # Retrieve existing tokens to filter them out from the insert
        existing_tokens = {result.token for result in db_session.query(SymToken.token).all()}

        # Filter out records with tokens that already exist
        filtered_records = [row for row in records if row['token'] not in existing_tokens]

        # Insert in bulk the filtered records
        if filtered_records:
            logger.info(f"Performing bulk insert of {len(filtered_records)} instruments")
            db_session.bulk_insert_mappings(SymToken, filtered_records)
            db_session.commit()

            duration_ms = (time.perf_counter() - start) * 1000
            logger.info(
                "Persisted %s Jainam instruments in %.2f ms",
                len(filtered_records),
                duration_ms,
            )
        else:
            logger.info("No new records to insert")

    except Exception as exc:
        logger.error("Failed to persist Jainam master contract: %s", exc)
        db_session.rollback()
        raise RuntimeError("Error persisting Jainam master contract") from exc

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
