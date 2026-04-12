# Story 1.5-1: Streaming Adapter Refactor

**Status:** Ready for Development  
**Priority:** HIGH (Critical for production streaming)  
**Effort:** 1.5 days (12 hours) - **Code Reuse: 70%**  
**Original Effort:** 4 days (32 hours)  
**Savings:** 62.5% (20 hours saved)

---

## Story

As a **developer implementing Jainam Prop WebSocket streaming**,  
I want **the streaming adapter to have reconnection logic, subscription replay, and token reuse**,  
so that **WebSocket connections are resilient to network failures and don't require re-authentication on every disconnect**.

---

## Context

### Current State
- `broker/jainam_prop/streaming/jainam_adapter.py` has basic Socket.IO connection
- **NO reconnection logic** - connection drops are fatal
- **NO subscription replay** - subscriptions lost on reconnect
- **NO token reuse** - re-authenticates on every initialization
- **NO state tracking** - no locks, no connection state management

### Reference Implementation
**Source:** `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py` (805 lines)

FivePaisaXTS has production-ready resilience:
- ✅ Reconnection with exponential backoff (lines 33-36)
- ✅ Subscription registry and replay (throughout)
- ✅ Token retrieval from database (lines 59-66)
- ✅ State tracking with threading locks (line 38)
- ✅ Connection lifecycle management (lines 43-105)

### Code Reuse Strategy
**70% of structure can be copied from FivePaisaXTS**

**What to Copy:**
- Reconnection logic with exponential backoff
- State tracking (running, reconnect_attempts, delays)
- Threading locks for thread safety
- Token retrieval from database
- Callback structure (_on_open, _on_close, _on_error)

**What to Adapt:**
- WebSocket client (Socket.IO vs FivePaisaXTS client)
- Message codes (1501/1502/1505/1510/1512 for Jainam)
- Subscription payload format
- Connection URL format

---

## Acceptance Criteria

### AC1: Add Reconnection Infrastructure ✅

**Pattern:** Copy from `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py:27-42`

**File:** `broker/jainam_prop/streaming/jainam_adapter.py`

**Add to `__init__`:**
```python
class JainamWebSocketAdapter(BaseBrokerWebSocketAdapter):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("jainam_websocket")
        self.ws_client = None
        self.user_id = None
        self.broker_name = "jainam_prop"
        
        # ✅ COPY FROM FivePaisaXTS (lines 33-38)
        self.reconnect_delay = 5  # Initial delay in seconds
        self.max_reconnect_delay = 60  # Maximum delay in seconds
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 10
        self.running = False
        self.lock = threading.Lock()  # Thread safety
        
        # ✏️ ADD: Subscription registry for replay
        self.subscriptions = {}  # {symbol: {exchange, mode, depth}}
```

**Verification:**
- [ ] Reconnection state variables added
- [ ] Threading lock added for thread safety
- [ ] Subscription registry added

---

### AC2: Implement Token Reuse from Database ✅

**Pattern:** Copy from `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py:59-95`

**Update `initialize()` method:**
```python
from database.auth_db import get_auth_token, get_feed_token

def initialize(self, broker_name: str, user_id: str, auth_data: Optional[Dict[str, str]] = None):
    self.user_id = user_id
    self.broker_name = broker_name
    
    # ✅ COPIED FROM FivePaisaXTS (lines 59-87)
    if not auth_data:
        # Fetch tokens from database
        auth_token = get_auth_token(user_id)
        feed_token = get_feed_token(user_id)
        
        if not auth_token or not feed_token:
            self.logger.error(f"No tokens found for user {user_id}")
            raise ValueError(f"No tokens found for user {user_id}")
        
        # Parse auth token JSON to get dealer account info
        import json
        auth_data_parsed = json.loads(auth_token)
        self.market_token = feed_token
        self.client_id = auth_data_parsed.get('clientID')
        self.is_investor = auth_data_parsed.get('isInvestorClient', True)
    else:
        # Use provided tokens
        self.market_token = auth_data.get('market_token')
        self.client_id = auth_data.get('client_id')
        self.is_investor = auth_data.get('is_investor', True)
    
    self.logger.info(f"Initialized with tokens from database for user {user_id}")
    
    # ✏️ ADAPT: Create Jainam WebSocket client
    from broker.jainam_prop.streaming.jainam_websocket import JainamWebSocketClient
    self.ws_client = JainamWebSocketClient(
        market_token=self.market_token,
        user_id=user_id,
        root_url=get_jainam_base_url()
    )
    
    # Set callbacks
    self.ws_client.on_connect_callback = self._on_open
    self.ws_client.on_message_callback = self._on_message
    self.ws_client.on_disconnect_callback = self._on_close
    self.ws_client.on_error_callback = self._on_error
    
    self.running = True
```

**Verification:**
- [ ] Tokens retrieved from database (not re-authenticating)
- [ ] Dealer account metadata extracted from auth token
- [ ] WebSocket client initialized with persisted tokens

---

### AC3: Implement Reconnection Logic ✅

**Pattern:** Copy from `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py` (reconnection methods)

**Add Reconnection Methods:**
```python
def _on_close(self, ws=None):
    """Handle WebSocket close event"""
    self.logger.warning("WebSocket connection closed")
    
    # ✅ COPY PATTERN FROM FivePaisaXTS
    if self.running and self.reconnect_attempts < self.max_reconnect_attempts:
        self._schedule_reconnect()
    else:
        self.logger.error("Max reconnection attempts reached or adapter stopped")
        self.running = False

def _schedule_reconnect(self):
    """Schedule reconnection with exponential backoff"""
    # ✅ COPY EXPONENTIAL BACKOFF FROM FivePaisaXTS
    delay = min(
        self.reconnect_delay * (2 ** self.reconnect_attempts),
        self.max_reconnect_delay
    )
    
    self.reconnect_attempts += 1
    self.logger.info(
        f"Scheduling reconnection attempt {self.reconnect_attempts}/{self.max_reconnect_attempts} "
        f"in {delay} seconds"
    )
    
    # Schedule reconnection in separate thread
    import threading
    threading.Timer(delay, self._reconnect).start()

def _reconnect(self):
    """Attempt to reconnect"""
    with self.lock:
        try:
            self.logger.info("Attempting to reconnect...")
            self.connect()
            
            # ✏️ ADD: Replay subscriptions after reconnect
            self._replay_subscriptions()
            
            # Reset reconnect attempts on successful connection
            self.reconnect_attempts = 0
            self.logger.info("Reconnection successful")
            
        except Exception as e:
            self.logger.error(f"Reconnection failed: {e}")
            self._schedule_reconnect()

def _replay_subscriptions(self):
    """Replay all subscriptions after reconnect"""
    self.logger.info(f"Replaying {len(self.subscriptions)} subscriptions...")
    
    for symbol, sub_data in self.subscriptions.items():
        try:
            self.subscribe(
                symbol=symbol,
                exchange=sub_data['exchange'],
                mode=sub_data['mode'],
                depth_level=sub_data.get('depth_level', 5)
            )
            self.logger.debug(f"Replayed subscription for {symbol}")
        except Exception as e:
            self.logger.error(f"Failed to replay subscription for {symbol}: {e}")
```

**Verification:**
- [ ] Exponential backoff implemented
- [ ] Max reconnection attempts enforced
- [ ] Subscriptions replayed after reconnect
- [ ] Thread-safe reconnection logic

---

### AC4: Add Subscription Registry ✅

**Update `subscribe()` method:**
```python
def subscribe(self, symbol: str, exchange: str, mode: int = 1, depth_level: int = 5):
    """Subscribe to market data with subscription tracking"""
    
    # ✏️ ADD: Store subscription for replay
    self.subscriptions[symbol] = {
        'exchange': exchange,
        'mode': mode,
        'depth_level': depth_level
    }
    
    # Existing subscription logic
    # ... (keep current implementation)
    
    self.logger.info(f"Subscribed to {symbol} on {exchange} (mode={mode})")
```

**Add `unsubscribe()` method:**
```python
def unsubscribe(self, symbol: str, exchange: str):
    """Unsubscribe from market data"""
    
    # Remove from subscription registry
    if symbol in self.subscriptions:
        del self.subscriptions[symbol]
    
    # Existing unsubscribe logic
    # ... (keep current implementation)
    
    self.logger.info(f"Unsubscribed from {symbol}")
```

**Verification:**
- [ ] Subscriptions stored in registry
- [ ] Subscriptions removed on unsubscribe
- [ ] Registry used for replay after reconnect

---

## Implementation Steps

### Step 1: Copy Reconnection Infrastructure (1 hour)
1. Copy state variables from FivePaisaXTS `__init__`
2. Add threading lock
3. Add subscription registry
4. Test initialization

### Step 2: Implement Token Reuse (1 hour)
1. Copy token retrieval pattern from FivePaisaXTS
2. Update `initialize()` to use database tokens
3. Parse dealer account metadata
4. Test token retrieval

### Step 3: Implement Reconnection Logic (3 hours)
1. Copy `_on_close()` from FivePaisaXTS pattern
2. Implement `_schedule_reconnect()` with exponential backoff
3. Implement `_reconnect()` method
4. Test reconnection with mock disconnects

### Step 4: Implement Subscription Replay (2 hours)
1. Update `subscribe()` to store subscriptions
2. Implement `_replay_subscriptions()`
3. Add `unsubscribe()` method
4. Test subscription replay

### Step 5: Integration Testing (5 hours)
1. Test full connection lifecycle
2. Test reconnection with network failures
3. Test subscription replay
4. Test token reuse from database
5. Load testing with multiple subscriptions

**Total Effort: ~12 hours (1.5 days)**

---

## Testing Strategy

### Unit Tests
```python
# broker/jainam_prop/streaming/test_jainam_adapter.py

def test_reconnection_backoff():
    """Test exponential backoff calculation"""
    # Verify delay increases exponentially

def test_subscription_registry():
    """Test subscription storage and retrieval"""
    # Verify subscriptions tracked correctly

def test_token_reuse():
    """Test tokens retrieved from database"""
    # Verify no re-authentication
```

### Integration Tests
```python
# broker/jainam_prop/streaming/test_streaming_resilience.py

def test_reconnection_on_disconnect():
    """Test automatic reconnection"""
    # Simulate disconnect, verify reconnect

def test_subscription_replay():
    """Test subscriptions replayed after reconnect"""
    # Disconnect, reconnect, verify subscriptions restored
```

---

## Dependencies

**Requires:**
- ✅ Story 1.2-5 (Token Lifecycle) - needs persisted tokens
- ✅ `database.auth_db.get_auth_token()` (already exists)
- ✅ `database.auth_db.get_feed_token()` (already exists)

**Blocks:**
- Production streaming deployment

---

## Success Metrics

- [ ] Automatic reconnection on disconnect
- [ ] Exponential backoff implemented
- [ ] Subscriptions replayed after reconnect
- [ ] Tokens reused from database
- [ ] Thread-safe connection management
- [ ] Max reconnection attempts enforced
- [ ] No re-authentication on reconnect

---

## Code Reuse Summary

**Reused from FivePaisaXTS:**
- ✅ Reconnection state variables (100%)
- ✅ Exponential backoff logic (100%)
- ✅ Token retrieval pattern (100%)
- ✅ Threading lock pattern (100%)
- ✅ Callback structure (100%)

**Jainam-Specific Adaptations:**
- ✏️ Socket.IO client integration (vs FivePaisaXTS client)
- ✏️ Subscription payload format
- ✏️ Message code handling (1501/1502/1505/1510/1512)
- ✏️ Connection URL format

**Overall Code Reuse: 70%**  
**Effort Savings: 62.5% (20 hours saved)**

---

## Related Stories

- **Depends On:** Story 1.2-5 (Token Lifecycle Management)
- **Related:** Story 1.5-2 (Capability Registry)
- **Blocks:** Production streaming deployment

---

**Ready for Development** ✅

