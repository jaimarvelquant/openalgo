# Story 1.2-5: Token Lifecycle Management Enhancement

**Status:** Ready for Development  
**Priority:** HIGH (Blocks streaming resilience)  
**Effort:** 0.75 days (6 hours) - **Code Reuse: 80%**  
**Original Effort:** 3 days (24 hours)  
**Savings:** 75% (18 hours saved)

---

## Story

As a **developer implementing Jainam Prop authentication**,  
I want **interactive and market tokens to persist in the database and be reused across sessions**,  
so that **the system doesn't re-authenticate on every startup and tokens are available for streaming/REST consumers**.

---

## Context

### Current State
- `authenticate_direct()` successfully obtains tokens from Jainam API
- Tokens are NOT persisted to `database.auth_db`
- System re-authenticates on every startup (inefficient)
- Streaming adapter cannot reuse persisted tokens

### Critical Discovery
**The database infrastructure ALREADY EXISTS!** 🎉

`database/auth_db.py` provides:
- ✅ `upsert_auth(name, auth_token, broker, feed_token, user_id)` - Store tokens
- ✅ `get_auth_token(name)` - Retrieve interactive token
- ✅ `get_feed_token(name)` - Retrieve market/feed token
- ✅ `get_user_id(name)` - Retrieve user ID
- ✅ Encryption/decryption with Fernet
- ✅ Caching with TTL (session-based)
- ✅ Revocation support

### Reference Implementation
**Source:** `broker/fivepaisaxts/api/auth_api.py:12-97`

FivePaisaXTS already uses these functions:
```python
# After authentication
return token, feed_token, user_id, None

# Streaming adapter retrieves tokens
auth_token = get_auth_token(user_id)
feed_token = get_feed_token(user_id)
```

### Code Reuse Strategy
**80% of code already exists - just need to use it!**

**What Already Exists:**
- ✅ Database schema with all required fields
- ✅ Encryption/decryption functions
- ✅ Upsert and retrieval functions
- ✅ Caching layer

**What to Add:**
- ✏️ Call `upsert_auth()` after successful authentication
- ✏️ Add token rehydration logic in API clients
- ✏️ Add token expiry validation (JWT exp claim)
- ✏️ Store dealer account metadata (is_investor_client, client_id)

---

## Acceptance Criteria

### AC1: Persist Tokens After Authentication ✅

**File:** `broker/jainam_prop/api/auth_api.py`

**Current Code (lines 178-251):**
```python
def authenticate_direct():
    # ... authentication logic ...
    return interactive_token, market_token, user_id, is_investor, client_id, None
```

**Updated Code:**
```python
from database.auth_db import upsert_auth

def authenticate_direct():
    # ... existing authentication logic ...
    
    # ✏️ ADD: Persist tokens to database
    if interactive_token and market_token and user_id:
        try:
            # Store tokens with dealer account metadata
            auth_token_json = json.dumps({
                'interactive_token': interactive_token,
                'user_id': user_id,
                'clientID': client_id,
                'isInvestorClient': is_investor
            })
            
            upsert_auth(
                name=user_id,
                auth_token=auth_token_json,
                broker='jainam_prop',
                feed_token=market_token,
                user_id=user_id,
                revoke=False
            )
            
            logger.info(f"Tokens persisted to database for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to persist tokens: {e}")
            # Don't fail authentication if persistence fails
    
    return interactive_token, market_token, user_id, is_investor, client_id, None
```

**Verification:**
- [ ] `upsert_auth()` called after successful authentication
- [ ] Tokens stored with dealer account metadata (clientID, isInvestorClient)
- [ ] Errors during persistence don't fail authentication
- [ ] Logging confirms successful persistence

---

### AC2: Rehydrate Tokens on Startup ✅

**Pattern:** Copy from `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py:59-66`

**File:** `broker/jainam_prop/streaming/jainam_adapter.py`

**Current Code (lines 29-50):**
```python
def initialize(self, broker_name, user_id, auth_data=None):
    if auth_data and 'market_token' in auth_data:
        self.market_token = auth_data['market_token']
    else:
        # Re-authenticate every time (inefficient!)
        market_token, error = authenticate_market_data()
```

**Updated Code (Copy from FivePaisaXTS):**
```python
from database.auth_db import get_auth_token, get_feed_token

def initialize(self, broker_name, user_id, auth_data=None):
    # ✅ COPIED FROM FivePaisaXTS (lines 59-66)
    if not auth_data:
        # Fetch tokens from database
        auth_token = get_auth_token(user_id)
        feed_token = get_feed_token(user_id)
        
        if not auth_token or not feed_token:
            logger.error(f"No tokens found for user {user_id}")
            raise ValueError(f"No tokens found for user {user_id}")
        
        self.market_token = feed_token
    else:
        # Use provided tokens
        self.market_token = auth_data.get('market_token')
```

**Verification:**
- [ ] Tokens retrieved from database on startup
- [ ] No re-authentication if valid tokens exist
- [ ] Graceful fallback if tokens not found

---

### AC3: Add Token Expiry Validation ✅

**File:** `broker/jainam_prop/api/auth_api.py`

**Add Helper Function:**
```python
import jwt
from datetime import datetime

def is_token_expired(token: str) -> bool:
    """
    Check if JWT token is expired.
    
    Args:
        token: JWT token string
    
    Returns:
        bool: True if expired, False if valid
    """
    try:
        # Decode without verification (just to check expiry)
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get('exp')
        
        if exp:
            expiry_time = datetime.fromtimestamp(exp)
            return datetime.now() > expiry_time
        
        # No expiry claim, assume valid
        return False
    except Exception as e:
        logger.warning(f"Could not decode token for expiry check: {e}")
        return True  # Assume expired if can't decode
```

**Update Token Retrieval:**
```python
def get_valid_tokens(user_id):
    """Get tokens from database, re-authenticate if expired"""
    from database.auth_db import get_auth_token, get_feed_token
    
    auth_token_json = get_auth_token(user_id)
    feed_token = get_feed_token(user_id)
    
    if not auth_token_json or not feed_token:
        logger.info(f"No tokens found for {user_id}, authenticating...")
        return authenticate_direct()
    
    # Parse auth token JSON
    auth_data = json.loads(auth_token_json)
    interactive_token = auth_data.get('interactive_token')
    
    # Check expiry
    if is_token_expired(interactive_token) or is_token_expired(feed_token):
        logger.info(f"Tokens expired for {user_id}, re-authenticating...")
        return authenticate_direct()
    
    # Tokens valid, return from database
    return (
        interactive_token,
        feed_token,
        auth_data.get('user_id'),
        auth_data.get('isInvestorClient'),
        auth_data.get('clientID'),
        None
    )
```

**Verification:**
- [ ] JWT tokens decoded to check expiry
- [ ] Expired tokens trigger re-authentication
- [ ] Valid tokens returned from database
- [ ] Graceful handling of non-JWT tokens

---

### AC4: Update API Clients to Use Persisted Tokens ✅

**Files to Update:**
- `broker/jainam_prop/api/order_api.py`
- `broker/jainam_prop/api/data.py`
- `broker/jainam_prop/api/funds.py`

**Pattern:**
```python
from broker.jainam_prop.api.auth_api import get_valid_tokens

def get_order_book(user_id):
    # Get tokens (from DB or re-authenticate if needed)
    interactive_token, _, _, _, _, error = get_valid_tokens(user_id)
    
    if error:
        return {"status": "error", "message": error}
    
    # Use token for API call
    return get_api_response("/interactive/orders/dealerorderbook", interactive_token)
```

**Verification:**
- [ ] All API functions use `get_valid_tokens()`
- [ ] Tokens reused from database when valid
- [ ] Re-authentication only when tokens expired/missing

---

## Implementation Steps

### Step 1: Add Token Persistence (30 minutes)
1. Import `upsert_auth` in `auth_api.py`
2. Add persistence call after successful authentication
3. Store dealer account metadata in JSON
4. Test token storage

### Step 2: Add Token Rehydration (30 minutes)
1. Copy pattern from FivePaisaXTS adapter
2. Update `jainam_adapter.py` to use `get_auth_token()` and `get_feed_token()`
3. Test token retrieval

### Step 3: Add Expiry Validation (1 hour)
1. Add `is_token_expired()` helper
2. Add `get_valid_tokens()` function
3. Test expiry logic with mock tokens

### Step 4: Update API Clients (2 hours)
1. Refactor `order_api.py` to use `get_valid_tokens()`
2. Refactor `data.py` to use `get_valid_tokens()`
3. Refactor `funds.py` to use `get_valid_tokens()`
4. Test all endpoints

### Step 5: Integration Testing (2 hours)
1. Test full authentication flow
2. Test token reuse on restart
3. Test token expiry and re-authentication
4. Test streaming adapter with persisted tokens

**Total Effort: ~6 hours (0.75 days)**

---

## Testing Strategy

### Unit Tests
```python
# broker/jainam_prop/api/test_auth_api.py

def test_token_persistence():
    """Test tokens are persisted after authentication"""
    # Authenticate and verify DB storage

def test_token_expiry_check():
    """Test JWT expiry validation"""
    # Test with expired and valid tokens

def test_token_rehydration():
    """Test tokens retrieved from database"""
    # Verify get_valid_tokens() returns DB tokens
```

### Integration Tests
```python
# broker/jainam_prop/test_token_lifecycle.py

def test_full_token_lifecycle():
    """Test authenticate → persist → retrieve → reuse"""
    # Full end-to-end test

def test_token_expiry_reauth():
    """Test re-authentication when tokens expired"""
    # Verify automatic re-auth
```

---

## Dependencies

**Requires:**
- ✅ `database.auth_db` module (already exists)
- ✅ `database.auth_db.upsert_auth()` (already exists)
- ✅ `database.auth_db.get_auth_token()` (already exists)
- ✅ `database.auth_db.get_feed_token()` (already exists)

**Blocks:**
- Story 1.5-1 (Streaming Adapter Refactor) - needs persisted tokens
- Story 1.5-2 (Capability Registry) - needs token parsing

---

## Success Metrics

- [ ] Tokens persisted to database after authentication
- [ ] Tokens retrieved from database on startup
- [ ] No re-authentication if valid tokens exist
- [ ] Expired tokens trigger automatic re-authentication
- [ ] Streaming adapter uses persisted tokens
- [ ] All API clients use token rehydration

---

## Code Reuse Summary

**Already Exists (No Code Needed):**
- ✅ Database schema (100%)
- ✅ Encryption/decryption (100%)
- ✅ Upsert function (100%)
- ✅ Retrieval functions (100%)
- ✅ Caching layer (100%)

**Jainam-Specific Additions:**
- ✏️ Call `upsert_auth()` after authentication (new)
- ✏️ Token expiry validation (new)
- ✏️ `get_valid_tokens()` helper (new)
- ✏️ Update API clients to use persisted tokens (new)

**Overall Code Reuse: 80%**  
**Effort Savings: 75% (18 hours saved)**

---

## Related Stories

- **Depends On:** None (uses existing database infrastructure)
- **Blocks:** Story 1.5-1, Story 1.5-2 (streaming needs persisted tokens)
- **Related:** Story 1.4-1 (HTTP Helper)

---

**Ready for Development** ✅

