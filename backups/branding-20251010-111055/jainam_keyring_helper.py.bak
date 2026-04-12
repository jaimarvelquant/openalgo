#!/usr/bin/env python3
"""
Utility helpers for storing and retrieving Jainam Prop API credentials in the
system keyring. This prevents tokens from being committed to the repository or
written to disk in plain text while still making them easy to load for live
validation scripts.

Usage examples:

    # Store credentials interactively (prompts, input hidden)
    python -m scripts.jainam_keyring_helper store

    # Emit shell exports for the currently stored credentials
    python -m scripts.jainam_keyring_helper export --format env

    # Load credentials as JSON payload for scripts
    python -m scripts.jainam_keyring_helper export --format json
"""

from __future__ import annotations

import argparse
import getpass
import json
import sys
from typing import Dict, Iterable

try:
    import keyring
except ImportError as exc:  # pragma: no cover - guarded import
    raise SystemExit(
        "The 'keyring' package is required. Install it inside your virtualenv with "
        "`python -m pip install keyring` before using this helper."
    ) from exc


SERVICE = "openalgo:jainam"
FIELDS = {
    "JAINAM_INTERACTIVE_API_KEY": "Interactive API key",
    "JAINAM_INTERACTIVE_API_SECRET": "Interactive API secret",
    "JAINAM_MARKET_API_KEY": "Market data API key",
    "JAINAM_MARKET_API_SECRET": "Market data API secret",
    "JAINAM_MARKET_API_USER_ID": "Market data user ID (optional)",
    "JAINAM_MARKET_API_APP_NAME": "Market data app name (optional)",
    "JAINAM_MARKET_API_EXPIRY": "Market token expiry (optional, YYYY-MM-DD)",
}


def store_credentials(fields: Iterable[str] = FIELDS.keys()) -> None:
    """Prompt for each credential and store it securely in the keyring."""
    print("Securely storing Jainam credentials in the system keyring...")
    for env_var in fields:
        prompt = FIELDS.get(env_var, env_var)
        value = getpass.getpass(f"{prompt}: ").strip()
        if not value:
            print(f"- Skipping {env_var} (left blank)")
            continue
        keyring.set_password(SERVICE, env_var, value)
        print(f"- Saved {env_var}")


def export_credentials(fmt: str) -> None:
    """Emit credentials from keyring in the requested format."""
    data: Dict[str, str] = {}
    for env_var in FIELDS:
        value = keyring.get_password(SERVICE, env_var)
        if value:
            data[env_var] = value

    if not data:
        raise SystemExit("No Jainam credentials found in keyring. Run the 'store' command first.")

    if fmt == "env":
        for key, value in data.items():
            print(f'export {key}="{value}"')
    elif fmt == "json":
        print(json.dumps(data, indent=2))
    else:  # pragma: no cover - argparse validation protects this
        raise ValueError(f"Unsupported format: {fmt}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Store or retrieve Jainam Prop API credentials via the system keyring."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("store", help="Interactively store Jainam credentials in the keyring")

    export_parser = subparsers.add_parser(
        "export", help="Retrieve credentials and print them as shell exports or JSON"
    )
    export_parser.add_argument(
        "--format",
        choices=("env", "json"),
        default="env",
        help="Output format (default: env exports suitable for `source <(…)`)",
    )

    return parser


def main(argv: Iterable[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.command == "store":
        store_credentials()
        return 0
    if args.command == "export":
        export_credentials(args.format)
        return 0

    parser.error("No command provided")
    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
