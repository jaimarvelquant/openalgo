# Story 1.3-2: Emergency-Closure

## Status
Draft

## Story

**As a** trader needing to quickly exit all positions,
**I want** a function that closes all open positions with market orders,
**so that** I can manage risk during market volatility or emergency situations.

## Acceptance Criteria

1. **AC1**: Implement `close_all_positions(current_api_key, auth_token)` that retrieves positions and places closing orders
2. **AC2**: Function determines order action based on position direction (quantity > 0: SELL, quantity < 0: BUY)
3. **AC3**: Function places market orders for absolute value of position quantity
4. **AC4**: Function continues closing remaining positions even if one fails
5. **AC5**: Function returns aggregated results with order IDs and status for each position
6. **AC6**: Function logs each position closure attempt

## Integration Verification

**IV1**: Verify `get_positions()` and `place_order_api()` continue to work
**IV2**: Test with multiple positions, mix of long/short, single position, no positions, partial failures
**IV3**: Measure execution time with 5 positions and verify reasonable performance

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

### Relevant Source Tree
- `broker/jainam_prop/api.py` - API client implementation
- `broker/jainam_prop/` - Position and order placement functions
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
