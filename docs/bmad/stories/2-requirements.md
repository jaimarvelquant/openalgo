# 2. Requirements

## 2.1 Functional Requirements

**FR1: Complete Trade Book Retrieval**
Implement `get_trade_book(auth_token)` function in `broker/jainam_prop/api/order_api.py` that retrieves executed trades from Jainam XTS API endpoint `/interactive/trades`, transforms the response to OpenAlgo format using the existing `transform_trade_book()` function from `mapping/order_data.py`, and returns trade data including trade ID, symbol, exchange, action, quantity, price, and timestamp.

**FR2: Complete Position Retrieval**
Implement `get_positions(auth_token)` function that calls Jainam XTS API endpoint `/interactive/portfolio/positions` with `dayOrNet=NetWise` parameter, returns position data in Jainam format including symbol, exchange, product type, quantity, average price, and P&L, maintaining compatibility with OpenAlgo's position tracking service layer.

**FR3: Complete Holdings Retrieval**
Implement `get_holdings(auth_token)` function that calls Jainam XTS API endpoint `/interactive/portfolio/holdings`, returns long-term holdings data including symbol, exchange, quantity, average price, current price, and P&L in Jainam format for OpenAlgo's holdings display.

**FR4: Complete Open Position Lookup**
Implement `get_open_position(tradingsymbol, exchange, producttype, auth_token)` function that retrieves all positions via `get_positions()`, filters for the specific symbol/exchange/product combination, and returns the net quantity as a string (e.g., "100", "-50", "0"), following the pattern used by other OpenAlgo broker integrations (Zebu, IBulls).

**FR5: Complete Smart Order Placement**
Implement `place_smartorder_api(data, auth_token)` function that:
- Extracts target `position_size` from request data
- Calls `get_open_position()` to fetch current position
- Calculates position delta (target - current)
- Determines order action (BUY/SELL) and quantity based on delta
- Calls `place_order_api()` with calculated parameters
- Returns success if position already matches target (delta = 0)

**FR6: Complete Emergency Position Closure**
Implement `close_all_positions(current_api_key, auth_token)` function that:
- Retrieves all open positions via `get_positions()`
- For each non-zero position, places a market order in the opposite direction
- Returns aggregated results with order IDs and status for each closed position
- Handles errors gracefully, continuing to close remaining positions if one fails

**FR7: Implement Database-Backed Token Lookup**
Replace the placeholder `get_token_from_symbol(symbol, exchange)` function in `broker/jainam_prop/mapping/transform_data.py` to:
- Query the `symbol_token` database table with `broker='jainam_prop'`, `symbol=<symbol>`, `exchange=<exchange>`
- Return the instrument token (exchangeInstrumentID) as an integer
- Raise a descriptive error if symbol not found in database
- Use the existing database connection pattern from OpenAlgo's `database/symbol_db.py`

**FR8: Implement Database Integration for Master Contract**
Update `save_master_contract_to_db(df)` function in `broker/jainam_prop/database/master_contract_db.py` to:
- Connect to OpenAlgo's SQLite database
- Delete existing records where `broker='jainam_prop'`
- Insert DataFrame rows into `symbol_token` table with proper field mapping
- Create indexes for fast lookup on (broker, symbol, exchange)
- Replace current CSV file export with actual database persistence

**FR9: Externalize API Credentials**
Move hardcoded API credentials from `broker/jainam_prop/api/auth_api.py` to environment variables:
- `JAINAM_MARKET_API_KEY` for Market Data API key
- `JAINAM_MARKET_API_SECRET` for Market Data API secret
- `JAINAM_INTERACTIVE_API_KEY` for Interactive Order API key
- `JAINAM_INTERACTIVE_API_SECRET` for Interactive Order API secret
- Add validation to raise descriptive error if credentials not configured
- Update `.env.example` file with placeholder entries

**FR10: Add Order Data Validation**
Integrate the existing `validate_order_data(order_data)` function from `broker/jainam_prop/mapping/order_data.py` into the order placement flow:
- Call validation before transforming data in `place_order_api()`
- Return validation errors with HTTP 400 status
- Validate required fields, action, exchange, price type, quantity, price, and trigger price
- Prevent invalid orders from reaching Jainam API

**FR11: Add Jainam Prop to Broker Selection UI**
Add Jainam Prop to the broker selection dropdown in `templates/broker.html`:
- Add option to broker dropdown: `<option value="jainam_prop">Jainam Prop</option>`
- Add switch case for Jainam Prop login URL routing
- Follow XTS OAuth pattern similar to Compositedge and Definedge
- Ensure option is enabled/disabled based on broker configuration

**FR12: Implement Authentication Callback Handler**
Implement authentication callback handler in `blueprints/brlogin.py`:
- Add `elif broker == 'jainam_prop':` case to handle authentication
- Extract request_token from OAuth callback
- Call `authenticate_broker(request_token)` from `broker.jainam_prop.api.auth_api`
- Store access_token in database via `handle_auth_success()`
- Handle authentication errors gracefully
- Follow XTS authentication pattern from Compositedge/Definedge

**FR13: Create Deployment Documentation**
Create comprehensive deployment guide at `docs/bmad/deployment-guide.md`:
- Document environment variable configuration (all 4 Jainam credentials)
- Document master contract download process
- Document application restart procedure
- Document broker availability verification
- Document rollback procedure
- Document troubleshooting common issues

## 2.2 Non-Functional Requirements

**NFR1: Performance - API Response Time**
All implemented API functions must complete within 5 seconds under normal network conditions, matching the performance characteristics of existing OpenAlgo broker integrations. Database token lookups must complete in <100ms using indexed queries.

**NFR2: Reliability - Error Handling**
All API functions must implement comprehensive error handling:
- Catch specific exceptions (HTTPError, Timeout, ConnectionError) rather than generic Exception
- Log errors with sufficient context for debugging (function name, parameters, error message)
- Return standardized error responses with `{'status': 'error', 'message': '<description>'}`
- Never expose internal implementation details or stack traces to API consumers

**NFR3: Reliability - Retry Logic**
Implement retry logic for transient network failures:
- Retry failed API calls up to 3 times with exponential backoff (1s, 2s, 4s)
- Only retry on network errors (Timeout, ConnectionError), not on business logic errors (400, 401, 403)
- Log retry attempts for monitoring
- Use existing `httpx_client` with built-in retry capabilities where possible

**NFR4: Security - Credential Management**
API credentials must never be stored in source code or version control:
- All credentials loaded from environment variables at runtime
- Application must fail fast with clear error message if credentials missing
- Credentials must not appear in logs or error messages
- Follow OpenAlgo's existing credential management patterns (e.g., `BROKER_API_KEY`, `BROKER_API_SECRET`)

**NFR5: Maintainability - Code Consistency**
Implementation must follow OpenAlgo's established patterns:
- Use existing `httpx_client` from `utils/httpx_client.py` for all HTTP requests
- Use existing logger from `utils/logging.py` for all logging
- Follow naming conventions from other broker integrations (e.g., `get_positions` not `getPositions`)
- Match function signatures of equivalent functions in other brokers (Zebu, IBulls, Shoonya)

**NFR6: Testability - Integration Testing**
All implemented functions must be testable with real Jainam API:
- Support test credentials via environment variables
- Provide clear error messages for authentication failures
- Log API requests and responses at DEBUG level for troubleshooting
- Support dry-run mode where applicable (e.g., order validation without placement)

**NFR7: Scalability - Rate Limiting**
Respect Jainam API rate limits to prevent account suspension:
- Implement rate limiting for order placement (max 10 orders/second)
- Add configurable delay between API calls (default 100ms)
- Use existing rate limiting patterns from OpenAlgo's `place_order_service.py`
- Log rate limit violations for monitoring

**NFR8: Compatibility - Database Schema**
Database integration must work with OpenAlgo's existing schema:
- Use existing `symbol_token` table structure without modifications
- Support concurrent access from multiple broker integrations
- Maintain backward compatibility with existing symbol lookup functions
- Use parameterized queries to prevent SQL injection

**NFR9: Observability - Logging**
Implement comprehensive logging for debugging and monitoring:
- Log all API calls with endpoint, parameters (excluding sensitive data), and response status
- Log position calculations for smart orders (current, target, delta, action, quantity)
- Log database queries and result counts
- Use appropriate log levels (DEBUG for details, INFO for operations, ERROR for failures)

**NFR10: Documentation - Code Comments**
All implemented functions must include:
- Docstrings with description, parameters, return values, and exceptions
- Inline comments explaining complex logic (e.g., position delta calculation)
- References to XTS API documentation where applicable
- Examples of expected input/output formats

## 2.3 Compatibility Requirements

**CR1: Existing API Compatibility**
All implemented functions must maintain compatibility with OpenAlgo's service layer:
- `place_order_api()` must return tuple: `(response_object, response_data, order_id)`
- `get_positions()` must return Jainam's native format (not transformed to OpenAlgo format)
- `get_open_position()` must return string representation of quantity (e.g., "100", not integer 100)
- Function signatures must match those defined in other broker integrations

**CR2: Database Schema Compatibility**
Database integration must use OpenAlgo's existing `symbol_token` table without schema changes:
- Table structure: `(broker, symbol, brsymbol, token, exchange, brexchange, lotsize, ...)`
- Broker identifier: `'jainam_prop'` (lowercase with underscore)
- No new columns or tables required
- Support SQLite database engine used by OpenAlgo

**CR3: UI/UX Consistency**
Error messages and responses must match OpenAlgo's existing patterns:
- Success responses: `{'status': 'success', 'message': '<description>', ...}`
- Error responses: `{'status': 'error', 'message': '<description>'}`
- Order IDs returned as strings, not integers
- Timestamps in ISO 8601 format or broker's native format (consistently)

**CR4: Integration Compatibility**
Implementation must work with OpenAlgo's existing infrastructure:
- Use existing `get_httpx_client()` for HTTP requests (connection pooling, timeouts)
- Use existing `get_auth_token()` from `database/auth_db.py` for token retrieval
- Support dynamic broker loading via `importlib` in service layer
- Work with existing WebSocket proxy architecture (no changes to streaming layer required)

---
