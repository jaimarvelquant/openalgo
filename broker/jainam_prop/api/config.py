import os

DEFAULT_JAINAM_BASE_URL = "https://smpb.jainam.in:4143"


def get_jainam_base_url() -> str:
    """
    Return the Jainam API base URL, configurable via environment variable
    `JAINAM_BASE_URL`. Falls back to the known production endpoint if unset.
    """
    base_url = os.getenv("JAINAM_BASE_URL", DEFAULT_JAINAM_BASE_URL).strip()
    normalized = base_url.rstrip("/")

    # CRITICAL FIX: Do NOT force HTTPS - respect the protocol in the URL
    # The server may require HTTP or HTTPS depending on configuration
    # User has confirmed base URL is: http://smpb.jainam.in:4143

    return normalized
