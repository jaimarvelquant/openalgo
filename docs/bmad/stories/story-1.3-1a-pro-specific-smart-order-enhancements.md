# Story 1.3-1a: Pro-Specific Smart Order Enhancements

**Status:** Ready for Development  
**Priority:** MEDIUM (Pro dealer-specific features)  
**Effort:** 1.5 days (12 hours) - **Code Reuse: 40%**  
**Original Effort:** 3 days (24 hours)  
**Savings:** 50% (12 hours saved)

---

## Story

As a **developer implementing Jainam Prop smart order functionality**,  
I want **smart order to use dealer-specific position endpoints and handle Pro/Normal dealer account differences**,  
so that **smart orders correctly calculate position deltas for dealer accounts and pass the appropriate clientID parameter**.

---

## Context

### Current State
- Base smart order implementation exists (Story 1.3-1 - Approved)
- Smart order uses regular position endpoints
- No dealer-specific logic for Pro vs Normal accounts
- clientID parameter not handled in smart order flow

### Reference Implementation
**Source:** `broker/fivepaisaxts/api/order_api.py:117-180`

FivePaisaXTS has proven smart order delta calculation:
- ✅ Fetches current positions (line 120)
- ✅ Calculates target vs current quantity (lines 130-145)
- ✅ Determines delta (buy/sell quantity needed)
- ✅ Places order only if delta != 0

### Dealer Account Requirements
From Story 1.9.1 (Complete), we know:
- **Pro Dealer (ZZJ13048):** Uses `clientID="*****"` in API requests
- **Normal Dealer (DLL7182):** Uses actual `clientID="DLL7182"` in API requests
- Both use dealer-specific endpoints: `/interactive/portfolio/dealerpositions`

### Code Reuse Strategy
**40% can be copied from FivePaisaXTS**

**What to Copy:**
- Delta calculation logic (target - current)
- Order side determination (BUY if delta > 0, SELL if delta < 0)
- Zero-delta handling (no action needed)
- Position data parsing

**What to Adapt (Dealer-Specific):**
- Use `get_dealer_positions()` instead of `get_positions()`
- Add clientID parameter handling (Pro="*****", Normal=actual)
- Parse dealer position data structure
- Add dealer-specific error handling

---

## Acceptance Criteria

### AC1: Extend Smart Order with Dealer Position Lookup ✅

**Pattern:** Copy from `broker/fivepaisaxts/api/order_api.py:117-145`

**File:** `broker/jainam_prop/api/order_api.py`

**Current Smart Order (Base Implementation):**
```python
def placesmartorder_api(data, auth):
    # Existing implementation from Story 1.3-1
    # Uses regular position endpoints
```

**Enhanced Smart Order (Dealer-Aware):**
```python
from broker.jainam_prop.api.order_api import _parse_auth_token

def placesmartorder_api(data, auth):
    """
    Place smart order with dealer account support.
    
    ✅ COPY DELTA LOGIC FROM FivePaisaXTS (lines 117-145)
    ✏️ ADAPT for dealer-specific position endpoints
    """
    try:
        # ✏️ ADAPT: Parse auth token to get dealer account info
        interactive_token, user_id, client_id, is_investor_client, is_dealer_account, \
        is_pro_dealer, is_normal_dealer, api_client_id = _parse_auth_token(auth)
        
        # Extract order parameters
        symbol = data.get('symbol')
        exchange = data.get('exchange')
        target_quantity = int(data.get('quantity', 0))
        product_type = data.get('product', 'NRML')
        
        # ✅ COPY PATTERN FROM FivePaisaXTS (line 120)
        # ✏️ ADAPT: Use dealer-specific position endpoint
        if is_dealer_account:
            logger.info(f"Fetching dealer positions for smart order (clientID={api_client_id})")
            positions_response = get_positions(auth)  # Uses dealer endpoint internally
        else:
            logger.info("Fetching regular positions for smart order")
            positions_response = get_positions(auth)
        
        # ✅ COPY POSITION PARSING FROM FivePaisaXTS (lines 130-145)
        current_quantity = 0
        if positions_response and positions_response.get('status') == 'success':
            positions = positions_response.get('data', [])
            
            # Find matching position
            for position in positions:
                if (position.get('tradingsymbol') == symbol and 
                    position.get('exchange') == exchange and
                    position.get('product') == product_type):
                    # ✏️ ADAPT: Parse dealer position data structure
                    current_quantity = int(position.get('netqty', 0))
                    logger.info(f"Found existing position: {current_quantity} for {symbol}")
                    break
        
        # ✅ COPY DELTA CALCULATION FROM FivePaisaXTS (lines 147-155)
        delta = target_quantity - current_quantity
        
        logger.info(
            f"Smart order calculation: target={target_quantity}, "
            f"current={current_quantity}, delta={delta}"
        )
        
        # ✅ COPY ZERO-DELTA HANDLING FROM FivePaisaXTS (lines 157-160)
        if delta == 0:
            return {
                "status": "success",
                "message": f"Position already at target quantity {target_quantity}",
                "action": "none"
            }
        
        # ✅ COPY ORDER SIDE DETERMINATION FROM FivePaisaXTS (lines 162-165)
        order_side = "BUY" if delta > 0 else "SELL"
        order_quantity = abs(delta)
        
        # ✏️ ADAPT: Place order with dealer account clientID
        order_data = {
            'symbol': symbol,
            'exchange': exchange,
            'action': order_side,
            'quantity': str(order_quantity),
            'price': data.get('price', '0'),
            'product': product_type,
            'pricetype': data.get('pricetype', 'MARKET'),
            'ordertype': data.get('ordertype', 'MARKET')
        }
        
        # Place order using existing place_order_api (handles dealer clientID)
        order_response = place_order_api(order_data, auth)
        
        return {
            "status": "success",
            "message": f"Smart order placed: {order_side} {order_quantity} {symbol}",
            "delta": delta,
            "order_response": order_response
        }
        
    except Exception as e:
        logger.error(f"Smart order failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
```

**Verification:**
- [ ] Delta calculation matches FivePaisaXTS logic
- [ ] Uses dealer position endpoints for dealer accounts
- [ ] Handles Pro dealer (clientID="*****") correctly
- [ ] Handles Normal dealer (clientID=actual) correctly
- [ ] Zero-delta returns success without placing order
- [ ] Order side determined correctly (BUY/SELL)

---

### AC2: Add Dealer-Specific Position Data Parsing ✅

**Position Data Structure Differences:**

**Regular Position:**
```json
{
  "tradingsymbol": "SBIN-EQ",
  "exchange": "NSE",
  "netqty": "10",
  "product": "NRML"
}
```

**Dealer Position (may have additional fields):**
```json
{
  "tradingsymbol": "SBIN-EQ",
  "exchange": "NSE",
  "Quantity": "10",  // Note: Capital Q
  "ProductType": "NRML",
  "clientID": "*****"
}
```

**Add Robust Parsing:**
```python
def _parse_position_quantity(position: dict) -> int:
    """
    Parse position quantity from dealer or regular position data.
    
    ✏️ JAINAM-SPECIFIC: Handle both data formats
    """
    # Try different field names
    qty_fields = ['netqty', 'Quantity', 'NetQuantity', 'qty']
    
    for field in qty_fields:
        if field in position:
            try:
                return int(position[field])
            except (ValueError, TypeError):
                continue
    
    return 0
```

**Verification:**
- [ ] Handles both regular and dealer position formats
- [ ] Tries multiple field name variations
- [ ] Returns 0 if quantity not found
- [ ] Logs warnings for unexpected formats

---

### AC3: Add Smart Order Testing ✅

**Test Cases:**

```python
# broker/jainam_prop/api/test_smart_order_dealer.py

def test_smart_order_pro_dealer_buy():
    """Test smart order BUY with Pro dealer account"""
    # Target: 100, Current: 50, Delta: +50 (BUY)
    # Verify clientID="*****" passed to order

def test_smart_order_normal_dealer_sell():
    """Test smart order SELL with Normal dealer account"""
    # Target: 20, Current: 50, Delta: -30 (SELL)
    # Verify clientID="DLL7182" passed to order

def test_smart_order_zero_delta():
    """Test smart order with zero delta"""
    # Target: 50, Current: 50, Delta: 0
    # Verify no order placed

def test_smart_order_no_existing_position():
    """Test smart order with no existing position"""
    # Target: 100, Current: 0, Delta: +100 (BUY)
    # Verify full quantity order placed
```

**Verification:**
- [ ] All test cases pass
- [ ] Pro dealer uses clientID="*****"
- [ ] Normal dealer uses actual clientID
- [ ] Zero delta doesn't place order
- [ ] Delta calculation correct in all scenarios

---

## Implementation Steps

### Step 1: Copy Delta Calculation Logic (2 hours)
1. Open `broker/fivepaisaxts/api/order_api.py`
2. Copy lines 117-180 (smart order logic)
3. Paste into `broker/jainam_prop/api/order_api.py`
4. Review delta calculation logic

### Step 2: Adapt for Dealer Accounts (4 hours)
1. Add `_parse_auth_token()` call to get dealer account info
2. Update position fetching to use dealer endpoints
3. Add `_parse_position_quantity()` helper
4. Update order placement to pass dealer clientID
5. Test with Pro dealer account

### Step 3: Add Position Data Parsing (2 hours)
1. Implement `_parse_position_quantity()` helper
2. Handle multiple field name variations
3. Add logging for unexpected formats
4. Test with both regular and dealer positions

### Step 4: Testing (4 hours)
1. Unit tests for delta calculation
2. Integration tests with Pro dealer account
3. Integration tests with Normal dealer account
4. Test zero-delta scenario
5. Test no existing position scenario

**Total Effort: ~12 hours (1.5 days)**

---

## Testing Strategy

### Unit Tests
```python
def test_delta_calculation():
    """Test delta calculation logic"""
    assert calculate_delta(target=100, current=50) == 50  # BUY
    assert calculate_delta(target=20, current=50) == -30  # SELL
    assert calculate_delta(target=50, current=50) == 0    # No action

def test_position_quantity_parsing():
    """Test position quantity parsing"""
    # Test regular format
    # Test dealer format
    # Test missing quantity
```

### Integration Tests
```python
def test_smart_order_end_to_end_pro_dealer():
    """Test complete smart order flow with Pro dealer"""
    # Authenticate with Pro dealer account
    # Place smart order
    # Verify correct delta calculation
    # Verify clientID="*****" in order
```

---

## Dependencies

**Requires:**
- ✅ Story 1.3-1 (Smart Order base implementation) - Approved
- ✅ Story 1.9.1 (Dealer account configuration) - Complete
- ✅ `_parse_auth_token()` function (already exists)
- ✅ `get_positions()` with dealer support (already exists)
- ✅ `place_order_api()` with dealer support (already exists)

**Blocks:**
- None (enhancement to existing functionality)

---

## Success Metrics

- [ ] Smart order calculates delta correctly for dealer accounts
- [ ] Pro dealer uses clientID="*****" in orders
- [ ] Normal dealer uses actual clientID in orders
- [ ] Zero-delta scenarios handled correctly
- [ ] Position data parsed from both formats
- [ ] All unit tests passing
- [ ] All integration tests passing
- [ ] Code coverage >80% for smart order logic

---

## Code Reuse Summary

**Reused from FivePaisaXTS:**
- ✅ Delta calculation logic (100%)
- ✅ Order side determination (100%)
- ✅ Zero-delta handling (100%)
- ✅ Position iteration pattern (100%)

**Jainam-Specific Additions:**
- ✏️ Dealer account detection (new)
- ✏️ Dealer position endpoint usage (new)
- ✏️ clientID parameter handling (new)
- ✏️ Dealer position data parsing (new)

**Overall Code Reuse: 40%**  
**Effort Savings: 50% (12 hours saved)**

---

## Related Stories

- **Depends On:** Story 1.3-1 (Smart Order), Story 1.9.1 (Dealer Config)
- **Enhances:** Smart order functionality for dealer accounts
- **Related:** Story 1.3-2 (Emergency Closure)

---

## Notes

This story has lower code reuse (40%) because dealer-specific logic is unique to Jainam Pro accounts and doesn't exist in FivePaisaXTS. However, the core delta calculation logic is directly reusable, saving significant development time.

The key challenge is adapting the position data parsing to handle dealer-specific formats while maintaining compatibility with the base smart order implementation.

---

**Ready for Development** ✅

