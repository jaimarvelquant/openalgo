# Story 1.1-1: Database-Integration

## Status
Done

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

- [x] Task 1: Implement get_token_from_symbol function (AC: 1, 2)
  - [x] Subtask 1.1: Create database connection logic following existing broker patterns
  - [x] Subtask 1.2: Implement parameterized query for symbol_token table lookup
  - [x] Subtask 1.3: Add error handling for missing symbols with descriptive ValueError
  - [x] Subtask 1.4: Add logging for lookup attempts and results

- [x] Task 2: Implement save_master_contract_to_db function (AC: 3, 4)
  - [x] Subtask 2.1: Analyze existing broker database patterns for master contract storage
  - [x] Subtask 2.2: Implement bulk delete of existing jainam_prop records
  - [x] Subtask 2.3: Implement parameterized bulk insert of DataFrame rows
  - [x] Subtask 2.4: Add connection management and error handling

- [x] Task 3: Integrate master contract download (AC: 5)
  - [x] Subtask 3.1: Review existing master contract download patterns
  - [x] Subtask 3.2: Implement Jainam Prop master contract API call
  - [x] Subtask 3.3: Process API response into DataFrame format
  - [x] Subtask 3.4: Call save_master_contract_to_db with processed data

- [x] Task 4: Performance optimization and testing (AC: 6)
  - [x] Subtask 4.1: Add database connection pooling if needed
  - [x] Subtask 4.2: Implement query result caching strategy
  - [x] Subtask 4.3: Performance test token lookup operations
  - [x] Subtask 4.4: Optimize query performance to meet <100ms requirement

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
| 2025-10-06 | 1.1 | Implemented DB-backed token lookup and master contract persistence | James (Dev) |
| 2025-10-06 | 1.2 | Fixed QA findings for exchange mapping and added persistence regression tests | James (Dev) |
| 2025-10-06 | 1.3 | Routed CDS/BFO orders through canonical exchange mapping and added transform regression suite | James (Dev) |
| 2025-10-06 | 1.4 | Removed NSE fallback in transform_data and added regression coverage for unsupported exchanges | James (Dev) |
| 2025-10-07 | 1.5 | Added cached token lookup benchmark tooling and archived latency evidence | James (Dev) |

## Dev Agent Record

### Agent Model Used

- GPT-5 (Codex)

### Debug Log References

- 2025-10-06: `python3 -m pytest test/broker/jainam_prop/test_transform_data.py -q`
- 2025-10-07: `python3 -m pytest test/broker/jainam_prop -q`
- 2025-10-07: `python3 scripts/benchmark_jainam_token_lookup.py --instrument-count 120000 --iterations 500 --repeat 5`

### Completion Notes List

- Replaced placeholder Jainam token lookup with SQLAlchemy-powered resolver against `symbol_token`, including LRU caching and descriptive errors.
- Implemented master contract persistence that maps API payloads into database rows, removes stale broker entries, batches inserts, and builds indexes for <100ms lookups.
- Added cache invalidation post-refresh and verified <100 ms cached lookups via the benchmark script with a 120k instrument dataset.
- Imported Jainam segment mapping into persistence layer, extended mapping for NSECD/BSEFO, and captured regression coverage to lock the behaviour.
- Delegated order exchange segments to the shared `map_exchange_to_jainam` helper and added coverage proving CDS/BFO flows resolve correct segments and tokens (`python3 -m pytest test/broker/jainam_prop -q`).
- Removed the NSE default fallback so unsupported exchanges fail fast and added regression coverage for CDS/BFO routing plus error handling of unknown segments.
- Captured benchmark artefacts in `docs/bmad/qa/evidence/story-1.1-1-token-lookup-latency.md` to close AC6 traceability.

### File List

- broker/jainam_prop/mapping/transform_data.py
- broker/jainam_prop/database/master_contract_db.py
- test/broker/jainam_prop/test_master_contract_db.py
- test/broker/jainam_prop/test_transform_data.py
- scripts/benchmark_jainam_token_lookup.py
- docs/bmad/qa/evidence/story-1.1-1-token-lookup-latency.md

### QA Re-Review Request

- Previous QA decision: PASS with outstanding latency evidence.
- Issues addressed: Captured cached token lookup latency metrics (<0.001 ms per call) using `scripts/benchmark_jainam_token_lookup.py` seeded with 120k instruments; archived results in `docs/bmad/qa/evidence/story-1.1-1-token-lookup-latency.md`.
- Testing results: `python3 -m pytest test/broker/jainam_prop -q` (5 passed, 0 failed, 6 warnings) on 2025-10-07.
- Risk assessment: Low — tooling-only addition; no runtime code paths modified.

## QA Results

### Review Date: 2025-10-06

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment
`transform_data.transform_data` now delegates exchange resolution to `map_exchange_to_jainam`, preserving CDS/BFO routing for order placement (broker/jainam_prop/mapping/transform_data.py:181-205).
`get_token_from_symbol` exercises the cached `_lookup_token_cached` path with guarded fallbacks so cached hits stay in-memory and missing symbols raise actionable `ValueError`s (broker/jainam_prop/mapping/transform_data.py:42-120).
`save_master_contract_to_db` prepares per-segment records, bulk refreshes, builds indexes, and clears the lookup cache so subsequent lookups remain hot (broker/jainam_prop/database/master_contract_db.py:320-470).
Master contract download continues to batch every Jainam exchange and persist to `symbol_token` using SQLAlchemy parameter binding (broker/jainam_prop/database/master_contract_db.py:29-139).

### Refactoring Performed
- None; review only.

### Compliance Check
- Coding Standards: ✗ Unable to verify — `docs/coding-standards.md` not present in repo.
- Project Structure: ✓ Modules remain under `broker/jainam_prop`, aligned with current layout.
- Testing Strategy: ✓ Regression suites cover persistence and transform flows (test/broker/jainam_prop/test_master_contract_db.py, test/broker/jainam_prop/test_transform_data.py).
- All ACs Met: ✓ AC1-AC6 satisfied pending documented latency evidence (see checklist).

### Improvements Checklist
- [ ] Capture cached lookup latency (<100 ms) against a production-like dataset and record evidence.

### Security Review
Queries continue to use SQLAlchemy parameter binding; no new secrets introduced and credential handling is unchanged.

### Performance Considerations
LRU caching keeps steady-state lookups hot after refresh; collect staging metrics to prove the <100 ms target and monitor cache hit ratios post-refresh.

### Test Evidence
- `python3 -m pytest test/broker/jainam_prop -q` (5 passed, 0 failed, 6 warnings) on 2025-10-06.

### Files Modified During Review
- None (QA review only).

### Gate Status
Gate: PASS → docs/bmad/qa/gates/1.1-1-database-integration.yml
Risk profile: Not generated (QA review only)
NFR assessment: Updated in gate record (performance noted for follow-up)

### Recommended Status
✓ Ready for release once latency evidence is documented.

---
#### Review 2025-10-06 (QA Cycle 3 - Quinn)
- Verified CDS/BFO routing now comes from `map_exchange_to_jainam`, resolving the regression flagged previously (broker/jainam_prop/mapping/transform_data.py:181-205).
- Confirmed token lookup hits the database once per symbol/exchange before serving cached responses and surfacing missing instruments (broker/jainam_prop/mapping/transform_data.py:42-120).
- `python3 -m pytest test/broker/jainam_prop -q` ✅ demonstrates transform plus persistence coverage, superseding the failed revalidation.
- Gate: PASS with a follow-up to log production latency metrics before closing AC6 evidence.

#### Review 2025-10-06 (Revalidation by Quinn)
- Critical: `transform_data` still hard-codes exchange segments and omits `CDS`/`BFO`, so currency and BSE derivatives orders leave with the fallback `NSECM`, causing Jainam to reject or misroute those trades; this breaks Integration Verification IV2 despite the DB fixes (broker/jainam_prop/mapping/transform_data.py:181).
- Verification: `python3 -m pytest test/broker/jainam_prop/test_master_contract_db.py` ✅ (2 passed) - confirms persistence fixes but no coverage yet for the transform/order path.
- Gate: FAIL — unblock only after the exchange mapping delegates to `map_exchange_to_jainam` (or adds the missing segments) and automated coverage exercises the token lookup through `transform_data`.

### Review Date: 2025-10-07

### Reviewed By: Quinn (Test Architect)

### Code Quality Assessment
AC1 & AC2: `_lookup_token_cached` performs parameterised lookups against `symbol_token` and normalises fallback symbols so cached results stay hot while missing instruments raise descriptive `ValueError`s (broker/jainam_prop/mapping/transform_data.py:42-120, 138-171).
AC3 & AC4: `save_master_contract_to_db` deletes/refreshes Jainam rows in a transaction, batches inserts, and recreates indexes using SQLAlchemy `text` bindings to avoid interpolation risks (broker/jainam_prop/database/master_contract_db.py:407-468).
AC5: Master contract ingestion reuses `_prepare_symbol_token_records` to map all Jainam segments into OpenAlgo exchanges, protecting CDS/BFO routing that feeds order placement (broker/jainam_prop/database/master_contract_db.py:330-404; broker/jainam_prop/mapping/transform_data.py:182-209).
AC6: Cached lookups benchmark below 0.001 ms across a 120k instrument dataset, with cache invalidation tied to the persistence refresh, satisfying the <100 ms SLA (docs/bmad/qa/evidence/story-1.1-1-token-lookup-latency.md).

### Refactoring Performed
- None; review only.

### Compliance Check
- Coding Standards: ✗ Unable to verify — `docs/coding-standards.md` absent in repo.
- Project Structure: ✓ Changes remain scoped to `broker/jainam_prop` modules, aligned with current layout.
- Testing Strategy: ✓ Regression suites exercise persistence and order transform flows via temporary SQLite databases (test/broker/jainam_prop/test_master_contract_db.py, test/broker/jainam_prop/test_transform_data.py).
- All ACs Met: ✓ AC1-AC6 validated via regression tests and latency evidence (docs/bmad/qa/evidence/story-1.1-1-token-lookup-latency.md).

### Improvements Checklist
- [x] Capture cached lookup latency (<100 ms) against production-sized dataset (docs/bmad/qa/evidence/story-1.1-1-token-lookup-latency.md).
- [ ] Monitor cached token lookup SLA in staging/production after deployment to catch drift (handoff to release ops).

### Security Review
SQLAlchemy parameter binding prevents injection; exceptions surface generic messages and no new secrets are persisted (broker/jainam_prop/database/master_contract_db.py:439-467).

### Performance Considerations
Cached lookups complete in <0.001 ms and master contract refresh clears the LRU cache after batch inserts so subsequent orders avoid cold-miss penalties; evidence captured on 2025-10-07.

### Test Evidence
- 2025-10-07: `python3 -m pytest test/broker/jainam_prop -q`
- 2025-10-07: Verified benchmark artefact `docs/bmad/qa/evidence/story-1.1-1-token-lookup-latency.md`.

### Files Modified During Review
- None (QA review only).

### Gate Status
Gate: PASS → docs/bmad/qa/gates/1.1-1-database-integration.yml
Risk profile: Not generated (QA review only)
NFR assessment: Updated in gate record (performance PASS with cached evidence).

### Recommended Status
✓ Ready for Done.

---
#### Review 2025-10-07 (QA Cycle 4 - Quinn)
- Confirmed cached token lookup path meets AC1-AC6 with benchmark evidence and regression tests.
- Noted follow-up to monitor latency in staging; no code changes required for this cycle.
