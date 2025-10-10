"""
Centralized route definitions for Jainam XTS API endpoints.

Based on:
- Reference: _sample_strategy/xts_connect.py lines 322-378
- Official SDK: _sample_strategy/xts_PRO_SDK/Connect.py lines 83-139

IMPORTANT: Production uses Binary Market Data API (/apibinarymarketdata/)
not standard Market Data API (/apimarketdata/)

This was discovered during Phase 1 (Task 18) when the standard endpoint
returned HTTP 404 errors. The binary endpoint works correctly on production
server (https://smpb.jainam.in:4143).
"""

# Main route dictionary for Jainam XTS API
JAINAM_ROUTES = {
    # ========================================================================
    # Interactive API Endpoints
    # ========================================================================
    
    "interactive.prefix": "interactive",
    
    # Authentication
    # CRITICAL FIX: Endpoint is /user/session NOT /interactive/user/session
    # Reference: Hostlookup_B.pdf shows endpoint as "/user/session"
    # But we need to check if base URL includes /interactive or not
    # For now, trying /user/session (without /interactive prefix)
    "user.login": "/user/session",
    "user.logout": "/user/session",
    "user.profile": "/interactive/user/profile",
    "user.balance": "/interactive/user/balance",
    
    # Order Management
    "orders": "/interactive/orders",
    "order.place": "/interactive/orders",
    "order.modify": "/interactive/orders",
    "order.cancel": "/interactive/orders",
    "order.cancelall": "/interactive/orders/cancelall",
    "order.history": "/interactive/orders",
    "order.status": "/interactive/orders",
    
    # Trade Management
    "trades": "/interactive/orders/trades",
    
    # Bracket Orders
    "bracketorder.place": "/interactive/orders/bracket",
    "bracketorder.modify": "/interactive/orders/bracket",
    "bracketorder.cancel": "/interactive/orders/bracket",
    
    # Cover Orders
    "order.place.cover": "/interactive/orders/cover",
    "order.exit.cover": "/interactive/orders/cover",
    
    # Portfolio Management
    "portfolio.positions": "/interactive/portfolio/positions",
    "portfolio.holdings": "/interactive/portfolio/holdings",
    "portfolio.positions.convert": "/interactive/portfolio/positions/convert",
    "portfolio.squareoff": "/interactive/portfolio/squareoff",
    
    # Dealer-Specific Endpoints (Professional/Dealer API)
    # These endpoints require dealer/professional account access
    "portfolio.dealerpositions": "/interactive/portfolio/dealerpositions",
    "order.dealer.status": "/interactive/orders/dealerorderbook",
    "dealer.trades": "/interactive/orders/dealertradebook",
    
    # ========================================================================
    # Binary Market Data API Endpoints (Production)
    # ========================================================================
    # IMPORTANT: Use /apibinarymarketdata/ not /apimarketdata/
    # This is the correct endpoint for production server (smpb.jainam.in:4143)
    
    "marketdata.prefix": "apibinarymarketdata",
    
    # Authentication
    "market.login": "/apibinarymarketdata/auth/login",
    "market.logout": "/apibinarymarketdata/auth/logout",
    
    # Configuration
    "market.config": "/apibinarymarketdata/config/clientConfig",
    
    # Instruments
    "market.instruments.master": "/apibinarymarketdata/instruments/master",
    "market.instruments.subscription": "/apibinarymarketdata/instruments/subscription",
    "market.instruments.unsubscription": "/apibinarymarketdata/instruments/subscription",
    "market.instruments.ohlc": "/apibinarymarketdata/instruments/ohlc",
    "market.instruments.indexlist": "/apibinarymarketdata/instruments/indexlist",
    "market.instruments.quotes": "/apibinarymarketdata/instruments/quotes",
    
    # Search
    "market.search.instrumentsbyid": "/apibinarymarketdata/search/instrumentsbyid",
    "market.search.instrumentsbystring": "/apibinarymarketdata/search/instruments",
    
    # Instrument Details
    "market.instruments.instrument.series": "/apibinarymarketdata/instruments/instrument/series",
    "market.instruments.instrument.equitysymbol": "/apibinarymarketdata/instruments/instrument/symbol",
    "market.instruments.instrument.futuresymbol": "/apibinarymarketdata/instruments/instrument/futureSymbol",
    "market.instruments.instrument.optionsymbol": "/apibinarymarketdata/instruments/instrument/optionsymbol",
    "market.instruments.instrument.optiontype": "/apibinarymarketdata/instruments/instrument/optionType",
    "market.instruments.instrument.expirydate": "/apibinarymarketdata/instruments/instrument/expiryDate",
}

# Fallback routes for standard Market Data API (for testing/development)
# These may not work on production server but can be used for testing
JAINAM_ROUTES_STANDARD_MARKETDATA = {
    "marketdata.prefix": "apimarketdata",
    "market.login": "/apimarketdata/auth/login",
    "market.logout": "/apimarketdata/auth/logout",
    "market.config": "/apimarketdata/config/clientConfig",
    "market.instruments.master": "/apimarketdata/instruments/master",
    "market.instruments.subscription": "/apimarketdata/instruments/subscription",
    "market.instruments.unsubscription": "/apimarketdata/instruments/subscription",
    "market.instruments.ohlc": "/apimarketdata/instruments/ohlc",
    "market.instruments.indexlist": "/apimarketdata/instruments/indexlist",
    "market.instruments.quotes": "/apimarketdata/instruments/quotes",
    "market.search.instrumentsbyid": "/apimarketdata/search/instrumentsbyid",
    "market.search.instrumentsbystring": "/apimarketdata/search/instruments",
    "market.instruments.instrument.series": "/apimarketdata/instruments/instrument/series",
    "market.instruments.instrument.equitysymbol": "/apimarketdata/instruments/instrument/symbol",
    "market.instruments.instrument.futuresymbol": "/apimarketdata/instruments/instrument/futureSymbol",
    "market.instruments.instrument.optionsymbol": "/apimarketdata/instruments/instrument/optionsymbol",
    "market.instruments.instrument.optiontype": "/apimarketdata/instruments/instrument/optionType",
    "market.instruments.instrument.expirydate": "/apimarketdata/instruments/instrument/expiryDate",
}


def get_route(route_key: str, use_standard_marketdata: bool = False) -> str:
    """
    Get API route by key with validation.
    
    Args:
        route_key: Route key (e.g., 'user.login', 'order.place', 'market.instruments.master')
        use_standard_marketdata: If True, use standard market data routes instead of binary
                                 (default: False - use binary market data routes)
    
    Returns:
        Route path (e.g., '/interactive/user/session', '/apibinarymarketdata/instruments/master')
    
    Raises:
        KeyError: If route_key not found in route dictionary
    
    Examples:
        >>> get_route('user.login')
        '/interactive/user/session'
        
        >>> get_route('market.instruments.master')
        '/apibinarymarketdata/instruments/master'
        
        >>> get_route('market.instruments.master', use_standard_marketdata=True)
        '/apimarketdata/instruments/master'
    """
    # For market data routes, check if we should use standard API
    if use_standard_marketdata and route_key.startswith('market.'):
        if route_key in JAINAM_ROUTES_STANDARD_MARKETDATA:
            return JAINAM_ROUTES_STANDARD_MARKETDATA[route_key]
    
    # Use main routes dictionary
    if route_key not in JAINAM_ROUTES:
        raise KeyError(
            f"Route '{route_key}' not found in JAINAM_ROUTES. "
            f"Available routes: {', '.join(sorted(JAINAM_ROUTES.keys()))}"
        )
    
    return JAINAM_ROUTES[route_key]


def get_all_routes() -> dict:
    """
    Get all available routes.
    
    Returns:
        Dictionary of all route keys and paths
    """
    return JAINAM_ROUTES.copy()


def get_interactive_routes() -> dict:
    """
    Get only Interactive API routes.
    
    Returns:
        Dictionary of Interactive API route keys and paths
    """
    return {
        key: value
        for key, value in JAINAM_ROUTES.items()
        if not key.startswith('market.')
    }


def get_marketdata_routes(use_standard: bool = False) -> dict:
    """
    Get only Market Data API routes.
    
    Args:
        use_standard: If True, return standard market data routes instead of binary
    
    Returns:
        Dictionary of Market Data API route keys and paths
    """
    if use_standard:
        return JAINAM_ROUTES_STANDARD_MARKETDATA.copy()
    
    return {
        key: value
        for key, value in JAINAM_ROUTES.items()
        if key.startswith('market.')
    }

