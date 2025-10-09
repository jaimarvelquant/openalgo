import os
from typing import Optional, Tuple

import httpx

from utils.logging import get_logger
from utils.httpx_client import get_httpx_client
from broker.jainam_prop.api.config import get_jainam_base_url

logger = get_logger(__name__)

SOURCE_HEADER_VALUE = "WEBAPI"


def _validate_credentials(
    *,
    require_interactive: bool = True,
    require_market: bool = True,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Validate Jainam credentials based on the requested requirements."""
    interactive_key = os.getenv("JAINAM_INTERACTIVE_API_KEY")
    interactive_secret = os.getenv("JAINAM_INTERACTIVE_API_SECRET")
    market_key = os.getenv("JAINAM_MARKET_API_KEY")
    market_secret = os.getenv("JAINAM_MARKET_API_SECRET")

    missing = [
        name
        for name, value, required in (
            ("JAINAM_INTERACTIVE_API_KEY", interactive_key, require_interactive),
            ("JAINAM_INTERACTIVE_API_SECRET", interactive_secret, require_interactive),
            ("JAINAM_MARKET_API_KEY", market_key, require_market),
            ("JAINAM_MARKET_API_SECRET", market_secret, require_market),
        )
        if required and not value
    ]

    if missing:
        joined = ", ".join(missing)
        raise ValueError(
            f"Missing required Jainam credentials: {joined}. "
            "Set these environment variables before attempting authentication."
        )

    return interactive_key, interactive_secret, market_key, market_secret


def _request_token(
    client: httpx.Client,
    url: str,
    payload: dict,
    context: str,
) -> Tuple[str, Optional[str], Optional[bool]]:
    """
    Execute a POST request to the Jainam API and return the token plus metadata.

    Returns:
        tuple: (token, user_id, is_investor_client)
    """
    headers = {"Content-Type": "application/json"}

    try:
        response = client.post(url, json=payload, headers=headers)
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        detail = _extract_error_detail(exc.response)
        raise RuntimeError(f"{context} authentication failed: {detail}") from exc
    except httpx.RequestError as exc:
        raise RuntimeError(f"{context} authentication network error: {exc}") from exc

    data = response.json()
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


def _login_market_data(
    client: httpx.Client,
    base_url: str,
    payload: dict,
) -> Tuple[str, Optional[str], Optional[bool]]:
    """
    Attempt to authenticate market data session, supporting endpoint variations.
    """
    endpoints = [
        f"{base_url}/apimarketdata/auth/login",
        f"{base_url}/marketdata/auth/login",
        f"{base_url}/apibinarymarketdata/auth/login",
    ]
    last_error: Optional[str] = None

    for url in endpoints:
        try:
            return _request_token(client, url, payload, "Market data")
        except RuntimeError as exc:
            last_error = str(exc)
            cause = getattr(exc, "__cause__", None)
            status_code = cause.response.status_code if isinstance(cause, httpx.HTTPStatusError) else None
            if status_code:
                logger.debug(
                    "Market data login attempt failed at %s (status=%s): %s",
                    url,
                    status_code,
                    last_error,
                )
            # Allow fallback when server indicates CTCL-only restriction (binary API required).
            if status_code == 400 and last_error and "only enabled for ctcl" in last_error.lower():
                continue
            # Only continue if the failure was a 404 (endpoint missing); otherwise surface immediately.
            if status_code != 404:
                break

    raise RuntimeError(last_error or "Market data authentication failed")


def authenticate_direct() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Authenticate with Jainam XTS using direct API key/secret login.

    Returns:
        tuple: (interactive_token, market_token, user_id, error_message)
    """
    try:
        interactive_key, interactive_secret, market_key, market_secret = _validate_credentials()
    except ValueError as exc:
        logger.error(str(exc))
        return None, None, None, str(exc)

    client = get_httpx_client()
    base_url = get_jainam_base_url()

    interactive_payload = {
        "appKey": interactive_key,
        "secretKey": interactive_secret,
        "source": SOURCE_HEADER_VALUE,
    }

    market_payload = {
        "appKey": market_key,
        "secretKey": market_secret,
        "source": SOURCE_HEADER_VALUE,
    }

    try:
        interactive_token, user_id, is_investor = _request_token(
            client,
            f"{base_url}/interactive/user/session",
            interactive_payload,
            "Interactive",
        )

        market_token, _, _ = _login_market_data(client, base_url, market_payload)

        logger.info(
            "Jainam direct authentication succeeded (user_id=%s, investor_client=%s)",
            user_id,
            bool(is_investor),
        )
        return interactive_token, market_token, user_id, None
    except Exception as exc:
        error_message = str(exc)
        logger.error("Jainam direct authentication failed: %s", error_message)
        return None, None, None, error_message


def authenticate_broker(*_args, **_kwargs):
    """
    Backwards-compatible wrapper to support plugin loader expectations.

    Returns:
        tuple: (interactive_token, market_token, user_id, error_message)
    """
    return authenticate_direct()


def authenticate_market_data():
    """
    Authenticate only the Jainam market data session.

    Returns:
        tuple: (market_token, error_message)
    """
    try:
        _, _, market_key, market_secret = _validate_credentials(require_interactive=False, require_market=True)
    except ValueError as exc:
        logger.error(str(exc))
        return None, str(exc)

    client = get_httpx_client()
    base_url = get_jainam_base_url()

    payload = {
        "appKey": market_key,
        "secretKey": market_secret,
        "source": SOURCE_HEADER_VALUE,
    }

    try:
        market_token, user_id, _ = _login_market_data(client, base_url, payload)
        logger.info("Jainam market data authentication succeeded (user_id=%s)", user_id)
        return market_token, None
    except Exception as exc:
        error_message = str(exc)
        logger.error("Jainam market data authentication failed: %s", error_message)
        return None, error_message
