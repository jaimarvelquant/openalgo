"""Jainam API modules for authentication, orders, data, and funds"""

# Core infrastructure (Task 24.1)
from .routes import JAINAM_ROUTES, get_route, get_all_routes
from .base_client import BaseAPIClient

# API functions
from .auth_api import authenticate_broker, logout_broker
from .order_api import (
    place_order_api,
    place_smartorder_api,
    modify_order_api,
    cancel_order_api,
    # cancel_all_orders_api,  # Not implemented
    # close_all_positions_api,  # Not implemented
    get_order_book,
    get_trade_book,
    get_positions,
    get_holdings,
    get_open_position,
)
from .funds import get_margin_data

__all__ = [
    # Core infrastructure
    "JAINAM_ROUTES",
    "get_route",
    "get_all_routes",
    "BaseAPIClient",
    # API functions
    "authenticate_broker",
    "logout_broker",
    "place_order_api",
    "place_smartorder_api",
    "modify_order_api",
    "cancel_order_api",
    # "cancel_all_orders_api",  # Not implemented
    # "close_all_positions_api",  # Not implemented
    "get_order_book",
    "get_trade_book",
    "get_positions",
    "get_holdings",
    "get_open_position",
    "get_margin_data",
]
