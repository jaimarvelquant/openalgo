import os
from typing import Tuple

from utils.logging import get_logger

logger = get_logger(__name__)

# Symphony server URL mapping derived from Jainam documentation
SYMPHONY_SERVERS = {
    "A": "https://smpa.jainam.in:6543",
    "B": "https://smpb.jainam.in:4143",
    "C": "https://smpc.jainam.in:14543",
}

DEFAULT_SYMPHONY_SERVER = "B"
DEFAULT_ACCOUNT_TYPE = "PRO"

LEGACY_ENV_VARS = (
    "JAINAM_INTERACTIVE_API_KEY",
    "JAINAM_INTERACTIVE_API_SECRET",
    "JAINAM_MARKET_API_KEY",
    "JAINAM_MARKET_API_SECRET",
    "JAINAM_BASE_URL",
)


def _read_env(name: str, default: str | None = None) -> str | None:
    """Return environment variable stripped of whitespace or None if unset."""
    value = os.getenv(name, default)
    if value is None:
        return None
    stripped = value.strip().strip("\"'")
    return stripped or None


def _log_legacy_warnings() -> None:
    legacy_present = [name for name in LEGACY_ENV_VARS if os.getenv(name)]
    if legacy_present:
        logger.warning(
            "Legacy Jainam environment variables detected (%s). "
            "Please migrate to JAINAM_SYMPHONY_* variables as described in the docs.",
            ", ".join(sorted(legacy_present)),
        )


def get_jainam_base_url() -> str:
    """Return the base URL for the active Jainam Symphony server."""
    server = (_read_env("JAINAM_ACTIVE_SYMPHONY_SERVER", DEFAULT_SYMPHONY_SERVER) or "").upper()
    if server not in SYMPHONY_SERVERS:
        raise ValueError(
            f"Invalid Symphony server '{server}'. Supported values: {', '.join(SYMPHONY_SERVERS)}"
        )

    url = SYMPHONY_SERVERS[server].rstrip("/")
    logger.debug("Using Jainam Symphony server %s (%s)", server, url)
    return url


def get_jainam_credentials() -> Tuple[str, str, str, str, str, str, str]:
    """
    Load Jainam credentials for the active Symphony server/account combination.

    Returns a tuple containing:
        interactive_key, interactive_secret,
        market_key, market_secret,
        server, account_type, client_id

    Raises:
        ValueError: when configuration is invalid or required values are missing.
    """
    _log_legacy_warnings()

    server = (_read_env("JAINAM_ACTIVE_SYMPHONY_SERVER", DEFAULT_SYMPHONY_SERVER) or "").upper()
    if server not in SYMPHONY_SERVERS:
        raise ValueError(
            f"Invalid Symphony server '{server}'. Supported values: {', '.join(SYMPHONY_SERVERS)}"
        )

    account_type = (_read_env("JAINAM_ACTIVE_ACCOUNT_TYPE", DEFAULT_ACCOUNT_TYPE) or "").upper()
    if account_type not in {"PRO", "NORMAL"}:
        raise ValueError("Invalid Jainam account type '{account_type}'. Supported values: PRO, NORMAL")

    prefix = f"JAINAM_SYMPHONY_{server}_{account_type}"
    env_keys = {
        "interactive_key": f"{prefix}_INTERACTIVE_API_KEY",
        "interactive_secret": f"{prefix}_INTERACTIVE_API_SECRET",
        "market_key": f"{prefix}_MARKET_API_KEY",
        "market_secret": f"{prefix}_MARKET_API_SECRET",
        "client_id": f"{prefix}_CLIENT_ID",
    }

    values = {name: _read_env(env_name) for name, env_name in env_keys.items()}
    missing = [env_keys[name] for name, value in values.items() if not value]
    if missing:
        raise ValueError(
            "Missing Jainam credentials for Symphony {server} {account_type} account.\n"
            "Set the following environment variables:\n  " + "\n  ".join(missing)
        )

    expected_client_id = "ZZJ13048" if account_type == "PRO" else "DLL7182"
    client_id = values["client_id"]

    logger.info(
        "Loaded Jainam credentials for Symphony %s (%s account, clientID=%s)",
        server,
        account_type,
        client_id,
    )
    if client_id != expected_client_id:
        logger.warning(
            "Configured clientID '%s' differs from expected '%s' for %s accounts.",
            client_id,
            expected_client_id,
            account_type,
        )

    return (
        values["interactive_key"],
        values["interactive_secret"],
        values["market_key"],
        values["market_secret"],
        server,
        account_type,
        client_id,
    )
