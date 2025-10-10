#!/usr/bin/env python3
"""
Unit tests for scripts/jainam_keyring_helper.py
Tests credential storage and export functions with mocked keyring.
"""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

# Import the module under test
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Mock keyring module before importing jainam_keyring_helper
sys.modules['keyring'] = MagicMock()

from scripts.jainam_keyring_helper import (
    FIELDS,
    SERVICE,
    build_parser,
    export_credentials,
    main,
    store_credentials,
)


class TestStoreCredentials:
    """Test secure credential storage."""

    @patch("scripts.jainam_keyring_helper.keyring.set_password")
    @patch("scripts.jainam_keyring_helper.getpass.getpass")
    @patch("builtins.print")
    def test_store_all_credentials(self, mock_print, mock_getpass, mock_set_password):
        """Store all credentials successfully."""
        # Simulate user entering values for all fields
        mock_getpass.side_effect = [
            "api_key_value",
            "api_secret_value",
            "market_key_value",
            "market_secret_value",
            "user_id_value",
            "app_name_value",
            "2025-12-31"
        ]

        store_credentials()

        # Verify keyring.set_password was called for each field
        assert mock_set_password.call_count == 7
        calls = mock_set_password.call_args_list
        assert calls[0][0] == (SERVICE, "JAINAM_INTERACTIVE_API_KEY", "api_key_value")
        assert calls[1][0] == (SERVICE, "JAINAM_INTERACTIVE_API_SECRET", "api_secret_value")

    @patch("scripts.jainam_keyring_helper.keyring.set_password")
    @patch("scripts.jainam_keyring_helper.getpass.getpass")
    @patch("builtins.print")
    def test_store_with_skipped_fields(self, mock_print, mock_getpass, mock_set_password):
        """Skip empty fields during storage."""
        # User enters some values and leaves others blank
        mock_getpass.side_effect = [
            "api_key_value",
            "",  # Skip API secret
            "market_key_value",
            "",  # Skip market secret
            "",  # Skip user ID
            "",  # Skip app name
            ""   # Skip expiry
        ]

        store_credentials()

        # Only non-empty values should be stored
        assert mock_set_password.call_count == 2
        calls = mock_set_password.call_args_list
        assert calls[0][0] == (SERVICE, "JAINAM_INTERACTIVE_API_KEY", "api_key_value")
        assert calls[1][0] == (SERVICE, "JAINAM_MARKET_API_KEY", "market_key_value")

    @patch("scripts.jainam_keyring_helper.keyring.set_password")
    @patch("scripts.jainam_keyring_helper.getpass.getpass")
    def test_store_specific_fields(self, mock_getpass, mock_set_password):
        """Store only specific fields."""
        mock_getpass.side_effect = ["value1", "value2"]

        store_credentials(["JAINAM_INTERACTIVE_API_KEY", "JAINAM_MARKET_API_KEY"])

        assert mock_set_password.call_count == 2


class TestExportCredentials:
    """Test credential export in various formats."""

    @patch("scripts.jainam_keyring_helper.keyring.get_password")
    @patch("builtins.print")
    def test_export_env_format(self, mock_print, mock_get_password):
        """Export credentials as environment variables."""
        # Mock keyring to return values for some fields
        def get_password_side_effect(service, key):
            credentials = {
                "JAINAM_INTERACTIVE_API_KEY": "int_key_123",
                "JAINAM_INTERACTIVE_API_SECRET": "int_secret_456",
                "JAINAM_MARKET_API_KEY": "mkt_key_789",
            }
            return credentials.get(key)

        mock_get_password.side_effect = get_password_side_effect

        export_credentials("env")

        # Verify print was called with export statements
        assert mock_print.call_count == 3
        calls = [call[0][0] for call in mock_print.call_args_list]
        assert 'export JAINAM_INTERACTIVE_API_KEY="int_key_123"' in calls
        assert 'export JAINAM_INTERACTIVE_API_SECRET="int_secret_456"' in calls
        assert 'export JAINAM_MARKET_API_KEY="mkt_key_789"' in calls

    @patch("scripts.jainam_keyring_helper.keyring.get_password")
    @patch("builtins.print")
    def test_export_json_format(self, mock_print, mock_get_password):
        """Export credentials as JSON."""
        def get_password_side_effect(service, key):
            credentials = {
                "JAINAM_INTERACTIVE_API_KEY": "int_key_123",
                "JAINAM_MARKET_API_KEY": "mkt_key_789",
            }
            return credentials.get(key)

        mock_get_password.side_effect = get_password_side_effect

        export_credentials("json")

        # Verify JSON output
        assert mock_print.call_count == 1
        json_output = mock_print.call_args[0][0]
        data = json.loads(json_output)
        assert data["JAINAM_INTERACTIVE_API_KEY"] == "int_key_123"
        assert data["JAINAM_MARKET_API_KEY"] == "mkt_key_789"

    @patch("scripts.jainam_keyring_helper.keyring.get_password")
    def test_export_no_credentials_stored(self, mock_get_password):
        """Raise error when no credentials are found."""
        mock_get_password.return_value = None

        with pytest.raises(SystemExit, match="No Jainam credentials found in keyring"):
            export_credentials("env")

    @patch("scripts.jainam_keyring_helper.keyring.get_password")
    @patch("builtins.print")
    def test_export_partial_credentials(self, mock_print, mock_get_password):
        """Export only the credentials that exist."""
        def get_password_side_effect(service, key):
            if key == "JAINAM_INTERACTIVE_API_KEY":
                return "int_key_123"
            return None

        mock_get_password.side_effect = get_password_side_effect

        export_credentials("env")

        # Only one credential should be exported
        assert mock_print.call_count == 1
        assert 'export JAINAM_INTERACTIVE_API_KEY="int_key_123"' in mock_print.call_args[0][0]


class TestBuildParser:
    """Test argument parser construction."""

    def test_parser_has_store_command(self):
        """Parser includes 'store' subcommand."""
        parser = build_parser()
        args = parser.parse_args(["store"])
        assert args.command == "store"

    def test_parser_has_export_command(self):
        """Parser includes 'export' subcommand."""
        parser = build_parser()
        args = parser.parse_args(["export"])
        assert args.command == "export"
        assert args.format == "env"  # Default format

    def test_parser_export_json_format(self):
        """Parser accepts JSON format for export."""
        parser = build_parser()
        args = parser.parse_args(["export", "--format", "json"])
        assert args.command == "export"
        assert args.format == "json"

    def test_parser_requires_command(self):
        """Parser requires a command."""
        parser = build_parser()
        with pytest.raises(SystemExit):
            parser.parse_args([])


class TestMain:
    """Test main entry point."""

    @patch("scripts.jainam_keyring_helper.store_credentials")
    def test_main_store_command(self, mock_store):
        """Main executes store command."""
        exit_code = main(["store"])
        assert exit_code == 0
        mock_store.assert_called_once()

    @patch("scripts.jainam_keyring_helper.export_credentials")
    def test_main_export_env_command(self, mock_export):
        """Main executes export command with env format."""
        exit_code = main(["export"])
        assert exit_code == 0
        mock_export.assert_called_once_with("env")

    @patch("scripts.jainam_keyring_helper.export_credentials")
    def test_main_export_json_command(self, mock_export):
        """Main executes export command with JSON format."""
        exit_code = main(["export", "--format", "json"])
        assert exit_code == 0
        mock_export.assert_called_once_with("json")

    @patch("scripts.jainam_keyring_helper.store_credentials")
    def test_main_with_argv_none(self, mock_store):
        """Main handles argv=None (uses sys.argv)."""
        with patch("sys.argv", ["script_name", "store"]):
            exit_code = main(None)
            assert exit_code == 0
            mock_store.assert_called_once()


class TestConstants:
    """Test module constants."""

    def test_service_name(self):
        """SERVICE constant is defined."""
        assert SERVICE == "openalgo:jainam"

    def test_fields_defined(self):
        """FIELDS contains all expected credential keys."""
        expected_keys = {
            "JAINAM_INTERACTIVE_API_KEY",
            "JAINAM_INTERACTIVE_API_SECRET",
            "JAINAM_MARKET_API_KEY",
            "JAINAM_MARKET_API_SECRET",
            "JAINAM_MARKET_API_USER_ID",
            "JAINAM_MARKET_API_APP_NAME",
            "JAINAM_MARKET_API_EXPIRY",
        }
        assert set(FIELDS.keys()) == expected_keys

    def test_fields_have_descriptions(self):
        """Each field has a human-readable description."""
        for key, description in FIELDS.items():
            assert isinstance(description, str)
            assert len(description) > 0
