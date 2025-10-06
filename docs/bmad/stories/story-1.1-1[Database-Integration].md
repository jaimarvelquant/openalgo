# Story 1.1-1: Database-Integration

## Status
Approved

## Story

**As a** developer implementing the Jainam Prop integration,
**I want** symbol-to-token lookup to query the actual database instead of returning placeholder value 123456,
**so that** order placement can resolve symbols to correct instrument tokens and successfully place orders with Jainam API.

## Acceptance Criteria

1. **AC1**: `get_token_from_symbol(symbol, exchange)` function queries the `symbol_token` table with `broker='jainam_prop'` and returns the integer token value
2. **AC2**: Function raises `ValueError` with descriptive message if symbol not found in database
3. **AC3**: `save_master_contract_to_db(df)` function connects to database, deletes existing `broker='jainam_prop'` records, and inserts DataFrame rows
4. **AC4**: Database operations use parameterized queries and properly close connections
5. **AC5**: Master contract download populates database with 100,000+ instruments across all exchanges
6. **AC6**: Token lookup performance is <100ms for cached queries

## Integration Verification

**IV1**: Verify other broker integrations continue to work after database changes
**IV2**: Test that `place_order_api()` successfully uses token lookup to place orders
**IV3**: Measure database query time and verify <100ms performance

## Tasks / Subtasks

- [ ] Task 1: Implement get_token_from_symbol function (AC: 1, 2)
  - [ ] Subtask 1.1: Create database connection logic following existing broker patterns
  - [ ] Subtask 1.2: Implement parameterized query for symbol_token table lookup
  - [ ] Subtask 1.3: Add error handling for missing symbols with descriptive ValueError
  - [ ] Subtask 1.4: Add logging for lookup attempts and results

- [ ] Task 2: Implement save_master_contract_to_db function (AC: 3, 4)
  - [ ] Subtask 2.1: Analyze existing broker database patterns for master contract storage
  - [ ] Subtask 2.2: Implement bulk delete of existing jainam_prop records
  - [ ] Subtask 2.3: Implement parameterized bulk insert of DataFrame rows
  - [ ] Subtask 2.4: Add connection management and error handling

- [ ] Task 3: Integrate master contract download (AC: 5)
  - [ ] Subtask 3.1: Review existing master contract download patterns
  - [ ] Subtask 3.2: Implement Jainam Prop master contract API call
  - [ ] Subtask 3.3: Process API response into DataFrame format
  - [ ] Subtask 3.4: Call save_master_contract_to_db with processed data

- [ ] Task 4: Performance optimization and testing (AC: 6)
  - [ ] Subtask 4.1: Add database connection pooling if needed
  - [ ] Subtask 4.2: Implement query result caching strategy
  - [ ] Subtask 4.3: Performance test token lookup operations
  - [ ] Subtask 4.4: Optimize query performance to meet <100ms requirement

## Dev Notes

### Relevant Source Tree
- `broker/jainam_prop/` - Main broker implementation directory
- `database/` - Database connection and schema utilities
- `database/token_db.py` - Token database operations (reference for patterns)
- `database/symbol.py` - Symbol handling utilities
- `utils.py` - Common utilities including database helpers

### Database Schema Context
- `symbol_token` table exists with columns: symbol, exchange, token, broker
- Follow existing patterns from other brokers (zerodha, upstox, etc.)
- Use existing database connection patterns from `database/__init__.py`

### API Integration Context
- Jainam Prop uses XTS API similar to other XTS-based brokers
- Master contract endpoint: `/interactive/instruments/master`
- Authentication follows existing broker patterns
- Token lookup must be fast for order placement workflow

### Testing Standards
- Unit tests in `test/broker/jainam_prop/`
- Integration tests must verify database operations work correctly
- Performance tests for token lookup speed requirement
- Follow existing test patterns from other broker integrations

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial story creation from Epic 1.1 | Bob (Scrum Master) |

## Dev Agent Record

### Agent Model Used

### Debug Log References

### Completion Notes List

### File List

## QA Results
