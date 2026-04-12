"""Regression tests for Jainam master contract persistence.

These tests focus on the failure modes caught during QA:

* ``save_master_contract_to_db`` previously crashed due to a missing
  ``map_jainam_to_exchange`` import.
* Currency (``NSECD``) and BSE derivatives (``BSEFO``) segments were being
  persisted under the fallback ``NSE`` exchange, breaking downstream lookups.

The suite uses a throwaway SQLite database so it can run without touching the
developer's real symbol store.  Each test reloads the required modules after
pointing ``DATABASE_URL`` at the temporary database to ensure isolation.
"""

from __future__ import annotations

import importlib

import pandas as pd
import pytest
from sqlalchemy import text


def _reload_jainam_modules(monkeypatch: pytest.MonkeyPatch, tmp_path) -> tuple:
    """Point DATABASE_URL at a temp SQLite DB and reload dependent modules."""

    db_path = tmp_path / "jainam_symbols.sqlite"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")

    import database.symbol
    import broker.jainam_prop.mapping.transform_data as transform_data
    import broker.jainam_prop.database.master_contract_db as master_contract_db

    importlib.reload(database.symbol)
    importlib.reload(transform_data)
    importlib.reload(master_contract_db)

    with database.symbol.engine.begin() as connection:
        connection.execute(
            text(
                """
                CREATE TABLE symbol_token (
                    broker TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    brsymbol TEXT NOT NULL,
                    token INTEGER NOT NULL,
                    exchange TEXT NOT NULL,
                    brexchange TEXT NOT NULL,
                    lotsize INTEGER,
                    instrumenttype TEXT,
                    expiry TEXT,
                    strike REAL,
                    name TEXT,
                    tick_size REAL
                )
                """
            )
        )

    transform_data.clear_token_lookup_cache()
    return database.symbol, transform_data, master_contract_db


def test_save_master_contract_to_db_maps_all_segments(tmp_path, monkeypatch):
    database_symbol, _transform_data, master_contract_db = _reload_jainam_modules(
        monkeypatch,
        tmp_path,
    )

    master_df = pd.DataFrame(
        [
            {
                "ExchangeInstrumentID": 101,
                "NameWithSeries": "USDINR24OCTFUT",
                "DisplayName": "USDINR OCT 2024 FUT",
                "ExchangeSegment": "NSECD",
                "LotSize": 1,
                "InstrumentType": "FUTCUR",
                "TickSize": "0.0025",
                "ContractExpiration": "2024-10-29",
            },
            {
                "ExchangeInstrumentID": 202,
                "NameWithSeries": "SENSEX24OCTFUT",
                "DisplayName": "SENSEX OCT 2024 FUT",
                "ExchangeSegment": "BSEFO",
                "LotSize": 15,
                "InstrumentType": "FUTIDX",
                "TickSize": "5",
                "ContractExpiration": "2024-10-31",
            },
        ]
    )

    master_contract_db.save_master_contract_to_db(master_df)

    with database_symbol.engine.connect() as connection:
        rows = connection.execute(
            text(
                "SELECT symbol, exchange, brexchange FROM symbol_token "
                "ORDER BY token"
            )
        ).all()

    assert rows == [
        ("USDINR24OCTFUT", "CDS", "NSECD"),
        ("SENSEX24OCTFUT", "BFO", "BSEFO"),
    ]


def test_map_jainam_to_exchange_handles_extended_segments(tmp_path, monkeypatch):
    _database_symbol, transform_data, _master_contract_db = _reload_jainam_modules(
        monkeypatch,
        tmp_path,
    )

    assert transform_data.map_jainam_to_exchange("NSECM") == "NSE"
    assert transform_data.map_jainam_to_exchange("NSECD") == "CDS"
    assert transform_data.map_jainam_to_exchange("BSEFO") == "BFO"
    # Unknown segments should round-trip without forcing an incorrect fallback
    assert transform_data.map_jainam_to_exchange("XYZSEG") == "XYZSEG"
