# Jainam Prop Broker Integration Completion - Brownfield Enhancement PRD

**Version:** 1.0  
**Date:** 2025-10-06  
**Status:** Draft  
**Author:** John (PM Agent)

---

## 1. Intro Project Analysis and Context

### 1.1 Analysis Source

**Source:** IDE-based fresh analysis combined with comprehensive audit report

The analysis is based on:
- Direct examination of the existing Jainam Prop broker integration codebase at `/Users/maruth/projects/openalgo/broker/jainam_prop/`
- Comprehensive security and functionality audit report completed October 6, 2025
- Reference implementation analysis from `_sample_strategy/xts_connect.py` (1,422 lines of working XTS API code)
- OpenAlgo platform documentation including broker factory patterns and integration guides

---

### 1.2 Current Project State

**OpenAlgo Platform Overview:**

OpenAlgo is an open-source, Flask-based Python algorithmic trading platform that bridges traders with 20+ major Indian brokers. The platform provides:

- **Unified API Layer** (`/api/v1/`) with standardized endpoints across all brokers
- **WebSocket Architecture** with ZeroMQ message bus for real-time market data
- **Broker Plugin Architecture** with dynamic module loading via `importlib`
- **Master Contract Database** for symbol-to-token resolution
- **Smart Order Management** including position-based order placement
- **Sandbox Mode** for strategy testing without real trades

**Current Jainam Prop Integration State (60% Complete):**

The Jainam Prop broker integration was initiated but remains incomplete with critical functionality missing. The integration uses the **XTS (Symphony Fintech) API architecture**, which is a standardized API used by multiple Indian brokers.

**What Exists:**
- ✅ Proper directory structure following OpenAlgo's broker plugin pattern
- ✅ Authentication system with dual API support (Market Data + Interactive Order)
- ✅ Basic order placement, modification, and cancellation functions
- ✅ Quote fetching and historical data retrieval
- ✅ Funds/margin data retrieval
- ✅ Master contract download logic
- ✅ Data transformation layer (OpenAlgo ↔ Jainam format)
- ✅ WebSocket streaming implementation (jainam_adapter.py, jainam_websocket.py)
- ✅ Excellent reference implementation (`xts_connect.py` with 1,422 lines of working code)

**What's Missing (Critical Gaps):**
- ❌ **6 Core Functions Not Implemented:**
  - `get_trade_book()` - View executed trades
  - `get_positions()` - Fetch current positions
  - `get_holdings()` - Fetch long-term holdings
  - `get_open_position()` - Get position for specific symbol (required for smart orders)
  - `place_smartorder_api()` - Position-based intelligent order placement
  - `close_all_positions()` - Emergency position closure
- ❌ **Database Integration:** Token lookup returns placeholder value `123456` instead of querying database
- ❌ **Security Vulnerability:** API credentials hardcoded in source code
- ❌ **Symbol Resolution:** No actual symbol-to-token lookup implementation

**Impact of Missing Functions:**
- Smart order feature completely non-functional (depends on `get_open_position()`)
- Position tracking unavailable
- Trade history inaccessible
- All order placements will fail due to invalid token (123456)

---

### 1.3 Available Documentation Analysis

**Document-Project Status:** Not previously run for Jainam Prop integration

**Available Documentation:**

✅ **Tech Stack Documentation**
- OpenAlgo platform architecture documented in README.md
- XTS API reference implementation in `_sample_strategy/xts_connect.py`
- Symphony Fintech GitHub: https://github.com/symphonyfintech

✅ **Source Tree/Architecture**
- Broker factory pattern documented in `docs/broker_factory.md`
- International broker integration guide in `docs/international_broker_integration.md`
- Clear broker plugin structure established

✅ **API Documentation**
- XTS Connect API fully documented in reference implementation
- OpenAlgo API endpoints documented in README.md
- Broker-specific transformation patterns available

✅ **External API Documentation**
- Symphony Fintech XTS API documentation available on GitHub
- Jainam Prop trading platform: http://smpb.jainam.in:4143

✅ **Technical Debt Documentation**
- Comprehensive audit report identifying all gaps and security issues
- Detailed implementation guide for missing functions provided in audit

⚠️ **Partially Available:**
- Coding standards (inferred from existing broker implementations)
- Testing patterns (not explicitly documented for broker integrations)

❌ **Missing:**
- UX/UI guidelines specific to broker integration
- Jainam Prop-specific deployment procedures

**Recommendation:** The existing documentation is sufficient to proceed. The comprehensive audit report and reference implementation provide all necessary technical details for completion.

---

### 1.4 Enhancement Scope Definition

**Enhancement Type:**
☑️ **Integration with New Systems** (Completing partial XTS API integration)
☑️ **Bug Fix and Stability Improvements** (Fixing broken token lookup, security issues)
☑️ **UI/UX Enhancement** (Adding broker to selection UI and authentication flow)
☐ New Feature Addition
☐ Major Feature Modification
☐ Performance/Scalability Improvements
☐ Technology Stack Upgrade

**Enhancement Description:**

Complete the partially implemented Jainam Prop broker integration to make it production-ready by implementing the 6 missing critical API functions, adding UI/UX components for broker selection and authentication, fixing the database integration for symbol-to-token resolution, resolving security vulnerabilities (hardcoded credentials), and adding comprehensive error handling and validation. This enhancement will enable Jainam Prop users to fully utilize OpenAlgo's trading platform including smart orders, position tracking, and trade history.

**Impact Assessment:**
☑️ **Moderate Impact** (some existing code changes + UI additions)

**Rationale:**
- **Mostly isolated to broker module:** Backend changes contained within `broker/jainam_prop/` directory
- **Minimal UI changes:** Only broker selection dropdown and authentication callback need updates
- **No core platform changes:** OpenAlgo's broker factory and service layer remain unchanged
- **Follows established patterns:** Implementation mirrors existing broker integrations (Zebu, Compositedge, Definedge)
- **Database schema exists:** Symbol token table already supports multiple brokers
- **Some refactoring needed:** Security fix requires moving credentials to environment variables

---

### 1.5 Goals and Background Context

**Goals:**

1. **Complete Core API Functions** - Implement all 6 missing functions (`get_trade_book`, `get_positions`, `get_holdings`, `get_open_position`, `place_smartorder_api`, `close_all_positions`) following XTS API patterns from reference implementation

2. **Enable Smart Order Functionality** - Make position-based intelligent order placement operational for Jainam Prop users

3. **Fix Symbol Resolution** - Implement proper database integration for symbol-to-token lookup to replace placeholder value

4. **Resolve Security Vulnerabilities** - Move hardcoded API credentials to environment variables following OpenAlgo's configuration patterns

5. **Achieve Production Readiness** - Add comprehensive error handling, retry logic, rate limiting, and validation to meet OpenAlgo's quality standards

6. **Maintain Integration Consistency** - Ensure Jainam Prop integration matches the quality and completeness of other broker integrations (Zerodha, Angel, Upstox, etc.)

**Background Context:**

The Jainam Prop broker integration was initiated to expand OpenAlgo's broker support to include Jainam's proprietary trading platform, which uses the Symphony Fintech XTS API architecture. This is the same API architecture used by several other brokers already supported by OpenAlgo (5paisa XTS, Compositedge, Definedge), making the integration pattern well-established.

The integration was started with proper architectural planning—correct directory structure, authentication system, and reference implementation—but was left incomplete with only 60% of required functionality implemented. The missing 40% includes critical functions that are essential for basic trading operations (position tracking, trade history) and advanced features (smart orders, emergency position closure).

**Why This Enhancement is Needed:**

1. **User Demand:** Jainam Prop users cannot currently use OpenAlgo due to incomplete integration
2. **Platform Completeness:** Incomplete broker integrations undermine OpenAlgo's value proposition of unified multi-broker support
3. **Security Risk:** Hardcoded credentials in source code pose immediate security threat if code is shared or deployed
4. **Technical Debt:** Placeholder implementations (token lookup returning 123456) will cause all orders to fail
5. **Feature Parity:** Smart order functionality is a key OpenAlgo differentiator that must work across all brokers

**How It Fits with Existing Project:**

This enhancement completes an existing integration rather than adding new functionality to OpenAlgo. It follows the established broker plugin architecture, uses existing database schemas, and requires no changes to the core platform. The work is entirely additive—implementing missing functions and fixing broken implementations—with no risk to existing broker integrations.

---

### 1.6 Change Log

| Change | Date | Version | Description | Author |
|--------|------|---------|-------------|--------|
| Initial PRD Creation | 2025-10-06 | 1.0 | Created brownfield PRD for Jainam Prop integration completion | John (PM Agent) |

---

## 2. Requirements

### 2.1 Functional Requirements

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

### 2.2 Non-Functional Requirements

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

### 2.3 Compatibility Requirements

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

## 3. Technical Constraints and Integration Requirements

### 3.1 Existing Technology Stack

**Languages:**
- Python 3.8+ (OpenAlgo platform requirement)
- SQL (SQLite database queries)

**Frameworks:**
- Flask 2.x (OpenAlgo web framework)
- SQLAlchemy (database ORM - if used, otherwise raw SQL)
- httpx (async HTTP client for API calls)

**Database:**
- SQLite 3.x (OpenAlgo's embedded database)
- Database file: `openalgo.db` (or similar, located in project root)
- Table: `symbol_token` for instrument master data
- Table: `auth` for user authentication tokens

**Infrastructure:**
- Local deployment (no cloud dependencies)
- WebSocket server on port 8765 (for real-time data)
- ZeroMQ message bus (for broker adapter communication)
- Flask development server or production WSGI server (Gunicorn/uWSGI)

**External Dependencies:**
- **Jainam XTS API**: http://smpb.jainam.in:4143
  - Market Data API: `/apimarketdata/*` endpoints
  - Interactive Order API: `/interactive/*` endpoints
  - Authentication: Token-based with dual API keys
- **Symphony Fintech XTS SDK**: Reference implementation patterns
- **httpx**: HTTP client with connection pooling and retry support
- **pandas**: DataFrame operations for master contract processing

**Version Constraints:**
- Must maintain compatibility with Python 3.8+ (OpenAlgo's minimum version)
- Must use httpx (not requests) per OpenAlgo's standardization
- Must use OpenAlgo's custom logger (not standard logging)

---

### 3.2 Integration Approach

**Database Integration Strategy:**
- Use OpenAlgo's existing database connection pattern from `database/symbol_db.py`
- Implement token lookup with parameterized SQL queries for security
- Bulk insert master contract data using DataFrame iteration
- Clear existing broker data before inserting new data
- Close database connections properly after use

**API Integration Strategy:**
- Use OpenAlgo's httpx client pattern from `utils/httpx_client.py`
- Load credentials from environment variables at module initialization
- Implement consistent header management for authentication
- Use appropriate timeouts (10 seconds default)
- Follow XTS API patterns from reference implementation

**Frontend Integration Strategy:**
- **Minimal frontend changes required** for broker selection and authentication
- **Broker Selection UI:** Add Jainam Prop to dropdown in `templates/broker.html`
- **Authentication Flow:** Add callback handler in `blueprints/brlogin.py`
- **Existing UI Components:** Order placement, positions, holdings, and trade history pages will automatically work once backend functions and authentication are implemented
- Order placement form routes to `place_order_api()`
- Smart order form routes to `place_smartorder_api()`
- Positions page routes to `get_positions()`
- Trade history routes to `get_trade_book()`

**Testing Integration Strategy:**
- Unit testing with mocked API responses
- Integration testing with real Jainam API using test credentials
- Use small quantities and market orders for safety during testing
- Set environment variable `JAINAM_TEST_MODE=true` for test mode if supported

---

### 3.3 Code Organization and Standards

**File Structure:**
```
broker/jainam_prop/
├── api/
│   ├── auth_api.py          # ✅ Complete - no changes
│   ├── order_api.py         # 🔧 Add 6 missing functions
│   ├── data.py              # ✅ Complete - no changes
│   └── funds.py             # ✅ Complete - no changes
├── mapping/
│   ├── transform_data.py    # 🔧 Fix get_token_from_symbol()
│   └── order_data.py        # ✅ Complete - integrate validation
├── database/
│   └── master_contract_db.py # 🔧 Fix save_master_contract_to_db()
├── streaming/
│   ├── jainam_adapter.py    # ✅ Assumed complete
│   └── jainam_websocket.py  # ✅ Assumed complete
└── plugin.json              # ✅ Complete - no changes
```

**Naming Conventions:**
- Functions: `snake_case` (e.g., `get_open_position`)
- Classes: `PascalCase` (e.g., `JainamAPI`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `ROOT_URL`)
- Private functions: `_leading_underscore` (e.g., `_get_headers`)

**Coding Standards:**
- Follow OpenAlgo's existing patterns from other broker integrations
- Use docstrings for all public functions (Google style)
- Implement specific exception handling (not generic Exception)
- Return standardized response formats
- Log operations with appropriate levels (DEBUG, INFO, ERROR)

---

### 3.4 Deployment and Operations

**Deployment Strategy:**
1. Update environment variables in `.env` file with Jainam API credentials
2. Download master contract via OpenAlgo admin UI or API endpoint
3. Restart Flask application (development or production)
4. Verify broker availability in broker list endpoint

**Monitoring and Logging:**
- Log all API calls with endpoint, parameters, and response status
- Log position calculations for smart orders
- Log database query performance
- Monitor authentication token refresh events
- Track rate limit violations

**Configuration Management:**
- Environment variables for API credentials (required)
- Optional configuration for timeout, rate limit, retry count
- Configuration validation at startup with fail-fast behavior
- Document all configuration options in deployment guide

---

### 3.5 Risk Assessment and Mitigation

**Technical Risks:**

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| XTS API changes | High | Medium | Validate endpoints against current documentation; test early |
| Database schema mismatch | High | Low | Examine actual schema before implementation; use parameterized queries |
| Token lookup failures | High | Medium | Implement graceful error handling; provide master contract refresh UI |
| Credential exposure | Critical | Low | Add `.env` to `.gitignore`; validate at startup; rotate if exposed |
| Rate limiting | Medium | Medium | Implement rate limiting; add delays; monitor violations |

**Integration Risks:**

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Service layer incompatibility | High | Low | Match function signatures with other brokers; test with service layer |
| WebSocket streaming issues | Medium | Medium | Audit streaming implementation; test real-time data |
| Authentication token expiry | Medium | High | Implement token refresh logic; retry with fresh token |
| Position calculation errors | High | Low | Add comprehensive logging; implement unit tests |
| Master contract staleness | Medium | Medium | Implement scheduled refresh; add last-update timestamp |

**Deployment Risks:**

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| Missing environment variables | High | Medium | Implement startup validation; document requirements; provide template |
| Database migration issues | Medium | Low | Test with actual database; provide migration script if needed |
| Backward compatibility | Critical | Very Low | Changes isolated to broker module; test other brokers |
| Production testing limitations | High | High | Implement comprehensive logging; use small quantities initially |

---

## 4. Epic and Story Structure

### 4.1 Epic Approach

**Epic Structure Decision:** Single comprehensive epic

**Rationale:**
For this brownfield enhancement, all work contributes to a single objective—making the Jainam Prop broker integration production-ready. The 6 missing functions, database integration, and security fixes are interdependent parts of one deliverable. A single epic provides better traceability, makes dependencies explicit, and clearly indicates when the integration is complete.

---

## Epic 1: Complete Jainam Prop Broker Integration for Production Readiness

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

### Story Sequence Overview

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

### Story 1.1: Implement Database Integration for Symbol-to-Token Resolution

As a **developer implementing the Jainam Prop integration**,
I want **symbol-to-token lookup to query the actual database instead of returning placeholder value 123456**,
so that **order placement can resolve symbols to correct instrument tokens and successfully place orders with Jainam API**.

#### Acceptance Criteria

1. **AC1**: `get_token_from_symbol(symbol, exchange)` function queries the `symbol_token` table with `broker='jainam_prop'` and returns the integer token value
2. **AC2**: Function raises `ValueError` with descriptive message if symbol not found in database
3. **AC3**: `save_master_contract_to_db(df)` function connects to database, deletes existing `broker='jainam_prop'` records, and inserts DataFrame rows
4. **AC4**: Database operations use parameterized queries and properly close connections
5. **AC5**: Master contract download populates database with 100,000+ instruments across all exchanges
6. **AC6**: Token lookup performance is <100ms for cached queries

#### Integration Verification

**IV1**: Verify other broker integrations continue to work after database changes
**IV2**: Test that `place_order_api()` successfully uses token lookup to place orders
**IV3**: Measure database query time and verify <100ms performance

---

### Story 1.2: Externalize API Credentials to Environment Variables

As a **security-conscious developer**,
I want **Jainam API credentials loaded from environment variables instead of hardcoded in source code**,
so that **credentials are not exposed in version control and can be rotated without code changes**.

#### Acceptance Criteria

1. **AC1**: Remove hardcoded credentials and replace with `os.getenv()` calls for all four credentials
2. **AC2**: Add validation that raises `ValueError` if any required credential is missing
3. **AC3**: Update `.env.example` file with placeholder entries and descriptive comments
4. **AC4**: Verify credentials never appear in logs or error messages
5. **AC5**: Document credential configuration in deployment guide

#### Integration Verification

**IV1**: Verify authentication works correctly after externalizing credentials
**IV2**: Test application fails fast with clear error when credentials missing
**IV3**: Verify no measurable latency added to authentication process

---

### Story 1.3: Implement Position and Holdings Retrieval Functions

As a **trader using Jainam Prop with OpenAlgo**,
I want **to view my current positions and long-term holdings in the OpenAlgo UI**,
so that **I can monitor my portfolio and make informed trading decisions**.

#### Acceptance Criteria

1. **AC1**: Implement `get_positions(auth_token)` that calls `/interactive/portfolio/positions` with `dayOrNet=NetWise`
2. **AC2**: Implement `get_holdings(auth_token)` that calls `/interactive/portfolio/holdings`
3. **AC3**: Both functions handle authentication token parsing consistently
4. **AC4**: Both functions implement error handling and return standardized error responses
5. **AC5**: Functions use `get_httpx_client()` with 10-second timeout
6. **AC6**: Response data includes all required fields (symbol, exchange, product, quantity, price, P&L)

#### Integration Verification

**IV1**: Verify existing order placement and quote fetching continue to work
**IV2**: Test OpenAlgo's positions and holdings pages display data correctly
**IV3**: Measure API response time and verify <5 seconds completion

---

### Story 1.4: Implement Trade Book Retrieval Function

As a **trader using Jainam Prop with OpenAlgo**,
I want **to view my executed trades in the OpenAlgo UI**,
so that **I can review my trading history and analyze my performance**.

#### Acceptance Criteria

1. **AC1**: Implement `get_trade_book(auth_token)` that calls `/interactive/trades`
2. **AC2**: Function transforms response using `transform_trade_book()` from `mapping/order_data.py`
3. **AC3**: Transformed response includes all required fields (order ID, trade ID, symbol, action, quantity, price, timestamp)
4. **AC4**: Function handles empty trade book gracefully (returns empty list)
5. **AC5**: Function implements error handling, logging, and uses `get_httpx_client()`

#### Integration Verification

**IV1**: Verify order book retrieval continues to work
**IV2**: Test OpenAlgo's trade history page displays trades correctly
**IV3**: Measure response time with large trade history (100+ trades) and verify <5 seconds

---

### Story 1.5: Implement Open Position Lookup Function

As a **developer implementing smart order functionality**,
I want **a function that returns the current position quantity for a specific symbol**,
so that **smart order placement can calculate position delta and determine order action/quantity**.

#### Acceptance Criteria

1. **AC1**: Implement `get_open_position(tradingsymbol, exchange, producttype, auth_token)` that filters positions
2. **AC2**: Function returns net quantity as string (e.g., "100", "-50", "0")
3. **AC3**: Function handles position not found (returns "0")
4. **AC4**: Function handles `get_positions()` failure (returns "0" and logs error)
5. **AC5**: Function matches symbol, exchange, and product type exactly
6. **AC6**: Function logs lookup result for debugging

#### Integration Verification

**IV1**: Verify `get_positions()` continues to work correctly
**IV2**: Test with various scenarios (long position, short position, no position, invalid symbol)
**IV3**: Measure execution time and verify <5 seconds completion

---

### Story 1.6: Implement Smart Order Placement Function

As a **trader using OpenAlgo's smart order feature**,
I want **to specify a target position size and have OpenAlgo automatically calculate and place the correct order**,
so that **I can manage positions efficiently without manual calculation of buy/sell quantities**.

#### Acceptance Criteria

1. **AC1**: Implement `place_smartorder_api(data, auth_token)` that extracts `position_size` and calls `get_open_position()`
2. **AC2**: Function calculates position delta and determines action/quantity (delta > 0: BUY, delta < 0: SELL, delta == 0: success message)
3. **AC3**: Function logs position calculation details (symbol, current, target, delta, action, quantity)
4. **AC4**: Function calls `place_order_api()` with calculated parameters
5. **AC5**: Function handles errors gracefully (position lookup failure, order placement failure)
6. **AC6**: Function returns success message when delta is zero (no order needed)

#### Integration Verification

**IV1**: Verify regular order placement continues to work
**IV2**: Test smart order with all scenarios (opening, increasing, reducing, closing, reversing, no change)
**IV3**: Measure execution time and verify <10 seconds completion

---

### Story 1.7: Implement Emergency Position Closure Function

As a **trader needing to quickly exit all positions**,
I want **a function that closes all open positions with market orders**,
so that **I can manage risk during market volatility or emergency situations**.

#### Acceptance Criteria

1. **AC1**: Implement `close_all_positions(current_api_key, auth_token)` that retrieves positions and places closing orders
2. **AC2**: Function determines order action based on position direction (quantity > 0: SELL, quantity < 0: BUY)
3. **AC3**: Function places market orders for absolute value of position quantity
4. **AC4**: Function continues closing remaining positions even if one fails
5. **AC5**: Function returns aggregated results with order IDs and status for each position
6. **AC6**: Function logs each position closure attempt

#### Integration Verification

**IV1**: Verify `get_positions()` and `place_order_api()` continue to work
**IV2**: Test with multiple positions, mix of long/short, single position, no positions, partial failures
**IV3**: Measure execution time with 5 positions and verify reasonable performance

---

### Story 1.8: Add Comprehensive Error Handling, Validation, and Integration Testing

As a **developer ensuring production readiness**,
I want **comprehensive error handling, input validation, and integration testing across all implemented functions**,
so that **the Jainam Prop integration is robust, reliable, and ready for production use**.

#### Acceptance Criteria

1. **AC1**: Integrate `validate_order_data()` into `place_order_api()` and `place_smartorder_api()`
2. **AC2**: All API functions implement specific exception handling (HTTPError, Timeout, ConnectionError)
3. **AC3**: All API functions log errors with sufficient context (function, parameters, error type/message)
4. **AC4**: All API functions return standardized error responses without exposing internal details
5. **AC5**: Add retry logic with exponential backoff (1s, 2s, 4s) for network errors
6. **AC6**: Conduct integration testing with real Jainam API for all functions (authentication, orders, positions, holdings, trades, smart orders, position closure, token lookup, master contract)
7. **AC7**: Document discovered issues or limitations in code comments and deployment guide

#### Integration Verification

**IV1**: Run regression tests on existing OpenAlgo broker integrations (test 3 other brokers)
**IV2**: Test complete user workflow (login, master contract, orders, positions, holdings, trades, smart order, close all)
**IV3**: Measure end-to-end performance (order <3s, positions <5s, smart order <10s, master contract <60s, token lookup <100ms)

---

## 5. Success Metrics

**Completion Criteria:**
- ✅ All 6 missing backend functions implemented and tested
- ✅ UI/UX integration complete (broker selection + authentication)
- ✅ Database integration complete with token lookup working
- ✅ Security vulnerabilities resolved (credentials externalized)
- ✅ All integration tests passing with real Jainam API
- ✅ Performance targets met for all operations
- ✅ No regression in existing broker integrations
- ✅ Documentation updated (code comments, deployment guide)

**Production Readiness Checklist:**
- [ ] All functional requirements (FR1-FR13) implemented
- [ ] All non-functional requirements (NFR1-NFR10) met
- [ ] All compatibility requirements (CR1-CR4) verified
- [ ] All user stories (1.1-1.11) completed and accepted
- [ ] Integration testing completed successfully (including UI/UX)
- [ ] Performance benchmarks met
- [ ] Security audit passed (no hardcoded credentials)
- [ ] Deployment guide created and validated
- [ ] Code review completed
- [ ] Production deployment approved

---

## 6. Appendix

### 6.1 Reference Documentation

- **OpenAlgo Platform**: https://docs.openalgo.in/
- **Symphony Fintech XTS API**: https://github.com/symphonyfintech
- **Jainam Prop Trading Platform**: http://smpb.jainam.in:4143
- **Broker Factory Documentation**: `/docs/broker_factory.md`
- **International Broker Integration Guide**: `/docs/international_broker_integration.md`
- **Comprehensive Audit Report**: Completed October 6, 2025

### 6.2 Key Contacts

- **Product Owner**: TBD
- **Technical Lead**: TBD
- **QA Lead**: TBD
- **Jainam Prop Support**: TBD

### 6.3 Glossary

- **XTS**: Symphony Fintech's eXchange Trading System API
- **Smart Order**: Position-based order placement that calculates required action/quantity
- **Master Contract**: Database of all tradable instruments with tokens and metadata
- **Token**: Unique identifier for an instrument used by broker API
- **Position Delta**: Difference between target position size and current position
- **Broker Plugin**: Modular broker integration following OpenAlgo's architecture

---

**Document Status:** Draft - Ready for Review
**Next Steps:** Review with stakeholders, validate technical approach, begin Story 1.1 implementation

---

*This PRD was generated using the BMAD™ Core brownfield PRD template v2.0*

