# Story 1.6-2: SDK Integration Strategy

**Status:** Ready for Development  
**Priority:** MEDIUM (Maintainability and SDK management)  
**Effort:** 1 day (8 hours) - **Code Reuse: 50%**  
**Original Effort:** 2 days (16 hours)  
**Savings:** 50% (8 hours saved)

---

## Story

As a **developer maintaining Jainam Prop broker integration**,  
I want **XTS Pro SDK usage standardized with wrapper utilities and upgrade documentation**,  
so that **SDK dependencies are isolated, upgrades are manageable, and custom logic is separated from SDK code**.

---

## Context

### Current State
- XTS Pro SDK used directly in some modules
- SDK imports scattered across codebase
- No wrapper layer for SDK-specific logic
- No SDK upgrade procedure documented
- SDK version compatibility unclear

### Reference Implementation
**Source:** `broker/fivepaisaxts/streaming/fivepaisaxts_websocket.py`

FivePaisaXTS has SDK wrapper pattern:
- ✅ SDK imports isolated to specific modules
- ✅ Wrapper classes for SDK clients
- ✅ Custom logic separated from SDK calls
- ✅ Clear SDK boundaries

### Code Reuse Strategy
**50% can be copied from FivePaisaXTS**

**What to Copy:**
- SDK wrapper class structure
- Import isolation pattern
- Error handling patterns
- Logging patterns

**What to Build (Jainam-Specific):**
- XTS Pro SDK wrapper
- Upgrade procedure documentation
- Version compatibility matrix
- SDK-specific utilities

---

## Acceptance Criteria

### AC1: Create SDK Wrapper Module ✅

**Pattern:** Copy from `broker/fivepaisaxts/streaming/fivepaisaxts_websocket.py`

**File:** `broker/jainam_prop/sdk/xts_wrapper.py`

**Implementation:**
```python
"""
XTS Pro SDK Wrapper

Isolates XTS Pro SDK dependencies and provides a clean interface
for authentication and WebSocket operations.

✅ COPY WRAPPER PATTERN FROM FivePaisaXTS
✏️ ADAPT for XTS Pro SDK
"""
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class XTSProSDKWrapper:
    """
    Wrapper for XTS Pro SDK to isolate SDK-specific logic.
    
    ✅ COPY STRUCTURE FROM FivePaisaXTS websocket wrapper
    ✏️ ADAPT for XTS Pro SDK
    """
    
    def __init__(self, api_key: str, api_secret: str, source: str = "WEBAPI"):
        """
        Initialize XTS Pro SDK wrapper.
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
            source: API source identifier
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.source = source
        self._sdk_client = None
        self.logger = logger
    
    def _import_sdk(self):
        """
        Lazy import of XTS Pro SDK.
        
        ✅ COPY LAZY IMPORT PATTERN FROM FivePaisaXTS
        
        This isolates SDK imports to only when needed,
        making it easier to mock for testing.
        """
        try:
            # ✏️ ADAPT: Import XTS Pro SDK
            from broker.jainam_prop._sample_strategy.xts_connect import XTSConnect
            return XTSConnect
        except ImportError as e:
            self.logger.error(f"Failed to import XTS Pro SDK: {e}")
            raise ImportError(
                "XTS Pro SDK not found. Ensure _sample_strategy/xts_connect.py exists."
            )
    
    def login_interactive(self) -> Dict[str, Any]:
        """
        Login to Interactive API using SDK.
        
        ✅ COPY ERROR HANDLING PATTERN FROM FivePaisaXTS
        ✏️ ADAPT for XTS Pro SDK login
        
        Returns:
            dict: Login response with token
        """
        try:
            XTSConnect = self._import_sdk()
            
            # ✏️ ADAPT: Create XTS Pro SDK client
            self._sdk_client = XTSConnect(
                apiKey=self.api_key,
                secretKey=self.api_secret,
                source=self.source
            )
            
            # ✏️ ADAPT: Call SDK login method
            response = self._sdk_client.interactive_login()
            
            self.logger.info("Interactive API login successful via SDK")
            return response
            
        except Exception as e:
            self.logger.error(f"Interactive API login failed: {e}")
            raise
    
    def login_market_data(self) -> Dict[str, Any]:
        """
        Login to Market Data API using SDK.
        
        ✅ COPY ERROR HANDLING PATTERN FROM FivePaisaXTS
        ✏️ ADAPT for XTS Pro SDK market data login
        
        Returns:
            dict: Login response with token
        """
        try:
            XTSConnect = self._import_sdk()
            
            # ✏️ ADAPT: Create XTS Pro SDK client
            self._sdk_client = XTSConnect(
                apiKey=self.api_key,
                secretKey=self.api_secret,
                source=self.source
            )
            
            # ✏️ ADAPT: Call SDK market data login
            response = self._sdk_client.marketdata_login()
            
            self.logger.info("Market Data API login successful via SDK")
            return response
            
        except Exception as e:
            self.logger.error(f"Market Data API login failed: {e}")
            raise
    
    def get_sdk_client(self):
        """
        Get the underlying SDK client instance.
        
        Use sparingly - prefer wrapper methods.
        """
        return self._sdk_client


class XTSProWebSocketWrapper:
    """
    Wrapper for XTS Pro WebSocket SDK.
    
    ✅ COPY STRUCTURE FROM FivePaisaXTS
    ✏️ ADAPT for XTS Pro WebSocket
    """
    
    def __init__(self, token: str, user_id: str):
        """
        Initialize WebSocket wrapper.
        
        Args:
            token: Market data token
            user_id: User ID
        """
        self.token = token
        self.user_id = user_id
        self._ws_client = None
        self.logger = logger
    
    def _import_sdk(self):
        """Lazy import of XTS WebSocket SDK."""
        try:
            from broker.jainam_prop._sample_strategy.xts_connect import XTSConnect
            return XTSConnect
        except ImportError as e:
            self.logger.error(f"Failed to import XTS WebSocket SDK: {e}")
            raise
    
    def connect(self, on_message_callback, on_connect_callback=None, on_disconnect_callback=None):
        """
        Connect to WebSocket with callbacks.
        
        ✅ COPY CALLBACK PATTERN FROM FivePaisaXTS
        ✏️ ADAPT for XTS Pro WebSocket
        """
        try:
            XTSConnect = self._import_sdk()
            
            # ✏️ ADAPT: Create WebSocket client
            self._ws_client = XTSConnect(
                token=self.token,
                userID=self.user_id
            )
            
            # ✏️ ADAPT: Set callbacks
            if on_message_callback:
                self._ws_client.on_message = on_message_callback
            if on_connect_callback:
                self._ws_client.on_connect = on_connect_callback
            if on_disconnect_callback:
                self._ws_client.on_disconnect = on_disconnect_callback
            
            # ✏️ ADAPT: Connect
            self._ws_client.connect()
            
            self.logger.info("WebSocket connected via SDK")
            
        except Exception as e:
            self.logger.error(f"WebSocket connection failed: {e}")
            raise
    
    def subscribe(self, instruments: list, mode: int):
        """
        Subscribe to instruments.
        
        ✏️ ADAPT for XTS Pro subscription format
        """
        if not self._ws_client:
            raise RuntimeError("WebSocket not connected")
        
        try:
            self._ws_client.subscribe(instruments, mode)
            self.logger.info(f"Subscribed to {len(instruments)} instruments")
        except Exception as e:
            self.logger.error(f"Subscription failed: {e}")
            raise
    
    def unsubscribe(self, instruments: list):
        """Unsubscribe from instruments."""
        if not self._ws_client:
            raise RuntimeError("WebSocket not connected")
        
        try:
            self._ws_client.unsubscribe(instruments)
            self.logger.info(f"Unsubscribed from {len(instruments)} instruments")
        except Exception as e:
            self.logger.error(f"Unsubscription failed: {e}")
            raise
    
    def disconnect(self):
        """Disconnect WebSocket."""
        if self._ws_client:
            try:
                self._ws_client.disconnect()
                self.logger.info("WebSocket disconnected")
            except Exception as e:
                self.logger.error(f"Disconnect failed: {e}")
```

**Verification:**
- [ ] SDK imports isolated to wrapper module
- [ ] Lazy import pattern implemented
- [ ] Error handling consistent
- [ ] Logging added for all operations
- [ ] Wrapper methods cover all SDK usage

---

### AC2: Update Existing Code to Use Wrapper ✅

**Modules to Update:**

1. **`broker/jainam_prop/api/auth_api.py`**
```python
# Before
from _sample_strategy.xts_connect import XTSConnect
client = XTSConnect(api_key, api_secret)

# After
from broker.jainam_prop.sdk.xts_wrapper import XTSProSDKWrapper
wrapper = XTSProSDKWrapper(api_key, api_secret)
response = wrapper.login_interactive()
```

2. **`broker/jainam_prop/streaming/jainam_websocket.py`**
```python
# Before
from _sample_strategy.xts_connect import XTSConnect
ws_client = XTSConnect(token, user_id)

# After
from broker.jainam_prop.sdk.xts_wrapper import XTSProWebSocketWrapper
ws_wrapper = XTSProWebSocketWrapper(token, user_id)
ws_wrapper.connect(on_message_callback)
```

**Verification:**
- [ ] No direct SDK imports outside wrapper
- [ ] All SDK usage goes through wrapper
- [ ] Existing functionality preserved

---

### AC3: Document SDK Upgrade Procedure ✅

**Create:** `broker/jainam_prop/sdk/SDK_UPGRADE_GUIDE.md`

```markdown
# XTS Pro SDK Upgrade Guide

## Current SDK Version
- **Version:** XTS Pro SDK (from _sample_strategy)
- **Location:** `broker/jainam_prop/_sample_strategy/`
- **Wrapper:** `broker/jainam_prop/sdk/xts_wrapper.py`

## SDK Version Compatibility Matrix

| OpenAlgo Version | XTS Pro SDK Version | Compatibility | Notes |
|------------------|---------------------|---------------|-------|
| 1.0.0 | Current | ✅ Compatible | Initial integration |

## Upgrade Procedure

### Step 1: Backup Current SDK
```bash
cp -r broker/jainam_prop/_sample_strategy broker/jainam_prop/_sample_strategy.backup
```

### Step 2: Review SDK Changes
- Check SDK changelog for breaking changes
- Review new features and deprecations
- Identify affected wrapper methods

### Step 3: Update SDK Files
```bash
# Replace SDK files with new version
# Preserve any custom modifications
```

### Step 4: Update Wrapper
- Update `xts_wrapper.py` for SDK changes
- Add new SDK methods if needed
- Update error handling if SDK errors changed

### Step 5: Run Tests
```bash
pytest broker/jainam_prop/sdk/test_xts_wrapper.py
pytest broker/jainam_prop/api/test_auth_api.py
pytest broker/jainam_prop/streaming/test_jainam_adapter.py
```

### Step 6: Integration Testing
- Test authentication (interactive + market data)
- Test WebSocket connection
- Test order placement
- Test position retrieval

### Step 7: Rollback Plan
```bash
# If upgrade fails, restore backup
rm -rf broker/jainam_prop/_sample_strategy
mv broker/jainam_prop/_sample_strategy.backup broker/jainam_prop/_sample_strategy
```

## Breaking Change Checklist

- [ ] Authentication method signatures changed?
- [ ] WebSocket connection parameters changed?
- [ ] Response format changed?
- [ ] Error codes changed?
- [ ] New required parameters added?

## Post-Upgrade Validation

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Authentication works (interactive + market data)
- [ ] WebSocket streaming works
- [ ] Order placement works
- [ ] Position retrieval works
- [ ] No regression in existing functionality
```

**Verification:**
- [ ] Upgrade procedure documented
- [ ] Compatibility matrix created
- [ ] Rollback plan documented
- [ ] Testing checklist provided

---

## Implementation Steps

### Step 1: Create SDK Wrapper (3 hours)
1. Create `broker/jainam_prop/sdk/` directory
2. Create `xts_wrapper.py` with wrapper classes
3. Implement lazy import pattern
4. Add error handling and logging

### Step 2: Update Existing Code (3 hours)
1. Update `auth_api.py` to use wrapper
2. Update `jainam_websocket.py` to use wrapper
3. Remove direct SDK imports
4. Test all updated modules

### Step 3: Create Documentation (2 hours)
1. Create `SDK_UPGRADE_GUIDE.md`
2. Document upgrade procedure
3. Create compatibility matrix
4. Add testing checklist

**Total Effort: ~8 hours (1 day)**

---

## Testing Strategy

### Wrapper Tests
```python
# broker/jainam_prop/sdk/test_xts_wrapper.py

def test_sdk_wrapper_login():
    """Test SDK wrapper login"""
    # Test interactive login
    # Test market data login

def test_sdk_lazy_import():
    """Test lazy import pattern"""
    # Verify SDK not imported until needed

def test_websocket_wrapper():
    """Test WebSocket wrapper"""
    # Test connection
    # Test subscription
```

---

## Dependencies

**Requires:**
- ✅ XTS Pro SDK in `_sample_strategy/` (already exists)

**Blocks:**
- None (enhancement to existing functionality)

---

## Success Metrics

- [ ] SDK wrapper module created
- [ ] All SDK usage goes through wrapper
- [ ] No direct SDK imports outside wrapper
- [ ] Upgrade procedure documented
- [ ] Compatibility matrix created
- [ ] All tests passing

---

## Code Reuse Summary

**Reused from FivePaisaXTS:**
- ✅ Wrapper class structure (100%)
- ✅ Lazy import pattern (100%)
- ✅ Error handling patterns (100%)
- ✅ Callback patterns (100%)

**Jainam-Specific Additions:**
- ✏️ XTS Pro SDK integration (new)
- ✏️ Upgrade procedure (new)
- ✏️ Compatibility matrix (new)
- ✏️ SDK-specific utilities (new)

**Overall Code Reuse: 50%**  
**Effort Savings: 50% (8 hours saved)**

---

## Related Stories

- **Enhances:** All stories using SDK
- **Related:** Story 1.6-1 (Configuration)

---

**Ready for Development** ✅

