"""
Helpers for constructing broker authentication payloads that bundle
interactive (trading) and market-data tokens.
"""
from typing import Optional, Union, Dict


def build_broker_auth_payload(
    interactive_token: Optional[str],
    feed_token: Optional[str]
) -> Optional[Union[str, Dict[str, str]]]:
    """
    Combine the interactive session token and optional feed token into a single
    payload that downstream broker modules can consume.

    Returns the plain interactive token when no feed token is available so
    legacy code paths continue to operate unchanged. When a feed token is
    present, a dictionary is returned with both values under the most common
    key aliases used across the codebase.
    """
    if not interactive_token:
        # Without an interactive token we cannot call broker APIs, so signal
        # the caller to handle the missing credentials.
        return None

    if not feed_token:
        return interactive_token

    return {
        'token': interactive_token,
        # Provide common aliases so downstream helpers can extract the market
        # data credential without additional branching.
        'market_token': feed_token,
        'marketToken': feed_token,
        'marketAuthToken': feed_token,
        'feed_token': feed_token,
    }
