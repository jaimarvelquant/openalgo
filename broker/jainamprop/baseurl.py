"""Jainam Prop (XTS) broker base URLs configuration."""

import os

# Base URL for Jainam Prop API endpoints.
# Defaults to the SMPB host; can be overridden from environment.
BASE_URL = os.getenv("JAINAMPROP_BASE_URL", "https://smpb.jainam.in:4143").rstrip("/")

# Derived URLs for specific API endpoints
MARKET_DATA_URL = f"{BASE_URL}/apibinarymarketdata"
INTERACTIVE_URL = f"{BASE_URL}/interactive"
