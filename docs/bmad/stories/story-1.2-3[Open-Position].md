# Story 1.2-3: Open-Position

## Status
Draft

## Story

**As a** developer implementing smart order functionality,
**I want** a function that returns the current position quantity for a specific symbol,
**so that** smart order placement can calculate position delta and determine order action/quantity.

## Acceptance Criteria

1. **AC1**: Implement `get_open_position(tradingsymbol, exchange, producttype, auth_token)` that filters positions
2. **AC2**: Function returns net quantity as string (e.g., "100", "-50", "0")
3. **AC3**: Function handles position not found (returns "0")
4. **AC4**: Function handles `get_positions()` failure (returns "0" and logs error)
5. **AC5**: Function matches symbol, exchange, and product type exactly
6. **AC6**: Function logs lookup result for debugging

## Integration Verification

**IV1**: Verify `get_positions()` continues to work correctly
**IV2**: Test with various scenarios (long position, short position, no position, invalid symbol)
**IV3**: Measure execution time and verify <5 seconds completion

## Tasks / Subtasks

- [ ] Task 1: Implement get_open_position function core logic (AC: 1, 2, 3, 4, 5)
  - [ ] Subtask 1.1: Analyze existing broker position lookup patterns
  - [ ] Subtask 1.2: Implement call to get_positions() function
  - [ ] Subtask 1.3: Add filtering logic for tradingsymbol, exchange, and producttype matching
  - [ ] Subtask 1.4: Extract and return net quantity as string format
  - [ ] Subtask 1.5: Handle position not found scenario (return "0")
  - [ ] Subtask 1.6: Handle get_positions() failure gracefully (return "0" with error logging)

- [ ] Task 2: Add validation and logging (AC: 5, 6)
  - [ ] Subtask 2.1: Implement exact matching for symbol, exchange, and product type
  - [ ] Subtask 2.2: Add comprehensive input validation for parameters
  - [ ] Subtask 2.3: Implement detailed logging for lookup results and debugging
  - [ ] Subtask 2.4: Add performance logging for execution time tracking

- [ ] Task 3: Error handling and edge cases (AC: 3, 4)
  - [ ] Subtask 3.1: Test and handle empty positions response
  - [ ] Subtask 3.2: Implement graceful handling of malformed position data
  - [ ] Subtask 3.3: Add appropriate error logging without exposing sensitive data
  - [ ] Subtask 3.4: Ensure function always returns valid string quantity

## Dev Notes

### Relevant Source Tree
- `broker/jainam_prop/api.py` - API client implementation
- `broker/jainam_prop/` - Position-related functions to be implemented
- `services/` - Service layer patterns for position functions
- `broker/` - Other broker implementations for reference (zerodha, upstox, etc.)

### Function Context
- This function is a utility for smart order placement logic
- Called by `place_smartorder_api()` to calculate position deltas
- Must be fast and reliable for real-time order placement
- Returns standardized string format for quantity calculations

### Position Data Context
- Leverages `get_positions()` function from Story 1.2-1
- Filters positions by exact symbol, exchange, and product type match
- Returns net quantity (positive for long, negative for short, zero for flat)
- Handles various position scenarios and error conditions

### Testing Standards
- Unit tests for position filtering and quantity calculation
- Integration tests with mock position data
- Edge case tests (no positions, multiple positions, exact matching)
- Performance tests to verify <5 second execution time
- Error handling tests for get_positions() failures

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial story creation from Epic 1.5 | Bob (Scrum Master) |

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## QA Results
