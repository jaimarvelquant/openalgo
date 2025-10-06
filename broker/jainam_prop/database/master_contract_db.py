"""
Master contract database module for Jainam
Handles downloading and managing symbol database
"""

import os
import pandas as pd
import json
from datetime import datetime
from utils.logging import get_logger
from utils.httpx_client import get_httpx_client

logger = get_logger(__name__)

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

def save_master_contract_to_db(df):
    """
    Save master contract data to database

    Args:
        df: DataFrame with instrument data
    """
    try:
        # This should be implemented to save to the actual database
        # For now, just log the operation
        logger.info(f"Would save {len(df)} instruments to database")

        # In a real implementation, you would:
        # 1. Connect to the database
        # 2. Clear existing data for this broker
        # 3. Insert new data
        # 4. Create indexes for fast lookup

        # Placeholder implementation
        output_file = f"master_contract_jainam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(output_file, index=False)
        logger.info(f"Master contract saved to {output_file}")

    except Exception as e:
        logger.error(f"Error saving master contract to database: {e}")

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
