# Epic 1: Complete Jainam Prop Broker Integration for Production Readiness

**Epic Goal:**
Complete the partially implemented Jainam Prop broker integration by implementing all missing API functions, fixing database integration for symbol-to-token resolution, resolving security vulnerabilities, and adding comprehensive error handling to achieve production readiness and feature parity with other OpenAlgo broker integrations.

**Integration Requirements:**
1. Maintain existing functionality without regression
2. Follow established patterns from other XTS-based brokers
3. Use existing database schema without modifications
4. Match service layer expectations for function signatures
5. Ensure WebSocket compatibility (no streaming changes required)
6. Follow OpenAlgo's environment variable patterns

---

## Story Sequence Overview

**Phase 1: Foundation (Stories 1.1-1.2)** - Fix critical blockers
- Story 1.1: Database integration (enables all other work)
- Story 1.2: Security hardening (removes immediate risk)

**Phase 2: Core API Functions (Stories 1.3-1.5)** - Enable basic functionality
- Story 1.3: Position and holdings retrieval
- Story 1.4: Trade book retrieval
- Story 1.5: Open position lookup

**Phase 3: Advanced Features (Stories 1.6-1.7)** - Enable smart orders
- Story 1.6: Smart order placement
- Story 1.7: Emergency position closure

**Phase 4: Production Readiness (Story 1.8)** - Polish and validation
- Story 1.8: Error handling, validation, and testing

**Dependency Chain:**
```
1.1 (Database) → 1.3, 1.4, 1.5 (All depend on token lookup)
1.2 (Security) → Independent, can run in parallel
1.5 (Open Position) → 1.6 (Smart Order depends on it)
1.3, 1.4, 1.5, 1.6, 1.7 → 1.8 (Testing validates all functions)
```

---

## Story 1.1: Implement Database Integration for Symbol-to-Token Resolution

As a **developer implementing the Jainam Prop integration**,
I want **symbol-to-token lookup to query the actual database instead of returning placeholder value 123456**,
so that **order placement can resolve symbols to correct instrument tokens and successfully place orders with Jainam API**.

### Acceptance Criteria

1. **AC1**: `get_token_from_symbol(symbol, exchange)` function queries the `symbol_token` table with `broker='jainam_prop'` and returns the integer token value
2. **AC2**: Function raises `ValueError` with descriptive message if symbol not found in database
3. **AC3**: `save_master_contract_to_db(df)` function connects to database, deletes existing `broker='jainam_prop'` records, and inserts DataFrame rows
4. **AC4**: Database operations use parameterized queries and properly close connections
5. **AC5**: Master contract download populates database with 100,000+ instruments across all exchanges
6. **AC6**: Token lookup performance is <100ms for cached queries

### Integration Verification

**IV1**: Verify other broker integrations continue to work after database changes
**IV2**: Test that `place_order_api()` successfully uses token lookup to place orders
**IV3**: Measure database query time and verify <100ms performance

---

## Story 1.2: Externalize API Credentials to Environment Variables

As a **security-conscious developer**,
I want **Jainam API credentials loaded from environment variables instead of hardcoded in source code**,
so that **credentials are not exposed in version control and can be rotated without code changes**.

### Acceptance Criteria

1. **AC1**: Remove hardcoded credentials and replace with `os.getenv()` calls for all four credentials
2. **AC2**: Add validation that raises `ValueError` if any required credential is missing
3. **AC3**: Update `.env.example` file with placeholder entries and descriptive comments
4. **AC4**: Verify credentials never appear in logs or error messages
5. **AC5**: Document credential configuration in deployment guide

### Integration Verification

**IV1**: Verify authentication works correctly after externalizing credentials
**IV2**: Test application fails fast with clear error when credentials missing
**IV3**: Verify no measurable latency added to authentication process

---

## Story 1.3: Implement Position and Holdings Retrieval Functions

As a **trader using Jainam Prop with OpenAlgo**,
I want **to view my current positions and long-term holdings in the OpenAlgo UI**,
so that **I can monitor my portfolio and make informed trading decisions**.

### Acceptance Criteria

1. **AC1**: Implement `get_positions(auth_token)` that calls `/interactive/portfolio/positions` with `dayOrNet=NetWise`
2. **AC2**: Implement `get_holdings(auth_token)` that calls `/interactive/portfolio/holdings`
3. **AC3**: Both functions handle authentication token parsing consistently
4. **AC4**: Both functions implement error handling and return standardized error responses
5. **AC5**: Functions use `get_httpx_client()` with 10-second timeout
6. **AC6**: Response data includes all required fields (symbol, exchange, product, quantity, price, P&L)

### Integration Verification

**IV1**: Verify existing order placement and quote fetching continue to work
**IV2**: Test OpenAlgo's positions and holdings pages display data correctly
**IV3**: Measure API response time and verify <5 seconds completion

---

## Story 1.4: Implement Trade Book Retrieval Function

As a **trader using Jainam Prop with OpenAlgo**,
I want **to view my executed trades in the OpenAlgo UI**,
so that **I can review my trading history and analyze my performance**.

### Acceptance Criteria

1. **AC1**: Implement `get_trade_book(auth_token)` that calls `/interactive/trades`
2. **AC2**: Function transforms response using `transform_trade_book()` from `mapping/order_data.py`
3. **AC3**: Transformed response includes all required fields (order ID, trade ID, symbol, action, quantity, price, timestamp)
4. **AC4**: Function handles empty trade book gracefully (returns empty list)
5. **AC5**: Function implements error handling, logging, and uses `get_httpx_client()`

### Integration Verification

**IV1**: Verify order book retrieval continues to work
**IV2**: Test OpenAlgo's trade history page displays trades correctly
**IV3**: Measure response time with large trade history (100+ trades) and verify <5 seconds

---

## Story 1.5: Implement Open Position Lookup Function

As a **developer implementing smart order functionality**,
I want **a function that returns the current position quantity for a specific symbol**,
so that **smart order placement can calculate position delta and determine order action/quantity**.

### Acceptance Criteria

1. **AC1**: Implement `get_open_position(tradingsymbol, exchange, producttype, auth_token)` that filters positions
2. **AC2**: Function returns net quantity as string (e.g., "100", "-50", "0")
3. **AC3**: Function handles position not found (returns "0")
4. **AC4**: Function handles `get_positions()` failure (returns "0" and logs error)
5. **AC5**: Function matches symbol, exchange, and product type exactly
6. **AC6**: Function logs lookup result for debugging

### Integration Verification

**IV1**: Verify `get_positions()` continues to work correctly
**IV2**: Test with various scenarios (long position, short position, no position, invalid symbol)
**IV3**: Measure execution time and verify <5 seconds completion

---

## Story 1.6: Implement Smart Order Placement Function

As a **trader using OpenAlgo's smart order feature**,
I want **to specify a target position size and have OpenAlgo automatically calculate and place the correct order**,
so that **I can manage positions efficiently without manual calculation of buy/sell quantities**.

### Acceptance Criteria

1. **AC1**: Implement `place_smartorder_api(data, auth_token)` that extracts `position_size` and calls `get_open_position()`
2. **AC2**: Function calculates position delta and determines action/quantity (delta > 0: BUY, delta < 0: SELL, delta == 0: success message)
3. **AC3**: Function logs position calculation details (symbol, current, target, delta, action, quantity)
4. **AC4**: Function calls `place_order_api()` with calculated parameters
5. **AC5**: Function handles errors gracefully (position lookup failure, order placement failure)
6. **AC6**: Function returns success message when delta is zero (no order needed)

### Integration Verification

**IV1**: Verify regular order placement continues to work
**IV2**: Test smart order with all scenarios (opening, increasing, reducing, closing, reversing, no change)
**IV3**: Measure execution time and verify <10 seconds completion

---

## Story 1.7: Implement Emergency Position Closure Function

As a **trader needing to quickly exit all positions**,
I want **a function that closes all open positions with market orders**,
so that **I can manage risk during market volatility or emergency situations**.

### Acceptance Criteria

1. **AC1**: Implement `close_all_positions(current_api_key, auth_token)` that retrieves positions and places closing orders
2. **AC2**: Function determines order action based on position direction (quantity > 0: SELL, quantity < 0: BUY)
3. **AC3**: Function places market orders for absolute value of position quantity
4. **AC4**: Function continues closing remaining positions even if one fails
5. **AC5**: Function returns aggregated results with order IDs and status for each position
6. **AC6**: Function logs each position closure attempt

### Integration Verification

**IV1**: Verify `get_positions()` and `place_order_api()` continue to work
**IV2**: Test with multiple positions, mix of long/short, single position, no positions, partial failures
**IV3**: Measure execution time with 5 positions and verify reasonable performance

---

## Story 1.8: Add Comprehensive Error Handling, Validation, and Integration Testing

As a **developer ensuring production readiness**,
I want **comprehensive error handling, input validation, and integration testing across all implemented functions**,
so that **the Jainam Prop integration is robust, reliable, and ready for production use**.

### Acceptance Criteria

1. **AC1**: Integrate `validate_order_data()` into `place_order_api()` and `place_smartorder_api()`
2. **AC2**: All API functions implement specific exception handling (HTTPError, Timeout, ConnectionError)
3. **AC3**: All API functions log errors with sufficient context (function, parameters, error type/message)
4. **AC4**: All API functions return standardized error responses without exposing internal details
5. **AC5**: Add retry logic with exponential backoff (1s, 2s, 4s) for network errors
6. **AC6**: Conduct integration testing with real Jainam API for all functions (authentication, orders, positions, holdings, trades, smart orders, position closure, token lookup, master contract)
7. **AC7**: Document discovered issues or limitations in code comments and deployment guide

### Integration Verification

**IV1**: Run regression tests on existing OpenAlgo broker integrations (test 3 other brokers)
**IV2**: Test complete user workflow (login, master contract, orders, positions, holdings, trades, smart order, close all)
**IV3**: Measure end-to-end performance (order <3s, positions <5s, smart order <10s, master contract <60s, token lookup <100ms)

---
