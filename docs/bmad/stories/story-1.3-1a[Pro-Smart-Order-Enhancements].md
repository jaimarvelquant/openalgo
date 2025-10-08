# Story 1.3-1a: Pro-Smart-Order-Enhancements

## Status
Draft

## Estimated Effort
**4-6 hours** (Pro-specific feature, requires XTS Pro SDK integration)

## ⚠️ CRITICAL: Pro-Specific Feature

**This is a PRO-ONLY feature** - Not available in retail brokers like FivePaisaXTS

**Code Reuse:**
- ✅ Smart order logic: 70% reusable from existing Story 1.3-1
- ⚠️ Dealer endpoints: 0% reusable (Pro-specific, must use XTS Pro SDK)
- ✅ Order placement: 85% reusable (existing `place_order_api()`)

**Reference:**
- **Pro Pattern:** `broker/jainam_prop/_sample_strategy/xts_connect.py` (dealer operations)
- **XTS Pro SDK:** `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/`
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 3

## Story

**As a** trader using Jainam Pro with dealer account capabilities,
**I want** smart orders to leverage dealer position endpoints and support `clientID` passthrough,
**so that** I can manage positions for multiple clients and ensure delta calculations use Pro-specific data sources.

## Acceptance Criteria

1. **AC1**: Extend smart order logic to call `get_dealerposition_netwise(clientID=...)` when `clientID` provided
   - **Reference:** `xts_connect.py` for dealer endpoint patterns
   - **Effort:** 1-2 hours

2. **AC2**: Compute delta using dealer net quantity vs. target position
   - **Reuse:** 70% from existing smart order logic
   - **Effort:** 1 hour

3. **AC3**: Pass `clientID` through to `place_order()` for dealer order attribution
   - **Reuse:** 85% from existing `place_order_api()`
   - **Effort:** 30 minutes

4. **AC4**: Maintain backward compatibility: when `clientID` absent, fall back to standard `get_positions()` flow
   - **Reuse:** 100% from existing flow
   - **Effort:** 30 minutes

5. **AC5**: Add Pro dealer position scenario tests
   - **Effort:** 1-2 hours

6. **AC6**: Document Pro dealer smart order usage
   - **Effort:** 30 minutes

## Integration Verification

**IV1**: Verify standard smart order flow (no `clientID`) continues to work without regression
**IV2**: Test Pro dealer smart order with `clientID` provided (position fetch, delta calc, order placement)
**IV3**: Measure execution time for dealer smart order and verify <12s completion (allowing for dealer endpoint latency)

## Dependencies
- Enhances Story 1.3-1 (Smart Order Placement)
- Depends on Story 1.0-1 (Auth) for Pro credentials
- Coordinates with Implementation Plan Phase 2.5 Task 2.6

## Dev Notes

### Code Reuse Guidance - Pro vs Retail

**⚠️ CRITICAL: This is a PRO-ONLY Feature**

**Cannot Use FivePaisaXTS (Retail) For:**
- ❌ Dealer position endpoints (not available in retail)
- ❌ Dealer order book (not available in retail)
- ❌ Dealer trade book (not available in retail)
- ❌ `clientID` passthrough (not available in retail)

**Must Use XTS Pro SDK For:**
- ✅ `get_dealerposition_netwise(clientID)` - Pro dealer endpoint
- ✅ `get_dealer_orderbook(clientID)` - Pro dealer endpoint
- ✅ `get_dealer_tradebook(clientID)` - Pro dealer endpoint
- ✅ `clientID` parameter handling

**Can Reuse From Existing Code:**
- ✅ Smart order logic (70% from Story 1.3-1)
- ✅ Order placement (85% from `place_order_api()`)
- ✅ Delta calculation pattern (adapt for dealer positions)
- ✅ Error handling (FivePaisaXTS pattern)

### Reference Files

**Pro Dealer Endpoints:**
- **File:** `broker/jainam_prop/_sample_strategy/xts_connect.py`
- **Purpose:** Reference implementation for dealer operations
- **Key Functions:**
  - Dealer position endpoints
  - `clientID` parameter handling
  - Pro-specific response parsing

**XTS Pro SDK:**
- **Location:** `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/`
- **Purpose:** Pro-specific functionality
- **Usage:** Wrap SDK, don't modify sources

**Existing Smart Order Logic:**
- **File:** `broker/jainam_prop/api/order_api.py` (from Story 1.3-1)
- **Reuse:** 70% of logic (position fetch, delta calc, order placement)
- **Adapt:** Replace `get_positions()` with `get_dealerposition_netwise(clientID)`

**Code Reuse Analysis:**
- **File:** `docs/bmad/research/jainam-code-reuse-analysis.md`
- **Section:** Section 3 (API Implementation)
- **Relevant:** Pro-specific features discussion

### Implementation Guidance

**Step 1: Add Dealer Position Endpoint (1-2 hours)**
```python
# broker/jainam_prop/api/order_api.py

def get_dealerposition_netwise(client_id, auth_token):
    """
    Get dealer net-wise positions for specific client (Pro-only)

    Reference: xts_connect.py for Pro dealer endpoint patterns
    """
    jainam_api = JainamAPI()
    jainam_api.interactive_token = auth_token

    # Pro-specific endpoint
    url = f"{jainam_api.root_url}/interactive/dealer/positions/netwise"

    payload = {
        'clientID': client_id  # Pro-specific parameter
    }

    response = jainam_api.client.post(
        url,
        headers=jainam_api._get_headers(),
        json=payload
    )

    # Parse Pro-specific response format
    response_data = response.json()
    return transform_dealer_positions(response_data)
```

**Step 2: Extend Smart Order Logic (1 hour)**
```python
# Extend existing smart order function

def smart_order(symbol, target_qty, client_id=None, auth_token=None):
    """
    Smart order with Pro dealer support

    Args:
        client_id: Optional. If provided, uses dealer endpoints (Pro-only)
    """
    if client_id:
        # ✅ Pro dealer flow
        current_positions = get_dealerposition_netwise(client_id, auth_token)
    else:
        # ✅ Standard flow (backward compatible)
        current_positions = get_positions(auth_token)

    # Rest of logic 70% reusable from Story 1.3-1
    current_qty = extract_position_qty(current_positions, symbol)
    delta = target_qty - current_qty

    if delta != 0:
        order_data = {
            'symbol': symbol,
            'quantity': abs(delta),
            'action': 'BUY' if delta > 0 else 'SELL',
            'clientID': client_id  # ✅ Pro-specific passthrough
        }
        place_order_api(order_data, auth_token)
```

**Step 3: Add Backward Compatibility (30 minutes)**
```python
# Ensure standard flow still works

def smart_order(symbol, target_qty, client_id=None, auth_token=None):
    # Detect Pro vs standard flow
    is_pro_dealer = client_id is not None

    if is_pro_dealer:
        # Pro dealer flow
        positions = get_dealerposition_netwise(client_id, auth_token)
    else:
        # Standard flow (existing)
        positions = get_positions(auth_token)

    # Common logic (70% reusable)
    # ...
```

**Step 4: Test (1-2 hours)**
```bash
# Test standard flow (backward compatibility)
python -m pytest tests/test_smart_order.py::test_standard_flow

# Test Pro dealer flow
python -m pytest tests/test_smart_order.py::test_dealer_flow
```

### Pro vs Retail Feature Matrix

| Feature | Retail (FivePaisaXTS) | Pro (Jainam) | Implementation |
|---------|----------------------|--------------|----------------|
| **Standard Positions** | ✅ Available | ✅ Available | ✅ Reuse existing |
| **Dealer Positions** | ❌ Not available | ✅ Available | ⚠️ Use XTS Pro SDK |
| **clientID Parameter** | ❌ Not available | ✅ Available | ⚠️ Pro-specific |
| **Smart Order Logic** | ✅ Available | ✅ Available | ✅ 70% reusable |
| **Order Placement** | ✅ Available | ✅ Available | ✅ 85% reusable |

### Anti-Patterns to Avoid

**❌ DO NOT:**
- Try to use FivePaisaXTS for dealer endpoints (not available)
- Modify XTS Pro SDK sources (wrap, don't modify)
- Break backward compatibility (standard flow must still work)
- Hardcode `clientID` values (must be parameter)

**✅ DO:**
- Reference `xts_connect.py` for Pro dealer patterns
- Wrap XTS Pro SDK for dealer operations
- Maintain backward compatibility (check if `clientID` provided)
- Reuse existing smart order logic (70%)
- Follow FivePaisaXTS error handling pattern

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-08 | 1.0 | Initial story from Sprint Change Proposal | Sarah (PO) |
