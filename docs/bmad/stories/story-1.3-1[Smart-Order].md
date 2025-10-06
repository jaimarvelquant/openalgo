# Story 1.3-1: Smart-Order

## Status
Draft

## Story

**As a** trader using OpenAlgo's smart order feature,
**I want** to specify a target position size and have OpenAlgo automatically calculate and place the correct order,
**so that** I can manage positions efficiently without manual calculation of buy/sell quantities.

## Acceptance Criteria

1. **AC1**: Implement `place_smartorder_api(data, auth_token)` that extracts `position_size` and calls `get_open_position()`
2. **AC2**: Function calculates position delta and determines action/quantity (delta > 0: BUY, delta < 0: SELL, delta == 0: success message)
3. **AC3**: Function logs position calculation details (symbol, current, target, delta, action, quantity)
4. **AC4**: Function calls `place_order_api()` with calculated parameters
5. **AC5**: Function handles errors gracefully (position lookup failure, order placement failure)
6. **AC6**: Function returns success message when delta is zero (no order needed)

## Integration Verification

**IV1**: Verify regular order placement continues to work
**IV2**: Test smart order with all scenarios (opening, increasing, reducing, closing, reversing, no change)
**IV3**: Measure execution time and verify <10 seconds completion

## Tasks / Subtasks

- [ ] Task 1: Implement smart order core logic (AC: 1, 2, 3, 6)
  - [ ] Subtask 1.1: Analyze existing order placement patterns and smart order requirements
  - [ ] Subtask 1.2: Extract position_size from input data parameter
  - [ ] Subtask 1.3: Call get_open_position() to get current position quantity
  - [ ] Subtask 1.4: Calculate position delta (target - current)
  - [ ] Subtask 1.5: Determine order action based on delta (BUY/SELL) and quantity
  - [ ] Subtask 1.6: Handle delta == 0 case (return success message, no order needed)
  - [ ] Subtask 1.7: Add comprehensive logging for position calculations

- [ ] Task 2: Integrate with order placement (AC: 4, 5)
  - [ ] Subtask 2.1: Prepare order parameters from calculated delta and action
  - [ ] Subtask 2.2: Call place_order_api() with calculated parameters
  - [ ] Subtask 2.3: Handle order placement success and return appropriate response
  - [ ] Subtask 2.4: Implement error handling for order placement failures
  - [ ] Subtask 2.5: Add error logging for failed operations

- [ ] Task 3: Error handling and validation (AC: 5)
  - [ ] Subtask 3.1: Handle get_open_position() failures gracefully
  - [ ] Subtask 3.2: Validate input data contains required position_size field
  - [ ] Subtask 3.3: Add input validation for all required order parameters
  - [ ] Subtask 3.4: Implement standardized error response format
  - [ ] Subtask 3.5: Add appropriate error logging without exposing sensitive data

## Dev Notes

### Relevant Source Tree
- `broker/jainam_prop/api.py` - API client implementation
- `broker/jainam_prop/` - Order placement and position functions
- `services/` - Service layer patterns for order functions
- `broker/` - Other broker implementations for reference (zerodha, upstox, etc.)

### Smart Order Logic Context
- Function calculates position delta: target_position - current_position
- Delta > 0: BUY order for delta quantity
- Delta < 0: SELL order for absolute value of delta
- Delta = 0: No order needed, return success message
- Depends on get_open_position() from Story 1.2-3

### Order Placement Context
- Uses existing place_order_api() function with calculated parameters
- Must handle all order placement error scenarios
- Returns standardized response format
- Includes comprehensive logging for debugging and monitoring

### Testing Standards
- Unit tests for delta calculation logic and action determination
- Integration tests with mock position data and order placement
- Edge case tests (zero delta, large deltas, position lookup failures)
- Performance tests to verify <10 second execution time
- Error handling tests for various failure scenarios

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial story creation from Epic 1.6 | Bob (Scrum Master) |

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## QA Results
