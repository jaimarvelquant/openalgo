#!/usr/bin/env python3
"""
Fetch live Jainam portfolio data (positions, holdings, trade book) and capture
latency metrics for release readiness validation.

The script expects Jainam credentials to be present via environment variables
or the system keyring (use `scripts/jainam_keyring_helper.py` to populate).
"""

from __future__ import annotations

import argparse
import getpass
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from broker.jainam_prop.api.auth_api import authenticate_broker, authenticate_market_data
from broker.jainam_prop.api.order_api import get_positions, get_holdings, get_trade_book
from broker.jainam_prop.mapping.order_data import (
    map_position_data,
    transform_positions_data,
    map_portfolio_data,
    transform_holdings_data,
    calculate_portfolio_statistics,
    map_trade_data,
    transform_tradebook_data,
)
from utils.logging import get_logger

logger = get_logger(__name__)

FETCH_CHOICES = ("positions", "holdings", "tradebook")
SENSITIVE_KEYS = {"orderid", "order_id", "exchange_order_id", "exchangeorderid", "trade_id", "exchangetradeid", "clientid"}


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def redact_payload(obj: Any) -> Any:
    if isinstance(obj, dict):
        redacted = {}
        for key, value in obj.items():
            key_lower = key.lower()
            if key_lower in SENSITIVE_KEYS:
                redacted[key] = "***redacted***"
            else:
                redacted[key] = redact_payload(value)
        return redacted
    if isinstance(obj, list):
        return [redact_payload(item) for item in obj]
    return obj


def build_auth_payload(interactive_token: str, market_token: str | None, client_id: str | None) -> Dict[str, Any]:
    payload: Dict[str, Any] = {"token": interactive_token}
    if market_token:
        payload["market_token"] = market_token
    if client_id:
        payload["client_id"] = client_id
    return payload


def resolve_interactive_token(request_token: str | None) -> str:
    interactive = (
        os.getenv("JAINAM_INTERACTIVE_SESSION_TOKEN")
        or os.getenv("JAINAM_INTERACTIVE_TOKEN")
        or os.getenv("JAINAM_SESSION_TOKEN")
    )
    if interactive:
        return interactive

    if not request_token:
        request_token = getpass.getpass("Jainam request token (from OAuth callback): ").strip()
    token, error = authenticate_broker(request_token)
    if error or not token:
        raise RuntimeError(f"Interactive authentication failed: {error or 'unknown error'}")
    return token


def resolve_market_token() -> str:
    market_token = (
        os.getenv("JAINAM_MARKET_TOKEN")
        or os.getenv("JAINAM_MARKET_SESSION_TOKEN")
        or os.getenv("JAINAM_FEED_TOKEN")
    )
    if market_token:
        return market_token

    token, error = authenticate_market_data()
    if error or not token:
        raise RuntimeError(f"Market data authentication failed: {error or 'unknown error'}")
    return token


def fetch_positions(auth_payload: Dict[str, Any]) -> Dict[str, Any]:
    started = iso_now()
    t0 = time.perf_counter()
    raw = get_positions(auth_payload)
    elapsed = time.perf_counter() - t0

    result: Dict[str, Any] = {
        "flow": "positions",
        "started_at": started,
        "duration_seconds": round(elapsed, 3),
        "raw": raw,
    }
    try:
        mapped = map_position_data(raw)
        transformed = transform_positions_data(mapped)
        result["transformed"] = transformed
    except Exception as exc:  # pragma: no cover - defensive only
        result["transformation_error"] = str(exc)
    return result


def fetch_holdings(auth_payload: Dict[str, Any]) -> Dict[str, Any]:
    started = iso_now()
    t0 = time.perf_counter()
    raw = get_holdings(auth_payload)
    elapsed = time.perf_counter() - t0

    result: Dict[str, Any] = {
        "flow": "holdings",
        "started_at": started,
        "duration_seconds": round(elapsed, 3),
        "raw": raw,
    }
    try:
        mapped = map_portfolio_data(raw, auth_token=auth_payload)
        stats = calculate_portfolio_statistics(mapped)
        transformed = transform_holdings_data(mapped)
        result["transformed"] = transformed
        result["statistics"] = stats
    except Exception as exc:  # pragma: no cover - defensive only
        result["transformation_error"] = str(exc)
    return result


def fetch_tradebook(auth_payload: Dict[str, Any]) -> Dict[str, Any]:
    started = iso_now()
    t0 = time.perf_counter()
    raw = get_trade_book(auth_payload)
    elapsed = time.perf_counter() - t0

    result: Dict[str, Any] = {
        "flow": "tradebook",
        "started_at": started,
        "duration_seconds": round(elapsed, 3),
        "raw": raw,
    }
    try:
        mapped = map_trade_data(trade_data=raw)
        transformed = transform_tradebook_data(mapped)
        result["transformed"] = transformed
    except Exception as exc:  # pragma: no cover - defensive only
        result["transformation_error"] = str(exc)
    return result


def run_fetches(flows: Iterable[str], auth_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    results = []
    for flow in flows:
        if flow == "positions":
            results.append(fetch_positions(auth_payload))
        elif flow == "holdings":
            results.append(fetch_holdings(auth_payload))
        elif flow == "tradebook":
            results.append(fetch_tradebook(auth_payload))
        else:  # pragma: no cover - guarded by argparse
            raise ValueError(f"Unsupported flow: {flow}")
    return results


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Capture live Jainam portfolio data with latency metrics.")
    parser.add_argument(
        "--fetch",
        nargs="+",
        choices=FETCH_CHOICES,
        default=list(FETCH_CHOICES),
        help="Flows to fetch (default: positions holdings tradebook).",
    )
    parser.add_argument(
        "--request-token",
        help="Interactive request token from OAuth callback. If omitted, the script prompts when needed.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON file to write sanitized output (redacted IDs).",
    )
    parser.add_argument(
        "--no-redact",
        action="store_true",
        help="Disable automatic redaction of order/trade/client identifiers.",
    )
    parser.add_argument(
        "--client-id",
        help="Optional client ID to pass through to Jainam APIs (defaults to env JAINAM_CLIENT_ID).",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv)

    client_id = args.client_id or os.getenv("JAINAM_CLIENT_ID")

    try:
        interactive_token = resolve_interactive_token(args.request_token)
        market_token = resolve_market_token()
    except Exception as exc:
        logger.error("Credential resolution failed: %s", exc)
        return 2

    auth_payload = build_auth_payload(interactive_token, market_token, client_id)
    logger.info("Beginning live fetch for flows: %s", ", ".join(args.fetch))

    try:
        results = run_fetches(args.fetch, auth_payload)
    except Exception as exc:
        logger.error("Live fetch failed: %s", exc, exc_info=True)
        return 1

    printable = results if args.no_redact else redact_payload(results)
    print(json.dumps(printable, indent=2, default=str))

    if args.output:
        args.output.write_text(json.dumps(printable, indent=2, default=str))
        logger.info("Wrote sanitized output to %s", args.output)

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
