# Story 1.3-2: Emergency-Closure

## ⚠️ DEPRECATED - DO NOT USE

**Status:** SUPERSEDED
**Superseded By:** `story-1.3-2-emergency-position-closure.md`
**Date Deprecated:** 2025-10-11
**Reason:** Replaced with code reuse-first version (35% reuse from FivePaisaXTS, effort reduced from 3 days to 2 days)

---

## Status
Draft

## Estimated Effort
**3-4 hours** (High code reuse from existing position/order functions)

## Code Reuse Summary

**Reuse Breakdown:**
- ✅ Position retrieval: 85% reusable from existing `get_positions()` (Story 1.2-1)
- ✅ Order placement: 85% reusable from existing `place_order_api()` (existing code)
- ✅ Error handling: 95% reusable from FivePaisaXTS pattern
- ✅ Dealer positions: 70% reusable from Story 1.3-1a (Pro smart order)
- ✅ Logic pattern: 80% reusable from other broker emergency closure functions

**Reference:**
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 3
- **Existing Functions:** `broker/jainam_prop/api/order_api.py` (85% reusable)
- **Pro Pattern:** Story 1.3-1a (dealer position handling)

**Effort Reduction:** ~60% (from 8-10 hours to 3-4 hours)

## Story

**As a** trader needing to quickly exit all positions (including dealer positions for Pro accounts),
**I want** a function that closes all open positions with market orders and supports `clientID` passthrough for dealer flows,
**so that** I can manage risk during market volatility or emergency situations across standard and dealer accounts.

## Acceptance Criteria

1. **AC1**: Implement `close_all_positions()` that retrieves positions and places closing orders
   - **Reuse:** 85% from existing `get_positions()` and `place_order_api()`
   - **Effort:** 1 hour

2. **AC2**: Determine order action based on position direction (quantity > 0: SELL, quantity < 0: BUY)
   - **Reuse:** 100% standard logic
   - **Effort:** 15 minutes

3. **AC3**: Place market orders for absolute value of position quantity
   - **Reuse:** 85% from existing `place_order_api()`
   - **Effort:** 15 minutes

4. **AC4**: Continue closing remaining positions even if one fails
   - **Reuse:** 90% from standard error handling pattern
   - **Effort:** 30 minutes

5. **AC5**: Return aggregated results with order IDs and status
   - **Reuse:** 80% from standard response patterns
   - **Effort:** 30 minutes

6. **AC6**: Log each position closure attempt
   - **Reuse:** 100% from FivePaisaXTS logging pattern
   - **Effort:** 15 minutes

7. **AC7**: When `clientID` provided, use `get_dealerposition_netwise()` (Pro-only)
   - **Reuse:** 70% from Story 1.3-1a (Pro smart order)
   - **Effort:** 30 minutes

8. **AC8**: Pass `clientID` through to order placement (Pro-only)
   - **Reuse:** 85% from existing order placement
   - **Effort:** 15 minutes

9. **AC9**: Maintain backward compatibility (no `clientID` = standard flow)
   - **Reuse:** 100% from existing flow
   - **Effort:** 15 minutes

## Integration Verification

**IV1**: Verify `get_positions()` and `place_order_api()` continue to work
**IV2**: Test with multiple positions, mix of long/short, single position, no positions, partial failures
**IV3**: Measure execution time with 5 positions and verify reasonable performance
**IV4**: Test dealer position closure with `clientID` provided (dealer position fetch, order placement with attribution)
**IV5**: Verify standard position closure (no `clientID`) continues to work without regression

## Tasks / Subtasks

- [ ] Task 1: Implement position retrieval and processing (AC: 1, 6)
  - [ ] Subtask 1.1: Analyze existing emergency closure patterns from other brokers
  - [ ] Subtask 1.2: Call get_positions() to retrieve all open positions
  - [ ] Subtask 1.3: Process position data to extract symbol, quantity, and direction
  - [ ] Subtask 1.4: Add comprehensive logging for each position being processed
  - [ ] Subtask 1.5: Handle empty positions scenario (no positions to close)

- [ ] Task 2: Implement order placement logic (AC: 2, 3, 4, 5)
  - [ ] Subtask 2.1: Determine order action based on position quantity (positive: SELL, negative: BUY)
  - [ ] Subtask 2.2: Calculate absolute quantity for order placement
  - [ ] Subtask 2.3: Prepare market order parameters for each position
  - [ ] Subtask 2.4: Call place_order_api() for each position with error handling
  - [ ] Subtask 2.5: Continue processing remaining positions even if one fails
  - [ ] Subtask 2.6: Aggregate results with order IDs and status for each position

- [ ] Task 3: Error handling and response formatting (AC: 4, 5, 6)
  - [ ] Subtask 3.1: Implement graceful error handling for individual order failures
  - [ ] Subtask 3.2: Add detailed logging for each closure attempt and result
  - [ ] Subtask 3.3: Format aggregated response with order IDs and status
  - [ ] Subtask 3.4: Handle get_positions() failures appropriately
  - [ ] Subtask 3.5: Add input validation for current_api_key and auth_token

## Dev Notes

### Code Reuse Guidance - Emergency Closure

**Primary Reuse Sources:**
1. **Position Retrieval:** Existing `get_positions()` (85% reusable)
2. **Order Placement:** Existing `place_order_api()` (85% reusable)
3. **Error Handling:** FivePaisaXTS pattern (95% reusable)
4. **Dealer Positions:** Story 1.3-1a pattern (70% reusable)

**Implementation Pattern:**
```python
# broker/jainam_prop/api/order_api.py

def close_all_positions(auth_token, client_id=None):
    """
    Close all open positions with market orders

    Args:
        auth_token: Authentication token
        client_id: Optional. If provided, uses dealer positions (Pro-only)

    Returns:
        dict: {
            'success': bool,
            'closed_positions': [list of closed positions],
            'failed_positions': [list of failed positions],
            'total': int,
            'successful': int,
            'failed': int
        }
    """
    # Step 1: Get positions (85% reusable from existing code)
    if client_id:
        # Pro dealer flow (70% reusable from Story 1.3-1a)
        positions = get_dealerposition_netwise(client_id, auth_token)
    else:
        # Standard flow (85% reusable from existing)
        positions = get_positions(auth_token)

    if not positions:
        return {'success': True, 'closed_positions': [], 'total': 0}

    # Step 2: Process each position (100% standard logic)
    results = {
        'closed_positions': [],
        'failed_positions': [],
        'total': len(positions),
        'successful': 0,
        'failed': 0
    }

    for position in positions:
        try:
            # Determine action (100% standard logic)
            quantity = position['netQuantity']
            if quantity == 0:
                continue

            action = 'SELL' if quantity > 0 else 'BUY'
            abs_quantity = abs(quantity)

            # Prepare order (85% reusable from existing)
            order_data = {
                'symbol': position['symbol'],
                'exchange': position['exchange'],
                'action': action,
                'quantity': abs_quantity,
                'order_type': 'MARKET',
                'product': position['product'],
                'clientID': client_id  # Pro-specific passthrough
            }

            # Place order (85% reusable from existing)
            order_result = place_order_api(order_data, auth_token)

            if order_result.get('status') == 'success':
                results['closed_positions'].append({
                    'symbol': position['symbol'],
                    'quantity': abs_quantity,
                    'action': action,
                    'order_id': order_result.get('order_id')
                })
                results['successful'] += 1
            else:
                results['failed_positions'].append({
                    'symbol': position['symbol'],
                    'error': order_result.get('message')
                })
                results['failed'] += 1

        except Exception as e:
            # Error handling (95% reusable from FivePaisaXTS)
            logger.error(f"Failed to close position {position['symbol']}: {e}")
            results['failed_positions'].append({
                'symbol': position['symbol'],
                'error': str(e)
            })
            results['failed'] += 1
            # Continue with remaining positions (AC4)

    results['success'] = results['failed'] == 0
    return results
```

**Reuse Percentages:**
- Position retrieval logic: 85%
- Order placement logic: 85%
- Error handling: 95%
- Dealer position support: 70%
- Overall: 80-85%

### Relevant Source Tree
- `broker/jainam_prop/api/order_api.py` – ✅ Existing functions (85% reusable)
  - `get_positions()` – Position retrieval
  - `place_order_api()` – Order placement
  - `get_dealerposition_netwise()` – Pro dealer positions (Story 1.3-1a)
- `broker/fivepaisaxts/api/auth_api.py` – ✅ Error handling pattern (95% reusable)
- `services/` - Service layer patterns for emergency functions
- `broker/` - Other broker implementations for reference (zerodha, upstox, etc.)

### Emergency Closure Context
- Critical risk management function for emergency situations
- Must be robust and continue operation even with partial failures
- Uses market orders to ensure fast execution
- Processes all positions regardless of individual order failures

### Order Logic Context
- Long positions (quantity > 0): Place SELL orders to close
- Short positions (quantity < 0): Place BUY orders to close
- Always use absolute value of quantity for order size
- Market orders for immediate execution

### Response Format Context
- Returns aggregated results for all position closure attempts
- Includes order IDs and status for each position
- Allows caller to track which closures succeeded/failed
- Comprehensive logging for audit and debugging

### Testing Standards
- Unit tests for position processing and order action determination
- Integration tests with mock positions and order placement
- Edge case tests (no positions, single position, mixed long/short)
- Error handling tests for partial failures and get_positions() failures
- Performance tests with multiple positions

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial story creation from Epic 1.7 | Bob (Scrum Master) |

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## QA Results
