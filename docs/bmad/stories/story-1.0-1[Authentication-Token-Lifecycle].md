# Story 1.0-1: Authentication-Token-Lifecycle

## Status
Draft

## Estimated Effort
**3 hours** (reduced from 38-44 hours due to code reuse from FivePaisaXTS retail pattern)

## Story

**As a** developer implementing production-ready Jainam Pro integration,
**I want** direct API key/secret authentication with dual-token persistence,
**so that** interactive and market data flows reuse tokens without re-authentication and support Pro-specific dealer operations.

## ⚠️ CRITICAL: Pro vs Retail Distinction

**Jainam Prop is a PRO broker, not retail**
- **Authentication pattern:** Use FivePaisaXTS (retail) template - same direct login works for Pro
- **Pro-specific features:** Use XTS Pro SDK for dealer ops, bracket/cover orders, Pro market data
- **Implementation strategy:** Leverage retail patterns for common functionality, Pro SDK for Pro features

**Code Reuse Sources:**
- **Primary Template:** `broker/fivepaisaxts/api/auth_api.py` (retail authentication - 90% reusable)
- **Pro SDK:** `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/` (Pro-specific features)
- **Pro Pattern:** `broker/jainam_prop/_sample_strategy/xts_connect.py` (proven Pro implementation)
- **Database:** `database/auth_db.py` (100% reusable - works for all brokers)

**Reference:** See `docs/bmad/research/jainam-code-reuse-analysis.md` for complete analysis

## Acceptance Criteria

1. **AC1**: Implement `authenticate_direct()` by adapting FivePaisaXTS retail authentication pattern
   - **Template:** `broker/fivepaisaxts/api/auth_api.py` (lines 12-102)
   - **Why:** Same direct login pattern works for both retail and Pro
   - **Reuse:** 90% - Change environment variable names and URLs only
   - **Effort:** 30 minutes

2. **AC2**: Persist `(interactive_token, market_token, user_id)` using existing `database.auth_db.upsert_auth()`
   - **Status:** ✅ Already complete - no changes needed
   - **Works for:** Both retail and Pro brokers
   - **Effort:** 0 minutes

3. **AC3**: Read credentials from environment variables
   - **Template:** Existing Jainam `auth_api.py` credential validation (lines 22-29)
   - **Reuse:** 100% - Keep as-is
   - **Effort:** 0 minutes

4. **AC4**: Update REST/streaming modules to rehydrate tokens from DB
   - **Template:** `database/auth_db.py` `get_auth_token()` and `get_feed_token()`
   - **Status:** ✅ Already complete - works for all brokers
   - **Effort:** 0 minutes

5. **AC5**: Validate credentials with actionable errors
   - **Template:** Helper script `get_jainam_tokens.py` (lines 53-70)
   - **Reuse:** 100% - Extract to production
   - **Effort:** 15 minutes

6. **AC6**: Provide helper script for testing
   - **Status:** ✅ Already complete - `broker/jainam_prop/get_jainam_tokens.py`
   - **Effort:** 0 minutes

7. **AC7**: Catalog Pro-specific endpoints and verify wrapper exposure
   - **Reference:** `xts_connect.py` for Pro patterns (dealer ops, bracket/cover orders, Pro market data codes)
   - **Pro Features:** Dealer endpoints, bracket/cover orders, Pro market data codes (1501, 1502, 1505, 1510, 1512)
   - **Effort:** 30 minutes (documentation/verification)

8. **AC8**: Define verification checklist for Pro features
   - **Reference:** `xts_connect.py` for Pro feature inventory
   - **Create:** `docs/bmad/qa/pro-feature-checklist.md`
   - **Effort:** 30 minutes

## Integration Verification

**IV1**: Verify other broker integrations continue to work after `database.auth_db` schema extensions
**IV2**: Test that `place_order_api()` and streaming adapters successfully use rehydrated tokens
**IV3**: Measure authentication latency (initial login + token rehydration) and verify <2s total

## Tasks / Subtasks

- [ ] Task 1: Adapt FivePaisaXTS retail authentication (AC: 1, 3, 5) - **1.5 hours**
  - [ ] Subtask 1.1: Copy `broker/fivepaisaxts/api/auth_api.py::authenticate_broker()` function (30 min)
  - [ ] Subtask 1.2: Rename to `authenticate_direct()` and update environment variable names (15 min)
  - [ ] Subtask 1.3: Update URL construction for Jainam endpoints (15 min)
  - [ ] Subtask 1.4: Extract credential validation from helper script (15 min)
  - [ ] Subtask 1.5: Test with helper script credentials (15 min)

- [ ] Task 2: Update web integration (AC: 1) - **20 minutes**
  - [ ] Subtask 2.1: Add Jainam case to `blueprints/brlogin.py` using FivePaisaXTS pattern (10 min)
  - [ ] Subtask 2.2: Test web login flow (10 min)

- [ ] Task 3: Verify token persistence (AC: 2, 4) - **30 minutes**
  - [ ] Subtask 3.1: Verify `upsert_auth()` stores both tokens correctly (10 min)
  - [ ] Subtask 3.2: Verify `get_auth_token()` retrieves interactive token (10 min)
  - [ ] Subtask 3.3: Verify `get_feed_token()` retrieves market token (10 min)
  - [ ] Note: Database functions already complete - verification only

- [ ] Task 4: Pro feature inventory and verification (AC: 7, 8) - **1 hour**
  - [ ] Subtask 4.1: Catalog dealer endpoints from `xts_connect.py` (15 min)
  - [ ] Subtask 4.2: Catalog bracket/cover order wrappers from Pro SDK (15 min)
  - [ ] Subtask 4.3: Catalog Pro market data message codes (1501, 1502, 1505, 1510, 1512) (15 min)
  - [ ] Subtask 4.4: Verify `clientID` passthrough for dealer operations (15 min)
  - [ ] Subtask 4.5: Create Pro feature verification checklist in `docs/bmad/qa/pro-feature-checklist.md` (15 min)
  - [ ] Subtask 4.6: Document Pro vs retail differences in code comments (15 min)

**Total Effort:** 3 hours

## Dev Notes

### Code Reuse Guidance - Pro vs Retail

**⚠️ CRITICAL DISTINCTION:**

**Use FivePaisaXTS (Retail) For:**
- ✅ Authentication pattern (direct login)
- ✅ HTTP client usage (`get_httpx_client()`)
- ✅ Error handling patterns
- ✅ Database integration (`upsert_auth`, `get_auth_token`, `get_feed_token`)
- ✅ Web integration (callback handler in `brlogin.py`)

**Use XTS Pro SDK For:**
- ✅ Dealer operations (`get_dealerposition_netwise`, `get_dealer_orderbook`, `get_dealer_tradebook`)
- ✅ Bracket/cover orders (`place_bracketorder`, `place_cover_order`)
- ✅ Pro market data codes (1501, 1502, 1505, 1510, 1512)
- ✅ Pro-specific parameters (`clientID` passthrough)

### Reference Files

**Primary Template (Retail Authentication):**
- **File:** `broker/fivepaisaxts/api/auth_api.py`
- **Lines:** 12-102
- **Why:** Same direct login pattern for retail and Pro
- **Reuse:** 90% - Only change environment variable names and URLs

**Pro SDK (Pro-Specific Features):**
- **Location:** `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/`
- **Purpose:** Pro-specific functionality (dealer ops, Pro orders, Pro market data)
- **Usage:** Wrap SDK, don't modify SDK sources

**Proven Pro Pattern:**
- **File:** `broker/jainam_prop/_sample_strategy/xts_connect.py`
- **Lines:** 46 (interactive_login), 225 (marketdata_login)
- **Purpose:** Reference implementation for Pro features
- **Usage:** Follow patterns for Pro-specific implementations

**Database Integration (Works for All):**
- **File:** `database/auth_db.py`
- **Functions:** `upsert_auth()`, `get_auth_token()`, `get_feed_token()`
- **Status:** ✅ 100% compatible with both retail and Pro
- **Usage:** Reuse as-is

**Helper Script (Validates Pattern):**
- **File:** `broker/jainam_prop/get_jainam_tokens.py`
- **Purpose:** Manual token generation for testing
- **Status:** ✅ Working, validates authentication pattern
- **Usage:** Test authentication before web integration

**Complete Analysis:**
- **File:** `docs/bmad/research/jainam-code-reuse-analysis.md`
- **Purpose:** Comprehensive code reuse analysis (1,266 lines)
- **Sections:** Authentication, Database, API, Mapping, Streaming, Web, Testing

### Implementation Steps

**Step 1: Copy FivePaisaXTS Retail Template (30 minutes)**
```python
# Copy from broker/fivepaisaxts/api/auth_api.py lines 12-102
# This is a RETAIL pattern but works for Pro authentication too

# Change environment variables:
# - BROKER_API_KEY → JAINAM_INTERACTIVE_API_KEY
# - BROKER_API_SECRET → JAINAM_INTERACTIVE_API_SECRET
# - BROKER_API_KEY_MARKET → JAINAM_MARKET_API_KEY
# - BROKER_API_SECRET_MARKET → JAINAM_MARKET_API_SECRET

# Change URLs:
# - INTERACTIVE_URL → get_jainam_base_url() + "/interactive"
# - MARKET_DATA_URL → get_jainam_base_url() + "/apimarketdata"

# Keep everything else the same - retail pattern works for Pro auth
```

**Step 2: Add Web Integration Using Retail Pattern (20 minutes)**
```python
# In blueprints/brlogin.py after line 410:
# Use FivePaisaXTS (retail) pattern - works for Pro too

elif broker == 'jainam_prop':
    logger.debug(f'Jainam Prop broker - direct login')
    auth_token, feed_token, user_id, error_message = auth_function()
    forward_url = 'broker.html'
```

**Step 3: Catalog Pro-Specific Features (1 hour)**
```python
# Reference: broker/jainam_prop/_sample_strategy/xts_connect.py

# Pro Dealer Endpoints (not in retail):
# - get_dealerposition_netwise()
# - get_dealer_orderbook()
# - get_dealer_tradebook()

# Pro Order Types (not in retail):
# - place_bracketorder()
# - place_cover_order()
# - modify_bracketorder()
# - cancel_bracketorder()

# Pro Market Data Codes (not in retail):
# - 1501: Touchline
# - 1502: Market Depth
# - 1505: Candle Data
# - 1510: Open Interest
# - 1512: LTP

# Pro Parameters:
# - clientID: Required for dealer operations
```

**Step 4: Test (30 minutes)**
```bash
# Run helper script to verify retail pattern works for Pro
python broker/jainam_prop/get_jainam_tokens.py

# Test web login
# Verify database storage
# Confirm session management
```

### Target Implementation (Adapted from FivePaisaXTS):
```python
# broker/jainam_prop/api/auth_api.py
import os
import httpx
from database.auth_db import store_broker_auth_token
from broker.jainam_prop.api.config import get_jainam_base_url

def authenticate_direct():
    """
    Direct authentication with Jainam XTS API (no request token needed)

    Returns:
        dict: {
            'interactive_token': str,
            'market_token': str,
            'user_id': str,
            'is_investor_client': bool
        }
    """
    # Get credentials from environment
    interactive_api_key = os.getenv('JAINAM_INTERACTIVE_API_KEY')
    interactive_api_secret = os.getenv('JAINAM_INTERACTIVE_API_SECRET')
    market_api_key = os.getenv('JAINAM_MARKET_API_KEY')
    market_api_secret = os.getenv('JAINAM_MARKET_API_SECRET')
    base_url = get_jainam_base_url()

    # Login to Interactive API
    interactive_response = httpx.post(
        f"{base_url}/interactive/user/session",
        json={"appKey": interactive_api_key, "secretKey": interactive_api_secret, "source": "WEBAPI"}
    )
    interactive_token = interactive_response.json()['result']['token']
    user_id = interactive_response.json()['result']['userID']

    # Login to Market Data API
    market_response = httpx.post(
        f"{base_url}/apimarketdata/auth/login",
        json={"appKey": market_api_key, "secretKey": market_api_secret, "source": "WEBAPI"}
    )
    market_token = market_response.json()['result']['token']

    # Store tokens
    store_broker_auth_token(broker="jainam_prop", user_id=user_id,
                           auth_token=interactive_token, market_token=market_token)

    return {'interactive_token': interactive_token, 'market_token': market_token,
            'user_id': user_id, 'is_investor_client': False}
```

**Reference Documentation:** See `docs/bmad/research/jainam-authentication-guide.md` for complete details.

**Helper Script:** Use `broker/jainam_prop/get_jainam_tokens.py` for manual token generation during testing.

### Anti-Patterns to Avoid

**❌ DO NOT:**
- Use checksum generation (existing Jainam code lines 34-37) - Kite/Zerodha pattern
- Use OAuth access tokens (Compositedge pattern) - Not applicable to Jainam
- Use request token parameters - Jainam uses direct login
- Create new database schema - Already compatible
- **Modify XTS Pro SDK sources** - Wrap, don't modify
- **Use retail endpoints for Pro features** - Use Pro SDK

**✅ DO:**
- Copy FivePaisaXTS retail authentication pattern (works for Pro)
- Use existing database functions (work for all brokers)
- Extract validation from helper script
- **Wrap XTS Pro SDK for Pro features**
- **Reference xts_connect.py for Pro patterns**
- Follow code reuse analysis guidance

### Pro vs Retail Feature Matrix

| Feature | Retail (FivePaisaXTS) | Pro (Jainam) | Implementation |
|---------|----------------------|--------------|----------------|
| **Authentication** | Direct login | Direct login | ✅ Use FivePaisaXTS pattern |
| **Database** | Dual-token | Dual-token | ✅ Use existing functions |
| **HTTP Client** | httpx | httpx | ✅ Use FivePaisaXTS pattern |
| **Error Handling** | Standard | Standard | ✅ Use FivePaisaXTS pattern |
| **Web Integration** | Direct callback | Direct callback | ✅ Use FivePaisaXTS pattern |
| **Dealer Operations** | ❌ Not available | ✅ Available | ⚠️ Use XTS Pro SDK |
| **Bracket Orders** | ❌ Not available | ✅ Available | ⚠️ Use XTS Pro SDK |
| **Cover Orders** | ❌ Not available | ✅ Available | ⚠️ Use XTS Pro SDK |
| **Pro Market Data** | ❌ Not available | ✅ Available | ⚠️ Use XTS Pro SDK |

**Key Takeaway:** Use retail patterns for common functionality, Pro SDK for Pro-specific features.

### Token Lifecycle Pattern

**Flow:**
```
1. User Login → authenticate_direct() (adapted from FivePaisaXTS)
2. Persist → database.auth_db.upsert_auth(user_id, auth_token, feed_token)
3. REST Call → Rehydrate auth_token via get_auth_token()
4. Streaming → Rehydrate feed_token via get_feed_token()
5. No re-auth on subsequent calls (tokens reused)
```

### Pro Feature Context

**Dealer Endpoints (require Pro account):**
- `get_dealer_orderbook(clientID)` - Fetch dealer-attributed orders
- `get_dealer_tradebook(clientID)` - Fetch dealer-attributed trades
- `get_dealerposition_netwise(clientID)` - Fetch dealer net positions

**Advanced Orders:**
- `place_bracketorder(...)` - Entry + Target + Stop-Loss
- `place_cover_order(...)` - Entry + Stop-Loss
- Modify/cancel variants for bracket/cover orders

**Market Data Codes:**
- 1501: Ticker
- 1502: Market Depth
- 1505: Open Interest
- 1510: Candlestick
- 1512: Index Data

### Database Schema Extension

**Existing `database.auth_db` table:**
```sql
user_id VARCHAR(255)
broker VARCHAR(50)
auth_token TEXT
token_expiry TIMESTAMP
```

**Required Extension:**
```sql
ALTER TABLE auth_db ADD COLUMN feed_token TEXT;  -- Market data token
```

### Testing Standards
- Unit tests for SDK login flow (mock SDK responses)
- Integration tests for token persistence and rehydration
- Regression tests confirming other brokers unaffected
- Pro feature inventory validation tests
- Performance tests for authentication latency (<2s)

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-08 | 1.0 | Initial story creation from Sprint Change Proposal | Sarah (PO) |

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## QA Results
