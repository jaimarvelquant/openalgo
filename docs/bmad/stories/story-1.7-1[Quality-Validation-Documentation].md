# Story 1.7-1: Quality Validation & Documentation

## Status
Draft

## Estimated Effort
**8-12 hours** (Testing, documentation, validation)

## Code Reuse Summary

**Reuse Breakdown:**
- ✅ Test patterns: 70% reusable from other broker tests
- ✅ Performance benchmarks: 80% reusable from existing benchmarks
- ✅ Documentation templates: 75% reusable from other broker docs
- ✅ Validation scripts: 60% reusable from existing scripts

**Reference:**
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 7
- **Test Patterns:** Other broker test suites (70% reusable)
- **Documentation:** Other broker READMEs and runbooks (75% reusable)

**Effort Reduction:** ~40% (from 15-20 hours to 8-12 hours)

## Story

**As a** release manager for the Jainam Prop integration,
**I want** comprehensive testing, performance benchmarking, and updated documentation covering all enhancement phases,
**so that** the integration meets production-readiness criteria, parity with Fivepaisa is documented and validated, and operational teams have complete runbooks for deployment, monitoring, and troubleshooting.

## Acceptance Criteria

1. **AC1**: Update existing pytest suites (`test_auth_api.py`, `test_order_api.py`, `test_jainam_websocket.py`, etc.) to reflect new authentication flows, token persistence, HTTP helper usage, and streaming reconnect logic, ensuring all tests pass without regressions.
2. **AC2**: Add new test modules covering HTTP helper error paths, token lifecycle edge cases (expired tokens, missing DB entries), streaming reconnect scenarios, subscription replay logic, and capability registry validation.
3. **AC3**: Extend performance benchmarks (`test_auth_benchmark.py`, `test_performance_standalone.py`) to assert authentication latency (<2s), token cache lookup (<100ms), smart order delta handling (<10s), and streaming reconnect time (<30s).
4. **AC4**: Create live validation scripts (`scripts/validate_jainam_*.py`) for manual operational testing covering authentication, order placement, market data queries, streaming connections, and smart order flows with production-like credentials.
5. **AC5**: Update broker README and operational runbooks (`docs/bmad/qa/`, `docs/bmad/research/`) documenting credential setup, token storage, configuration management, streaming operations, error handling procedures, and parity status vs Fivepaisa.
6. **AC6**: Produce parity checklist comparing Jainam Prop features against Fivepaisa reference implementation, documenting gaps, workarounds, and Pro-specific capabilities (dealer endpoints, bracket orders, market depth message codes).
7. **AC7**: Conduct final sign-off review against Phase 1-4 success criteria, documenting validation outcomes, residual risks, and post-deployment monitoring requirements.

## Integration Verification

**IV1**: Verify CI/CD pipeline executes full test suite (unit, integration, performance) without failures; all new tests integrated into CI configuration.
**IV2**: Confirm live validation scripts execute successfully in staging environment with test credentials, demonstrating end-to-end workflows.
**IV3**: Ensure documentation accuracy by having operations team execute runbooks independently without developer support, capturing feedback and gaps.

## Tasks / Subtasks

- [ ] Task 1: Test suite updates and regression validation (AC: 1, 2)
  - [ ] Subtask 1.1: Update `test_auth_api.py` to test new authentication flows with SDK wrapper, token persistence, and JWT validation.
  - [ ] Subtask 1.2: Update `test_order_api.py` to test HTTP helper integration, smart order delta logic, and Pro-specific endpoints (dealer orderbook, bracket orders).
  - [ ] Subtask 1.3: Update `test_jainam_websocket.py` to test streaming adapter reconnect logic, subscription replay, and capability validation.
  - [ ] Subtask 1.4: Create `test_http_helper.py` testing retry logic, backoff timing, timeout handling, and error propagation.
  - [ ] Subtask 1.5: Create `test_token_lifecycle.py` testing token persistence, expiration handling, DB lookup failures, and JWT parsing edge cases.
  - [ ] Subtask 1.6: Create `test_capability_registry.py` testing capability queries, unsupported exchange validation, and message code lookups.
  - [ ] Subtask 1.7: Run full pytest suite and resolve all test failures; document any intentional behavioral changes.

- [ ] Task 2: Performance benchmarking and validation (AC: 3)
  - [ ] Subtask 2.1: Extend `test_auth_benchmark.py` to assert authentication latency (<2s) and token cache lookup (<100ms).
  - [ ] Subtask 2.2: Add smart order benchmark test asserting end-to-end delta handling completes within 10s.
  - [ ] Subtask 2.3: Add streaming reconnect benchmark asserting reconnection completes within 30s of disconnect event.
  - [ ] Subtask 2.4: Add HTTP helper benchmark testing retry overhead under simulated 5xx responses.
  - [ ] Subtask 2.5: Run benchmarks in controlled environment; document baseline metrics and acceptable thresholds.

- [ ] Task 3: Live validation scripts and operational testing (AC: 4)
  - [ ] Subtask 3.1: Create `scripts/validate_jainam_auth.py` testing authentication, token persistence, and JWT validation with test credentials.
  - [ ] Subtask 3.2: Create `scripts/validate_jainam_orders.py` testing order placement, smart orders, order book/trade book queries.
  - [ ] Subtask 3.3: Create `scripts/validate_jainam_data.py` testing market data queries, historical data, search endpoints.
  - [ ] Subtask 3.4: Create `scripts/validate_jainam_streaming.py` testing WebSocket connection, subscriptions, reconnect scenarios.
  - [ ] Subtask 3.5: Execute validation scripts in staging environment; document outcomes and edge cases discovered.

- [ ] Task 4: Documentation updates and parity analysis (AC: 5, 6)
  - [ ] Subtask 4.1: Update `broker/jainam_prop/README.md` with credential setup, configuration variables, token lifecycle overview.
  - [ ] Subtask 4.2: Update `docs/bmad/qa/live-validation-runbook.md` with validation script usage, troubleshooting steps, expected outputs.
  - [ ] Subtask 4.3: Create `docs/bmad/research/jainam-fivepaisa-parity.md` comparing features, capabilities, and implementation patterns.
  - [ ] Subtask 4.4: Document Pro-specific capabilities (dealer endpoints, bracket/cover orders, market depth codes) in parity checklist.
  - [ ] Subtask 4.5: Create operational monitoring guide covering key metrics, log patterns, alert thresholds for streaming reconnects, token expiration.
  - [ ] Subtask 4.6: Update configuration guide (`docs/bmad/research/configuration-guide.md`) with all environment variables and deployment examples.

- [ ] Task 5: Sign-off review and validation (AC: 7, IV1, IV2, IV3)
  - [ ] Subtask 5.1: Conduct walkthrough of Phase 1-4 acceptance criteria against implementation outcomes.
  - [ ] Subtask 5.2: Execute full CI/CD test suite; document pass/fail status and coverage metrics.
  - [ ] Subtask 5.3: Run live validation scripts in staging; capture execution logs and validation evidence.
  - [ ] Subtask 5.4: Facilitate operations team runbook review; collect feedback and update documentation gaps.
  - [ ] Subtask 5.5: Document residual risks, known limitations, and post-deployment monitoring plan.
  - [ ] Subtask 5.6: Produce final sign-off report summarizing validation outcomes, parity status, and launch readiness.

## Dev Notes

### Code Reuse Guidance - Testing & Documentation

**Test Pattern Reuse:**
- ✅ **Other broker tests:** 70% reusable patterns
- ✅ **Existing Jainam tests:** 60% already complete, need updates
- ✅ **Performance benchmarks:** 80% reusable from existing benchmarks

**Documentation Reuse:**
- ✅ **Other broker READMEs:** 75% reusable structure
- ✅ **Existing runbooks:** 70% reusable procedures
- ✅ **Configuration guides:** 80% reusable templates

**Test Pattern Example (from other brokers):**
```python
# test_auth_api.py (70% reusable pattern)
def test_authenticate_direct():
    """Test direct authentication flow"""
    # Arrange
    auth_api = JainamAPI()

    # Act
    auth_token, feed_token, user_id, error = authenticate_direct()

    # Assert
    assert auth_token is not None
    assert feed_token is not None
    assert user_id is not None
    assert error is None

def test_authenticate_invalid_credentials():
    """Test authentication with invalid credentials"""
    # Pattern 70% reusable from other broker tests
    # ...
```

**Documentation Template (75% reusable):**
```markdown
# Jainam Prop Broker Integration

## Configuration
- JAINAM_INTERACTIVE_API_KEY
- JAINAM_INTERACTIVE_API_SECRET
- JAINAM_MARKET_API_KEY
- JAINAM_MARKET_API_SECRET
- JAINAM_BASE_URL

## Authentication
[Copy from FivePaisaXTS README - 75% reusable]

## Pro-Specific Features
[Add Pro-specific documentation - 25% new]
- Dealer operations
- Bracket/cover orders
- Pro market data codes
```

**Reuse Percentages:**
- Test updates: 70% reusable patterns
- New tests: 60% reusable patterns
- Performance benchmarks: 80% reusable
- Documentation: 75% reusable
- Validation scripts: 60% reusable
- Overall: 70% reusable

### Relevant Source Tree
- `broker/jainam_prop/test_*.py` – ⚠️ Existing tests (60% complete, need updates)
- `broker/jainam_prop/test_auth_benchmark.py` – ✅ Performance benchmarks (80% reusable)
- `scripts/validate_jainam_*.py` – ⚠️ Validation scripts (to be created, 60% reusable)
- `docs/bmad/qa/live-validation-runbook.md` – ✅ Runbook template (70% reusable)
- `docs/bmad/research/jainam-code-reuse-analysis.md` – ✅ Code reuse analysis (reference)
- `broker/jainam_prop/README.md` – ⚠️ Needs updates (75% reusable from other brokers)
- Other broker test suites – ✅ Reference for patterns (70% reusable)

### Integration Approach
- ✅ Reuse test patterns from other brokers (70%)
- ⚠️ Update existing Jainam tests (60% complete)
- ✅ Reuse documentation templates (75%)
- ⚠️ Add Pro-specific documentation (25% new)
- Add new test modules targeting specific enhancement areas (token lifecycle, streaming resilience, capability validation).
- Create live validation scripts mirroring test structure but using real credentials and operational workflows.
- Document all changes in runbooks and README with examples, troubleshooting steps, and parity analysis.

### Existing Pattern Reference
- **Testing Strategy:** Implementation plan Section 10 describes test layers (unit, integration, streaming, performance, regression) with tooling and coverage focus (lines 413–423).
- **Success Criteria:** Implementation plan Section 12 defines acceptance thresholds for authentication, REST parity, streaming resilience, and documentation completeness (lines 437–447).
- **Parity Requirements:** Reference Fivepaisa implementation for order lifecycle, data services, streaming adapter patterns to document gaps and Pro-specific enhancements.

### Key Constraints
- All tests must run in CI/CD without manual intervention; no hardcoded credentials or environment-specific dependencies.
- Live validation scripts must support credential injection via environment variables or secure credential stores.
- Documentation must be accessible to operations teams unfamiliar with implementation details; avoid excessive technical jargon.
- Parity analysis must distinguish between intentional differences (Pro-specific features) and unimplemented capabilities.

### Validation Checklist Template

#### Authentication & Token Lifecycle
- [ ] Interactive login returns valid `auth_token`, `userID`, and persists to DB
- [ ] Market data login returns valid `market_token` and persists to DB
- [ ] Token rehydration from DB succeeds without re-authentication
- [ ] JWT parsing extracts `userID` and expiration from feed token
- [ ] Expired token handling triggers re-authentication workflow

#### REST API Parity
- [ ] Order placement (market, limit, SL, SL-M) matches Fivepaisa behavior
- [ ] Smart order delta calculation handles all scenarios (open, increase, reduce, close, reverse, no-change)
- [ ] Order book, trade book, positions, holdings return consistent structures
- [ ] Market data queries (quotes, historical, search) deliver expected results
- [ ] Funds endpoint returns accurate available/utilized balances

#### Streaming & Realtime
- [ ] WebSocket adapter establishes connection with feed token
- [ ] Subscriptions deliver market data for supported exchanges/message codes
- [ ] Reconnect logic triggers on disconnect with exponential backoff
- [ ] Subscription replay restores all active subscriptions after reconnect
- [ ] Capability registry accurately reflects supported exchanges and depth levels

#### Pro-Specific Features
- [ ] Dealer order book returns `clientID`-scoped orders
- [ ] Dealer trade book returns `clientID`-scoped trades
- [ ] Dealer positions (`get_dealerposition_netwise`) return accurate net quantities
- [ ] Bracket order placement with target/stoploss parameters succeeds
- [ ] Cover order placement with trigger price succeeds
- [ ] Market depth message codes (1501/1502/1505/1510/1512) deliver expected data

#### Configuration & Operations
- [ ] Base URL configurable via environment variable without code changes
- [ ] SSL verification configurable via `JAINAM_DISABLE_SSL` flag
- [ ] Retry parameters tunable via environment variables
- [ ] Logs emit structured events for monitoring and alerting
- [ ] Documentation runbooks enable independent operations team deployment

## Testing

- **Unit Tests:** All test modules (auth, order, data, streaming, config, SDK wrapper) with mocked dependencies.
- **Integration Tests:** Live validation scripts with test credentials exercising end-to-end workflows.
- **Performance Tests:** Benchmarks asserting latency thresholds (authentication, token lookup, smart order, streaming reconnect).
- **Regression Tests:** Full pytest suite confirming no regressions in existing functionality.
- **Documentation Tests:** Operations team walkthrough of runbooks without developer support.

## Dependencies

- **Story 1.0-1**: Authentication & Token Lifecycle (Phase 1) – Authentication flows must be complete for validation testing.
- **Story 1.3-1**: Smart Order (Phase 2.5) – Smart order implementation required for delta handling validation.
- **Story 1.5-1**: Streaming Adapter Refactor (Phase 3) – Streaming resilience required for reconnect/replay validation.
- **Story 1.6-1**: Configuration Management (Phase 3.4) – Config module required for environment-specific validation.
- **Story 1.6-2**: SDK Integration Strategy (Phase 3.4) – SDK wrapper required for authentication and order placement testing.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-08 | 0.1 | Initial draft: quality validation and documentation story created from Phase 4 implementation plan | Sarah (PO) |

## Dev Agent Record

### Agent Model Used
_To be populated during implementation_

### Debug Log References
_To be populated during implementation_

### Completion Notes List
_To be populated during implementation_

### File List
_To be populated during implementation_

## QA Results
_To be populated after implementation and testing_
