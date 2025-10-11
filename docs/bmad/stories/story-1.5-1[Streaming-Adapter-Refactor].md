# Story 1.5-1: Streaming Adapter Refactor

## ⚠️ DEPRECATED - DO NOT USE

**Status:** SUPERSEDED
**Superseded By:** `story-1.5-1-streaming-adapter-refactor.md`
**Date Deprecated:** 2025-10-11
**Reason:** Replaced with code reuse-first version (70% reuse from FivePaisaXTS, effort reduced from 4 days to 1.5 days)

---

## Original Status
Draft (OBSOLETE)

## Estimated Effort
**8-12 hours** (Deferred to Phase 2 - Streaming implementation)

## Code Reuse Summary

**Reuse Breakdown:**
- ✅ Reconnection logic: 70% reusable from FivePaisaXTS streaming adapter
- ✅ Token rehydration: 100% reusable from Story 1.0-1 (database functions)
- ✅ Subscription management: 60% reusable from other broker adapters
- ⚠️ Pro market data codes: 0% reusable (Pro-specific, must use XTS Pro SDK)

**Reference:**
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 6
- **FivePaisaXTS:** `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py` (70% reusable)
- **Pro SDK:** `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/` (Pro market data)
- **Token Functions:** `database/auth_db.py` (100% reusable)

**Effort Reduction:** ~40% (from 15-20 hours to 8-12 hours)

**Note:** This story is deferred to Phase 2 (Streaming & Realtime Reliability)

## Story

**As a** realtime market data consumer for the Jainam Prop integration,
**I want** a resilient WebSocket adapter with automatic reconnection, subscription replay, and feed token reuse,
**so that** streaming data flows remain uninterrupted during transient network failures and sessions persist without redundant authentication.

## Acceptance Criteria

1. **AC1**: Refactor `streaming/jainam_websocket.py` to inherit from `websocket_proxy.base_adapter` (or `websocket_adapters.base_adapter`), introducing state tracking, thread-safe lock usage, and reconnect attempt counters matching Fivepaisa patterns.
2. **AC2**: Implement automatic reconnection with exponential backoff (initial delay 1s, max delay 60s, max attempts 10) when Socket.IO connections drop or error callbacks fire.
3. **AC3**: Persist active subscriptions in an in-memory registry keyed by exchange segment and instrument ID, ensuring subscriptions are replayed automatically after successful reconnection.
4. **AC4**: Reuse persisted feed tokens from `database.auth_db` during adapter initialization, eliminating redundant market data login calls on each WebSocket instantiation.
5. **AC5**: Add telemetry hooks emitting structured logs for reconnect attempts, subscription replay counts, token reuse success, and connection lifecycle events (connect, disconnect, error).
6. **AC6**: Support graceful shutdown and unsubscription semantics, allowing clean teardown of Socket.IO connections and releasing resources without orphaned event handlers.
7. **AC7**: Validate adapter resilience by simulating connection drops (manual socket close, network interruption) and confirming automatic reconnect with subscription replay within max backoff threshold.

## Integration Verification

**IV1**: Verify the refactored adapter does not regress existing streaming functionality (`test_jainam_websocket.py` passes, live feeds continue delivering market data).
**IV2**: Confirm subscription replay restores all active subscriptions after a reconnect event, with no duplicate or missed instruments.
**IV3**: Ensure reconnection logic honors backoff thresholds and emits appropriate alerts when max reconnect attempts are exhausted.

## Tasks / Subtasks

- [ ] Task 1: Adapter architecture alignment (AC: 1, 4, 6)
  - [ ] Subtask 1.1: Audit Fivepaisa `streaming/fivepaisaxts_adapter.py` for reconnect, state management, and base adapter inheritance patterns.
  - [ ] Subtask 1.2: Refactor `streaming/jainam_websocket.py` to extend base adapter class with `__init__`, `connect`, `disconnect`, and `subscribe` methods.
  - [ ] Subtask 1.3: Introduce thread-safe locks (`threading.Lock`) to protect shared state (connection status, subscription registry).
  - [ ] Subtask 1.4: Load feed token from `database.auth_db.get_feed_token()` during adapter initialization instead of invoking market login.
  - [ ] Subtask 1.5: Implement `shutdown()` method to gracefully close Socket.IO connections and clear event handlers.

- [ ] Task 2: Reconnection and backoff logic (AC: 2, 3, 5)
  - [ ] Subtask 2.1: Add reconnect attempt counter and exponential backoff calculator (base 1s, factor 2.0, max 60s).
  - [ ] Subtask 2.2: Attach error and disconnect callbacks to Socket.IO client that trigger reconnect logic.
  - [ ] Subtask 2.3: Implement subscription replay: iterate registry and reissue subscription payloads after successful reconnection.
  - [ ] Subtask 2.4: Emit structured logs for each reconnect attempt (attempt number, delay, success/failure).
  - [ ] Subtask 2.5: Surface alert when max reconnect attempts are reached without successful connection.

- [ ] Task 3: Subscription registry and lifecycle management (AC: 3, 6, 7)
  - [ ] Subtask 3.1: Introduce in-memory subscription registry (`dict[str, set[int]]` keyed by exchange segment).
  - [ ] Subtask 3.2: Update `subscribe()` method to persist subscriptions in registry before sending Socket.IO payload.
  - [ ] Subtask 3.3: Implement `unsubscribe()` method to remove from registry and send unsubscription payload.
  - [ ] Subtask 3.4: Add registry clear logic in `shutdown()` to prevent replay after intentional disconnect.

- [ ] Task 4: Testing and validation (AC: 7, IV1, IV2, IV3)
  - [ ] Subtask 4.1: Extend `test_jainam_websocket.py` with mock Socket.IO server supporting disconnect/reconnect simulation.
  - [ ] Subtask 4.2: Add test cases verifying subscription replay after reconnect (compare registry before/after).
  - [ ] Subtask 4.3: Validate backoff timing with controlled disconnect/reconnect cycles.
  - [ ] Subtask 4.4: Run regression tests confirming existing streaming functionality remains intact.

## Dev Notes

### Relevant Source Tree
- `broker/jainam_prop/streaming/jainam_websocket.py` – Current WebSocket adapter implementation requiring refactor.
- `broker/fivepaisaxts/streaming/fivepaisaxts_adapter.py` – Reference implementation with reconnect, backoff, and subscription replay.
- `broker/jainam_prop/database/auth_db.py` – Token persistence helpers (`get_feed_token`, `store_broker_auth_token`).
- `broker/jainam_prop/_sample_strategy/xts_connect.py` – Sample SDK Socket.IO usage patterns (reference only).
- `websocket_proxy/base_adapter.py` or `websocket_adapters/base_adapter.py` – Base adapter interface for inheritance.

### Integration Approach
- Mirror Fivepaisa adapter structure: state tracking, lock-protected operations, and DB-backed token reuse.
- Leverage existing SDK Socket.IO client with added error callbacks and reconnect orchestration.
- Persist subscriptions before transmission; replay after reconnect by iterating registry.
- Emit structured logs compatible with OpenAlgo logging pipeline (`utils.logging.get_logger`).

### Existing Pattern Reference
- **Reconnection Logic:** Fivepaisa `fivepaisaxts_adapter.py` implements exponential backoff with configurable thresholds (reference Phase 3 implementation plan, lines 305–324).
- **Token Reuse:** Load feed token from DB during initialization to avoid redundant authentication (`_sample_strategy/xts_connect.py:46`, implementation plan lines 211–254).
- **Subscription Replay:** Maintain in-memory registry and reissue subscriptions post-reconnect (implementation plan lines 313–316).

### Key Constraints
- Adapter must remain thread-safe; protect registry and connection state with locks.
- Backoff parameters should be configurable via environment variables or config module.
- Avoid logging sensitive token payloads; redact credentials in structured logs.
- Reconnection attempts should respect max threshold to prevent infinite loops.

## Testing

- **Unit Tests:** Mock Socket.IO client disconnect/reconnect cycles, validate backoff timing and subscription replay logic.
- **Integration Tests:** Live WebSocket connection with controlled network interruptions, confirming automatic recovery.
- **Performance Tests:** Measure reconnect latency and subscription replay time under simulated load.
- **Regression Tests:** Verify existing `test_jainam_websocket.py` suite passes without modification.

## Dependencies

- **Story 1.2-5**: Token Lifecycle Management Enhancement – Feed token persistence in `database.auth_db` must be operational for adapter to reuse tokens.
- **Phase 3 Implementation Plan**: Streaming & Realtime Reliability (Section 6) – Architectural patterns and acceptance criteria for reconnect, backoff, and subscription management.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-08 | 0.1 | Initial draft: streaming adapter refactor story created from Phase 3 implementation plan | Sarah (PO) |

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
