# Story 1.3-2: Emergency Position Closure

**Status:** Ready for Development  
**Priority:** MEDIUM (Risk management feature)  
**Effort:** 2 days (16 hours) - **Code Reuse: 35%**  
**Original Effort:** 3 days (24 hours)  
**Savings:** 33% (8 hours saved)

---

## Story

As a **developer implementing Jainam Prop risk management features**,  
I want **an emergency position closure function that closes all open positions for dealer accounts with batch processing and error recovery**,  
so that **users can quickly exit all positions in emergency situations with proper dealer account clientID handling**.

---

## Context

### Current State
- No emergency closure functionality exists
- Individual position closure requires manual iteration
- No batch processing for multiple positions
- No error recovery if some closures fail

### Reference Implementation
**Source:** `broker/fivepaisaxts/api/order_api.py:58-73`

FivePaisaXTS has basic position iteration pattern:
- ✅ Fetches all positions (line 60)
- ✅ Iterates through positions (line 64)
- ✅ Parses position data (lines 65-68)
- ✅ Checks for non-zero quantity (line 70)

### Dealer Account Requirements
From Story 1.9.1 (Complete), we know:
- **Pro Dealer (ZZJ13048):** Uses `clientID="*****"` in API requests
- **Normal Dealer (DLL7182):** Uses actual `clientID="DLL7182"` in API requests
- Both use dealer-specific endpoints: `/interactive/portfolio/dealerpositions`

### Code Reuse Strategy
**35% can be copied from FivePaisaXTS**

**What to Copy:**
- Position iteration pattern
- Position data parsing
- Non-zero quantity check

**What to Build (Dealer-Specific):**
- Dealer position endpoint usage
- Batch closure with error recovery
- clientID parameter handling
- Partial success reporting
- Closure order prioritization

---

## Acceptance Criteria

### AC1: Implement Emergency Closure Function ✅

**Pattern:** Copy from `broker/fivepaisaxts/api/order_api.py:58-73`

**File:** `broker/jainam_prop/api/order_api.py`

**Implementation:**
```python
from broker.jainam_prop.api.order_api import _parse_auth_token

def close_all_positions_api(auth, product_type=None):
    """
    Close all open positions with dealer account support.
    
    ✅ COPY ITERATION PATTERN FROM FivePaisaXTS (lines 58-73)
    ✏️ ADD batch processing and error recovery
    
    Args:
        auth: Authentication token
        product_type: Optional filter (NRML, MIS, etc.)
    
    Returns:
        dict: Closure results with success/failure details
    """
    try:
        # ✏️ ADAPT: Parse auth token to get dealer account info
        interactive_token, user_id, client_id, is_investor_client, is_dealer_account, \
        is_pro_dealer, is_normal_dealer, api_client_id = _parse_auth_token(auth)
        
        logger.info(
            f"Emergency position closure initiated for user {user_id}, "
            f"isDealerAccount={is_dealer_account}, clientID={api_client_id}"
        )
        
        # ✅ COPY PATTERN FROM FivePaisaXTS (line 60)
        # ✏️ ADAPT: Use dealer-specific position endpoint
        positions_response = get_positions(auth)
        
        if not positions_response or positions_response.get('status') != 'success':
            return {
                "status": "error",
                "message": "Failed to fetch positions",
                "data": positions_response
            }
        
        positions = positions_response.get('data', [])
        
        if not positions:
            return {
                "status": "success",
                "message": "No open positions to close",
                "closed": 0,
                "failed": 0
            }
        
        # ✏️ ADD: Filter positions if product_type specified
        if product_type:
            positions = [p for p in positions if p.get('product') == product_type]
        
        # ✏️ ADD: Batch closure with error tracking
        closure_results = {
            "total": len(positions),
            "closed": 0,
            "failed": 0,
            "errors": [],
            "details": []
        }
        
        # ✅ COPY ITERATION FROM FivePaisaXTS (line 64)
        for position in positions:
            try:
                # ✅ COPY PARSING FROM FivePaisaXTS (lines 65-68)
                symbol = position.get('tradingsymbol')
                exchange = position.get('exchange')
                product = position.get('product', 'NRML')
                
                # ✅ COPY QUANTITY CHECK FROM FivePaisaXTS (line 70)
                # ✏️ ADAPT: Handle multiple field names
                net_qty = _parse_position_quantity(position)
                
                if net_qty == 0:
                    logger.debug(f"Skipping {symbol} - zero quantity")
                    continue
                
                # ✏️ ADD: Determine closure side (opposite of position)
                closure_side = "SELL" if net_qty > 0 else "BUY"
                closure_qty = abs(net_qty)
                
                logger.info(
                    f"Closing position: {symbol} {exchange} "
                    f"{closure_side} {closure_qty} (product={product})"
                )
                
                # ✏️ ADD: Place closure order
                closure_order = {
                    'symbol': symbol,
                    'exchange': exchange,
                    'action': closure_side,
                    'quantity': str(closure_qty),
                    'product': product,
                    'pricetype': 'MARKET',
                    'ordertype': 'MARKET',
                    'price': '0'
                }
                
                # Place order (handles dealer clientID automatically)
                order_response = place_order_api(closure_order, auth)
                
                if order_response.get('status') == 'success':
                    closure_results['closed'] += 1
                    closure_results['details'].append({
                        'symbol': symbol,
                        'status': 'success',
                        'quantity': closure_qty,
                        'side': closure_side
                    })
                else:
                    closure_results['failed'] += 1
                    closure_results['errors'].append({
                        'symbol': symbol,
                        'error': order_response.get('message', 'Unknown error')
                    })
                
            except Exception as e:
                logger.error(f"Failed to close position {symbol}: {e}")
                closure_results['failed'] += 1
                closure_results['errors'].append({
                    'symbol': symbol,
                    'error': str(e)
                })
        
        # ✏️ ADD: Summary response
        return {
            "status": "success" if closure_results['failed'] == 0 else "partial",
            "message": f"Closed {closure_results['closed']} of {closure_results['total']} positions",
            "data": closure_results
        }
        
    except Exception as e:
        logger.error(f"Emergency closure failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
```

**Verification:**
- [ ] Fetches positions using dealer endpoints
- [ ] Iterates through all positions
- [ ] Closes each position with market order
- [ ] Handles Pro dealer (clientID="*****") correctly
- [ ] Handles Normal dealer (clientID=actual) correctly
- [ ] Tracks success/failure for each position
- [ ] Returns detailed closure results

---

### AC2: Add Error Recovery and Partial Success Handling ✅

**Add Retry Logic for Failed Closures:**
```python
def close_all_positions_with_retry(auth, product_type=None, max_retries=2):
    """
    Close all positions with retry logic for failed closures.
    
    ✏️ JAINAM-SPECIFIC: Batch closure with retry
    """
    # First attempt
    result = close_all_positions_api(auth, product_type)
    
    # Retry failed closures
    retry_count = 0
    while result.get('data', {}).get('failed', 0) > 0 and retry_count < max_retries:
        retry_count += 1
        logger.info(f"Retrying failed closures (attempt {retry_count}/{max_retries})")
        
        # Get current positions again
        time.sleep(1)  # Brief delay before retry
        retry_result = close_all_positions_api(auth, product_type)
        
        # Update results
        result['data']['closed'] += retry_result.get('data', {}).get('closed', 0)
        result['data']['failed'] = retry_result.get('data', {}).get('failed', 0)
    
    return result
```

**Verification:**
- [ ] Retries failed closures up to max_retries
- [ ] Delays between retry attempts
- [ ] Updates closure statistics
- [ ] Logs retry attempts

---

### AC3: Add Position Closure Prioritization ✅

**Add Priority-Based Closure:**
```python
def _prioritize_positions(positions):
    """
    Prioritize positions for closure (high risk first).
    
    ✏️ JAINAM-SPECIFIC: Risk-based prioritization
    
    Priority order:
    1. Options (highest risk)
    2. Futures
    3. Equity
    """
    priority_map = {
        'NFO': 1,  # Options/Futures
        'BFO': 1,  # BSE F&O
        'MCX': 1,  # Commodities
        'CDS': 2,  # Currency
        'NSE': 3,  # Equity
        'BSE': 3   # BSE Equity
    }
    
    def get_priority(position):
        exchange = position.get('exchange', 'NSE')
        return priority_map.get(exchange, 99)
    
    return sorted(positions, key=get_priority)
```

**Update Closure Function:**
```python
# In close_all_positions_api, before iteration:
# ✏️ ADD: Prioritize positions
positions = _prioritize_positions(positions)
logger.info(f"Prioritized {len(positions)} positions for closure")
```

**Verification:**
- [ ] Options/Futures closed first
- [ ] Equity positions closed last
- [ ] Priority order logged
- [ ] All positions eventually closed

---

## Implementation Steps

### Step 1: Copy Position Iteration Pattern (2 hours)
1. Open `broker/fivepaisaxts/api/order_api.py`
2. Copy lines 58-73 (position iteration)
3. Paste into `broker/jainam_prop/api/order_api.py`
4. Review iteration logic

### Step 2: Add Dealer Account Support (4 hours)
1. Add `_parse_auth_token()` call
2. Update position fetching for dealer endpoints
3. Add `_parse_position_quantity()` helper
4. Test with Pro dealer account

### Step 3: Implement Batch Closure (4 hours)
1. Add closure order creation logic
2. Add error tracking
3. Implement partial success handling
4. Test with multiple positions

### Step 4: Add Error Recovery (3 hours)
1. Implement retry logic
2. Add delay between retries
3. Update closure statistics
4. Test retry scenarios

### Step 5: Add Prioritization (1 hour)
1. Implement `_prioritize_positions()`
2. Integrate into closure function
3. Test priority order

### Step 6: Testing (2 hours)
1. Unit tests for prioritization
2. Integration tests with dealer accounts
3. Test partial failure scenarios
4. Test retry logic

**Total Effort: ~16 hours (2 days)**

---

## Testing Strategy

### Unit Tests
```python
def test_position_prioritization():
    """Test position priority ordering"""
    # Test NFO before NSE
    # Test BFO before BSE
    # Test MCX before equity

def test_closure_side_determination():
    """Test closure side logic"""
    # Long position → SELL
    # Short position → BUY
```

### Integration Tests
```python
def test_emergency_closure_pro_dealer():
    """Test emergency closure with Pro dealer"""
    # Create test positions
    # Close all positions
    # Verify clientID="*****" in orders

def test_emergency_closure_partial_failure():
    """Test partial failure handling"""
    # Simulate some failures
    # Verify partial success reported
    # Verify retry logic
```

---

## Dependencies

**Requires:**
- ✅ Story 1.2-3 (Open Position) - Done
- ✅ Story 1.9.1 (Dealer Config) - Complete
- ✅ `_parse_auth_token()` function (already exists)
- ✅ `get_positions()` with dealer support (already exists)
- ✅ `place_order_api()` with dealer support (already exists)

**Blocks:**
- None (standalone risk management feature)

---

## Success Metrics

- [ ] Closes all open positions successfully
- [ ] Handles Pro dealer (clientID="*****") correctly
- [ ] Handles Normal dealer (clientID=actual) correctly
- [ ] Tracks success/failure for each position
- [ ] Retries failed closures
- [ ] Prioritizes high-risk positions
- [ ] Returns detailed closure results
- [ ] All tests passing

---

## Code Reuse Summary

**Reused from FivePaisaXTS:**
- ✅ Position iteration pattern (100%)
- ✅ Position data parsing (100%)
- ✅ Non-zero quantity check (100%)

**Jainam-Specific Additions:**
- ✏️ Dealer account detection (new)
- ✏️ Batch closure logic (new)
- ✏️ Error recovery and retry (new)
- ✏️ Partial success handling (new)
- ✏️ Position prioritization (new)
- ✏️ clientID parameter handling (new)

**Overall Code Reuse: 35%**  
**Effort Savings: 33% (8 hours saved)**

---

## Related Stories

- **Depends On:** Story 1.2-3 (Open Position), Story 1.9.1 (Dealer Config)
- **Related:** Story 1.3-1a (Pro Smart Order)
- **Enhances:** Risk management capabilities

---

**Ready for Development** ✅

