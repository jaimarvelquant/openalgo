# Story 1.5-2: Capability Registry & Token Validation

**Status:** Ready for Development  
**Priority:** HIGH (Streaming metadata and validation)  
**Effort:** 0.5 days (4 hours) - **Code Reuse: 85%**  
**Original Effort:** 2 days (16 hours)  
**Savings:** 75% (12 hours saved)

---

## Story

As a **developer implementing Jainam Prop streaming**,  
I want **a capability registry defining supported exchanges/depth levels and JWT token parsing for user ID extraction**,  
so that **the system validates subscriptions against broker capabilities and extracts actual user IDs from feed tokens**.

---

## Context

### Current State
- No capability metadata for Jainam broker
- No validation of exchange/depth level support
- Feed tokens not parsed to extract user IDs
- No fallback logic for unsupported depth levels

### Reference Implementation
**Source:** `broker/fivepaisaxts/streaming/fivepaisaxts_mapping.py:121-184`

FivePaisaXTS has complete capability registry:
- ✅ Supported exchanges list (line 128)
- ✅ Subscription modes (line 129)
- ✅ Depth support by exchange (lines 130-137)
- ✅ Depth level validation (lines 153-165)
- ✅ Fallback depth calculation (lines 167-184)

**Source:** `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py:140-175`

FivePaisaXTS has JWT token parsing:
- ✅ Base64 decode JWT payload (lines 151-158)
- ✅ Extract userID from token (line 165)
- ✅ Graceful fallback on parse errors (line 173)

### Code Reuse Strategy
**85% can be copied directly from FivePaisaXTS**

**What to Copy:**
- Capability registry class structure
- All class methods (get_supported_depth_levels, is_depth_level_supported, get_fallback_depth_level)
- JWT parsing logic
- Error handling patterns

**What to Adapt:**
- Message codes (1501/1502/1505/1510/1512 for Jainam)
- Exchange list (verify Jainam supports same exchanges)
- Depth support (verify Jainam depth levels)

---

## Acceptance Criteria

### AC1: Create Jainam Capability Registry ✅

**Pattern:** Copy from `broker/fivepaisaxts/streaming/fivepaisaxts_mapping.py:121-184`

**File:** `broker/jainam_prop/streaming/jainam_mapping.py`

**Implementation:**
```python
class JainamCapabilityRegistry:
    """
    Registry of Jainam broker capabilities including supported exchanges,
    subscription modes, and market depth levels.
    
    Copied from FivepaisaXTSCapabilityRegistry with Jainam-specific adaptations.
    """
    
    # ✅ COPY STRUCTURE FROM FivePaisaXTS (line 128)
    # ✏️ ADAPT: Verify Jainam supports these exchanges
    exchanges = ['NSE', 'NFO', 'CDS', 'BSE', 'BFO', 'MCX']
    
    # ✏️ ADAPT: Jainam message codes (not subscription modes 1/2/3)
    message_codes = [1501, 1502, 1505, 1510, 1512]
    
    # ✅ COPY FROM FivePaisaXTS (lines 130-137)
    # ✏️ ADAPT: Verify Jainam depth support
    depth_support = {
        'NSE': [5, 20],   # NSE supports 5 and 20 levels
        'NFO': [5, 20],   # NFO supports 5 and 20 levels
        'CDS': [5],       # Currency derivatives supports 5 levels
        'BSE': [5],       # BSE supports only 5 levels
        'BFO': [5],       # BSE F&O supports only 5 levels
        'MCX': [5]        # MCX supports 5 levels
    }
    
    @classmethod
    def get_supported_depth_levels(cls, exchange):
        """
        Get supported depth levels for an exchange.
        
        ✅ COPIED EXACTLY FROM FivePaisaXTS (lines 140-150)
        """
        return cls.depth_support.get(exchange, [5])
    
    @classmethod
    def is_depth_level_supported(cls, exchange, depth_level):
        """
        Check if a depth level is supported for the given exchange.
        
        ✅ COPIED EXACTLY FROM FivePaisaXTS (lines 152-165)
        """
        supported_depths = cls.get_supported_depth_levels(exchange)
        return depth_level in supported_depths
    
    @classmethod
    def get_fallback_depth_level(cls, exchange, requested_depth):
        """
        Get the best available depth level as a fallback.
        
        ✅ COPIED EXACTLY FROM FivePaisaXTS (lines 167-184)
        """
        supported_depths = cls.get_supported_depth_levels(exchange)
        # Find the highest supported depth that's less than or equal to requested depth
        fallbacks = [d for d in supported_depths if d <= requested_depth]
        if fallbacks:
            return max(fallbacks)
        return 5  # Default to basic depth
    
    @classmethod
    def get_message_code_for_mode(cls, mode):
        """
        Map subscription mode to Jainam message code.
        
        ✏️ JAINAM-SPECIFIC: Message code mapping
        
        Args:
            mode: Subscription mode (1=LTP, 2=Quote, 3=Depth)
        
        Returns:
            int: Jainam message code
        """
        mode_to_message_code = {
            1: 1512,  # LTP
            2: 1501,  # Touchline/Quote
            3: 1502   # Market Depth
        }
        return mode_to_message_code.get(mode, 1512)
```

**Verification:**
- [ ] All methods copied from FivePaisaXTS
- [ ] Exchange list verified for Jainam
- [ ] Depth support verified for Jainam
- [ ] Message code mapping added

---

### AC2: Add JWT Token Parsing ✅

**Pattern:** Copy from `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py:140-175`

**File:** `broker/jainam_prop/streaming/jainam_adapter.py`

**Add Method:**
```python
def _extract_client_id_from_token(self, feed_token: str, fallback_user_id: str) -> str:
    """
    Extract the actual client ID from the JWT feed token.
    
    ✅ COPIED FROM FivePaisaXTS (lines 140-175)
    
    Args:
        feed_token: JWT token containing client information
        fallback_user_id: Fallback user ID if extraction fails
    
    Returns:
        str: Actual client ID from the token
    """
    try:
        import base64
        import json
        
        # ✅ COPY JWT PARSING LOGIC FROM FivePaisaXTS (lines 151-158)
        parts = feed_token.split('.')
        if len(parts) != 3:
            self.logger.warning("Feed token is not a valid JWT")
            return fallback_user_id
        
        payload = parts[1]
        
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        # Decode base64
        decoded = base64.urlsafe_b64decode(payload)
        token_data = json.loads(decoded)
        
        # ✅ COPY USER ID EXTRACTION (line 165)
        # ✏️ ADAPT: Jainam may use different field name
        user_id = token_data.get('userID') or token_data.get('userId') or token_data.get('sub')
        
        if user_id:
            self.logger.info(f"Extracted userID from token: {user_id}")
            return user_id
        else:
            self.logger.warning("No userID found in token, using fallback")
            return fallback_user_id
            
    except Exception as e:
        # ✅ COPY ERROR HANDLING (line 173)
        self.logger.warning(f"Could not extract client ID from token: {e}")
        return fallback_user_id
```

**Update `initialize()` to use token parsing:**
```python
def initialize(self, broker_name, user_id, auth_data=None):
    # ... existing token retrieval ...
    
    # ✏️ ADD: Extract actual user ID from feed token
    if self.market_token:
        actual_user_id = self._extract_client_id_from_token(
            self.market_token,
            fallback_user_id=user_id
        )
        self.logger.info(f"Using userID: {actual_user_id} (from token)")
        self.user_id = actual_user_id
    else:
        self.user_id = user_id
```

**Verification:**
- [ ] JWT parsing logic copied from FivePaisaXTS
- [ ] Base64 decoding with padding
- [ ] User ID extraction from token
- [ ] Graceful fallback on errors

---

### AC3: Integrate Capability Registry in Subscription ✅

**Update `subscribe()` method:**
```python
from broker.jainam_prop.streaming.jainam_mapping import JainamCapabilityRegistry

def subscribe(self, symbol: str, exchange: str, mode: int = 1, depth_level: int = 5):
    """Subscribe to market data with capability validation"""
    
    # ✏️ ADD: Validate exchange support
    if exchange not in JainamCapabilityRegistry.exchanges:
        self.logger.warning(f"Exchange {exchange} not in supported list, attempting anyway")
    
    # ✏️ ADD: Validate depth level support
    if not JainamCapabilityRegistry.is_depth_level_supported(exchange, depth_level):
        fallback_depth = JainamCapabilityRegistry.get_fallback_depth_level(exchange, depth_level)
        self.logger.warning(
            f"Depth level {depth_level} not supported for {exchange}, "
            f"using fallback: {fallback_depth}"
        )
        depth_level = fallback_depth
    
    # ✏️ ADD: Map mode to message code
    message_code = JainamCapabilityRegistry.get_message_code_for_mode(mode)
    
    # Existing subscription logic with validated parameters
    # ... (use message_code, validated depth_level)
```

**Verification:**
- [ ] Exchange validation before subscription
- [ ] Depth level validation with fallback
- [ ] Mode to message code mapping
- [ ] Warnings logged for unsupported parameters

---

## Implementation Steps

### Step 1: Create Capability Registry (1 hour)
1. Create `broker/jainam_prop/streaming/jainam_mapping.py`
2. Copy `JainamCapabilityRegistry` class from FivePaisaXTS
3. Adapt exchange list and depth support
4. Add message code mapping
5. Test all methods

### Step 2: Add JWT Token Parsing (1 hour)
1. Copy `_extract_client_id_from_token()` from FivePaisaXTS
2. Add to `jainam_adapter.py`
3. Update `initialize()` to use token parsing
4. Test with real JWT tokens

### Step 3: Integrate in Subscription (1 hour)
1. Import capability registry in adapter
2. Add validation in `subscribe()` method
3. Add fallback logic
4. Test subscription validation

### Step 4: Testing (1 hour)
1. Unit tests for capability registry
2. Unit tests for JWT parsing
3. Integration tests for subscription validation
4. Test with various exchanges and depth levels

**Total Effort: ~4 hours (0.5 days)**

---

## Testing Strategy

### Unit Tests
```python
# broker/jainam_prop/streaming/test_jainam_mapping.py

def test_depth_level_support():
    """Test depth level validation"""
    assert JainamCapabilityRegistry.is_depth_level_supported('NSE', 5)
    assert JainamCapabilityRegistry.is_depth_level_supported('NSE', 20)
    assert not JainamCapabilityRegistry.is_depth_level_supported('BSE', 20)

def test_fallback_depth():
    """Test fallback depth calculation"""
    assert JainamCapabilityRegistry.get_fallback_depth_level('NSE', 25) == 20
    assert JainamCapabilityRegistry.get_fallback_depth_level('BSE', 20) == 5

def test_message_code_mapping():
    """Test mode to message code mapping"""
    assert JainamCapabilityRegistry.get_message_code_for_mode(1) == 1512
    assert JainamCapabilityRegistry.get_message_code_for_mode(2) == 1501
```

```python
# broker/jainam_prop/streaming/test_token_parsing.py

def test_jwt_parsing():
    """Test JWT token parsing"""
    # Test with valid JWT
    # Test with invalid JWT
    # Test with missing userID
```

---

## Dependencies

**Requires:**
- ✅ Story 1.2-5 (Token Lifecycle) - provides feed tokens
- ✅ Story 1.5-1 (Streaming Adapter) - integrates capability registry

**Blocks:**
- None (enhances streaming but not blocking)

---

## Success Metrics

- [ ] Capability registry created with all methods
- [ ] JWT token parsing implemented
- [ ] User ID extracted from feed tokens
- [ ] Subscription validation with fallback
- [ ] All unit tests passing
- [ ] Integration with streaming adapter

---

## Code Reuse Summary

**Reused from FivePaisaXTS:**
- ✅ Capability registry structure (100%)
- ✅ All class methods (100%)
- ✅ JWT parsing logic (100%)
- ✅ Error handling patterns (100%)

**Jainam-Specific Adaptations:**
- ✏️ Message code mapping (new)
- ✏️ Exchange list verification (minimal)
- ✏️ Depth support verification (minimal)

**Overall Code Reuse: 85%**  
**Effort Savings: 75% (12 hours saved)**

---

## Related Stories

- **Depends On:** Story 1.2-5 (Token Lifecycle)
- **Related:** Story 1.5-1 (Streaming Adapter Refactor)
- **Enhances:** Streaming reliability and validation

---

**Ready for Development** ✅

---

## Notes

This story has the highest code reuse percentage (85%) and can be completed quickly. It provides immediate value by:
1. Preventing invalid subscriptions
2. Extracting actual user IDs from tokens
3. Providing fallback logic for unsupported depth levels

The capability registry is a direct copy from FivePaisaXTS with minimal adaptations needed.

