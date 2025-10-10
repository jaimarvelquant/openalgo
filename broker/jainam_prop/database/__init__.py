"""Jainam master contract database modules"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATABASE_PATH = PROJECT_ROOT / 'database'

if DATABASE_PATH.exists():
    resolved = str(DATABASE_PATH)
    __path__ = [resolved] + [p for p in __path__ if p != resolved]
    if __spec__ is not None:
        __spec__.submodule_search_locations = __path__

# Explicit exports for dynamic import compatibility
# Required by auth_utils which calls master_contract_download
from broker.jainam_prop.database.master_contract_db import (
    master_contract_download,
    get_master_contract,
    save_master_contract_to_db,
    get_instrument_by_token,
)

__all__ = [
    'master_contract_download',
    'get_master_contract',
    'save_master_contract_to_db',
    'get_instrument_by_token',
]
