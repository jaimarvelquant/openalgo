"""
Kotak WebSocket streaming integration for MarvelQuant.
Exposes the high-level adapter and core websocket client.
"""
from .kotak_adapter import KotakWebSocketAdapter
from .kotak_websocket import KotakWebSocket

__all__ = ["KotakWebSocketAdapter", "KotakWebSocket"]
