# 3. Technical Constraints and Integration Requirements

## 3.1 Existing Technology Stack

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

## 3.2 Integration Approach

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

## 3.3 Code Organization and Standards

**File Structure:**
```
broker/jainam_prop/
├── api/
│   ├── auth_api.py          # 🔧 Add authenticate_direct() function
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

## 3.4 Deployment and Operations

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

## 3.5 Risk Assessment and Mitigation

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
