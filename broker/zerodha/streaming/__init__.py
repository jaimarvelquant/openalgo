"""
Zerodha WebSocket streaming module for MarvelQuant.

This module provides WebSocket integration with Zerodha's market data streaming API,
following the MarvelQuant WebSocket proxy architecture.
"""

from .zerodha_adapter import ZerodhaWebSocketAdapter

__all__ = ['ZerodhaWebSocketAdapter']
