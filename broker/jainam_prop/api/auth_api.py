import os
from typing import Optional, Tuple

import httpx

from utils.logging import get_logger
from utils.httpx_client import get_httpx_client
from broker.jainam_prop.api.config import get_jainam_base_url, get_jainam_credentials
from broker.jainam_prop.api.base_client import BaseAPIClient

logger = get_logger(__name__)

SOURCE_HEADER_VALUE = "WEBAPI"


# ============================================================================
# API Client Classes (Task 24.1 - Refactored to use BaseAPIClient)
# ============================================================================

class InteractiveAuthClient(BaseAPIClient):
    """Client for Interactive API authentication."""

    def login(self, api_key: str, api_secret: str, source: str = SOURCE_HEADER_VALUE) -> dict:
        """
        Authenticate with Interactive API.

        Args:
            api_key: Interactive API key
            api_secret: Interactive API secret
            source: API source (default: WEBAPI)

        Returns:
            Authentication response with token and user details

        Raises:
            httpx.HTTPStatusError: For HTTP error responses
        """
        payload = {
            "appKey": api_key,
            "secretKey": api_secret,
            "source": source
        }
        return self._post('user.login', json_data=payload, timeout=10.0)


class MarketDataAuthClient(BaseAPIClient):
    """Client for Market Data API authentication with endpoint fallback."""

    def login(self, api_key: str, api_secret: str, source: str = SOURCE_HEADER_VALUE) -> dict:
        """
        Authenticate with Market Data API.

        Tries multiple endpoints in order:
        1. Binary Market Data API (/apibinarymarketdata/) - Production
        2. Standard Market Data API (/apimarketdata/) - Fallback
        3. Simplified Market Data API (/marketdata/) - Legacy fallback

        Args:
            api_key: Market Data API key
            api_secret: Market Data API secret
            source: API source (default: WEBAPI)

        Returns:
            Authentication response with token

        Raises:
            RuntimeError: If all endpoints fail
        """
        payload = {
            "appKey": api_key,
            "secretKey": api_secret,
            "source": source
        }

        # Try binary endpoint first (production)
        try:
            return self._post('market.login', json_data=payload, timeout=10.0)
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code
            logger.debug(f"Binary market data login failed (status={status_code}), trying fallback...")

            # Only try fallback for 404 or 400 "ctcl only" errors
            if status_code == 404 or (status_code == 400 and "only enabled for ctcl" in exc.response.text.lower()):
                # Try standard market data API
                try:
                    return self._post('market.login', json_data=payload, timeout=10.0, use_standard_marketdata=True)
                except httpx.HTTPStatusError:
                    # If standard also fails, raise original error
                    raise exc
            else:
                # For other errors, raise immediately
                raise


def _validate_credentials(
    *,
    require_interactive: bool = True,
    require_market: bool = True,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Validate Jainam credentials based on the requested requirements."""
    try:
        (
            interactive_key,
            interactive_secret,
            market_key,
            market_secret,
            server,
            account_type,
            client_id,
        ) = get_jainam_credentials()
    except ValueError as exc:
        raise ValueError(str(exc)) from exc

    logger.debug(
        "Credential validation: server=%s account=%s clientID=%s \u2013 requirements: interactive=%s, market=%s",
        server,
        account_type,
        client_id,
        require_interactive,
        require_market,
    )

    if not require_interactive and require_market:
        return None, None, market_key, market_secret
    if require_interactive and not require_market:
        return interactive_key, interactive_secret, None, None

    return interactive_key, interactive_secret, market_key, market_secret


def _extract_token_from_response(
    data: dict,
    context: str,
) -> Tuple[str, Optional[str], Optional[bool]]:
    """
    Extract token and metadata from authentication response.

    Args:
        data: Response JSON data
        context: Context string for error messages (e.g., "Interactive", "Market data")

    Returns:
        tuple: (token, user_id, is_investor_client)

    Raises:
        RuntimeError: If response indicates failure or token is missing
    """
    if data.get("type") != "success":
        detail = data.get("description") or data.get("message") or str(data)
        raise RuntimeError(f"{context} authentication failed: {detail}")

    result = data.get("result", {})
    token = result.get("token")
    user_id = result.get("userID")
    is_investor = result.get("isInvestorClient")

    if not token:
        raise RuntimeError(f"{context} authentication succeeded but no token was returned by the API.")

    return token, user_id, is_investor


def _extract_error_detail(response: Optional[httpx.Response]) -> str:
    """Best-effort extraction of error details from Jainam responses."""
    if not response:
        return "Unknown error"

    try:
        body = response.json()
        return body.get("description") or body.get("message") or body.get("error", str(body))
    except Exception:  # pragma: no cover - defensive logging only
        return response.text or f"HTTP {response.status_code}"


# Removed _login_market_data - now handled by MarketDataAuthClient class


def authenticate_direct() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[bool], Optional[str], Optional[str]]:
    """
    Authenticate with Jainam XTS using direct API key/secret login.

    Returns:
        tuple: (interactive_token, market_token, user_id, is_investor_client, client_id, error_message)
    """
    try:
        (
            interactive_key,
            interactive_secret,
            market_key,
            market_secret,
            server,
            account_type,
            client_id,
        ) = get_jainam_credentials()
    except ValueError as exc:
        message = str(exc)
        logger.error(message)
        return None, None, None, None, None, message

    base_url = get_jainam_base_url()

    logger.info(
        "Authenticating Jainam account: server=%s account_type=%s clientID=%s",
        server,
        account_type,
        client_id,
    )

    interactive_token = market_token = user_id = None
    is_investor = None

    try:
        interactive_client = InteractiveAuthClient(base_url=base_url)
        interactive_response = interactive_client.login(interactive_key, interactive_secret)
        interactive_token, user_id, is_investor = _extract_token_from_response(
            interactive_response,
            "Interactive",
        )

        market_client = MarketDataAuthClient(base_url=base_url)
        market_response = market_client.login(market_key, market_secret)
        market_token, _, _ = _extract_token_from_response(market_response, "Market data")

        logger.info(
            "Jainam authentication successful: server=%s account=%s userID=%s clientID=%s investor=%s",
            server,
            account_type,
            user_id,
            client_id,
            bool(is_investor),
        )

        if is_investor:
            logger.warning(
                "isInvestorClient=True returned for %s account (clientID=%s); dealer accounts should report False",
                account_type,
                client_id,
            )

        return interactive_token, market_token, user_id, is_investor, client_id, None

    except Exception as exc:  # noqa: BLE001
        error_message = str(exc)
        logger.error(
            "Jainam authentication failed: server=%s account=%s clientID=%s error=%s",
            server,
            account_type,
            client_id,
            error_message,
        )
        return None, None, None, None, None, error_message


def authenticate_broker(*_args, **_kwargs):
    """
    Backwards-compatible wrapper to support plugin loader expectations.

    Returns:
        tuple: (interactive_token, market_token, user_id, is_investor_client, client_id, error_message)
    """
    return authenticate_direct()


def logout_broker(auth_token: str) -> dict:
    """
    Logout from Jainam XTS (both Interactive and Market Data sessions).

    Refactored to use BaseAPIClient (Task 24.1).

    Args:
        auth_token: JSON string containing both tokens:
                   {"interactive_token": "...", "market_token": "...", "user_id": "..."}

    Returns:
        dict: Logout results for both sessions
    """
    import json

    try:
        # Parse auth_token JSON
        tokens = json.loads(auth_token)
        interactive_token = tokens.get("interactive_token")
        market_token = tokens.get("market_token")
        user_id = tokens.get("user_id")

        base_url = get_jainam_base_url()
        results = {}

        # Logout from Interactive API
        if interactive_token:
            try:
                interactive_client = BaseAPIClient(base_url=base_url, auth_token=interactive_token)
                # Interactive logout is a DELETE request to user.logout
                interactive_response = interactive_client._delete('user.logout', params={'clientID': user_id} if user_id else {})
                results["interactive_logout"] = interactive_response
                logger.info("Interactive API logout successful")
            except Exception as exc:
                logger.error(f"Interactive API logout failed: {exc}")
                results["interactive_logout"] = {"error": str(exc)}
        else:
            results["interactive_logout"] = "No interactive token provided"

        # Logout from Market Data API
        if market_token:
            try:
                market_client = BaseAPIClient(base_url=base_url, auth_token=market_token)
                # Market data logout is a DELETE request to market.logout
                market_response = market_client._delete('market.logout', params={})
                results["market_logout"] = market_response
                logger.info("Market Data API logout successful")
            except Exception as exc:
                logger.error(f"Market Data API logout failed: {exc}")
                results["market_logout"] = {"error": str(exc)}
        else:
            results["market_logout"] = "No market token provided"

        return results

    except Exception as exc:
        logger.error(f"Logout failed: {exc}")
        return {"error": str(exc)}


def authenticate_market_data():
    """
    Authenticate only the Jainam market data session.

    Refactored to use BaseAPIClient (Task 24.1).

    Returns:
        tuple: (market_token, error_message)
    """
    try:
        _, _, market_key, market_secret = _validate_credentials(require_interactive=False, require_market=True)
    except ValueError as exc:
        logger.error(str(exc))
        return None, str(exc)

    base_url = get_jainam_base_url()

    try:
        # Authenticate Market Data API
        market_client = MarketDataAuthClient(base_url=base_url)
        market_response = market_client.login(market_key, market_secret)
        market_token, user_id, _ = _extract_token_from_response(market_response, "Market data")

        logger.info("Jainam market data authentication succeeded (user_id=%s)", user_id)
        return market_token, None
    except Exception as exc:
        error_message = str(exc)
        logger.error("Jainam market data authentication failed: %s", error_message)
        return None, error_message
