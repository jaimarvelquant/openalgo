# Sprint Change Proposal: Jainam Prop Implementation Plan Integration

**Date:** 2025-10-08
**Prepared by:** Sarah (Product Owner)
**Change Trigger:** Implementation plan analysis reveals significant architectural enhancements needed beyond current story scope
**Affected Epic:** Epic 1 - Complete Jainam Prop Broker Integration for Production Readiness

---

## Executive Summary

### Issue Context

The comprehensive implementation plan (`docs/bmad/research/jainam-prop-implementation-plan.md`) identifies critical architectural gaps and production-readiness requirements that extend beyond the current 8-story epic structure. Analysis of the Fivepaisa XTS reference implementation and Jainam sample SDK reveals:

1. **Authentication Architecture Gap**: Current stories assume basic credential externalization, but production requires SDK-based token lifecycle management with interactive + market token persistence
2. **REST Infrastructure Gap**: No centralized HTTP helper with retry logic, leading to duplicated error handling across modules
3. **Pro-Specific Features Gap**: Dealer endpoints, bracket/cover orders, and enhanced market data handling not addressed in current stories
4. **Streaming Resilience Gap**: WebSocket reconnection, subscription replay, and token reuse requirements not captured
5. **Configuration Management Gap**: Base URLs and SDK integration strategy need formal treatment

### Impact Analysis

**Timeline Impact:**
- Current Epic 1: 14–17 calendar days (estimated from 8 stories)
- Implementation Plan: 21–24 calendar days, 147–178 engineering hours
- **Delta:** +7 days, +41–54 hours of additional scope

**Story Impact:**
- **Stories Completed (3):** 1.1-1, 1.2-3, 1.3-1 — minor enhancements needed
- **Stories In Review (4):** 1.1-2, 1.2-1, 1.2-2, 1.2-4 — align with Phase 2 recommendations
- **Stories Draft (2):** 1.3-2, 1.4-1 — major expansion required
- **New Stories Required (7):** Authentication lifecycle, HTTP helper, token management, streaming, config, SDK integration, Pro features

**Artifact Impact:**
- **Epic 1**: Scope expansion, phased structure, updated success criteria
- **PRD**: Add SDK-based architecture, Pro feature inventory
- **Stories**: 7 new stories + 2 major story enhancements
- **Documentation**: Deployment guide, architecture notes, Pro-specific runbook

### Recommended Path Forward

**Adopt Option 1: Direct Adjustment / Integration**

Rather than rolling back completed work or initiating a full replan, we integrate the implementation plan by:

1. **Restructure Epic 1** with 6-phase organization aligned to the implementation plan
2. **Create 7 new stories** addressing Phases 1, 2.5, 3, and 3.4 gaps
3. **Enhance 2 existing draft stories** (1.3-2, 1.4-1) with Phase 2.5 and Phase 4 requirements
4. **Preserve completed work** while adding SDK integration and Pro feature support
5. **Update documentation** to reflect architectural decisions and Pro-specific capabilities

**Rationale:**
- Completed stories (Database, Security, Open Position, Smart Order) provide solid foundation
- Stories in review align well with Phase 2 REST API parity goals
- New phases build incrementally on existing work without requiring rollback
- Pro features and streaming are additive, not destructive to current implementation

---

## Analysis Summary

### Section 1: Trigger & Context

**Triggering Document:** `/Users/maruth/projects/openalgo/docs/bmad/research/jainam-prop-implementation-plan.md`

**Core Problem:**
The implementation plan, developed through analysis of the Fivepaisa reference broker and Jainam sample SDK, exposes several critical architectural patterns not captured in the current story backlog:

1. **Authentication Mismatch**: Current `authenticate_broker()` expects Kite-style checksums; actual Jainam XTS requires symmetric interactive + market login with persisted tokens
2. **REST Plumbing Divergence**: No shared `get_api_response` helper → duplicated HTTP logic, inconsistent error handling
3. **Streaming Gaps**: No reconnect/backoff, no DB-token reuse, re-authentication on every init
4. **SDK Leverage Gap**: Working sample demonstrates full Socket.IO + route constants, not mirrored in production
5. **Pro Feature Blind Spots**: Dealer endpoints, bracket/cover orders, enhanced market data codes not captured

**Issue Type:**
- ☑ Newly discovered architectural requirements (SDK, token lifecycle, streaming)
- ☑ Necessary pivot based on reference implementation analysis
- ☑ Technical limitations in current approach (checksum auth, placeholder defaults)

**Evidence:**
- Implementation plan executive summary (lines 28–39): Lists authentication mismatch, REST divergence, streaming gaps
- Phase 1 goals (lines 75–81): "Replace checksum-based authenticate_broker flow"
- Phase 2.5 overview (lines 135–139): "Highest-impact enhancements that rely directly on XTS Pro SDK"
- Phase 3 goals (lines 305–312): "Bring Jainam Socket.IO handling up to Fivepaisa resilience level"

### Section 2: Epic Impact Assessment

**Current Epic Status:**
Epic 1 contains 8 stories across 4 phases:
- Phase 1 (Foundation): Stories 1.1-1 ✅, 1.1-2 🔄
- Phase 2 (Core API): Stories 1.2-1 🔄, 1.2-2 🔄, 1.2-3 ✅, 1.2-4 🔄
- Phase 3 (Advanced): Stories 1.3-1 ✅, 1.3-2 📝
- Phase 4 (Production): Story 1.4-1 📝

**Impact on Current Epic:**
✅ **Epic can be completed with modifications** — No need to abandon, but must:
- Expand scope to incorporate 6 implementation plan phases
- Add 7 new stories for uncovered work (Auth, HTTP, Tokens, Streaming, Config, SDK, Pro)
- Enhance 2 draft stories with Phase 2.5/4 recommendations
- Update timeline from 14–17 days → 21–24 days

**Impact on Future Epics:**
⚠️ **Review required** — Implementation plan Phase 3 (Streaming) is substantial enough to warrant separate epic consideration, but can remain in Epic 1 if prioritized appropriately.

**Epic Sequence Changes:**
No reordering needed; all new work builds on completed foundation stories.

**Epic Summary:**
Current Epic 1 structure maps well to implementation plan Phases 2 & 4, but is missing critical Phase 1 (Auth), Phase 2.5 (SDK/HTTP), Phase 3 (Streaming), and Phase 3.4 (Config/SDK Integration) work. Expanding Epic 1 to include these phases preserves completed work while closing the architectural gaps.

### Section 3: Artifact Conflict & Impact Analysis

#### PRD Impact

**Conflicts Identified:**
- PRD Section 3 (Technical Constraints) references "existing authentication patterns" but doesn't specify SDK-based dual-token lifecycle
- No mention of Pro-specific dealer endpoints or bracket/cover order capabilities
- Streaming requirements mention "WebSocket compatibility" but don't specify reconnection resilience

**Updates Needed:**
- Add subsection documenting XTS Pro SDK architecture (interactive + market token lifecycle)
- Add Pro Feature Inventory table listing dealer endpoints, bracket/cover orders, enhanced market data codes
- Update streaming section with reconnection, subscription replay, and token reuse requirements

#### Epic Document Impact

**Epic 1: `epic-1-complete-jainam-prop-broker-integration-for-production-readiness.md`**

**Conflicts Identified:**
- Epic Goal references "feature parity with other brokers" but doesn't include Pro-specific capabilities
- Story Sequence Overview has 4 phases; implementation plan has 6 phases
- Integration Requirements list doesn't mention SDK usage or token persistence patterns
- No mention of centralized HTTP helper or retry logic requirements
- Missing streaming resilience and configuration management stories

**Updates Needed:**
- Update Epic Goal to include "SDK-based architecture" and "Pro feature support"
- Add Phase 0 (Authentication & Token Lifecycle) before current Phase 1
- Add Phase 2.5 (SDK Integration & Pro Features) between current Phase 2 and 3
- Add Phase 3.5 (Configuration & SDK Strategy) after current Phase 3
- Expand Phase 4 scope to include comprehensive testing per implementation plan
- Update Integration Requirements to include SDK, token persistence, HTTP helper patterns
- Update timeline estimate to 21–24 days, 147–178 hours

#### Story Impacts

**Stories Requiring Minor Enhancements:**
- **Story 1.1-1** (Database): Add token persistence schema validation for `interactive_token`, `feed_token`, `user_id` fields
- **Story 1.2-3** (Open Position): Add Pro dealer position endpoint support (`get_dealerposition_netwise`)
- **Story 1.3-1** (Smart Order): Add Pro dealer position integration and `clientID` passthrough

**Stories Requiring Alignment:**
- **Story 1.1-2** (Security): Already externalizes credentials; validate alignment with SDK config patterns
- **Story 1.2-1** (Position/Holdings): Already includes market token propagation; validate against Phase 2.5 requirements
- **Story 1.2-2** (Trade Book): Validate field transformations align with implementation plan mapping guidance
- **Story 1.2-4** (Live Validation): Expand to include SDK-based auth flow validation

**Stories Requiring Major Expansion:**
- **Story 1.3-2** (Emergency Closure): Expand to include Pro dealer position closure flows
- **Story 1.4-1** (Error Handling/Testing): Expand significantly to incorporate:
  - Phase 2.5 Task 2.4 (HTTP helper with retry logic)
  - Phase 4 comprehensive testing strategy
  - SDK integration validation
  - Pro feature regression testing

**New Stories Required:**
- **Story 1.0-1**: Authentication & Token Lifecycle Overhaul (Phase 1, all tasks)
- **Story 1.2-5**: Token Lifecycle Management Enhancement (Phase 2.5, Task 2.5)
- **Story 1.3-1a**: Pro-Specific Smart Order Enhancements (Phase 2.5, Task 2.6 + Task 1.7)
- **Story 1.5-1**: Streaming Adapter Refactor (Phase 3, streaming tasks)
- **Story 1.5-2**: Capability Registry & Token Validation (Phase 3, capability/telemetry tasks)
- **Story 1.6-1**: Configuration Management (Phase 3.4, Task 3.4)
- **Story 1.6-2**: SDK Integration Strategy (Phase 3.4, Task 3.5)

#### Documentation Impacts

**Files Requiring Updates:**
- `docs/bmad/jainam-prop-completion-prd.md`: Add SDK architecture, Pro features
- `docs/bmad/deployment-guide.md`: Add SDK setup, token lifecycle, config management
- `docs/broker_factory.md`: Document Jainam Pro patterns vs. retail XTS patterns
- `docs/bmad/stories/1-intro-project-analysis-and-context.md`: Reference SDK-based approach
- `docs/bmad/stories/3-technical-constraints-and-integration-requirements.md`: Add SDK, token, HTTP requirements

**New Documentation Required:**
- `docs/bmad/architecture/jainam-pro-architecture.md`: SDK-based auth, token lifecycle, Pro features
- `docs/bmad/runbooks/jainam-pro-operations.md`: Token management, streaming operations, Pro endpoints

### Section 4: Path Forward Evaluation

#### Option 1: Direct Adjustment / Integration ✅ **RECOMMENDED**

**Approach:**
Integrate implementation plan by expanding Epic 1 structure, creating 7 new stories, enhancing 2 draft stories, and updating documentation to reflect SDK-based architecture and Pro features.

**Scope:**
- Epic 1 expansion to 6-phase structure (15 stories total: 8 existing + 7 new)
- 7 new stories addressing Auth, HTTP, Tokens, Streaming, Config, SDK, Pro features
- Enhance Stories 1.3-2 and 1.4-1 with Phase 2.5/4 requirements
- Documentation updates for PRD, architecture, deployment guide

**Effort:**
- Story creation/refinement: 16–20 hours (drafting, AC development, task breakdown)
- Documentation updates: 8–12 hours (PRD, architecture, deployment guide)
- Review cycles: 4–6 hours (PO/QA validation, stakeholder alignment)
- **Total:** 28–38 hours of planning work

**Risks:**
- ⚠️ Timeline extends by ~7 days (manageable with stakeholder communication)
- ⚠️ Scope expansion may impact other roadmap items (requires reprioritization)
- ✅ Completed work (Stories 1.1-1, 1.2-3, 1.3-1) provides solid foundation
- ✅ No rollback needed; all new work builds incrementally

**Benefits:**
- ✅ Preserves all completed work and progress
- ✅ Aligns implementation with production-grade reference patterns
- ✅ Addresses architectural gaps early (auth, streaming, config)
- ✅ Pro features enable differentiation vs. retail XTS brokers
- ✅ Clear phase structure improves progress tracking

**Assessment:** **FEASIBLE** — Incremental expansion is sustainable and preserves investment

---

#### Option 2: Potential Rollback ❌ **NOT RECOMMENDED**

**Approach:**
Revert completed stories to adopt SDK-first architecture from the beginning.

**Stories to Rollback:**
- Story 1.1-1 (Database): Revert token lookup to redesign for interactive + feed token pairs
- Story 1.1-2 (Security): Revert credential externalization to align with SDK config patterns
- Story 1.2-3 (Open Position): Revert to add Pro dealer position support from start
- Story 1.3-1 (Smart Order): Revert to integrate Pro dealer endpoints from start

**Effort:**
- Rollback commits: 2–4 hours
- Redesign stories with SDK-first approach: 20–30 hours
- Re-implementation: 40–60 hours
- **Total:** 62–94 hours (vs. 28–38 hours for Option 1)

**Impact:**
- ❌ Discards 100+ hours of completed, QA-validated work
- ❌ Delays production readiness by 2–3 weeks
- ❌ Demoralizes team with "wasted work" perception
- ⚠️ Database schema changes may require migration scripts

**Benefit vs. Option 1:**
- Minimal — SDK integration can be layered on existing work without rollback

**Assessment:** **NOT VIABLE** — Cost far exceeds benefit; rollback is unnecessary

---

#### Option 3: PRD MVP Review & Potential Re-scoping ⚠️ **CONSIDERED BUT NOT NEEDED**

**Approach:**
Reduce MVP scope by deferring Pro features, streaming resilience, and SDK enhancements to "Phase 2" post-launch.

**Items to Defer:**
- Phase 1 Task 1.7 (Pro Feature Preservation)
- Phase 2.5 Tasks 2.4, 2.5, 2.6 (HTTP helper, token lifecycle, Pro smart order)
- Phase 3 (Streaming resilience)
- Phase 3.4 (Config management, SDK integration)

**Reduced MVP:**
- Complete current 8 stories as-is
- Ship with basic auth, REST API parity, no Pro features, basic streaming
- Timeline: 14–17 days (no extension)

**Risks:**
- ❌ **CRITICAL:** Authentication gap — checksum-based auth may not work with Jainam (blocker)
- ❌ **HIGH:** No token persistence → re-auth on every request (performance/reliability issue)
- ❌ **HIGH:** No streaming resilience → dropped connections lose subscriptions (user-visible failures)
- ⚠️ **MEDIUM:** No Pro features → parity gap vs. Fivepaisa limits market positioning
- ⚠️ **MEDIUM:** No retry logic → transient failures surface as user errors

**Assessment:** **NOT RECOMMENDED** — Authentication and streaming gaps are likely production blockers; deferral creates unacceptable risk

---

## Recommended Path Forward: **Option 1 - Direct Adjustment / Integration**

Expand Epic 1 structure to align with implementation plan's 6-phase organization, create 7 new stories, enhance 2 draft stories, and update documentation. This preserves completed work, addresses architectural gaps incrementally, and delivers production-ready Jainam Prop integration.

---

## Specific Proposed Edits

### 1. Epic 1 Document Updates

**File:** `docs/bmad/stories/epic-1-complete-jainam-prop-broker-integration-for-production-readiness.md`

#### Change 1.1: Update Epic Goal

**FROM:**
```markdown
**Epic Goal:**
Complete the partially implemented Jainam Prop broker integration by implementing all missing API functions, fixing database integration for symbol-to-token resolution, resolving security vulnerabilities, and adding comprehensive error handling to achieve production readiness and feature parity with other OpenAlgo broker integrations.
```

**TO:**
```markdown
**Epic Goal:**
Complete the Jainam Prop broker integration by implementing SDK-based authentication with token lifecycle management, building REST API parity with centralized HTTP infrastructure, adding Pro-specific dealer and advanced order capabilities, hardening streaming resilience, and conducting comprehensive quality validation to achieve production readiness and feature differentiation vs. retail XTS brokers.
```

#### Change 1.2: Update Integration Requirements

**FROM:**
```markdown
**Integration Requirements:**
1. Maintain existing functionality without regression
2. Follow established patterns from other XTS-based brokers
3. Use existing database schema without modifications
4. Match service layer expectations for function signatures
5. Ensure WebSocket compatibility (no streaming changes required)
6. Follow OpenAlgo's environment variable patterns
```

**TO:**
```markdown
**Integration Requirements:**
1. Maintain existing functionality without regression
2. Follow Fivepaisa XTS reference patterns for HTTP, mapping, and streaming
3. Use existing database schema; extend auth_db for interactive + feed token persistence
4. Match service layer expectations for function signatures
5. Implement WebSocket reconnection, subscription replay, and token reuse for streaming resilience
6. Follow OpenAlgo's environment variable patterns; centralize config via broker/jainam_prop/api/config
7. Leverage XTS Pro SDK (`_sample_strategy/xts_PRO_SDK`) for authentication and streaming; wrap, don't modify SDK sources
```

#### Change 1.3: Restructure Story Sequence Overview

**FROM:**
```markdown
## Story Sequence Overview

**Phase 1: Foundation (Stories 1.1-1.2)** - Fix critical blockers
- Story 1.1: Database integration (enables all other work)
- Story 1.2: Security hardening (removes immediate risk)

**Phase 2: Core API Functions (Stories 1.3-1.5)** - Enable basic functionality
- Story 1.3: Position and holdings retrieval
- Story 1.4: Trade book retrieval
- Story 1.5: Open position lookup

**Phase 3: Advanced Features (Stories 1.6-1.7)** - Enable smart orders
- Story 1.6: Smart order placement
- Story 1.7: Emergency position closure

**Phase 4: Production Readiness (Story 1.8)** - Polish and validation
- Story 1.8: Error handling, validation, and testing

**Dependency Chain:**
```
1.1 (Database) → 1.3, 1.4, 1.5 (All depend on token lookup)
1.2 (Security) → Independent, can run in parallel
1.5 (Open Position) → 1.6 (Smart Order depends on it)
1.3, 1.4, 1.5, 1.6, 1.7 → 1.8 (Testing validates all functions)
```
```

**TO:**
```markdown
## Story Sequence Overview

**Phase 0: Authentication & Token Lifecycle (Story 1.0-1)** — 5–6 days, 38–44 hours
- Story 1.0-1: Authentication & Token Lifecycle Overhaul
  - Replace checksum auth with SDK-based interactive + market login
  - Persist tokens (interactive, feed, user ID) in `database.auth_db`
  - Remove placeholder values and require real client context

**Phase 1: Foundation (Stories 1.1-1, 1.1-2)** — 3–4 days, 24–30 hours
- Story 1.1-1: Database integration (token lookup; extend schema for auth tokens) ✅
- Story 1.1-2: Security hardening (credential externalization; validate SDK config alignment) 🔄

**Phase 2: Core API Functions (Stories 1.2-1, 1.2-2, 1.2-3, 1.2-4)** — 4–5 days, 30–36 hours
- Story 1.2-1: Position and holdings retrieval 🔄
- Story 1.2-2: Trade book retrieval 🔄
- Story 1.2-3: Open position lookup ✅
- Story 1.2-4: Live integration validation 🔄

**Phase 2.5: SDK Integration & Pro-Specific Features (Stories 1.2-5, 1.3-1a)** — 3–4 days, 24–30 hours
- Story 1.2-5: Token Lifecycle Management Enhancement
  - Wrap XTS Pro SDK for login; persist tokens to `database.auth_db`
  - Rehydrate tokens in REST/streaming consumers
- Story 1.3-1a: Pro-Specific Smart Order Enhancements
  - Extend smart order with Pro dealer position endpoints (`get_dealerposition_netwise`)
  - Add `clientID` passthrough for dealer flows

**Phase 3: Advanced Features (Stories 1.3-1, 1.3-2, 1.4-1)** — 2–3 days, 18–24 hours
- Story 1.3-1: Smart order placement (enhance with Pro dealer support) ✅
- Story 1.3-2: Emergency position closure (expand with Pro dealer closure flows) 📝
- Story 1.4-1: HTTP Helper with Retry Logic (centralized `request_with_retry`) 📝

**Phase 3.5: Streaming & Realtime Reliability (Stories 1.5-1, 1.5-2)** — 4–5 days, 28–34 hours
- Story 1.5-1: Streaming Adapter Refactor
  - Mirror Fivepaisa adapter: reconnect, backoff, subscription replay
  - Reuse persisted feed tokens
- Story 1.5-2: Capability Registry & Token Validation
  - Introduce `JainamCapabilityRegistry` for exchanges/depth/message codes
  - Parse feed-token JWTs to validate user IDs

**Phase 4: Configuration & SDK Strategy (Stories 1.6-1, 1.6-2)** — 2 days, 7–10 hours
- Story 1.6-1: Configuration Management
  - Centralize base URLs, SSL flags, retry tuning via `api/config.py`
- Story 1.6-2: SDK Integration Strategy
  - Standardize SDK imports; wrap custom logic in utilities
  - Document upgrade procedure for future SDK releases

**Phase 5: Quality Hardening & Documentation (Story 1.7-1)** — 3 days, 20–24 hours
- Story 1.7-1: Comprehensive Quality Validation & Documentation
  - Expand automated tests for new flows (auth, tokens, HTTP, streaming)
  - Add live validation scripts and benchmarks
  - Update documentation (PRD, architecture, deployment guide, runbooks)

**Updated Dependency Chain:**
```
1.0-1 (Auth) → All other stories (tokens required for API calls)
1.1-1 (Database) → Extend for token persistence
1.1-2 (Security) → Validate SDK config alignment
1.2-1, 1.2-2, 1.2-3, 1.2-4 → Phase 2 API stories
1.2-5 (Token Management) → 1.5-1, 1.5-2 (Streaming needs tokens)
1.3-1a (Pro Smart Order) → Enhances 1.3-1
1.3-2 (Emergency Closure) → Depends on 1.2-3, enhanced with Pro features
1.4-1 (HTTP Helper) → Refactors all REST modules
1.5-1, 1.5-2 (Streaming) → Depends on 1.0-1, 1.2-5
1.6-1, 1.6-2 (Config, SDK) → Supports all implementation modules
1.7-1 (Quality) → Validates all prior stories
```

**Timeline Estimate:** 21–24 calendar days, 147–178 engineering hours
```

#### Change 1.4: Add New Story Summaries to Epic Document

**INSERT AFTER** current Story 1.1-2 section:

```markdown
---

## Story 1.0-1: Authentication & Token Lifecycle Overhaul

**As a** developer implementing production-ready Jainam Pro integration,
**I want** SDK-based dual-token authentication with database persistence,
**so that** interactive and market data flows reuse tokens without re-authentication and support Pro-specific dealer operations.

### Acceptance Criteria

1. **AC1**: Replace `authenticate_broker()` checksum flow with direct XTS SDK `interactive_login()` and `marketdata_login()` calls
2. **AC2**: Persist `(auth_token, feed_token, user_id)` to `database.auth_db` keyed by user
3. **AC3**: Remove `"dummy_request_token"` and `"DEFAULT_USER"` placeholders; require caller-provided client context
4. **AC4**: Update all REST/streaming modules to rehydrate tokens from DB, not environment variables
5. **AC5**: Validate required credentials and surface actionable errors when missing
6. **AC6**: Catalog Pro-specific endpoints (dealer order/trade book, bracket/cover orders, market depth codes) and verify wrapper exposure
7. **AC7**: Define verification checklist for Pro features (REST, market data, streaming) and reference in Phase 5 testing

### Integration Verification

**IV1**: Verify other broker integrations continue to work after `database.auth_db` schema extensions
**IV2**: Test that `place_order_api()` and streaming adapters successfully use rehydrated tokens
**IV3**: Measure authentication latency (initial login + token rehydration) and verify <2s total

### Dependencies

- Blocks all other stories (tokens required for API calls)
- Extends Story 1.1-1 database schema for token persistence
```

**INSERT AFTER** current Story 1.2-4 section:

```markdown
---

## Story 1.2-5: Token Lifecycle Management Enhancement

**As a** developer ensuring reliable API operations,
**I want** centralized token lifecycle management backed by the XTS Pro SDK,
**so that** authentication, token persistence, and rehydration follow a single source of truth and support both interactive and market data flows.

### Acceptance Criteria

1. **AC1**: Create `authenticate_direct()` in `api/auth_api.py` that makes direct HTTP calls to XTS API endpoints (no SDK wrapper, no OAuth)
2. **AC2**: Extract `(interactive_token, market_token, user_id)` from API responses and commit to `database.auth_db` via `store_broker_auth_token()`
3. **AC3**: Read credentials from environment variables (`JAINAM_INTERACTIVE_API_KEY/SECRET`, `JAINAM_MARKET_API_KEY/SECRET`) - no request tokens
4. **AC4**: Update all REST consumers (`order_api.py`, `data.py`, `funds.py`) to rehydrate tokens via DB helper (no direct env reads for runtime tokens)
5. **AC5**: Update streaming adapter initialization to source market token from DB
6. **AC6**: Provide `get_jainam_tokens.py` helper script for manual token generation during testing
7. **AC7**: Reference `docs/bmad/research/jainam-authentication-guide.md` for complete authentication details

### Integration Verification

**IV1**: Verify authentication endpoints return structured payloads with `user_id`, `auth_token`, `market_token`
**IV2**: Test token rehydration in both REST calls and streaming adapter initialization
**IV3**: Run regression tests confirming login, persistence, and rehydration flows (mocked or sandbox)

### Dependencies

- Depends on Story 1.0-1 (Auth & Token Lifecycle)
- Blocks Stories 1.5-1, 1.5-2 (Streaming resilience needs token rehydration)
```

**INSERT AFTER** current Story 1.3-1 section:

```markdown
---

## Story 1.3-1a: Pro-Specific Smart Order Enhancements

**As a** trader using Jainam Pro with dealer account capabilities,
**I want** smart orders to leverage dealer position endpoints and support `clientID` passthrough,
**so that** I can manage positions for multiple clients and ensure delta calculations use Pro-specific data sources.

### Acceptance Criteria

1. **AC1**: Extend smart order logic to call `get_dealerposition_netwise(clientID=...)` when `clientID` is provided in request
2. **AC2**: Compute delta using dealer net quantity vs. target position
3. **AC3**: Pass `clientID` through to `place_order()` for dealer order attribution
4. **AC4**: Maintain backward compatibility: when `clientID` absent, fall back to standard `get_positions()` flow
5. **AC5**: Add Pro dealer position scenario tests (dealer net qty fetch, delta calc, order placement with clientID)
6. **AC6**: Document Pro dealer smart order usage in code comments and deployment guide

### Integration Verification

**IV1**: Verify standard smart order flow (no `clientID`) continues to work without regression
**IV2**: Test Pro dealer smart order with `clientID` provided (position fetch, delta calc, order placement)
**IV3**: Measure execution time for dealer smart order and verify <12s completion (allowing for dealer endpoint latency)

### Dependencies

- Enhances Story 1.3-1 (Smart Order Placement) with Pro dealer support
- Depends on Story 1.0-1 (Auth) for Pro-specific credentials
- Depends on Story 1.2-3 (Open Position) for `get_dealerposition_netwise()` wrapper
```

**INSERT AFTER** current Story 1.3-2 section:

```markdown
---

## Story 1.4-1: HTTP Helper with Retry Logic

**As a** developer ensuring resilient API operations,
**I want** a centralized HTTP helper with exponential backoff and structured logging,
**so that** all REST modules share error handling, retry logic, and telemetry without code duplication.

### Acceptance Criteria

1. **AC1**: Create `broker/jainam_prop/api/http.py` with `request_with_retry(endpoint, method, payload, *, auth_token, market, retries, backoff)` signature
2. **AC2**: Wrap `httpx` requests via `utils.httpx_client.get_httpx_client()` to reuse connection pools
3. **AC3**: Implement exponential backoff on retryable status codes (5xx, 429) and network errors
4. **AC4**: Emit structured logs (request metadata, attempt count, latency) using `utils.logging.get_logger`
5. **AC5**: Retrofit `order_api.py`, `data.py`, `funds.py` to depend on helper; remove direct `httpx` calls
6. **AC6**: Make backoff and retry parameters configurable via environment variables or module constants
7. **AC7**: Add unit tests simulating transient 5xx responses and confirm retry exhaustion/backoff timing

### Integration Verification

**IV1**: Verify all REST-facing modules use `request_with_retry`; no direct `httpx` calls remain outside helper
**IV2**: Test retry behavior with mocked 5xx/429 responses (backoff timing, retry exhaustion)
**IV3**: Confirm structured logs appear in OpenAlgo logging pipeline with consistent keys

### Dependencies

- Refactors Stories 1.2-1, 1.2-2, 1.2-3, 1.3-1 REST modules
- Coordinates with implementation plan Phase 2 Task 1 (Shared HTTP Helper)
```

**INSERT NEW SECTION** for Phase 3.5 stories:

```markdown
---

## Story 1.5-1: Streaming Adapter Refactor

**As a** trader relying on real-time market data,
**I want** WebSocket connections to automatically reconnect and replay subscriptions after disconnections,
**so that** I don't lose market data during network disruptions or broker restarts.

### Acceptance Criteria

1. **AC1**: Refactor streaming adapter to inherit from `websocket_proxy.base_adapter` with state tracking and lock usage
2. **AC2**: Implement reconnection logic with exponential backoff (0.5s, 1s, 2s, 4s delays) and max retry threshold
3. **AC3**: Persist active subscriptions in adapter state; replay all subscriptions after successful reconnect
4. **AC4**: Reuse persisted feed tokens from `database.auth_db` (no re-authentication on reconnect)
5. **AC5**: Emit telemetry for reconnect attempts, subscription replay success, and connection state transitions
6. **AC6**: Add unit/integration tests verifying reconnection, subscription replay, and token reuse (mocked Socket.IO server)

### Integration Verification

**IV1**: Test WebSocket disconnection → auto-reconnect → subscription replay flow with live Jainam feed
**IV2**: Verify feed token rehydration from DB (no interactive re-login on reconnect)
**IV3**: Measure reconnection time and verify <10s for reconnect + subscription replay

### Dependencies

- Depends on Story 1.0-1 (Auth) for feed token persistence
- Depends on Story 1.2-5 (Token Management) for token rehydration
- References Fivepaisa `streaming/fivepaisaxts_adapter.py` for reconnection pattern
```

**INSERT AFTER** Story 1.5-1:

```markdown
---

## Story 1.5-2: Capability Registry & Token Validation

**As a** developer ensuring streaming data integrity,
**I want** capability metadata and feed-token validation,
**so that** subscriptions use supported exchanges/depth levels and user IDs are verified before establishing sockets.

### Acceptance Criteria

1. **AC1**: Create `JainamCapabilityRegistry` documenting supported exchanges, depth levels, message codes (1501/1502/1505/1510/1512)
2. **AC2**: Normalize subscription payloads (mode → message code) using shared mapping utilities
3. **AC3**: Decode feed-token JWT to extract user IDs; log/emit for downstream consumers
4. **AC4**: Validate subscription requests against capability registry; reject unsupported exchanges/modes with descriptive errors
5. **AC5**: Add unit tests for capability checks, subscription normalization, and token JWT parsing

### Integration Verification

**IV1**: Test subscription requests for supported exchanges (NSE, NFO, MCX) succeed
**IV2**: Test subscription requests for unsupported exchanges/modes fail with clear errors
**IV3**: Verify feed-token user ID extraction and logging

### Dependencies

- Depends on Story 1.5-1 (Streaming Adapter) for capability-aware subscription management
- References Fivepaisa `streaming/fivepaisaxts_adapter.py` for capability registry pattern
```

**INSERT NEW SECTION** for Phase 4 stories:

```markdown
---

## Story 1.6-1: Configuration Management

**As a** developer deploying Jainam Prop to multiple environments,
**I want** centralized configuration for base URLs, SSL flags, and retry tuning,
**so that** environment-specific settings are managed consistently without code changes.

### Acceptance Criteria

1. **AC1**: Extend `broker/jainam_prop/api/config.py` to read `JAINAM_BASE_URL`, `JAINAM_DISABLE_SSL`, `JAINAM_HTTP_RETRIES`, `JAINAM_HTTP_BACKOFF_*` from environment
2. **AC2**: Document configuration precedence: environment variable → `.env`/deployment secret → fallback constant
3. **AC3**: Update `api/auth_api.py`, `api/http.py`, streaming adapters to source config via helper (no hard-coded URLs)
4. **AC4**: Provide example configuration files for local development, staging, and production environments
5. **AC5**: Add unit tests confirming config helper reads environment variables and applies fallback defaults

### Integration Verification

**IV1**: Verify all modules derive base URLs via `get_jainam_base_url()` or config helper (no hard-coded URLs remain)
**IV2**: Test SSL verification toggles correctly based on `JAINAM_DISABLE_SSL` setting
**IV3**: Confirm documentation outlines required environment variables for each deployment tier

### Dependencies

- Updates Stories 1.0-1, 1.2-5, 1.4-1, 1.5-1 modules to use centralized config
- Coordinates with implementation plan Phase 3.4 Task 3.4
```

**INSERT AFTER** Story 1.6-1:

```markdown
---

## Story 1.6-2: SDK Integration Strategy

**As a** developer maintaining the Jainam Prop integration long-term,
**I want** standardized SDK import patterns and upgrade procedures,
**so that** future SDK releases can be validated and integrated without risking custom logic drift.

### Acceptance Criteria

1. **AC1**: Audit modules for direct SDK class copies; replace with explicit imports from `broker.jainam_prop._sample_strategy.xts_PRO_SDK`
2. **AC2**: Encapsulate custom requirements (DataFrame shaping, logging) in helper modules that call SDK (no SDK source modifications)
3. **AC3**: Document upgrade procedure for future SDK releases (version pin, smoke tests, compatibility validation)
4. **AC4**: Create wrapper module (e.g., `api/sdk.py`) as single import point for SDK usage; production code never imports SDK directly
5. **AC5**: Add linting/tests confirming wrapper module is the sole SDK import point

### Integration Verification

**IV1**: Verify no production module duplicates SDK class definitions; all reuse shared import wrapper
**IV2**: Confirm upgrade playbook exists documenting SDK validation steps
**IV3**: Validate linting/tests enforce single SDK import point

### Dependencies

- Coordinates with Story 1.0-1 (Auth) and 1.2-5 (Token Management) SDK usage
- Supports future SDK version upgrades
- References implementation plan Phase 3.4 Task 3.5
```

**REPLACE** current Story 1.4-1 section entirely with:

```markdown
---

## Story 1.7-1: Comprehensive Quality Validation & Documentation

**As a** developer ensuring production readiness,
**I want** comprehensive automated testing, live validation scripts, and updated documentation,
**so that** the Jainam Prop integration is robust, reliable, and ready for production deployment.

### Acceptance Criteria

1. **AC1**: Expand automated test suite to cover new flows: SDK-based auth, token lifecycle, HTTP retry logic, streaming reconnection
2. **AC2**: Add regression tests for Pro-specific features (dealer endpoints, bracket/cover orders, enhanced market data codes)
3. **AC3**: Implement benchmark/monitoring tests for all performance targets (order <3s, positions <5s, smart order <10s, master contract <60s, token lookup <100ms)
4. **AC4**: Create live validation scripts for end-to-end workflows (login, master contract, orders, positions, holdings, trades, smart orders, streaming)
5. **AC5**: Update documentation:
   - PRD: Add SDK architecture, Pro feature inventory
   - Architecture document: Token lifecycle, HTTP helper, streaming resilience patterns
   - Deployment guide: SDK setup, config management, Pro endpoint usage
   - Operations runbook: Token management, streaming ops, troubleshooting
6. **AC6**: Conduct live validation with Jainam API (authentication, orders, positions, holdings, trades, smart orders, streaming, token lookup, master contract)
7. **AC7**: Document discovered issues, limitations, or Pro-specific behaviors in code comments and deployment guide

### Integration Verification

**IV1**: Run regression tests on existing OpenAlgo broker integrations (validate 3 other brokers still work)
**IV2**: Execute complete user workflow end-to-end (login → master contract → orders → positions → holdings → trades → smart order → streaming → close all)
**IV3**: Measure and validate all performance requirements against live Jainam API

### Dependencies

- Validates all prior stories (1.0-1 through 1.6-2)
- Coordinates with implementation plan Phase 4 (Quality Hardening & Documentation)
```

---

### 2. New Story File Creation

The following 7 new story files should be created:

1. **`docs/bmad/stories/story-1.0-1[Authentication-Token-Lifecycle].md`**
   Content: Full story structure for Authentication & Token Lifecycle Overhaul (Phase 1)

2. **`docs/bmad/stories/story-1.2-5[Token-Lifecycle-Management].md`**
   Content: Full story structure for Token Lifecycle Management Enhancement (Phase 2.5, Task 2.5)

3. **`docs/bmad/stories/story-1.3-1a[Pro-Smart-Order-Enhancements].md`**
   Content: Full story structure for Pro-Specific Smart Order Enhancements (Phase 2.5, Task 2.6 + Task 1.7)

4. **`docs/bmad/stories/story-1.4-1[HTTP-Helper-Retry-Logic].md`**
   Content: Full story structure for HTTP Helper with Retry Logic (Phase 2.5, Task 2.4)

5. **`docs/bmad/stories/story-1.5-1[Streaming-Adapter-Refactor].md`**
   Content: Full story structure for Streaming Adapter Refactor (Phase 3)

6. **`docs/bmad/stories/story-1.5-2[Capability-Registry-Token-Validation].md`**
   Content: Full story structure for Capability Registry & Token Validation (Phase 3)

7. **`docs/bmad/stories/story-1.6-1[Configuration-Management].md`**
   Content: Full story structure for Configuration Management (Phase 3.4, Task 3.4)

8. **`docs/bmad/stories/story-1.6-2[SDK-Integration-Strategy].md`**
   Content: Full story structure for SDK Integration Strategy (Phase 3.4, Task 3.5)

9. **`docs/bmad/stories/story-1.7-1[Quality-Validation-Documentation].md`**
   Content: Full story structure for Comprehensive Quality Validation & Documentation (Phase 4)

---

### 3. Existing Story Enhancements

#### Story 1.3-2 (Emergency Closure) Enhancement

**File:** `docs/bmad/stories/story-1.3-2[Emergency-Closure].md`

**Change 3.1: Update Story Description**

**FROM:**
```markdown
**As a** trader needing to quickly exit all positions,
**I want** a function that closes all open positions with market orders,
**so that** I can manage risk during market volatility or emergency situations.
```

**TO:**
```markdown
**As a** trader needing to quickly exit all positions (including dealer positions for Pro accounts),
**I want** a function that closes all open positions with market orders and supports `clientID` passthrough for dealer flows,
**so that** I can manage risk during market volatility or emergency situations across standard and dealer accounts.
```

**Change 3.2: Add Pro-Specific Acceptance Criteria**

**INSERT** after existing AC6:

```markdown
7. **AC7**: When `clientID` provided, use `get_dealerposition_netwise(clientID=...)` to fetch dealer positions
8. **AC8**: Pass `clientID` through to order placement for dealer position closure attribution
9. **AC9**: Maintain backward compatibility: when `clientID` absent, use standard `get_positions()` flow
```

**Change 3.3: Add Pro Integration Verification**

**INSERT** after existing IV3:

```markdown
**IV4**: Test dealer position closure with `clientID` provided (dealer position fetch, order placement with attribution)
**IV5**: Verify standard position closure (no `clientID`) continues to work without regression
```

---

### 4. PRD Updates

**File:** `docs/bmad/jainam-prop-completion-prd.md`

**Change 4.1: Add SDK Architecture Section**

**INSERT** new section after "Technical Constraints" section:

```markdown
## SDK-Based Architecture

### XTS Pro SDK Integration

The Jainam Prop integration leverages the XTS Pro SDK (`_sample_strategy/xts_PRO_SDK`) as the single source of truth for authentication and streaming operations:

**Authentication Architecture:**
- **Interactive Login**: Produces `auth_token` for REST API calls (orders, positions, holdings, funds)
- **Market Data Login**: Produces `feed_token` for WebSocket streaming subscriptions
- **Token Persistence**: Both tokens stored in `database.auth_db` keyed by `user_id` for reuse across sessions
- **Token Rehydration**: REST and streaming modules source tokens from DB, not environment variables

**SDK Usage Patterns:**
- **Imports**: Production code imports SDK via wrapper module (`api/sdk.py`); never modifies SDK sources directly
- **Custom Logic**: DataFrame shaping, logging, error handling encapsulated in helpers that call SDK
- **Version Management**: SDK pinned to tested version; upgrade procedure documented in operations runbook

**Token Lifecycle:**
```
User Login → SDK interactive_login() + marketdata_login()
          → Persist (auth_token, feed_token, user_id) to database.auth_db
          → REST calls rehydrate auth_token from DB
          → Streaming adapter rehydrates feed_token from DB
          → No re-authentication on reconnect (tokens reused)
```

---

## Pro-Specific Features

The Jainam Prop integration supports **Pro Account** capabilities beyond retail XTS brokers:

| Feature Category | Pro Endpoints | Description |
|------------------|---------------|-------------|
| **Dealer Operations** | `get_dealer_orderbook(clientID)` | Fetch dealer-attributed order book |
| | `get_dealer_tradebook(clientID)` | Fetch dealer-attributed trade book |
| | `get_dealerposition_netwise(clientID)` | Fetch dealer net positions |
| **Advanced Orders** | `place_bracketorder(...)` | Place bracket orders (entry + target + stop-loss) |
| | `place_cover_order(...)` | Place cover orders (entry + stop-loss) |
| | Modify/cancel bracket/cover orders | Full lifecycle management |
| **Market Data** | Message codes 1501, 1502, 1505, 1510, 1512 | Enhanced market depth, OI, ticker data |
| | Exchange segment resolution | Support for NSECD, BSEFO segments |

**Smart Order Pro Enhancements:**
- When `clientID` provided, smart order uses `get_dealerposition_netwise(clientID)` for delta calculation
- Order placement includes `clientID` for dealer attribution
- Backward compatible: `clientID` omission falls back to standard `get_positions()` flow

**Verification:**
- Pro feature checklist defined in Story 1.0-1 (Authentication & Token Lifecycle)
- Validated during Story 1.7-1 (Comprehensive Quality Validation)
```

---

### 5. Documentation Updates

#### 5.1 Architecture Documentation

**NEW FILE:** `docs/bmad/architecture/jainam-pro-architecture.md`

**Content:**
```markdown
# Jainam Prop Broker Integration Architecture

## Overview

The Jainam Prop integration is built on the XTS Pro SDK and follows architectural patterns established by the Fivepaisa XTS reference implementation. This document outlines key architectural decisions and implementation patterns.

## Authentication & Token Lifecycle

### Dual-Token Architecture

Jainam XTS requires two separate authentication tokens:

1. **Interactive Token (`auth_token`)**: Used for REST API calls (orders, positions, holdings, funds)
   - Obtained via `XTSConnect.interactive_login()`
   - Lifespan: Session-based (typically 1 day)
   - Stored in: `database.auth_db` table

2. **Market Data Token (`feed_token`)**: Used for WebSocket streaming subscriptions
   - Obtained via `XTSConnect.marketdata_login()`
   - Lifespan: Session-based (typically 1 day)
   - Stored in: `database.auth_db` table

### Token Persistence Strategy

**Database Schema Extension:**
```sql
-- database.auth_db table columns
user_id VARCHAR(255)
broker VARCHAR(50)
auth_token TEXT           -- Interactive token
feed_token TEXT           -- Market data token (NEW)
token_expiry TIMESTAMP
created_at TIMESTAMP
updated_at TIMESTAMP
```

**Token Lifecycle Flow:**
```
1. Initial Login:
   SDK.interactive_login() → auth_token
   SDK.marketdata_login() → feed_token
   ↓
   database.auth_db.store_broker_auth_token(user_id, auth_token, feed_token)

2. REST API Call:
   order_api.place_order(auth_token=database.auth_db.get_auth_token(user_id))

3. Streaming Connection:
   adapter.connect(feed_token=database.auth_db.get_feed_token(user_id))

4. Token Reuse:
   No re-authentication on subsequent calls (tokens reused from DB)
   Re-authentication only on token expiry or explicit logout
```

**Benefits:**
- ✅ Eliminates re-authentication overhead on every request
- ✅ Supports session persistence across application restarts
- ✅ Enables streaming reconnection without interactive re-login

## REST API Infrastructure

### Centralized HTTP Helper

**Module:** `broker/jainam_prop/api/http.py`

**Purpose:** Eliminate duplicated HTTP logic across `order_api.py`, `data.py`, `funds.py`

**Signature:**
```python
def request_with_retry(
    endpoint: str,
    method: str = "GET",
    payload: Optional[Dict[str, Any]] = None,
    *,
    auth_token: str,
    market: bool = False,
    retries: int = 3,
    backoff: tuple[float, float] = (0.25, 2.0)
) -> httpx.Response:
    """
    Centralized HTTP request handler with exponential backoff retry logic.

    Args:
        endpoint: API endpoint path (appended to base URL)
        method: HTTP method (GET, POST, PUT, DELETE)
        payload: Request payload (JSON for POST/PUT, params for GET)
        auth_token: Authentication token (interactive or market)
        market: If True, use market data base URL; else interactive
        retries: Max retry attempts (default: 3)
        backoff: (base_delay, multiplier) for exponential backoff

    Returns:
        httpx.Response with status code and JSON data

    Raises:
        httpx.RequestError: After retry exhaustion
    """
```

**Features:**
- ✅ Shared `httpx` client via `utils.httpx_client.get_httpx_client()`
- ✅ Exponential backoff on 5xx, 429, and network errors
- ✅ Structured logging (endpoint, status, attempt, latency)
- ✅ Configurable retry/backoff via environment variables

**Adoption:**
- All REST modules (`order_api.py`, `data.py`, `funds.py`) refactored to use helper
- No direct `httpx` calls remain outside helper
- Consistent error semantics across all API functions

## Streaming Architecture

### Adapter Resilience

**Module:** `broker/jainam_prop/streaming/jainam_adapter.py`

**Pattern:** Mirror Fivepaisa `streaming/fivepaisaxts_adapter.py` for reconnection, subscription replay, token reuse

**Key Features:**
1. **Reconnection with Exponential Backoff:**
   - Delays: 0.5s, 1s, 2s, 4s (max 5 attempts)
   - Auto-reconnect on dropped sockets or network disruptions

2. **Subscription Persistence:**
   - Active subscriptions stored in adapter state
   - Replayed automatically after successful reconnect
   - No data loss for traders relying on continuous feeds

3. **Feed Token Reuse:**
   - Rehydrate `feed_token` from `database.auth_db` on reconnect
   - No interactive re-login required (performance + reliability)

4. **Telemetry & Monitoring:**
   - Emit metrics for reconnect attempts, subscription replay success, connection state
   - Structured logging for operational visibility

### Capability Registry

**Module:** `broker/jainam_prop/streaming/capability_registry.py`

**Purpose:** Document supported exchanges, depth levels, message codes

**Content:**
```python
class JainamCapabilityRegistry:
    SUPPORTED_EXCHANGES = ["NSE", "NFO", "MCX", "NSECD", "BSE", "BSEFO"]
    SUPPORTED_DEPTH_LEVELS = [1, 5, 10, 20]
    MESSAGE_CODES = {
        1501: "Ticker",
        1502: "Market Depth",
        1505: "Open Interest",
        1510: "Candlestick",
        1512: "Index Data"
    }
```

**Usage:**
- Validate subscription requests before sending to Jainam
- Reject unsupported exchanges/modes with descriptive errors
- Normalize mode → message code mappings

## Pro-Specific Features

### Dealer Endpoints

Pro accounts support dealer-attributed operations via `clientID` parameter:

**Position Retrieval:**
```python
# Standard account
get_positions(auth_token) → positions for logged-in user

# Pro dealer account
get_dealerposition_netwise(auth_token, clientID="ABC123") → positions for specific client
```

**Smart Order Delta Calculation:**
```python
# Standard flow
current_qty = get_open_position(symbol, exchange, product, auth_token)
delta = target_qty - current_qty

# Pro dealer flow (when clientID provided)
dealer_response = get_dealerposition_netwise(auth_token, clientID=clientID)
current_qty = parse_dealer_net_qty(dealer_response, symbol, exchange, product)
delta = target_qty - current_qty

# Order placement
place_order(..., clientID=clientID)  # Dealer attribution
```

### Advanced Order Types

**Bracket Orders:**
- Entry + Target (profit) + Stop-Loss in single order
- Lifecycle: Place → Modify → Cancel

**Cover Orders:**
- Entry + Stop-Loss in single order
- Lifecycle: Place → Modify → Cancel

**Implementation:**
- Wrappers in `api/order_api.py`: `place_bracketorder()`, `place_cover_order()`
- Request validation for required bracket/cover parameters
- Service layer integration for UI flows

## Configuration Management

**Module:** `broker/jainam_prop/api/config.py`

**Environment Variables:**
```bash
# Base URLs
JAINAM_BASE_URL=https://smpb.jainam.in:4143
JAINAM_DISABLE_SSL=false

# HTTP Retry Tuning
JAINAM_HTTP_RETRIES=3
JAINAM_HTTP_BACKOFF_BASE=0.25
JAINAM_HTTP_BACKOFF_FACTOR=2.0
```

**Precedence:**
Environment variable → `.env` file → Fallback constant

**Adoption:**
- All modules (`auth_api.py`, `http.py`, `data.py`, `funds.py`, streaming adapters) source config via helper
- No hard-coded URLs in production code
- Environment-specific overrides without code changes

## SDK Integration Strategy

### Import Pattern

**Wrapper Module:** `broker/jainam_prop/api/sdk.py`

```python
from broker.jainam_prop._sample_strategy.xts_PRO_SDK.Connect import XTSConnect

def build_xts_client(api_key: str, api_secret: str, source: str, root_url: str) -> XTSConnect:
    """
    Return configured XTSConnect client. Production code imports this helper,
    never SDK modules directly.
    """
    return XTSConnect(api_key, api_secret, source, root=root_url)
```

**Production Usage:**
```python
# ✅ Correct
from broker.jainam_prop.api.sdk import build_xts_client
client = build_xts_client(...)

# ❌ Incorrect (bypasses wrapper)
from broker.jainam_prop._sample_strategy.xts_PRO_SDK.Connect import XTSConnect
client = XTSConnect(...)
```

**Benefits:**
- Single import point for SDK → easier version upgrades
- Custom logic (logging, DataFrame shaping) stays in helpers, not SDK sources
- Linting/tests enforce wrapper usage

### SDK Upgrade Procedure

**Steps:**
1. Update SDK version in `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/`
2. Run smoke tests: `pytest broker/jainam_prop/test_sdk_integration.py`
3. Validate auth flows: `scripts/validate_sdk_auth.py`
4. Check for breaking changes in SDK response schemas
5. Update wrapper (`api/sdk.py`) if SDK API changed
6. Deploy to staging; monitor logs for SDK-related errors
7. Promote to production after 48-hour staging validation

---

## Performance Targets

| Operation | Target | Validation Method |
|-----------|--------|-------------------|
| Order Placement | <3s | `test_performance_order_placement.py` |
| Position Retrieval | <5s | `test_performance_positions.py` |
| Smart Order | <10s | `test_performance_smart_order.py` |
| Master Contract | <60s | `test_performance_master_contract.py` |
| Token Lookup (Cached) | <100ms | `scripts/benchmark_jainam_token_lookup.py` |

**Enforcement:**
- Automated tests assert latency thresholds
- CI fails if performance regresses
- Production monitoring alerts on sustained SLA violations

---

## References

- Implementation Plan: `docs/bmad/research/jainam-prop-implementation-plan.md`
- Fivepaisa XTS Reference: `broker/fivepaisaxts/`
- Jainam Sample SDK: `broker/jainam_prop/_sample_strategy/xts_connect.py`
```

---

#### 5.2 Operations Runbook

**NEW FILE:** `docs/bmad/runbooks/jainam-pro-operations.md`

**Content:**
```markdown
# Jainam Prop Operations Runbook

## Token Management

### Initial Token Setup

1. **Obtain Credentials:**
   - Interactive API Key + Secret (for REST operations)
   - Market Data API Key + Secret (for streaming)
   - Source identifier (default: `"WEBAPI"`)

2. **Configure Environment:**
   ```bash
   # .env or deployment secrets
   JAINAM_INTERACTIVE_API_KEY=your_interactive_key
   JAINAM_INTERACTIVE_API_SECRET=your_interactive_secret
   JAINAM_MARKET_API_KEY=your_market_key
   JAINAM_MARKET_API_SECRET=your_market_secret
   JAINAM_BASE_URL=https://smpb.jainam.in:4143
   ```

3. **Initial Login:**
   ```python
   from broker.jainam_prop.api.auth_api import authenticate_and_store

   user_id, auth_token, market_token = authenticate_and_store(
       user_id="your_user_id",
       interactive_key=os.getenv("JAINAM_INTERACTIVE_API_KEY"),
       interactive_secret=os.getenv("JAINAM_INTERACTIVE_API_SECRET"),
       market_key=os.getenv("JAINAM_MARKET_API_KEY"),
       market_secret=os.getenv("JAINAM_MARKET_API_SECRET"),
       root_url=os.getenv("JAINAM_BASE_URL"),
       source="WEBAPI"
   )
   ```

4. **Verify Token Persistence:**
   ```sql
   SELECT user_id, broker, auth_token, feed_token, token_expiry
   FROM auth_db
   WHERE broker = 'jainam_prop' AND user_id = 'your_user_id';
   ```

### Token Expiry & Refresh

**Symptoms:**
- REST API returns `401 Unauthorized` or `"Invalid token"` errors
- Streaming adapter fails to connect with `"Token expired"` message

**Resolution:**
1. Re-run `authenticate_and_store()` to fetch fresh tokens
2. Tokens auto-persist to `database.auth_db`
3. Subsequent REST/streaming calls rehydrate new tokens

**Automation:**
- Schedule token refresh job (e.g., daily at 8am before market open)
- Monitor token expiry timestamp; refresh 1 hour before expiry

### Pro Account Token Management

**Dealer Flows:**
- Same interactive + market tokens used for dealer endpoints
- `clientID` parameter controls attribution, not authentication
- No separate dealer token required

---

## Streaming Operations

### WebSocket Connection Monitoring

**Health Checks:**
```python
# Check adapter connection state
adapter.is_connected()  # True if socket established

# Check subscription count
len(adapter.active_subscriptions)  # Number of active subscriptions
```

**Common Issues:**

1. **Connection Drops:**
   - **Symptom:** Adapter enters reconnection loop
   - **Logs:** `jainam_adapter: Reconnection attempt 1/5...`
   - **Resolution:** Auto-reconnects with exponential backoff; no manual intervention unless max retries exceeded

2. **Subscription Replay Failures:**
   - **Symptom:** After reconnect, subscriptions missing
   - **Logs:** `jainam_adapter: Subscription replay failed for NSE:RELIANCE`
   - **Resolution:** Check capability registry for unsupported exchanges/symbols; validate feed token not expired

3. **Token Rehydration Errors:**
   - **Symptom:** Reconnect triggers re-login instead of token reuse
   - **Logs:** `jainam_adapter: Feed token not found in DB, falling back to re-login`
   - **Resolution:** Verify `database.auth_db` contains valid `feed_token` for user; re-run `authenticate_and_store()` if missing

---

## Pro Feature Usage

### Dealer Position Retrieval

**Endpoint:** `get_dealerposition_netwise(auth_token, clientID)`

**Usage:**
```python
from broker.jainam_prop.api.order_api import get_dealerposition_netwise

response = get_dealerposition_netwise(
    auth_token=auth_token,
    clientID="ABC123"
)

# Parse dealer net quantity
positions = response["result"]
for pos in positions:
    symbol = pos["TradingSymbol"]
    net_qty = int(pos["NetQty"])
    print(f"{symbol}: {net_qty}")
```

**Troubleshooting:**
- **403 Forbidden:** User account not authorized for dealer operations (Pro account required)
- **Invalid clientID:** Verify clientID exists in dealer system

### Smart Order with Dealer Support

**Usage:**
```python
from broker.jainam_prop.api.order_api import place_smartorder_api

# Pro dealer smart order
order_data = {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "product": "MIS",
    "position_size": 100,  # Target quantity
    "clientID": "ABC123"   # Dealer attribution
}

result = place_smartorder_api(order_data, auth_token)
```

**Delta Calculation:**
- With `clientID`: Uses `get_dealerposition_netwise(clientID=...)`
- Without `clientID`: Uses standard `get_positions()`

### Bracket/Cover Orders

**Bracket Order:**
```python
from broker.jainam_prop.api.order_api import place_bracketorder

bracket_order = {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "quantity": 100,
    "entry_price": 2500,
    "target_price": 2550,  # Profit target
    "stop_loss": 2475      # Stop-loss
}

result = place_bracketorder(bracket_order, auth_token)
```

**Cover Order:**
```python
from broker.jainam_prop.api.order_api import place_cover_order

cover_order = {
    "symbol": "RELIANCE",
    "exchange": "NSE",
    "quantity": 100,
    "entry_price": 2500,
    "stop_loss": 2475
}

result = place_cover_order(cover_order, auth_token)
```

---

## Performance Monitoring

### Latency Tracking

**Key Metrics:**
- `order_placement_latency_ms`: REST order placement round-trip time
- `position_fetch_latency_ms`: Position retrieval time
- `smart_order_latency_ms`: Smart order end-to-end time (position fetch + delta calc + order placement)
- `token_lookup_latency_ms`: Cached token lookup time

**Alerting Thresholds:**
- Order placement > 3000ms (3s SLA)
- Position fetch > 5000ms (5s SLA)
- Smart order > 10000ms (10s SLA)
- Token lookup > 100ms (100ms SLA)

### Log Monitoring

**Critical Error Patterns:**
```bash
# Authentication failures
grep "JAINAM.*Invalid token" /var/log/openalgo/broker.log

# Streaming reconnection loops
grep "jainam_adapter.*Max retries exceeded" /var/log/openalgo/streaming.log

# HTTP retry exhaustion
grep "request_with_retry.*Unable to reach Jainam" /var/log/openalgo/http.log
```

---

## Troubleshooting Guide

### Common Issues

**1. "Invalid token" errors despite fresh login:**
- **Cause:** Token persistence failed; DB write error
- **Check:** `SELECT * FROM auth_db WHERE broker='jainam_prop'`
- **Fix:** Re-run `authenticate_and_store()`; check DB write permissions

**2. Smart order returns "Position not found" but positions exist:**
- **Cause:** Exchange/product mismatch in filter logic
- **Check:** Position data exchange segment vs. request exchange parameter
- **Fix:** Normalize exchange (NSE → NSECM) before `get_open_position()` call

**3. Streaming subscriptions fail with "Unsupported exchange":**
- **Cause:** Exchange not in capability registry
- **Check:** `JainamCapabilityRegistry.SUPPORTED_EXCHANGES`
- **Fix:** Add exchange to registry if Jainam supports; reject subscription otherwise

**4. Dealer endpoints return "403 Forbidden":**
- **Cause:** Account not authorized for Pro features
- **Check:** Verify account type with Jainam support
- **Fix:** Upgrade to Pro account or remove dealer flows from integration

---

## Emergency Procedures

### Complete Position Closure (Emergency)

**Trigger:** Market volatility, risk management event, system failure

**Procedure:**
```python
from broker.jainam_prop.api.order_api import close_all_positions

# Standard account
result = close_all_positions(
    current_api_key="your_api_key",
    auth_token=auth_token
)

# Pro dealer account
result = close_all_positions(
    current_api_key="your_api_key",
    auth_token=auth_token,
    clientID="ABC123"  # Close dealer positions
)

# Verify closure
print(f"Closed {len(result['orders'])} positions")
for order in result['orders']:
    print(f"Symbol: {order['symbol']}, Status: {order['status']}, Order ID: {order.get('order_id')}")
```

**Post-Closure Validation:**
```python
# Verify all positions flat
positions = get_positions(auth_token)
assert all(int(pos['NetQty']) == 0 for pos in positions['result']), "Positions not fully closed!"
```

---

## References

- Architecture: `docs/bmad/architecture/jainam-pro-architecture.md`
- Deployment Guide: `docs/bmad/deployment-guide.md`
- Implementation Plan: `docs/bmad/research/jainam-prop-implementation-plan.md`
```

---

## Agent Handoff Plan

**Roles Needed:**

1. **PO (Sarah) — Current Role**: Review and approve this Sprint Change Proposal
2. **PM**: Validate timeline extension (21–24 days vs. 14–17) and reprioritize roadmap if needed
3. **Dev Lead**: Review new story structure (7 new stories + 2 enhancements) and confirm feasibility
4. **QA Lead**: Review expanded testing requirements in Story 1.7-1 and validate Pro feature coverage
5. **Tech Lead/Architect**: Validate SDK-based architecture, token lifecycle, and streaming resilience patterns

**Next Steps:**

1. **User Approval** of this Sprint Change Proposal
2. **Create 7 new story files** with full AC/IV/task breakdowns
3. **Update Epic 1 document** with 6-phase structure and timeline
4. **Update PRD** with SDK architecture and Pro features sections
5. **Create architecture and operations runbooks**
6. **Dev handoff** to implement Phase 0 (Story 1.0-1) as foundation for all other work

---

## Success Criteria

✅ **Epic 1 restructured** with 6-phase organization, 15 total stories (8 existing + 7 new)
✅ **Timeline extended** to 21–24 days, 147–178 hours (stakeholder-approved)
✅ **SDK-based architecture** documented and adopted for auth, token lifecycle, streaming
✅ **Pro features** inventoried, implemented, and validated
✅ **HTTP helper** with retry logic eliminates duplicated error handling
✅ **Streaming resilience** provides reconnection, subscription replay, token reuse
✅ **Configuration management** centralizes base URLs, SSL flags, retry tuning
✅ **Comprehensive testing** validates auth, REST, Pro features, streaming, performance
✅ **Documentation complete**: PRD, architecture, deployment guide, operations runbook

---

**Prepared by:** Sarah (Product Owner)
**Date:** 2025-10-08
**Status:** Awaiting User Approval
```
