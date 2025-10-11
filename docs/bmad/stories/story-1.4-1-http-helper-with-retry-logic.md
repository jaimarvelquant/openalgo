# Story 1.4-1: HTTP Helper with Retry Logic

**Status:** Ready for Development  
**Priority:** HIGH (Foundation for all REST calls)  
**Effort:** 0.5 days (4 hours) - **Code Reuse: 90%**  
**Original Effort:** 2 days (16 hours)  
**Savings:** 75% (12 hours saved)

---

## Story

As a **developer implementing Jainam Prop REST API calls**,  
I want **a centralized HTTP helper function with retry logic and structured logging**,  
so that **all API calls have consistent error handling, automatic retries on transient failures, and detailed telemetry for debugging**.

---

## Context

### Current State
- REST modules (`order_api.py`, `data.py`, `funds.py`) make ad-hoc HTTP calls
- No retry logic for transient failures (5xx, 429, network errors)
- Inconsistent error handling across modules
- Missing structured logging (endpoint, status, latency, attempts)

### Reference Implementation
**Source:** `broker/fivepaisaxts/api/order_api.py:15-44`

FivePaisaXTS has a proven `get_api_response()` function that:
- ✅ Uses shared `httpx` client via `utils.httpx_client.get_httpx_client()`
- ✅ Provides consistent request/response handling
- ✅ Handles GET/POST/PUT/DELETE methods uniformly
- ✅ Returns JSON responses with status code

### Code Reuse Strategy
**90% of code can be copied directly from FivePaisaXTS**

**What to Copy:**
- Function signature and structure
- HTTP method handling (GET/POST/PUT/DELETE)
- Header construction pattern
- Response handling
- Shared httpx client usage

**What to Adapt:**
- Base URL (use `get_jainam_base_url()` instead of `INTERACTIVE_URL`)
- Add retry logic with exponential backoff
- Add structured logging
- Add network error handling

---

## Acceptance Criteria

### AC1: Create HTTP Helper Module ✅

**File:** `broker/jainam_prop/api/http_helper.py`

**Implementation Steps:**
1. **COPY** `get_api_response()` from `broker/fivepaisaxts/api/order_api.py:15-44`
2. **ADAPT** base URL to use `get_jainam_base_url()`
3. **ADD** retry logic with exponential backoff
4. **ADD** structured logging

**Function Signature:**
```python
def get_api_response(
    endpoint: str,
    auth: str,
    method: str = "GET",
    payload: dict = None,
    retries: int = 3,
    backoff_min: float = 0.25,
    backoff_max: float = 2.0
) -> dict:
```

**Verification:**
- [ ] Function uses shared `httpx` client from `utils.httpx_client.get_httpx_client()`
- [ ] Retries on 5xx, 429, network errors
- [ ] Exponential backoff: delay = min(backoff_min * (2 ** attempt), backoff_max)
- [ ] Structured logging includes: endpoint, method, status, latency, attempt
- [ ] Returns JSON response with `response.status` attribute (FivePaisaXTS pattern)

---

### AC2: Refactor `order_api.py` to Use Helper ✅

**Pattern:** Copy from `broker/fivepaisaxts/api/order_api.py:46-56`

**Before (Current):**
```python
def get_order_book(auth_token):
    client = OrderAPIClient(auth_token=auth_token)
    response_data = client.get_dealer_orderbook(client_id="*****")
    # ... manual error handling
```

**After (Using Helper):**
```python
from broker.jainam_prop.api.http_helper import get_api_response

def get_order_book(auth_token):
    return get_api_response(
        "/interactive/orders/dealerorderbook?clientID=*****",
        auth_token
    )
```

**Endpoints to Refactor:**
- [ ] `get_order_book()` → `/interactive/orders/dealerorderbook?clientID=*****`
- [ ] `get_trade_book()` → `/interactive/orders/dealertradebook?clientID=*****`
- [ ] `get_positions()` → `/interactive/portfolio/dealerpositions?dayOrNet=NetWise&clientID=*****`
- [ ] `get_holdings()` → `/interactive/portfolio/holdings?clientID=*****`
- [ ] `place_order_api()` → POST to `/interactive/orders` with clientID in body
- [ ] `modify_order_api()` → PUT to `/interactive/orders` with clientID in body
- [ ] `cancel_order_api()` → DELETE to `/interactive/orders` with clientID in body

**Verification:**
- [ ] All GET endpoints refactored
- [ ] All POST endpoints refactored
- [ ] All PUT/DELETE endpoints refactored
- [ ] No direct `httpx` calls remain in `order_api.py`
- [ ] Dealer account clientID parameter preserved

---

### AC3: Refactor `data.py` and `funds.py` ✅

**Apply same pattern as AC2**

**Files to Update:**
- [ ] `broker/jainam_prop/api/data.py` - all HTTP calls
- [ ] `broker/jainam_prop/api/funds.py` - all HTTP calls

**Verification:**
- [ ] All modules use `get_api_response()` helper
- [ ] Consistent error handling across all modules
- [ ] No direct `httpx` calls outside helper

---

### AC4: Add Configuration for Retry Behavior ✅

**File:** `broker/jainam_prop/api/config.py`

**Pattern:** Copy from `broker/fivepaisaxts/baseurl.py`

**Add Configuration:**
```python
import os

# Retry configuration
JAINAM_RETRY_ATTEMPTS = int(os.getenv('JAINAM_RETRY_ATTEMPTS', '3'))
JAINAM_RETRY_BACKOFF_MIN = float(os.getenv('JAINAM_RETRY_BACKOFF_MIN', '0.25'))
JAINAM_RETRY_BACKOFF_MAX = float(os.getenv('JAINAM_RETRY_BACKOFF_MAX', '2.0'))
```

**Update `.env.example`:**
```bash
# Jainam HTTP Retry Configuration
JAINAM_RETRY_ATTEMPTS=3
JAINAM_RETRY_BACKOFF_MIN=0.25
JAINAM_RETRY_BACKOFF_MAX=2.0
```

**Verification:**
- [ ] Configuration values can be overridden via environment variables
- [ ] Default values are sensible for production
- [ ] Helper function uses config values

---

## Implementation Steps

### Step 1: Copy Base Function (15 minutes)
1. Open `broker/fivepaisaxts/api/order_api.py`
2. Copy lines 15-44 (`get_api_response` function)
3. Create `broker/jainam_prop/api/http_helper.py`
4. Paste function

### Step 2: Adapt for Jainam (30 minutes)
1. Replace `INTERACTIVE_URL` with `get_jainam_base_url()`
2. Add retry loop with exponential backoff
3. Add structured logging (endpoint, method, status, latency, attempt)
4. Add error handling for network errors

### Step 3: Refactor order_api.py (1 hour)
1. Import `get_api_response` from `http_helper`
2. Replace all direct HTTP calls with helper calls
3. Preserve dealer account clientID logic
4. Test each endpoint

### Step 4: Refactor data.py and funds.py (1 hour)
1. Apply same refactoring pattern
2. Test all endpoints

### Step 5: Add Configuration (15 minutes)
1. Add retry config to `config.py`
2. Update helper to use config values
3. Update `.env.example`

### Step 6: Testing (1 hour)
1. Unit tests for retry logic
2. Integration tests for all refactored endpoints
3. Test with network failures (mock)

**Total Effort: ~4 hours (0.5 days)**

---

## Testing Strategy

### Unit Tests
**File:** `broker/jainam_prop/api/test_http_helper.py`

```python
import pytest
from unittest.mock import Mock, patch
from broker.jainam_prop.api.http_helper import get_api_response

def test_successful_request():
    """Test successful API call"""
    # Test happy path

def test_retry_on_500():
    """Test retry logic on 500 error"""
    # Verify exponential backoff

def test_no_retry_on_400():
    """Test no retry on client errors"""
    # Verify 4xx errors don't retry

def test_network_error_retry():
    """Test retry on network errors"""
    # Verify network errors trigger retry
```

### Integration Tests
**File:** `broker/jainam_prop/test_order_api_refactored.py`

```python
def test_get_order_book_with_retry():
    """Test order book retrieval with retry logic"""
    # Test actual API call with retry

def test_place_order_with_retry():
    """Test order placement with retry logic"""
    # Test POST with retry
```

---

## Dependencies

**Requires:**
- ✅ `utils.httpx_client.get_httpx_client()` (already exists)
- ✅ `broker.jainam_prop.api.config.get_jainam_base_url()` (already exists)
- ✅ `utils.logging.get_logger()` (already exists)

**Blocks:**
- All other stories benefit from this foundation
- Improves reliability of all REST endpoints immediately

---

## Success Metrics

- [ ] All REST modules use `get_api_response()` helper
- [ ] No direct `httpx` calls outside helper
- [ ] Retry logic tested with network failures
- [ ] Structured logging includes all required fields
- [ ] Configuration values can be overridden via environment
- [ ] Code coverage >90% for http_helper.py

---

## Code Reuse Summary

**Reused from FivePaisaXTS:**
- ✅ Function signature and structure (90%)
- ✅ HTTP method handling (100%)
- ✅ Header construction (100%)
- ✅ Response handling (100%)
- ✅ Shared httpx client usage (100%)

**Jainam-Specific Additions:**
- ✏️ Retry logic with exponential backoff (new)
- ✏️ Structured logging (new)
- ✏️ Network error handling (new)
- ✏️ Configuration for retry behavior (new)

**Overall Code Reuse: 90%**  
**Effort Savings: 75% (12 hours saved)**

---

## Related Stories

- **Depends On:** None (foundation story)
- **Blocks:** All REST API stories benefit from this
- **Related:** Story 1.6-1 (Configuration Management)

---

**Ready for Development** ✅

