from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetAssetsRequest
from alpaca.trading.enums import AssetStatus
from database.auth_db import get_auth_token
from database.symbol import SymToken, db_session
from database.master_contract_status_db import update_status
from utils.logging import get_logger
from sqlalchemy import text

logger = get_logger(__name__)

def master_contract_download():
    """
    Download Alpaca assets and save to local database.
    Standard signature for OpenAlgo master contract worker.
    """
    try:
        # Fetch the latest auth token for alpaca
        # We query the database directly since we don't have the session in this background thread
        from database.auth_db import Auth
        auth_record = db_session.query(Auth).filter(Auth.broker == "alpaca").order_by(Auth.id.desc()).first()
        
        if not auth_record:
            logger.error("No Alpaca credentials found in database")
            update_status("alpaca", "error", "No credentials found")
            return False
            
        from database.auth_db import decrypt_token
        auth_token = decrypt_token(auth_record.auth)
        
        parts = auth_token.split(":::")
        if len(parts) < 3:
            logger.error("Invalid Auth Format for Master Contract download")
            update_status("alpaca", "error", "Invalid Auth Format")
            return False
            
        mode = parts[0]
        api_key = parts[1]
        secret_key = parts[2]
        is_paper = (mode == "PAPER")
        
        update_status("alpaca", "downloading", "Fetching symbols from Alpaca...")
        
        # Initialize Client
        client = TradingClient(api_key, secret_key, paper=is_paper)
        
        # Fetch Active Assets
        search_params = GetAssetsRequest(status=AssetStatus.ACTIVE)
        assets = client.get_all_assets(search_params)
        
        if not assets:
            update_status("alpaca", "error", "No assets found")
            return False
            
        # Clear existing Alpaca symbols from DB
        try:
            db_session.query(SymToken).filter(SymToken.exchange == "ALPACA").delete()
            db_session.commit()
        except Exception as e:
            logger.error(f"Error clearing old Alpaca symbols: {e}")
            db_session.rollback()
            
        # Process assets
        sym_tokens = []
        total_count = len(assets)
        logger.info(f"Processing {total_count} Alpaca symbols...")
        
        for i, asset in enumerate(assets):
            # Only include tradable assets
            if not asset.tradable:
                continue
                
            # Alpaca symbol naming: 
            # Stocks: AAPL, TSLA
            # Crypto: BTC/USD, ETH/USD
            symbol = asset.symbol
            
            # Use asset_class (Enum) instead of class_
            asset_class_val = str(asset.asset_class).lower()
            is_equity = "us_equity" in asset_class_val
            
            sym_tokens.append(SymToken(
                symbol=symbol,
                brsymbol=symbol,
                name=asset.name,
                exchange="ALPACA",
                brexchange="ALPACA",
                token=str(asset.id),
                instrumenttype="EQUITY" if is_equity else "CRYPTO",
                lotsize=1 if is_equity else 0, # Crypto is fractional
                tick_size=0.01,
                expiry=""
            ))
            
            # Bulk insert every 1000 items
            if len(sym_tokens) >= 1000:
                db_session.bulk_save_objects(sym_tokens)
                db_session.commit()
                sym_tokens = []
                update_status("alpaca", "downloading", f"Saved {i+1}/{total_count} symbols...")

        # Final insert
        if sym_tokens:
            db_session.bulk_save_objects(sym_tokens)
            db_session.commit()
            
        update_status("alpaca", "success", "Download complete", total_symbols=total_count)
        logger.info(f"Alpaca Master Contract download complete: {total_count} symbols")
        return True
        
    except Exception as e:
        logger.exception(f"Alpaca Master Contract download error: {e}")
        update_status("alpaca", "error", f"Error: {str(e)}")
        return False
