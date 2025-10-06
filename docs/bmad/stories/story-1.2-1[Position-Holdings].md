# Story 1.2-1: Position-Holdings

## Status
Draft

## Story

**As a** trader using Jainam Prop with OpenAlgo,
**I want** to view my current positions and long-term holdings in the OpenAlgo UI,
**so that** I can monitor my portfolio and make informed trading decisions.

## Acceptance Criteria

1. **AC1**: Implement `get_positions(auth_token)` that calls `/interactive/portfolio/positions` with `dayOrNet=NetWise`
2. **AC2**: Implement `get_holdings(auth_token)` that calls `/interactive/portfolio/holdings`
3. **AC3**: Both functions handle authentication token parsing consistently
4. **AC4**: Both functions implement error handling and return standardized error responses
5. **AC5**: Functions use `get_httpx_client()` with 10-second timeout
6. **AC6**: Response data includes all required fields (symbol, exchange, product, quantity, price, P&L)

## Integration Verification

**IV1**: Verify existing order placement and quote fetching continue to work
**IV2**: Test OpenAlgo's positions and holdings pages display data correctly
**IV3**: Measure API response time and verify <5 seconds completion

## Tasks / Subtasks

- [ ] Task 1: Implement get_positions function (AC: 1, 3, 4, 5, 6)
  - [ ] Subtask 1.1: Analyze existing broker position retrieval patterns
  - [ ] Subtask 1.2: Implement API call to /interactive/portfolio/positions with NetWise parameter
  - [ ] Subtask 1.3: Add authentication token parsing and validation
  - [ ] Subtask 1.4: Implement httpx client usage with 10-second timeout
  - [ ] Subtask 1.5: Add comprehensive error handling and logging
  - [ ] Subtask 1.6: Format response data with required fields (symbol, exchange, product, quantity, price, P&L)

- [ ] Task 2: Implement get_holdings function (AC: 2, 3, 4, 5, 6)
  - [ ] Subtask 2.1: Analyze existing broker holdings retrieval patterns
  - [ ] Subtask 2.2: Implement API call to /interactive/portfolio/holdings
  - [ ] Subtask 2.3: Ensure consistent authentication token handling with positions
  - [ ] Subtask 2.4: Implement httpx client usage with 10-second timeout
  - [ ] Subtask 2.5: Add comprehensive error handling and logging
  - [ ] Subtask 2.6: Format response data with required fields matching positions format

- [ ] Task 3: Integration and standardization (AC: 4)
  - [ ] Subtask 3.1: Implement standardized error response format
  - [ ] Subtask 3.2: Add appropriate logging for debugging and monitoring
  - [ ] Subtask 3.3: Ensure functions follow OpenAlgo service layer patterns
  - [ ] Subtask 3.4: Add input validation for auth_token parameter

## Dev Notes

### Relevant Source Tree
- `broker/jainam_prop/api.py` - API client implementation
- `services/` - Service layer patterns for portfolio functions
- `broker/` - Other broker implementations for reference (zerodha, upstox, etc.)
- `utils.py` - HTTP client utilities including get_httpx_client()

### API Context
- Jainam Prop uses XTS API endpoints similar to other XTS-based brokers
- Positions endpoint: `/interactive/portfolio/positions` with `dayOrNet=NetWise`
- Holdings endpoint: `/interactive/portfolio/holdings`
- Authentication follows existing broker patterns
- Response format needs to match OpenAlgo's expected portfolio data structure

### Service Layer Patterns
- Follow existing portfolio function patterns from other brokers
- Use standardized error response format
- Implement proper logging and monitoring
- Ensure httpx client configuration matches other broker implementations

### Testing Standards
- Unit tests for API calls and response parsing
- Integration tests with mock API responses
- Performance tests to verify <5 second response time
- Error handling tests for various failure scenarios
- Follow existing test patterns from other broker portfolio functions

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial story creation from Epic 1.3 | Bob (Scrum Master) |

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## QA Results
