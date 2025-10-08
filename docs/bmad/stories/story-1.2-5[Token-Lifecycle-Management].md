# Story 1.2-5: Token-Lifecycle-Management

## Status
Draft

## Estimated Effort
**6-8 hours** (reduced from 24-30 hours due to code reuse)

**Note:** Most token lifecycle work completed in Story 1.0-1. This story focuses on:
1. Reviewing existing API functions (2-3 hours)
2. Testing with live API (3-4 hours)
3. Standardizing error handling (1 hour)

## Story

**As a** developer ensuring reliable API operations,
**I want** to review and test existing API functions with live Jainam API,
**so that** all REST and streaming consumers work correctly with persisted tokens.

## ⚠️ CRITICAL: Most Work Already Complete

**Authentication implemented in Story 1.0-1:**
- ✅ `authenticate_direct()` function created
- ✅ Token persistence via `database.auth_db.upsert_auth()`
- ✅ Token rehydration via `get_auth_token()` and `get_feed_token()`
- ✅ Database schema supports dual-token storage

**This story focuses on:**
- ⚠️ Reviewing existing API functions in `order_api.py`, `data.py`, `funds.py`
- ⚠️ Testing functions with live Jainam API
- ⚠️ Standardizing error handling patterns
- ⚠️ Removing `DEFAULT_USER` placeholders

**Code Reuse:** 85% of API code already exists and follows good patterns

**Reference:** See `docs/bmad/research/jainam-code-reuse-analysis.md` Section 3

## Acceptance Criteria

1. **AC1**: Review `JainamAPI.authenticate()` and update to call `authenticate_direct()`
   - **Status:** Implemented in Story 1.0-1
   - **Change needed:** Update existing function to call new `authenticate_direct()`
   - **Effort:** 15 minutes

2. **AC2**: Review and test existing API functions in `order_api.py`
   - **Functions:** `place_order_api()`, `modify_order_api()`, `cancel_order_api()`, `get_order_book()`, etc.
   - **Status:** 85-90% reusable, needs testing/validation
   - **Effort:** 2-3 hours

3. **AC3**: Review and test existing API functions in `data.py`
   - **Functions:** `get_quotes()`, `get_depth()`, `get_historical()`
   - **Status:** 85% reusable, needs market token verification
   - **Effort:** 1-2 hours

4. **AC4**: Review and test existing API functions in `funds.py`
   - **Functions:** `get_margin()`, `get_balance()`
   - **Status:** 90% reusable, needs testing
   - **Effort:** 30 minutes

5. **AC5**: Standardize error handling across all API functions
   - **Template:** FivePaisaXTS error handling pattern
   - **Effort:** 1 hour

6. **AC6**: Remove `DEFAULT_USER` placeholders, use real `user_id` from database
   - **Location:** `order_api.py` line 86 and similar locations
   - **Effort:** 30 minutes

## Integration Verification

**IV1**: Verify authentication endpoints return structured payloads with `user_id`, `auth_token`, `market_token`
**IV2**: Test token rehydration in both REST calls and streaming adapter initialization
**IV3**: Run regression tests confirming login, persistence, and rehydration flows (mocked or sandbox)

## Tasks / Subtasks

- [ ] Task 1: Update `JainamAPI.authenticate()` (AC: 1) - **15 minutes**
  - [ ] Subtask 1.1: Update `api/order_api.py::JainamAPI.authenticate()` to call `authenticate_direct()` (10 min)
  - [ ] Subtask 1.2: Test authentication flow (5 min)

- [ ] Task 2: Review and test order API functions (AC: 2, 6) - **2-3 hours**
  - [ ] Subtask 2.1: Review `place_order_api()` - verify token handling, remove DEFAULT_USER (30 min)
  - [ ] Subtask 2.2: Test `place_order_api()` with live API (30 min)
  - [ ] Subtask 2.3: Review `modify_order_api()` (15 min)
  - [ ] Subtask 2.4: Test `modify_order_api()` with live API (15 min)
  - [ ] Subtask 2.5: Review `cancel_order_api()` (15 min)
  - [ ] Subtask 2.6: Test `cancel_order_api()` with live API (15 min)
  - [ ] Subtask 2.7: Review `get_order_book()`, `get_trade_book()`, `get_positions()` (30 min)
  - [ ] Subtask 2.8: Test all retrieval functions with live API (30 min)

- [ ] Task 3: Review and test market data functions (AC: 3) - **1-2 hours**
  - [ ] Subtask 3.1: Review `data.py` functions - verify market token usage (30 min)
  - [ ] Subtask 3.2: Test `get_quotes()` with live API (30 min)
  - [ ] Subtask 3.3: Test `get_depth()` with live API (15 min)
  - [ ] Subtask 3.4: Test `get_historical()` with live API (15 min)

- [ ] Task 4: Review and test funds functions (AC: 4) - **30 minutes**
  - [ ] Subtask 4.1: Review `funds.py` functions (15 min)
  - [ ] Subtask 4.2: Test `get_margin()` and `get_balance()` with live API (15 min)

- [ ] Task 5: Standardize error handling (AC: 5) - **1 hour**
  - [ ] Subtask 5.1: Review FivePaisaXTS error handling pattern (15 min)
  - [ ] Subtask 5.2: Update error handling in `order_api.py` (15 min)
  - [ ] Subtask 5.3: Update error handling in `data.py` (15 min)
  - [ ] Subtask 5.4: Update error handling in `funds.py` (15 min)

**Total Effort:** 6-8 hours

## Dev Notes

### Code Reuse Guidance

**⚠️ CRITICAL: Most Work Already Complete in Story 1.0-1**

**Completed in Story 1.0-1:**
- ✅ `authenticate_direct()` function (adapted from FivePaisaXTS)
- ✅ Token persistence via `database.auth_db.upsert_auth()`
- ✅ Token rehydration via `get_auth_token()` and `get_feed_token()`
- ✅ Database schema supports dual-token storage

**This Story Focuses On:**
- ⚠️ Reviewing existing API functions (85% reusable)
- ⚠️ Testing with live Jainam API
- ⚠️ Standardizing error handling
- ⚠️ Removing placeholders

### Existing API Functions - Reuse Analysis

**File:** `broker/jainam_prop/api/order_api.py`
**Status:** 85-90% reusable
**Reference:** See `docs/bmad/research/jainam-code-reuse-analysis.md` Section 3

**Functions to Review:**
- `place_order_api()` - Lines 57-120 (90% reusable)
- `modify_order_api()` - Lines ~120-200 (85% reusable)
- `cancel_order_api()` - Lines ~200-280 (85% reusable)
- `get_order_book()` - Lines ~360-440 (85% reusable)
- `get_trade_book()` - Lines ~440-520 (85% reusable)
- `get_positions()` - Lines ~520-600 (85% reusable)

**Changes Needed:**
1. Update `JainamAPI.authenticate()` to call `authenticate_direct()` (15 min)
2. Remove `DEFAULT_USER` placeholders, use real user_id (30 min)
3. Standardize error handling per FivePaisaXTS pattern (1 hour)
4. Test all functions with live API (3-4 hours)

### Relevant Source Tree
- `broker/jainam_prop/api/auth_api.py` - Authentication (✅ complete in Story 1.0-1)
- `database/auth_db.py` - Token persistence (✅ complete, no changes needed)
- `broker/jainam_prop/api/order_api.py` - REST consumer (⚠️ review/test)
- `broker/jainam_prop/api/data.py` - REST consumer (⚠️ review/test)
- `broker/jainam_prop/api/funds.py` - REST consumer (⚠️ review/test)
- `broker/fivepaisaxts/api/auth_api.py` - Error handling reference

### Token Lifecycle Context

**Current State (After Story 1.0-1):**
- ✅ Tokens obtained via `authenticate_direct()`
- ✅ Tokens persisted to database
- ✅ Token rehydration functions available
- ⚠️ API functions need testing with live API

**Target State (This Story):**
- ✅ All API functions tested with live Jainam API
- ✅ Error handling standardized across all functions
- ✅ `DEFAULT_USER` placeholders removed
- ✅ Token rehydration working correctly

**Example: Update JainamAPI.authenticate():**
```python
# broker/jainam_prop/api/order_api.py
class JainamAPI:
    def authenticate(self):
        """Authenticate with Jainam API"""
        from broker.jainam_prop.api.auth_api import authenticate_direct

        # ✅ NEW - Use direct login (implemented in Story 1.0-1)
        auth_token, feed_token, user_id, error = authenticate_direct()
        if error:
            logger.error(f"Authentication failed: {error}")
            return False

        self.interactive_token = auth_token
        self.market_token = feed_token
        self.user_id = user_id
        return True
```

**Example: Remove DEFAULT_USER Placeholder:**
```python
# broker/jainam_prop/api/order_api.py
def place_order_api(data, auth_token):
    jainam_api = JainamAPI()
    jainam_api.interactive_token = auth_token

    # Transform data
    jainam_order = transform_data(data)

    # ❌ OLD - Don't use DEFAULT_USER
    # jainam_order['clientID'] = 'DEFAULT_USER'

    # ✅ NEW - Get real user_id from database
    from database.auth_db import get_auth_token_dbquery
    auth_obj = get_auth_token_dbquery(session['user'])
    jainam_order['clientID'] = auth_obj.user_id if auth_obj else 'DEFAULT_USER'

    # Make API call...
```

**Example: Standardize Error Handling (from FivePaisaXTS):**
```python
try:
    response = client.post(url, json=payload, headers=headers)
    response.raise_for_status()  # ✅ Raises HTTPStatusError for 4xx/5xx

    data = response.json()

    if data.get('type') == 'success':
        # Success case
        return result, None
    else:
        # API returned error
        error_msg = data.get('description', 'Unknown error')
        return None, f"API error: {error_msg}"

except httpx.HTTPStatusError as e:
    return None, f"HTTP error: {e.response.status_code} - {e.response.text}"
except httpx.RequestError as e:
    return None, f"Network error: {str(e)}"
except Exception as e:
    return None, f"Unexpected error: {str(e)}"
```

### Migration Guidance

**Existing Token Schema:**
```sql
-- Current auth_db table
user_id VARCHAR(255)
broker VARCHAR(50)
auth_token TEXT
token_expiry TIMESTAMP
```

**Migration Steps:**
1. Add `feed_token` column: `ALTER TABLE auth_db ADD COLUMN feed_token TEXT;`
2. Backfill missing `feed_token` values by re-running `authenticate_and_store()`
3. Update consuming code to use `get_auth_token_broker()` helper
4. Validate no direct environment variable reads remain for runtime tokens

### Service Layer Integration

**Services Requiring Updates:**
- `services/order_service.py` - Pass `user_id` to order API functions
- `services/holdings_service.py` - Pass `user_id` for token rehydration
- `services/positionbook_service.py` - Pass `user_id` for token rehydration
- `services/tradebook_service.py` - Pass `user_id` for token rehydration

### Testing Standards
- Unit tests for `authenticate_and_store()` with mocked SDK responses
- Integration tests for token persistence and rehydration (mocked or sandbox)
- Regression tests confirming REST and streaming flows work with DB tokens
- Performance tests for token lookup latency (<100ms from cache)
- Error handling tests for missing tokens in DB

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
