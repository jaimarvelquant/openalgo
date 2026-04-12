"""
Isolated credential validation tests for Jainam Prop direct authentication.

These tests execute without requiring the wider MarvelQuant environment by
mocking the minimal dependencies required by auth_api.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

# Stub dependencies before importing the module under test.
sys.modules.setdefault("database", MagicMock())
sys.modules.setdefault("database.auth_db", MagicMock())
sys.modules["utils"] = MagicMock()

mock_logging = MagicMock()
mock_logging.get_logger.return_value = MagicMock()
sys.modules["utils.logging"] = mock_logging

mock_httpx_client_module = MagicMock()
sys.modules["utils.httpx_client"] = mock_httpx_client_module

# Dynamically import auth_api after stubbing dependencies.
import importlib.util

spec = importlib.util.spec_from_file_location(
    "auth_api",
    os.path.join(os.path.dirname(__file__), "api", "auth_api.py"),
)
auth_api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(auth_api)

authenticate_direct = auth_api.authenticate_direct
authenticate_market_data = auth_api.authenticate_market_data


class TestJainamAuthIsolated(unittest.TestCase):
    """Tests targeting credential validation and error handling."""

    def test_authenticate_direct_missing_credentials(self):
        """Missing credentials should produce actionable error messages."""
        with patch.dict(
            os.environ,
            {
                "JAINAM_INTERACTIVE_API_KEY": "",
                "JAINAM_INTERACTIVE_API_SECRET": "",
                "JAINAM_MARKET_API_KEY": "",
                "JAINAM_MARKET_API_SECRET": "",
            },
            clear=True,
        ):
            auth_token, feed_token, user_id, error = authenticate_direct()

        self.assertIsNone(auth_token)
        self.assertIsNone(feed_token)
        self.assertIsNone(user_id)
        self.assertIsNotNone(error)
        self.assertIn("JAINAM_INTERACTIVE_API_KEY", error)

    def test_authenticate_market_data_missing_credentials(self):
        """Market data helper should surface errors for missing credentials."""
        with patch.dict(
            os.environ,
            {
                "JAINAM_INTERACTIVE_API_KEY": "key",
                "JAINAM_INTERACTIVE_API_SECRET": "secret",
                "JAINAM_MARKET_API_KEY": "",
                "JAINAM_MARKET_API_SECRET": "",
            },
            clear=True,
        ):
            market_token, error = authenticate_market_data()

        self.assertIsNone(market_token)
        self.assertIsNotNone(error)
        self.assertIn("JAINAM_MARKET_API_KEY", error)

    def test_error_flow_masks_credentials(self):
        """Failure responses must not expose secrets."""
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"type": "error", "description": "Bad credentials"}
        mock_response.raise_for_status = Mock()
        mock_client.post.return_value = mock_response
        secret = "super_secret"
        with patch.object(auth_api, "get_httpx_client", return_value=mock_client):
            with patch.dict(
                os.environ,
                {
                    "JAINAM_INTERACTIVE_API_KEY": "key",
                    "JAINAM_INTERACTIVE_API_SECRET": secret,
                    "JAINAM_MARKET_API_KEY": "market_key",
                    "JAINAM_MARKET_API_SECRET": "market_secret",
                },
                clear=True,
            ):
                _, _, _, error = authenticate_direct()

        self.assertIn("Bad credentials", error)
        self.assertNotIn(secret, error)

    def test_successful_login_returns_tokens(self):
        """Successful flow returns interactive token, market token, and user id."""
        interactive_response = Mock()
        interactive_response.status_code = 200
        interactive_response.json.return_value = {
            "type": "success",
            "result": {"token": "interactive-token", "userID": "ID001"},
        }
        interactive_response.raise_for_status = Mock()

        market_response = Mock()
        market_response.status_code = 200
        market_response.json.return_value = {
            "type": "success",
            "result": {"token": "market-token"},
        }
        market_response.raise_for_status = Mock()

        mock_client = MagicMock(post=MagicMock(side_effect=[interactive_response, market_response]))

        with patch.object(auth_api, "get_httpx_client", return_value=mock_client):
            with patch.dict(
                os.environ,
                {
                    "JAINAM_INTERACTIVE_API_KEY": "key",
                    "JAINAM_INTERACTIVE_API_SECRET": "secret",
                    "JAINAM_MARKET_API_KEY": "market_key",
                    "JAINAM_MARKET_API_SECRET": "market_secret",
                },
                clear=True,
            ):
                auth_token, feed_token, user_id, error = authenticate_direct()

        self.assertEqual(auth_token, "interactive-token")
        self.assertEqual(feed_token, "market-token")
        self.assertEqual(user_id, "ID001")
        self.assertIsNone(error)


if __name__ == "__main__":  # pragma: no cover
    unittest.main(verbosity=2)
