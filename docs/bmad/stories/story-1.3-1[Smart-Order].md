# Story 1.3-1: Smart-Order

## Status
Done

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

- [x] Task 1: Implement smart order core logic (AC: 1, 2, 3, 6)
  - [x] Subtask 1.1: Analyze existing order placement patterns and smart order requirements
  - [x] Subtask 1.2: Extract position_size from input data parameter
  - [x] Subtask 1.3: Call get_open_position() to get current position quantity
  - [x] Subtask 1.4: Calculate position delta (target - current)
  - [x] Subtask 1.5: Determine order action based on delta (BUY/SELL) and quantity
  - [x] Subtask 1.6: Handle delta == 0 case (return success message, no order needed)
  - [x] Subtask 1.7: Add comprehensive logging for position calculations

- [x] Task 2: Integrate with order placement (AC: 4, 5)
  - [x] Subtask 2.1: Prepare order parameters from calculated delta and action
  - [x] Subtask 2.2: Call place_order_api() with calculated parameters
  - [x] Subtask 2.3: Handle order placement success and return appropriate response
  - [x] Subtask 2.4: Implement error handling for order placement failures
  - [x] Subtask 2.5: Add error logging for failed operations

- [x] Task 3: Error handling and validation (AC: 5)
  - [x] Subtask 3.1: Handle get_open_position() failures gracefully
  - [x] Subtask 3.2: Validate input data contains required position_size field
  - [x] Subtask 3.3: Add input validation for all required order parameters
  - [x] Subtask 3.4: Implement standardized error response format
  - [x] Subtask 3.5: Add appropriate error logging without exposing sensitive data

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
- Codex GPT-5

### Debug Log References
- python3 -m pytest broker/jainam_prop/test_smart_order.py

### Completion Notes List
- Implemented `place_smartorder_api()` in `/broker/jainam_prop/api/order_api.py` to compute position deltas, emit detailed calculation logs, and return standardized responses for zero-delta scenarios.
- Added strict numeric parsing and required-field validation so smart orders reject malformed payloads before attempting broker calls.
- Forward the derived BUY/SELL action and quantity to `place_order_api()`, propagating success metadata and surfacing structured errors for lookup or order failures.
- Created targeted pytest suite in `/broker/jainam_prop/test_smart_order.py` covering BUY, SELL, no-op, lookup failure, invalid input, malformed broker responses, and latency gating assertions (10 tests passing).
- Extended smart order coverage with flat-open, flatten-to-zero, and reversal scenarios plus latency-threshold warning assertions to satisfy IV2.
- Instrumented smart orders with perf-counter timing, logging, and response metadata to demonstrate compliance with the 10-second IV3 SLA.

### File List
- Modified: `/broker/jainam_prop/api/order_api.py`
- Created: `/broker/jainam_prop/test_smart_order.py`
- Modified: `/docs/bmad/stories/story-1.3-1[Smart-Order].md`

## QA Results
### Initial Review - Quinn (QA)
- ✅ **Coverage:** AC1–AC6 behaviour verified by walking the new `place_smartorder_api` flow (`broker/jainam_prop/api/order_api.py:567`), and the associated pytest suite exercises happy-path BUY/SELL, zero-delta, lookup failures, invalid payloads, and malformed broker replies (`broker/jainam_prop/test_smart_order.py:24`).
- ⚠️ **Concern:** IV2 calls for exercising all smart-order scenarios (opening, increasing, reducing, closing, reversing, no-change). Current automated coverage hits increasing, reducing, and no-change only; there is no proof for opening-from-flat or reversing positions, nor full-close-to-zero cases in service-level tests.
- ⚠️ **Concern:** IV3 requires documenting execution time under 10 seconds, but the implementation never records or asserts end-to-end latency for smart orders. `get_positions()` inherits a 10s timeout, yet no benchmark or log evidence accompanies this story.

### Review Date: 2025-10-08
### Reviewed By: Quinn (Test Architect)

### Automated Verification
- `python3 -m pytest broker/jainam_prop/test_smart_order.py` (6 passed, 0 failed; 2 SQLAlchemy deprecation warnings)

### Follow-up Review - Quinn (QA)
- ✅ **AC Coverage:** The finalized `place_smartorder_api` flow now validates payloads, parses integer targets, computes deltas, logs full context, short-circuits zero-delta cases, and forwards BUY/SELL/quantity details into order placement, satisfying AC1–AC6 end to end (`broker/jainam_prop/api/order_api.py:569`).
- ✅ **Integration Verification:** The expanded pytest suite exercises opening-from-flat, increasing, reducing, flattening to zero, reversing, no-change, and latency-violation paths, giving evidence for IV1 and IV2 scenarios (`broker/jainam_prop/test_smart_order.py:27`, `broker/jainam_prop/test_smart_order.py:72`, `broker/jainam_prop/test_smart_order.py:96`, `broker/jainam_prop/test_smart_order.py:120`, `broker/jainam_prop/test_smart_order.py:144`, `broker/jainam_prop/test_smart_order.py:191`).
- ✅ **Performance Evidence:** Smart orders now annotate responses with latency metadata and emit warnings when exceeding the 10 second SLA; tests assert both the metadata and threshold handling, providing the proof requested in IV3 (`broker/jainam_prop/api/order_api.py:580`, `broker/jainam_prop/test_smart_order.py:191`).
- ⚠️ **Watch:** Real broker latency still depends on upstream services; monitor production logs for sustained `latency_status='exceeded_threshold'` signals to catch environmental regressions early.

### Review Date: 2025-10-08
### Reviewed By: Quinn (Test Architect)

### Automated Verification (2025-10-08)
- `python3 -m pytest broker/jainam_prop/test_smart_order.py` (10 passed, 0 failed; 2 SQLAlchemy deprecation warnings)
