#!/usr/bin/env python3
"""Benchmark Jainam token lookup latency for cached queries.

This script generates a synthetic master contract dataset (matching the Jainam
exchange segments) and measures the cached performance of
``broker.jainam_prop.mapping.transform_data.get_token_from_symbol``.

It is intended to provide reproducible evidence for Story 1.1-1 acceptance
criterion AC6 (<100 ms token lookup) by exercising the real persistence and
lookup logic against a large dataset.
"""

from __future__ import annotations

import argparse
import importlib
import os
import statistics
import sys
import tempfile
import time
import timeit
from pathlib import Path
from typing import Dict, Iterable, Tuple

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pandas as pd

_SEGMENTS = ["NSECM", "NSEFO", "NSECD", "BSECM", "BSEFO", "MCXFO"]
_SEGMENT_INSTRUMENT = {
    "NSECM": "EQ",
    "NSEFO": "FUTIDX",
    "NSECD": "FUTCUR",
    "BSECM": "EQ",
    "BSEFO": "FUTIDX",
    "MCXFO": "FUTCOM",
}


class BenchmarkError(RuntimeError):
    """Raised when the benchmark cannot be executed."""


def _reload_modules(database_url: str):
    """Reload database-backed modules against the supplied database URL."""

    previous_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = database_url

    import database.symbol  # pylint: disable=import-error
    import broker.jainam_prop.mapping.transform_data as transform_data  # noqa: E402
    import broker.jainam_prop.database.master_contract_db as master_contract_db  # noqa: E402

    importlib.reload(database.symbol)
    importlib.reload(transform_data)
    importlib.reload(master_contract_db)

    transform_data.clear_token_lookup_cache()
    return previous_url, database.symbol, transform_data, master_contract_db


def _restore_database_url(previous_url: str | None) -> None:
    if previous_url is None:
        os.environ.pop("DATABASE_URL", None)
    else:
        os.environ["DATABASE_URL"] = previous_url


def _build_synthetic_contract(
    instrument_count: int,
    transform_data_module,
) -> Tuple[pd.DataFrame, Dict[str, str]]:
    """Construct a synthetic master contract DataFrame.

    Returns the dataframe and a mapping of OpenAlgo exchange → sample symbol.
    """

    if instrument_count <= 0:
        raise BenchmarkError("instrument_count must be positive")

    rows = []
    sample_symbols: Dict[str, str] = {}

    for index in range(instrument_count):
        segment = _SEGMENTS[index % len(_SEGMENTS)]
        exchange = transform_data_module.map_jainam_to_exchange(segment)
        symbol = f"BMADSYM{index:06d}-{exchange}"

        rows.append(
            {
                "ExchangeInstrumentID": 1_000_000 + index,
                "NameWithSeries": symbol,
                "DisplayName": f"{symbol} INSTR",
                "ExchangeSegment": segment,
                "LotSize": 1,
                "InstrumentType": _SEGMENT_INSTRUMENT.get(segment, "EQ"),
                "TickSize": "0.05",
                "ContractExpiration": "2025-12-31",
            }
        )

        sample_symbols.setdefault(exchange, symbol)

    dataframe = pd.DataFrame(rows)
    return dataframe, sample_symbols


def _measure_cached_lookup(
    transform_data_module,
    symbol: str,
    exchange: str,
    number: int,
    repeat: int,
) -> Tuple[float, Iterable[float]]:
    """Return warm-call latency and per-call cached latency measurements."""

    lookup = lambda: transform_data_module.get_token_from_symbol(symbol, exchange)

    transform_data_module.clear_token_lookup_cache()

    warm_start = time.perf_counter()
    lookup()
    warm_ms = (time.perf_counter() - warm_start) * 1000

    durations = timeit.repeat(lookup, number=number, repeat=repeat)
    per_call_ms = [(duration / number) * 1000 for duration in durations]

    return warm_ms, per_call_ms


def _summarise_latencies(latencies: Iterable[float]) -> Dict[str, float]:
    data = list(latencies)
    if not data:
        raise BenchmarkError("No latency samples to summarise")

    sorted_samples = sorted(data)
    index_95 = max(0, min(len(sorted_samples) - 1, int(len(sorted_samples) * 0.95)))
    return {
        "avg": statistics.fmean(data),
        "min": min(sorted_samples),
        "max": max(sorted_samples),
        "p95": sorted_samples[index_95],
    }


def run_benchmark(
    instrument_count: int,
    iterations: int,
    repeat: int,
    database_url: str | None,
) -> Dict[str, object]:
    """Execute the benchmark and return structured results."""

    if iterations <= 0 or repeat <= 0:
        raise BenchmarkError("iterations and repeat must be positive integers")

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "jainam_benchmark.sqlite"
        resolved_url = database_url or f"sqlite:///{db_path}"

        previous_url, database_symbol, transform_data_module, master_contract_db = _reload_modules(
            resolved_url
        )
        try:
            dataframe, sample_symbols = _build_synthetic_contract(
                instrument_count, transform_data_module
            )

            with database_symbol.engine.begin() as connection:
                connection.execute(
                    text(
                        """
                        CREATE TABLE IF NOT EXISTS symbol_token (
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

            load_start = time.perf_counter()
            master_contract_db.save_master_contract_to_db(dataframe)
            load_ms = (time.perf_counter() - load_start) * 1000

            results = {
                "database_url": resolved_url,
                "instrument_count": int(dataframe.shape[0]),
                "load_ms": load_ms,
                "iterations": iterations,
                "repeat": repeat,
                "samples": {},
            }

            for exchange, symbol in sorted(sample_symbols.items()):
                warm_ms, per_call_ms = _measure_cached_lookup(
                    transform_data_module,
                    symbol,
                    exchange,
                    number=iterations,
                    repeat=repeat,
                )
                summary = _summarise_latencies(per_call_ms)
                results["samples"][exchange] = {
                    "symbol": symbol,
                    "warm_ms": warm_ms,
                    "cached_ms": summary,
                }

            return results
        finally:
            _restore_database_url(previous_url)
            # Reset cached engine connections to avoid holding open temp files
            if hasattr(database_symbol, "engine"):
                database_symbol.engine.dispose()


def _format_results(results: Dict[str, object]) -> str:
    lines = [
        "Jainam Token Lookup Benchmark",
        f"Dataset size: {results['instrument_count']} instruments",
        f"Master contract load time: {results['load_ms']:.2f} ms",
        f"Cached iterations per sample: {results['iterations']} (repeat {results['repeat']})",
    ]

    for exchange, sample in results["samples"].items():
        cached = sample["cached_ms"]
        lines.append(
            (
                f"  - {exchange}: warm {sample['warm_ms']:.2f} ms | "
                f"cached avg {cached['avg']:.4f} ms (min {cached['min']:.4f} ms, "
                f"max {cached['max']:.4f} ms, p95 {cached['p95']:.4f} ms)"
            )
        )

    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--instrument-count",
        type=int,
        default=120_000,
        help="Number of synthetic instruments to seed (default: 120000)",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=500,
        help="Number of cached lookups per measurement repeat (default: 500)",
    )
    parser.add_argument(
        "--repeat",
        type=int,
        default=5,
        help="Number of measurement repeats for cached lookups (default: 5)",
    )
    parser.add_argument(
        "--database-url",
        type=str,
        default=None,
        help="Optional SQLAlchemy database URL override",
    )

    args = parser.parse_args(argv)

    try:
        results = run_benchmark(
            instrument_count=args.instrument_count,
            iterations=args.iterations,
            repeat=args.repeat,
            database_url=args.database_url,
        )
    except BenchmarkError as exc:  # pragma: no cover - defensive
        print(f"Benchmark failed: {exc}", file=sys.stderr)
        return 2

    print(_format_results(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
