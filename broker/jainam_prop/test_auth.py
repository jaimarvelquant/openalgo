"""
Tests for Jainam Prop direct authentication helper functions.
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock, patch

import httpx

# Add project root for imports when running this module standalone
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from broker.jainam_prop.api.auth_api import authenticate_direct, authenticate_market_data


class TestJainamDirectAuthentication(unittest.TestCase):
    """Unit tests covering Jainam direct login workflow."""

    def test_authenticate_direct_missing_interactive_key(self):
        """Direct login should return an actionable error when API key is missing."""
        with patch.dict(
            os.environ,
            {
                "JAINAM_INTERACTIVE_API_KEY": "",
                "JAINAM_INTERACTIVE_API_SECRET": "secret",
                "JAINAM_MARKET_API_KEY": "market_key",
                "JAINAM_MARKET_API_SECRET": "market_secret",
            },
            clear=True,
        ):
            auth_token, feed_token, user_id, error = authenticate_direct()

            self.assertIsNone(auth_token)
            self.assertIsNone(feed_token)
            self.assertIsNone(user_id)
            self.assertIsNotNone(error)
            self.assertIn("JAINAM_INTERACTIVE_API_KEY", error)

    def test_authenticate_direct_missing_interactive_secret(self):
        """Missing interactive secret should surface a descriptive error."""
        with patch.dict(
            os.environ,
            {
                "JAINAM_INTERACTIVE_API_KEY": "key",
                "JAINAM_INTERACTIVE_API_SECRET": "",
                "JAINAM_MARKET_API_KEY": "market_key",
                "JAINAM_MARKET_API_SECRET": "market_secret",
            },
            clear=True,
        ):
            auth_token, feed_token, user_id, error = authenticate_direct()

            self.assertIsNone(auth_token)
            self.assertIsNone(feed_token)
            self.assertIsNone(user_id)
            self.assertIsNotNone(error)
            self.assertIn("JAINAM_INTERACTIVE_API_SECRET", error)

    def test_authenticate_market_data_missing_key(self):
        """Market data login should return an error when API key is absent."""
        with patch.dict(
            os.environ,
            {
                "JAINAM_INTERACTIVE_API_KEY": "key",
                "JAINAM_INTERACTIVE_API_SECRET": "secret",
                "JAINAM_MARKET_API_KEY": "",
                "JAINAM_MARKET_API_SECRET": "market_secret",
            },
            clear=True,
        ):
            market_token, error = authenticate_market_data()

            self.assertIsNone(market_token)
            self.assertIsNotNone(error)
            self.assertIn("JAINAM_MARKET_API_KEY", error)

    def test_authenticate_market_data_missing_secret(self):
        """Market data login should return an error when API secret is absent."""
        with patch.dict(
            os.environ,
            {
                "JAINAM_INTERACTIVE_API_KEY": "key",
                "JAINAM_INTERACTIVE_API_SECRET": "secret",
                "JAINAM_MARKET_API_KEY": "market_key",
                "JAINAM_MARKET_API_SECRET": "",
            },
            clear=True,
        ):
            market_token, error = authenticate_market_data()

            self.assertIsNone(market_token)
            self.assertIsNotNone(error)
            self.assertIn("JAINAM_MARKET_API_SECRET", error)

    @patch("broker.jainam_prop.api.auth_api.get_httpx_client")
    def test_error_response_does_not_expose_credentials(self, mock_get_client):
        """API error responses should not leak the provided credentials."""
        mock_client = MagicMock()
        error_response = Mock()
        error_response.status_code = 200
        error_response.json.return_value = {"type": "error", "description": "Invalid credentials"}
        error_response.raise_for_status = Mock()
        mock_client.post.return_value = error_response
        mock_get_client.return_value = mock_client

        secret_key = "super_secret_value"
        with patch.dict(
            os.environ,
            {
                "JAINAM_INTERACTIVE_API_KEY": "key",
                "JAINAM_INTERACTIVE_API_SECRET": secret_key,
                "JAINAM_MARKET_API_KEY": "market_key",
                "JAINAM_MARKET_API_SECRET": "market_secret",
            },
            clear=True,
        ):
            _, _, _, error = authenticate_direct()

        self.assertIsNotNone(error)
        self.assertNotIn(secret_key, error)
        self.assertIn("Invalid credentials", error)

    @patch("broker.jainam_prop.api.auth_api.get_httpx_client")
    def test_successful_authentication_returns_tokens(self, mock_get_client):
        """Happy path should return both tokens and user identifier."""
        interactive_response = Mock()
        interactive_response.status_code = 200
        interactive_response.json.return_value = {
            "type": "success",
            "result": {
                "token": "interactive-token",
                "userID": "JAINAM123",
                "isInvestorClient": False,
            },
        }
        interactive_response.raise_for_status = Mock()

        market_response = Mock()
        market_response.status_code = 200
        market_response.json.return_value = {
            "type": "success",
            "result": {
                "token": "market-token",
            },
        }
        market_response.raise_for_status = Mock()

        mock_get_client.return_value = MagicMock(post=MagicMock(side_effect=[interactive_response, market_response]))

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
        self.assertEqual(user_id, "JAINAM123")
        self.assertIsNone(error)

    @patch("broker.jainam_prop.api.auth_api.get_httpx_client")
    def test_market_login_fallback_handles_not_found(self, mock_get_client):
        """If the primary market endpoint is missing, fallback endpoint should be attempted."""
        interactive_response = Mock()
        interactive_response.status_code = 200
        interactive_response.json.return_value = {
            "type": "success",
            "result": {"token": "interactive-token", "userID": "JAINAM123"},
        }
        interactive_response.raise_for_status = Mock()

        def make_not_found(url: str):
            request = httpx.Request("POST", url)
            response = httpx.Response(404, request=request)

            def raiser():
                raise httpx.HTTPStatusError("Not found", request=request, response=response)

            failing_response = Mock()
            failing_response.raise_for_status = Mock(side_effect=raiser)
            return failing_response

        first_market_response = make_not_found("https://example.com/apimarketdata/auth/login")
        second_market_response = make_not_found("https://example.com/marketdata/auth/login")

        fallback_market_response = Mock()
        fallback_market_response.status_code = 200
        fallback_market_response.json.return_value = {
            "type": "success",
            "result": {"token": "market-token"},
        }
        fallback_market_response.raise_for_status = Mock()

        mock_get_client.return_value = MagicMock(
            post=MagicMock(
                side_effect=[
                    interactive_response,
                    first_market_response,
                    second_market_response,
                    fallback_market_response,
                ]
            )
        )

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
        self.assertEqual(user_id, "JAINAM123")
        self.assertIsNone(error)


def run_tests():
    """Helper to run tests directly."""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestJainamDirectAuthentication)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":  # pragma: no cover
    success = run_tests()
    sys.exit(0 if success else 1)
