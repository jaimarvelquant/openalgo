# Story 1.5-2: Capability Registry & Token Validation

## Status
Draft

## Estimated Effort
**4-6 hours** (Deferred to Phase 2 - Streaming implementation)

## Code Reuse Summary

**Reuse Breakdown:**
- ✅ Capability registry pattern: 70% reusable from FivePaisaXTS capability registry
- ✅ Token validation: 80% reusable from standard JWT validation patterns
- ⚠️ Pro market data codes: 0% reusable (Pro-specific, must catalog from XTS Pro SDK)

**Reference:**
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 6
- **FivePaisaXTS:** Capability registry pattern (70% reusable)
- **Pro SDK:** `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/` (Pro market data codes)
- **JWT Validation:** Standard patterns (80% reusable)

**Effort Reduction:** ~40% (from 8-10 hours to 4-6 hours)

**Note:** This story is deferred to Phase 2 (Streaming & Realtime Reliability)

## Story

**As a** streaming data infrastructure maintainer,
**I want** a capability registry describing supported exchanges, depth levels, and message codes with feed-token JWT validation,
**so that** subscription requests are validated against broker capabilities and downstream consumers receive accurate metadata about data availability.

## Acceptance Criteria

1. **AC1**: Implement `JainamCapabilityRegistry` class modeled after `FivepaisaXTSCapabilityRegistry`, exposing supported exchanges (NSE_CM, NSE_FO, BSE_CM, etc.), depth levels, and Pro-specific message codes (1501, 1502, 1505, 1510, 1512).
2. **AC2**: Provide `get_supported_exchanges()`, `get_depth_levels(exchange)`, and `get_message_codes()` methods returning structured metadata suitable for API documentation and runtime validation.
3. **AC3**: Parse feed token JWT payload to extract embedded `userID` and token expiration timestamp, validating tokens before establishing Socket.IO connections.
4. **AC4**: Emit structured warnings when subscription requests target unsupported exchanges or message codes, returning actionable error messages to callers.
5. **AC5**: Integrate capability validation into `subscribe()` flow: reject subscriptions for unsupported exchange segments with clear error responses.
6. **AC6**: Add unit tests confirming capability queries return expected metadata and JWT parsing handles valid tokens, malformed tokens, and expired tokens correctly.
7. **AC7**: Document capability registry usage in streaming adapter docstrings and operational runbooks, including Pro-specific message code reference.

## Integration Verification

**IV1**: Verify capability registry accurately reflects Jainam Pro API capabilities documented in SDK reference and implementation plan (Section 6, lines 309–324).
**IV2**: Confirm JWT parsing successfully extracts `userID` from valid feed tokens without introducing authentication regressions.
**IV3**: Ensure unsupported exchange/message code requests fail gracefully with structured error responses rather than silent failures or crashes.

## Tasks / Subtasks

- [ ] Task 1: Capability registry implementation (AC: 1, 2, 7)
  - [ ] Subtask 1.1: Create `broker/jainam_prop/streaming/capability_registry.py` defining `JainamCapabilityRegistry` class.
  - [ ] Subtask 1.2: Populate `SUPPORTED_EXCHANGES` constant with NSE_CM (1), NSE_FO (2), BSE_CM (11), BSE_FO (12), MCX_FO (51), etc.
  - [ ] Subtask 1.3: Define `DEPTH_LEVELS` mapping exchanges to supported depth modes (5-level, 20-level, etc.).
  - [ ] Subtask 1.4: Document Pro-specific message codes (1501: TouchLine, 1502: MarketDepth, 1505: Candle, 1510: OpenInterest, 1512: FullData).
  - [ ] Subtask 1.5: Implement getter methods returning capability metadata as structured dictionaries.
  - [ ] Subtask 1.6: Add docstrings referencing implementation plan and SDK documentation.

- [ ] Task 2: Feed token JWT validation (AC: 3, 6)
  - [ ] Subtask 2.1: Introduce `parse_feed_token(token: str)` function in `api/auth_api.py` or `streaming/capability_registry.py`.
  - [ ] Subtask 2.2: Decode JWT payload using `jwt.decode` (PyJWT library) without signature verification (reference only; adapt based on token format).
  - [ ] Subtask 2.3: Extract `userID`, `exp` (expiration), and other relevant claims from decoded payload.
  - [ ] Subtask 2.4: Validate token expiration against current timestamp; emit warning if token is near expiry (<5 min remaining).
  - [ ] Subtask 2.5: Handle malformed tokens gracefully (invalid base64, missing claims), returning structured error responses.

- [ ] Task 3: Subscription validation integration (AC: 4, 5)
  - [ ] Subtask 3.1: Update `subscribe()` method in streaming adapter to query capability registry before sending payloads.
  - [ ] Subtask 3.2: Reject subscriptions for unsupported exchange segments with error response `{"status": "error", "message": "Exchange {X} not supported"}`.
  - [ ] Subtask 3.3: Emit structured warning logs for attempted subscriptions to unsupported message codes.
  - [ ] Subtask 3.4: Return actionable error messages to callers including list of supported exchanges/codes.

- [ ] Task 4: Testing and documentation (AC: 6, 7, IV1, IV2, IV3)
  - [ ] Subtask 4.1: Create `test_capability_registry.py` with test cases for capability queries, supported exchange validation, and message code lookups.
  - [ ] Subtask 4.2: Add JWT parsing tests covering valid tokens, expired tokens, malformed tokens, and missing claims.
  - [ ] Subtask 4.3: Extend streaming adapter tests to simulate unsupported exchange subscription attempts and verify error responses.
  - [ ] Subtask 4.4: Update streaming adapter docstrings with capability registry usage examples.
  - [ ] Subtask 4.5: Document Pro message codes in `docs/bmad/research/` or broker README with mapping to data types.

## Dev Notes

### Relevant Source Tree
- `broker/jainam_prop/streaming/capability_registry.py` – New module for capability metadata (to be created).
- `broker/jainam_prop/api/auth_api.py` – Potential location for JWT parsing utilities.
- `broker/jainam_prop/streaming/jainam_websocket.py` – Streaming adapter requiring capability validation integration.
- `broker/fivepaisaxts/streaming/capability_registry.py` – Reference implementation for Fivepaisa capabilities (if exists).
- `broker/jainam_prop/_sample_strategy/xts_connect.py` – Reference for exchange segment constants and message codes (lines 78, 225).

### Integration Approach
- Define capability registry as singleton or module-level constants accessible from streaming adapter and API documentation.
- Integrate JWT parsing during adapter initialization to validate feed token before Socket.IO connection.
- Query capability registry in `subscribe()` method to reject invalid requests before network transmission.
- Emit structured logs compatible with OpenAlgo logging pipeline for monitoring and alerting.

### Existing Pattern Reference
- **Capability Metadata:** Implementation plan Section 6 (Phase 3) describes supported exchanges, depth levels, and Pro message codes (lines 309–324).
- **Feed Token Validation:** Fivepaisa adapter decodes feed tokens to extract user IDs (implementation plan lines 313–316).
- **Pro Message Codes:** Sample SDK demonstrates market data message codes 1501/1502/1505/1510/1512 with explicit exchange segment resolution (implementation plan lines 95–107).

### Key Constraints
- JWT parsing must not require signature verification if tokens are pre-validated by broker authentication flow.
- Capability registry should be version-controlled and synchronized with broker API updates.
- Token expiration warnings should trigger proactive re-authentication workflows if expiry is imminent.
- Unsupported exchange/message code errors must not crash adapter; graceful degradation required.

## Testing

- **Unit Tests:** Capability queries, JWT parsing (valid/invalid/expired tokens), subscription validation logic.
- **Integration Tests:** Live adapter initialization with real feed tokens, subscription attempts for supported/unsupported exchanges.
- **Regression Tests:** Verify existing streaming functionality unaffected by capability validation integration.
- **Documentation Tests:** Confirm capability metadata accuracy against Jainam Pro API documentation.

## Dependencies

- **Story 1.5-1**: Streaming Adapter Refactor – Adapter infrastructure must be in place for capability validation integration.
- **Story 1.2-5**: Token Lifecycle Management Enhancement – Feed token persistence enables JWT validation workflow.
- **Phase 3 Implementation Plan**: Streaming & Realtime Reliability (Section 6) – Capability metadata and feed token validation requirements.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-08 | 0.1 | Initial draft: capability registry and token validation story created from Phase 3 implementation plan | Sarah (PO) |

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
