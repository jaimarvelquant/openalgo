import os

DEFAULT_JAINAM_BASE_URL = "https://smpb.jainam.in:4143"


def get_jainam_base_url() -> str:
    """
    Return the Jainam API base URL, configurable via environment variable
    `JAINAM_BASE_URL`. Falls back to the known production endpoint if unset.
    """
    base_url = os.getenv("JAINAM_BASE_URL", DEFAULT_JAINAM_BASE_URL).strip()
    normalized = base_url.rstrip("/")

    # Jainam endpoints require HTTPS even on non-standard ports.
    if normalized.startswith("http://"):
        normalized = "https://" + normalized[len("http://") :]

    return normalized
