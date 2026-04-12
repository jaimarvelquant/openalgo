# Story 1.2-5: Token Lifecycle Management Enhancement

## Status
ContextReadyDraft

## Story

As a developer implementing Jainam Prop authentication,
I want interactive and market tokens to persist in the database and be reused across sessions,
so that the system doesn't re-authenticate on every startup and tokens are available for streaming/REST consumers.

## Acceptance Criteria

1. **AC1: Persist Tokens After Authentication**
   - `upsert_auth()` called after successful authentication in `auth_api.py`
   - Tokens stored with dealer account metadata (clientID, isInvestorClient)
   - Errors during persistence don't fail authentication
   - Logging confirms successful persistence

2. **AC2: Rehydrate Tokens on Startup**
   - Tokens retrieved from database on startup in streaming adapter
   - No re-authentication if valid tokens exist
   - Graceful fallback if tokens not found

3. **AC3: Add Token Expiry Validation**
   - JWT tokens decoded to check expiry
   - Expired tokens trigger re-authentication
   - Valid tokens returned from database
   - Graceful handling of non-JWT tokens

4. **AC4: Update API Clients to Use Persisted Tokens**
   - All API functions use `get_valid_tokens()`
   - Tokens reused from database when valid
   - Re-authentication only when tokens expired/missing

## Tasks / Subtasks

- [ ] Task 1: Add token persistence (AC: 1)
  - [ ] Subtask 1.1: Import `upsert_auth` in `auth_api.py` (5 min)
  - [ ] Subtask 1.2: Add persistence call after successful authentication (15 min)
  - [ ] Subtask 1.3: Store dealer account metadata in JSON format (10 min)
  - [ ] Subtask 1.4: Add error handling for persistence failures (10 min)
  - [ ] Subtask 1.5: Test token storage in database (10 min)

- [ ] Task 2: Add token rehydration (AC: 2)
  - [ ] Subtask 2.1: Copy pattern from `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py:59-66` (10 min)
  - [ ] Subtask 2.2: Update `jainam_adapter.py` initialize method (15 min)
  - [ ] Subtask 2.3: Add token retrieval from database (10 min)
  - [ ] Subtask 2.4: Test token retrieval on adapter startup (10 min)

- [ ] Task 3: Add expiry validation (AC: 3)
  - [ ] Subtask 3.1: Add `is_token_expired()` helper function (20 min)
  - [ ] Subtask 3.2: Add `get_valid_tokens()` function (25 min)
  - [ ] Subtask 3.3: Test expiry logic with mock JWT tokens (15 min)
  - [ ] Subtask 3.4: Test re-authentication on expired tokens (15 min)

- [ ] Task 4: Update API clients (AC: 4)
  - [ ] Subtask 4.1: Refactor `order_api.py` to use `get_valid_tokens()` (40 min)
  - [ ] Subtask 4.2: Refactor `data.py` to use `get_valid_tokens()` (30 min)
  - [ ] Subtask 4.3: Refactor `funds.py` to use `get_valid_tokens()` (20 min)
  - [ ] Subtask 4.4: Test all endpoints with token reuse (30 min)

- [ ] Task 5: Integration testing
  - [ ] Subtask 5.1: Test full authentication flow with persistence (30 min)
  - [ ] Subtask 5.2: Test token reuse on system restart (30 min)
  - [ ] Subtask 5.3: Test token expiry and automatic re-authentication (30 min)
  - [ ] Subtask 5.4: Test streaming adapter with persisted tokens (30 min)

## Dev Notes

### Current State & Requirements

**Current State:**
- `authenticate_direct()` successfully obtains tokens from Jainam API
- Tokens are NOT persisted to `database.auth_db`
- System re-authenticates on every startup (inefficient)
- Streaming adapter cannot reuse persisted tokens

**Priority:** HIGH (Blocks streaming resilience)
**Estimated Effort:** 0.75 days (6 hours)
**Code Reuse:** 80% (database infrastructure already exists)

**Critical Discovery:** The database infrastructure ALREADY EXISTS! 🎉

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

[Source: broker/fivepaisaxts/api/auth_api.py#authentication]
[Source: broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py#token-rehydration]

### Code Reuse Strategy

**80% of code already exists - just need to use it!**

**What Already Exists:**
- Database schema with all required fields (100%)
- Encryption/decryption functions (100%)
- Upsert and retrieval functions (100%)
- Caching layer (100%)

**What to Add:**
- Call `upsert_auth()` after successful authentication (new)
- Add token rehydration logic in API clients (new)
- Add token expiry validation using JWT exp claim (new)
- Store dealer account metadata (is_investor_client, client_id) (new)

**Effort Savings:** 75% (18 hours saved, reduced from 3 days to 0.75 days)

### Implementation Patterns

**Pattern 1: Token Persistence (auth_api.py lines 178-251)**
```python
from database.auth_db import upsert_auth
import json

def authenticate_direct():
    # ... existing authentication logic ...
    
    # ADD: Persist tokens to database
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

**Pattern 2: Token Rehydration (jainam_adapter.py lines 29-50)**
```python
from database.auth_db import get_auth_token, get_feed_token

def initialize(self, broker_name, user_id, auth_data=None):
    # COPIED FROM FivePaisaXTS (lines 59-66)
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

**Pattern 3: Token Expiry Validation**
```python
import jwt
from datetime import datetime

def is_token_expired(token: str) -> bool:
    """Check if JWT token is expired"""
    try:
        decoded = jwt.decode(token, options={"verify_signature": False})
        exp = decoded.get('exp')
        
        if exp:
            expiry_time = datetime.fromtimestamp(exp)
            return datetime.now() > expiry_time
        
        return False  # No expiry claim, assume valid
    except Exception as e:
        logger.warning(f"Could not decode token for expiry check: {e}")
        return True  # Assume expired if can't decode

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

**Pattern 4: API Client Usage**
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

### Project Structure Notes

**Files to Modify:**
- `broker/jainam_prop/api/auth_api.py` - Add persistence, expiry validation, get_valid_tokens()
- `broker/jainam_prop/streaming/jainam_adapter.py` - Add token rehydration
- `broker/jainam_prop/api/order_api.py` - Use get_valid_tokens()
- `broker/jainam_prop/api/data.py` - Use get_valid_tokens()
- `broker/jainam_prop/api/funds.py` - Use get_valid_tokens()

**No New Files Required** - all database infrastructure exists

### Testing Standards

**Unit Tests:** `broker/jainam_prop/api/test_auth_api.py`
- Test tokens are persisted after authentication
- Test JWT expiry validation with expired and valid tokens
- Test tokens retrieved from database
- Test graceful handling of missing tokens

**Integration Tests:** `broker/jainam_prop/test_token_lifecycle.py`
- Test full lifecycle: authenticate → persist → retrieve → reuse
- Test re-authentication when tokens expired
- Test streaming adapter with persisted tokens

**Success Metrics:**
- Tokens persisted to database after authentication
- Tokens retrieved from database on startup
- No re-authentication if valid tokens exist
- Expired tokens trigger automatic re-authentication
- Streaming adapter uses persisted tokens
- All API clients use token rehydration

### Dependencies

**Requires (all exist):**
- `database.auth_db` module
- `database.auth_db.upsert_auth()`
- `database.auth_db.get_auth_token()`
- `database.auth_db.get_feed_token()`

**Blocks:**
- Story 1.5-1 (Streaming Adapter Refactor) - needs persisted tokens
- Story 1.5-2 (Capability Registry) - needs token parsing

**Related Stories:**
- Story 1.4-1 (HTTP Helper)

### References

- [Source: database/auth_db.py#upsert_auth]
- [Source: database/auth_db.py#get_auth_token]
- [Source: database/auth_db.py#get_feed_token]
- [Source: broker/fivepaisaxts/api/auth_api.py#authentication]
- [Source: broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py#token-rehydration]

## Dev Agent Record

### Context Reference

- [Story Context XML](/Users/maruth/projects/openalgo/docs/bmad/story-context-1.2.5.xml) - Generated: 2025-10-12

### Agent Model Used

<!-- Will be populated by dev agent during implementation -->

### Debug Log References

<!-- Dev agent will add test execution logs and debugging information here -->

### Completion Notes List

<!-- Dev agent will document implementation decisions and deviations here -->

### File List

<!-- Dev agent will list all created/modified files here -->
