"""
Isolated credential validation tests for Jainam Prop broker integration
This test validates that:
1. Missing credentials raise appropriate ValueError
2. Credential validation messages are descriptive
3. No credentials are exposed in error messages
4. Tests run without requiring full OpenAlgo environment
"""

import os
import sys
import unittest
from unittest.mock import patch, Mock, MagicMock, mock_open

# Mock database dependencies before importing auth_api
sys.modules['database'] = MagicMock()
sys.modules['database.auth_db'] = MagicMock()
sys.modules['utils'] = MagicMock()
sys.modules['utils.logging'] = MagicMock()
sys.modules['utils.httpx_client'] = MagicMock()

# Now safe to import
import importlib.util
spec = importlib.util.spec_from_file_location(
    "auth_api",
    os.path.join(os.path.dirname(__file__), 'api', 'auth_api.py')
)
auth_api = importlib.util.module_from_spec(spec)

# Mock logger before executing module
auth_api.logger = MagicMock()

# Execute the module
spec.loader.exec_module(auth_api)

authenticate_broker = auth_api.authenticate_broker
authenticate_market_data = auth_api.authenticate_market_data


class TestJainamCredentialValidation(unittest.TestCase):
    """Test cases for Jainam credential validation"""

    def test_authenticate_broker_missing_api_key(self):
        """Test that missing JAINAM_INTERACTIVE_API_KEY raises ValueError"""
        with patch.dict(os.environ, {
            'JAINAM_INTERACTIVE_API_SECRET': 'test_secret',
            'JAINAM_INTERACTIVE_API_KEY': ''
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                authenticate_broker('test_request_token')

            error_message = str(context.exception)
            self.assertIn('JAINAM_INTERACTIVE_API_KEY', error_message)
            self.assertIn('not set', error_message)

    def test_authenticate_broker_missing_api_secret(self):
        """Test that missing JAINAM_INTERACTIVE_API_SECRET raises ValueError"""
        with patch.dict(os.environ, {
            'JAINAM_INTERACTIVE_API_KEY': 'test_key',
            'JAINAM_INTERACTIVE_API_SECRET': ''
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                authenticate_broker('test_request_token')

            error_message = str(context.exception)
            self.assertIn('JAINAM_INTERACTIVE_API_SECRET', error_message)
            self.assertIn('not set', error_message)

    def test_authenticate_market_data_missing_api_key(self):
        """Test that missing JAINAM_MARKET_API_KEY raises ValueError"""
        with patch.dict(os.environ, {
            'JAINAM_MARKET_API_SECRET': 'test_secret',
            'JAINAM_MARKET_API_KEY': ''
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                authenticate_market_data()

            error_message = str(context.exception)
            self.assertIn('JAINAM_MARKET_API_KEY', error_message)
            self.assertIn('not set', error_message)

    def test_authenticate_market_data_missing_api_secret(self):
        """Test that missing JAINAM_MARKET_API_SECRET raises ValueError"""
        with patch.dict(os.environ, {
            'JAINAM_MARKET_API_KEY': 'test_key',
            'JAINAM_MARKET_API_SECRET': ''
        }, clear=True):
            with self.assertRaises(ValueError) as context:
                authenticate_market_data()

            error_message = str(context.exception)
            self.assertIn('JAINAM_MARKET_API_SECRET', error_message)
            self.assertIn('not set', error_message)

    def test_error_messages_dont_expose_credentials(self):
        """Test that error messages don't expose actual credential values"""
        test_key = 'super_secret_key_123'
        test_secret = 'super_secret_value_456'

        # Mock HTTP client to avoid real network calls
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {'message': 'Invalid credentials'}
        mock_response.raise_for_status.side_effect = Exception("Authentication failed")
        mock_client.post.return_value = mock_response

        with patch.object(auth_api, 'get_httpx_client', return_value=mock_client):
            with patch.dict(os.environ, {
                'JAINAM_INTERACTIVE_API_KEY': test_key,
                'JAINAM_INTERACTIVE_API_SECRET': test_secret
            }, clear=True):
                # This will fail with API error, but should not expose credentials
                _, error = authenticate_broker('invalid_token')
                if error:
                    # Ensure actual credential values are NOT in error message
                    self.assertNotIn(test_key, error)
                    self.assertNotIn(test_secret, error)

    def test_all_credentials_none(self):
        """Test that all missing credentials are properly validated"""
        with patch.dict(os.environ, {}, clear=True):
            # Both functions should raise ValueError for missing credentials
            with self.assertRaises(ValueError) as context1:
                authenticate_broker('test_token')

            with self.assertRaises(ValueError) as context2:
                authenticate_market_data()

            # Both should mention the missing credential
            self.assertIn('JAINAM_INTERACTIVE_API_KEY', str(context1.exception))
            self.assertIn('JAINAM_MARKET_API_KEY', str(context2.exception))

    def test_successful_authentication_with_valid_credentials(self):
        """Test successful authentication flow with mocked HTTP client"""
        # Mock successful HTTP response
        mock_client = MagicMock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'data': {
                'access_token': 'mock_access_token_xyz'
            }
        }
        mock_response.raise_for_status = Mock()  # No exception
        mock_client.post.return_value = mock_response

        with patch.object(auth_api, 'get_httpx_client', return_value=mock_client):
            with patch.dict(os.environ, {
                'JAINAM_INTERACTIVE_API_KEY': 'valid_key',
                'JAINAM_INTERACTIVE_API_SECRET': 'valid_secret'
            }, clear=True):
                access_token, error = authenticate_broker('valid_request_token')

                # Verify success
                self.assertIsNone(error)
                self.assertEqual(access_token, 'mock_access_token_xyz')

    def test_value_error_propagates_for_fast_fail(self):
        """Test that ValueError propagates immediately (AC2 requirement)"""
        with patch.dict(os.environ, {}, clear=True):
            # ValueError should propagate, not be caught and returned as error tuple
            try:
                authenticate_broker('token')
                self.fail("Expected ValueError to be raised")
            except ValueError as e:
                # This is correct behavior - exception propagates for fast fail
                self.assertIn('JAINAM_INTERACTIVE_API_KEY', str(e))


def run_tests():
    """Run all test cases"""
    print("\n" + "="*70)
    print("Running Isolated Jainam Prop Credential Validation Tests")
    print("="*70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestJainamCredentialValidation)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success: {result.wasSuccessful()}")
    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
