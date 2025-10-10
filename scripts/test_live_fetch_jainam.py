#!/usr/bin/env python3
"""
Unit tests for scripts/live_fetch_jainam.py
Tests credential resolution, redaction logic, and API orchestration.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

# Import the module under test
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.live_fetch_jainam import (
    build_auth_payload,
    fetch_holdings,
    fetch_positions,
    fetch_tradebook,
    iso_now,
    main,
    parse_args,
    redact_payload,
    resolve_tokens,
    run_fetches,
)


class TestRedactPayload:
    """Test the PII redaction logic."""

    def test_redact_dict_with_sensitive_keys(self):
        """Redact sensitive keys in dict."""
        payload = {
            "orderid": "ORDER123",
            "symbol": "RELIANCE",
            "exchange_order_id": "EXC456",
            "clientid": "CLIENT789"
        }
        redacted = redact_payload(payload)
        assert redacted["orderid"] == "***redacted***"
        assert redacted["exchange_order_id"] == "***redacted***"
        assert redacted["clientid"] == "***redacted***"
        assert redacted["symbol"] == "RELIANCE"

    def test_redact_nested_dict(self):
        """Redact sensitive keys in nested structures."""
        payload = {
            "data": {
                "trade_id": "TRADE123",
                "price": 100.50
            }
        }
        redacted = redact_payload(payload)
        assert redacted["data"]["trade_id"] == "***redacted***"
        assert redacted["data"]["price"] == 100.50

    def test_redact_list_of_dicts(self):
        """Redact sensitive keys in list of dicts."""
        payload = [
            {"orderid": "O1", "symbol": "INFY"},
            {"orderid": "O2", "symbol": "TCS"}
        ]
        redacted = redact_payload(payload)
        assert redacted[0]["orderid"] == "***redacted***"
        assert redacted[1]["orderid"] == "***redacted***"
        assert redacted[0]["symbol"] == "INFY"

    def test_redact_preserves_primitives(self):
        """Primitives are passed through unchanged."""
        assert redact_payload(42) == 42
        assert redact_payload("test") == "test"
        assert redact_payload(None) is None

    def test_redact_case_insensitive(self):
        """Redaction is case-insensitive for keys."""
        payload = {"OrderID": "O123", "TRADE_ID": "T456"}
        redacted = redact_payload(payload)
        assert redacted["OrderID"] == "***redacted***"
        assert redacted["TRADE_ID"] == "***redacted***"


class TestBuildAuthPayload:
    """Test auth payload construction."""

    def test_build_with_all_params(self):
        """Build payload with all parameters."""
        payload = build_auth_payload("int_token", "mkt_token", "client123")
        assert payload["token"] == "int_token"
        assert payload["market_token"] == "mkt_token"
        assert payload["client_id"] == "client123"

    def test_build_without_market_token(self):
        """Build payload without market token."""
        payload = build_auth_payload("int_token", None, "client123")
        assert payload["token"] == "int_token"
        assert "market_token" not in payload
        assert payload["client_id"] == "client123"

    def test_build_without_client_id(self):
        """Build payload without client ID."""
        payload = build_auth_payload("int_token", "mkt_token", None)
        assert payload["token"] == "int_token"
        assert payload["market_token"] == "mkt_token"
        assert "client_id" not in payload


class TestResolveTokens:
    """Test credential resolution from environment."""

    @patch.dict(os.environ, {
        "JAINAM_INTERACTIVE_SESSION_TOKEN": "int_token",
        "JAINAM_MARKET_TOKEN": "mkt_token",
        "JAINAM_USER_ID": "user123"
    })
    def test_resolve_from_env_primary_vars(self):
        """Resolve tokens from primary environment variables."""
        interactive, market, user_id = resolve_tokens()
        assert interactive == "int_token"
        assert market == "mkt_token"
        assert user_id == "user123"

    @patch.dict(os.environ, {
        "JAINAM_INTERACTIVE_TOKEN": "int_token_alt",
        "JAINAM_FEED_TOKEN": "feed_token",
        "JAINAM_CLIENT_ID": "client456"
    })
    def test_resolve_from_env_fallback_vars(self):
        """Resolve tokens from fallback environment variables."""
        interactive, market, user_id = resolve_tokens()
        assert interactive == "int_token_alt"
        assert market == "feed_token"
        assert user_id == "client456"

    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.live_fetch_jainam.authenticate_direct")
    def test_resolve_via_direct_auth_success(self, mock_auth):
        """Resolve tokens via direct authentication when env vars missing."""
        mock_auth.return_value = ("int_direct", "mkt_direct", "user_direct", None)
        interactive, market, user_id = resolve_tokens()
        assert interactive == "int_direct"
        assert market == "mkt_direct"
        assert user_id == "user_direct"
        mock_auth.assert_called_once()

    @patch.dict(os.environ, {}, clear=True)
    @patch("scripts.live_fetch_jainam.authenticate_direct")
    def test_resolve_via_direct_auth_failure(self, mock_auth):
        """Raise error when direct authentication fails."""
        mock_auth.return_value = (None, None, None, "Auth failed")
        with pytest.raises(RuntimeError, match="Direct Jainam authentication failed"):
            resolve_tokens()


class TestFetchFunctions:
    """Test individual fetch functions (positions, holdings, tradebook)."""

    @patch("scripts.live_fetch_jainam.get_positions")
    @patch("scripts.live_fetch_jainam.map_position_data")
    @patch("scripts.live_fetch_jainam.transform_positions_data")
    def test_fetch_positions_success(self, mock_transform, mock_map, mock_api):
        """Fetch positions successfully."""
        mock_api.return_value = {"status": "success", "result": []}
        mock_map.return_value = {"mapped": True}
        mock_transform.return_value = {"transformed": True}

        result = fetch_positions({"token": "test"})

        assert result["flow"] == "positions"
        assert "started_at" in result
        assert "duration_seconds" in result
        assert result["raw"] == {"status": "success", "result": []}
        assert result["transformed"] == {"transformed": True}
        mock_api.assert_called_once_with({"token": "test"})

    @patch("scripts.live_fetch_jainam.get_holdings")
    @patch("scripts.live_fetch_jainam.map_portfolio_data")
    @patch("scripts.live_fetch_jainam.calculate_portfolio_statistics")
    @patch("scripts.live_fetch_jainam.transform_holdings_data")
    def test_fetch_holdings_success(self, mock_transform, mock_stats, mock_map, mock_api):
        """Fetch holdings successfully."""
        mock_api.return_value = {"status": "success"}
        mock_map.return_value = {"mapped": True}
        mock_stats.return_value = {"total_value": 1000}
        mock_transform.return_value = {"transformed": True}

        auth_payload = {"token": "test"}
        result = fetch_holdings(auth_payload)

        assert result["flow"] == "holdings"
        assert result["transformed"] == {"transformed": True}
        assert result["statistics"] == {"total_value": 1000}
        mock_map.assert_called_once_with({"status": "success"}, auth_token=auth_payload)

    @patch("scripts.live_fetch_jainam.get_trade_book")
    @patch("scripts.live_fetch_jainam.map_trade_data")
    @patch("scripts.live_fetch_jainam.transform_tradebook_data")
    def test_fetch_tradebook_success(self, mock_transform, mock_map, mock_api):
        """Fetch trade book successfully."""
        mock_api.return_value = {"status": "success"}
        mock_map.return_value = {"mapped": True}
        mock_transform.return_value = {"transformed": True}

        result = fetch_tradebook({"token": "test"})

        assert result["flow"] == "tradebook"
        assert result["transformed"] == {"transformed": True}
        mock_map.assert_called_once_with(trade_data={"status": "success"})

    @patch("scripts.live_fetch_jainam.get_positions")
    @patch("scripts.live_fetch_jainam.map_position_data")
    def test_fetch_positions_transformation_error(self, mock_map, mock_api):
        """Handle transformation errors gracefully."""
        mock_api.return_value = {"status": "success"}
        mock_map.side_effect = ValueError("Invalid data")

        result = fetch_positions({"token": "test"})

        assert result["flow"] == "positions"
        assert "transformation_error" in result
        assert "Invalid data" in result["transformation_error"]


class TestRunFetches:
    """Test orchestration of multiple fetches."""

    @patch("scripts.live_fetch_jainam.fetch_positions")
    @patch("scripts.live_fetch_jainam.fetch_holdings")
    @patch("scripts.live_fetch_jainam.fetch_tradebook")
    def test_run_all_flows(self, mock_tb, mock_h, mock_p):
        """Run all three flows."""
        mock_p.return_value = {"flow": "positions"}
        mock_h.return_value = {"flow": "holdings"}
        mock_tb.return_value = {"flow": "tradebook"}

        auth = {"token": "test"}
        results = run_fetches(["positions", "holdings", "tradebook"], auth)

        assert len(results) == 3
        assert results[0]["flow"] == "positions"
        assert results[1]["flow"] == "holdings"
        assert results[2]["flow"] == "tradebook"
        mock_p.assert_called_once_with(auth)
        mock_h.assert_called_once_with(auth)
        mock_tb.assert_called_once_with(auth)

    @patch("scripts.live_fetch_jainam.fetch_positions")
    def test_run_single_flow(self, mock_p):
        """Run a single flow."""
        mock_p.return_value = {"flow": "positions"}

        results = run_fetches(["positions"], {"token": "test"})

        assert len(results) == 1
        assert results[0]["flow"] == "positions"


class TestParseArgs:
    """Test CLI argument parsing."""

    def test_parse_default_args(self):
        """Parse with default arguments."""
        args = parse_args([])
        assert args.fetch == ["positions", "holdings", "tradebook"]
        assert args.request_token is None
        assert args.output is None
        assert args.no_redact is False

    def test_parse_specific_fetch(self):
        """Parse with specific fetch flows."""
        args = parse_args(["--fetch", "positions", "holdings"])
        assert args.fetch == ["positions", "holdings"]

    def test_parse_output_file(self):
        """Parse with output file."""
        args = parse_args(["--output", "/tmp/test.json"])
        assert args.output == Path("/tmp/test.json")

    def test_parse_no_redact_flag(self):
        """Parse with no-redact flag."""
        args = parse_args(["--no-redact"])
        assert args.no_redact is True

    def test_parse_client_id(self):
        """Parse with client ID."""
        args = parse_args(["--client-id", "CLIENT123"])
        assert args.client_id == "CLIENT123"


class TestMain:
    """Test main entry point."""

    @patch("scripts.live_fetch_jainam.resolve_tokens")
    @patch("scripts.live_fetch_jainam.run_fetches")
    @patch("builtins.print")
    def test_main_success(self, mock_print, mock_run, mock_resolve):
        """Main function executes successfully."""
        mock_resolve.return_value = ("int_token", "mkt_token", "user123")
        mock_run.return_value = [{"flow": "positions", "duration_seconds": 0.1}]

        exit_code = main(["--fetch", "positions"])

        assert exit_code == 0
        mock_resolve.assert_called_once()
        mock_run.assert_called_once()
        mock_print.assert_called_once()

    @patch("scripts.live_fetch_jainam.resolve_tokens")
    def test_main_credential_resolution_failure(self, mock_resolve):
        """Main function handles credential resolution failure."""
        mock_resolve.side_effect = RuntimeError("Auth failed")

        exit_code = main([])

        assert exit_code == 2

    @patch("scripts.live_fetch_jainam.resolve_tokens")
    @patch("scripts.live_fetch_jainam.run_fetches")
    def test_main_fetch_failure(self, mock_run, mock_resolve):
        """Main function handles fetch failure."""
        mock_resolve.return_value = ("int_token", "mkt_token", "user123")
        mock_run.side_effect = RuntimeError("Network error")

        exit_code = main([])

        assert exit_code == 1

    @patch("scripts.live_fetch_jainam.resolve_tokens")
    @patch("scripts.live_fetch_jainam.run_fetches")
    @patch("builtins.print")
    def test_main_with_output_file(self, mock_print, mock_run, mock_resolve, tmp_path):
        """Main function writes output file."""
        mock_resolve.return_value = ("int_token", "mkt_token", "user123")
        mock_run.return_value = [{"flow": "positions"}]

        output_file = tmp_path / "output.json"
        exit_code = main(["--output", str(output_file)])

        assert exit_code == 0
        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert len(data) == 1
        assert data[0]["flow"] == "positions"

    @patch("scripts.live_fetch_jainam.resolve_tokens")
    @patch("scripts.live_fetch_jainam.run_fetches")
    @patch("builtins.print")
    def test_main_redaction_applied_by_default(self, mock_print, mock_run, mock_resolve):
        """Main function applies redaction by default."""
        mock_resolve.return_value = ("int_token", "mkt_token", "user123")
        mock_run.return_value = [{"flow": "positions", "orderid": "ORDER123"}]

        exit_code = main([])

        assert exit_code == 0
        # Verify print was called with redacted data
        call_args = mock_print.call_args[0][0]
        assert "***redacted***" in call_args

    @patch("scripts.live_fetch_jainam.resolve_tokens")
    @patch("scripts.live_fetch_jainam.run_fetches")
    @patch("builtins.print")
    def test_main_no_redact_flag(self, mock_print, mock_run, mock_resolve):
        """Main function skips redaction when --no-redact is set."""
        mock_resolve.return_value = ("int_token", "mkt_token", "user123")
        mock_run.return_value = [{"flow": "positions", "orderid": "ORDER123"}]

        exit_code = main(["--no-redact"])

        assert exit_code == 0
        # Verify print was called with unredacted data
        call_args = mock_print.call_args[0][0]
        assert "ORDER123" in call_args


class TestUtilities:
    """Test utility functions."""

    def test_iso_now_format(self):
        """iso_now returns ISO8601 formatted UTC timestamp."""
        timestamp = iso_now()
        assert "T" in timestamp
        assert timestamp.endswith("+00:00") or timestamp.endswith("Z")
