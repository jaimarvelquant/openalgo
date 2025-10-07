"""Tests for Jainam transform_data helpers covering QA regressions."""

from __future__ import annotations

import importlib

import pandas as pd
import pytest
from sqlalchemy import text


def _reload_jainam_modules(monkeypatch: pytest.MonkeyPatch, tmp_path):
    """Reload broker modules against a temporary SQLite database."""

    db_path = tmp_path / "jainam_transform.sqlite"
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


def test_transform_data_resolves_currency_and_bse_derivatives(tmp_path, monkeypatch):
    _, transform_data, master_contract_db = _reload_jainam_modules(
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

    cds_payload = {
        "symbol": "USDINR24OCTFUT",
        "exchange": "CDS",
        "action": "BUY",
        "quantity": 1,
        "pricetype": "MARKET",
        "product": "NRML",
        "price": 0,
        "trigger_price": 0,
    }

    bfo_payload = {
        "symbol": "SENSEX24OCTFUT",
        "exchange": "BFO",
        "action": "SELL",
        "quantity": 15,
        "pricetype": "LIMIT",
        "product": "NRML",
        "price": 2500,
        "trigger_price": 0,
    }

    cds_result = transform_data.transform_data(cds_payload)
    bfo_result = transform_data.transform_data(bfo_payload)

    assert cds_result["exchangeSegment"] == "NSECD"
    assert cds_result["exchangeInstrumentID"] == 101

    assert bfo_result["exchangeSegment"] == "BSEFO"
    assert bfo_result["exchangeInstrumentID"] == 202


def test_map_exchange_to_jainam_accepts_segment_inputs(tmp_path, monkeypatch):
    _, transform_data, _ = _reload_jainam_modules(monkeypatch, tmp_path)

    assert transform_data.map_exchange_to_jainam("NSE") == "NSECM"
    assert transform_data.map_exchange_to_jainam("BFO") == "BSEFO"
    # Pre-segmented values should round-trip without raising
    assert transform_data.map_exchange_to_jainam("NSECM") == "NSECM"


def test_transform_data_rejects_unknown_exchange(tmp_path, monkeypatch):
    _, transform_data, master_contract_db = _reload_jainam_modules(
        monkeypatch,
        tmp_path,
    )

    master_df = pd.DataFrame(
        [
            {
                "ExchangeInstrumentID": 303,
                "NameWithSeries": "TESTSYM",
                "DisplayName": "Test Symbol",
                "ExchangeSegment": "NSECM",
                "LotSize": 1,
                "InstrumentType": "EQ",
                "TickSize": "0.05",
                "ContractExpiration": "",
            }
        ]
    )

    master_contract_db.save_master_contract_to_db(master_df)

    payload = {
        "symbol": "TESTSYM",
        "exchange": "UNSUPPORTED",
        "action": "BUY",
        "quantity": 1,
        "pricetype": "MARKET",
        "product": "NRML",
    }

    with pytest.raises(ValueError, match="Unsupported exchange 'UNSUPPORTED'"):
        transform_data.transform_data(payload)
