# Story 1.6-2: SDK Integration Strategy

## ⚠️ DEPRECATED - DO NOT USE

**Status:** SUPERSEDED
**Superseded By:** `story-1.6-2-sdk-integration-strategy.md`
**Date Deprecated:** 2025-10-11
**Reason:** Replaced with code reuse-first version (50% reuse from FivePaisaXTS, effort reduced from 2 days to 1 day)

---

## Original Status
Draft (OBSOLETE)

## Estimated Effort
**8-12 hours** (SDK wrapper creation, refactoring, documentation)

## ⚠️ CRITICAL: Pro SDK Integration

**This story focuses on XTS Pro SDK integration** - Not applicable to retail brokers

**Code Reuse:**
- ✅ Wrapper pattern: 60% reusable from other broker integrations
- ⚠️ Pro SDK specifics: 0% reusable (Pro-specific)
- ✅ Configuration management: 80% reusable from existing config
- ✅ Version detection: 70% reusable from standard patterns

**Reference:**
- **Pro SDK:** `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/`
- **Pro Pattern:** `broker/jainam_prop/_sample_strategy/xts_connect.py`
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 3
- **Authentication Guide:** `docs/bmad/research/jainam-authentication-guide.md`

**Key Decision:** Based on code reuse analysis, **direct HTTP calls are preferred over SDK wrapper** for authentication and API calls. SDK should only be used where absolutely necessary (Pro-specific features).

## Story

**As a** maintainer of the Jainam Prop integration codebase,
**I want** a standardized SDK integration strategy with centralized imports, thin wrapper utilities, and documented upgrade procedures,
**so that** SDK version updates are isolated from business logic, custom requirements are encapsulated without modifying vendor code, and future SDK releases can be validated and deployed safely.

## Acceptance Criteria

1. **AC1**: Audit all modules for direct copies or inline implementations of SDK classes (`XTSConnect`, `socketio.Client`, etc.) and replace with explicit imports from `broker/jainam_prop/_sample_strategy/xts_PRO_SDK`.
2. **AC2**: Create `broker/jainam_prop/api/sdk.py` wrapper module providing factory functions (`build_interactive_client()`, `build_market_client()`) that encapsulate SDK initialization, configuration injection, and logging, ensuring no production module imports SDK classes directly.
3. **AC3**: Encapsulate custom requirements (DataFrame shaping, structured logging, retry orchestration) in helper modules that call SDK methods rather than modifying SDK source files.
4. **AC4**: Document SDK import path, version pinning strategy, and upgrade procedure in `docs/bmad/research/sdk-integration-guide.md` or broker README, including smoke test checklist for validating new SDK releases.
5. **AC5**: Implement SDK version detection and compatibility validation: log SDK version on initialization, emit warnings if SDK version mismatches expected version range.
6. **AC6**: Provide linting/import rules (via `ruff`, `pylint`, or custom script) to enforce that production modules never import SDK classes directly; all SDK usage must route through wrapper module.
7. **AC7**: Add integration tests confirming wrapper functions correctly initialize SDK clients and propagate configuration (base URL, SSL flags, source identifier) from config module.

## Integration Verification

**IV1**: Verify all SDK usage (authentication, order placement, market data, streaming) routes through wrapper module; direct SDK imports exist only in wrapper module itself.
**IV2**: Confirm SDK version updates can be deployed by updating `_sample_strategy/xts_PRO_SDK` and running smoke tests without modifying business logic modules.
**IV3**: Ensure wrapper module correctly propagates configuration changes (base URL, SSL flags) from config module to SDK initialization.

## Tasks / Subtasks

- [ ] Task 1: SDK usage audit and centralization (AC: 1, 2, 6)
  - [ ] Subtask 1.1: Grep codebase for SDK class names (`XTSConnect`, `socketio.Client`) to identify all usage points.
  - [ ] Subtask 1.2: Create `broker/jainam_prop/api/sdk.py` wrapper module with factory functions for interactive and market data clients.
  - [ ] Subtask 1.3: Refactor `api/auth_api.py` to import wrapper functions instead of SDK classes directly.
  - [ ] Subtask 1.4: Refactor `streaming/jainam_websocket.py` to use wrapper-provided Socket.IO client.
  - [ ] Subtask 1.5: Add linting rule (`.ruff.toml`, `.pylintrc`, or custom pre-commit hook) prohibiting direct SDK imports outside wrapper module.
  - [ ] Subtask 1.6: Document wrapper usage in module docstrings and inline comments.

- [ ] Task 2: Custom requirement encapsulation (AC: 3)
  - [ ] Subtask 2.1: Identify custom behaviors currently implemented as SDK source modifications (if any).
  - [ ] Subtask 2.2: Extract custom behaviors into helper modules (`api/helpers.py`, `streaming/helpers.py`).
  - [ ] Subtask 2.3: Ensure helpers call SDK methods via wrapper functions rather than duplicating SDK logic.
  - [ ] Subtask 2.4: Add structured logging wrappers for SDK calls, capturing request/response metadata without modifying SDK sources.

- [ ] Task 3: SDK version management and upgrade procedure (AC: 4, 5)
  - [ ] Subtask 3.1: Document current SDK version in `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/VERSION` or similar manifest.
  - [ ] Subtask 3.2: Implement SDK version detection in wrapper module: read version file on initialization and log version.
  - [ ] Subtask 3.3: Define expected SDK version range; emit warning if detected version is outside range.
  - [ ] Subtask 3.4: Create `docs/bmad/research/sdk-integration-guide.md` documenting:
    - SDK import path and wrapper usage
    - Version pinning strategy (semantic versioning, compatibility matrix)
    - Upgrade procedure: backup, smoke tests, regression validation
    - Smoke test checklist: authentication, order placement, market data, streaming connection
  - [ ] Subtask 3.5: Provide example upgrade workflow: update SDK files → run smoke tests → run full test suite → deploy to staging → production.

- [ ] Task 4: Testing and validation (AC: 7, IV1, IV2, IV3)
  - [ ] Subtask 4.1: Create `test_sdk_wrapper.py` with unit tests for factory functions, configuration propagation, and SDK initialization.
  - [ ] Subtask 4.2: Add integration tests confirming wrapper-provided clients successfully authenticate and execute operations.
  - [ ] Subtask 4.3: Test SDK version detection logic with mock version files (valid version, missing version, incompatible version).
  - [ ] Subtask 4.4: Run linting tools to confirm no direct SDK imports exist outside wrapper module.
  - [ ] Subtask 4.5: Simulate SDK upgrade by swapping SDK files and running smoke tests to validate upgrade procedure.

## Dev Notes

### Code Reuse Guidance - SDK Integration

**⚠️ CRITICAL DECISION: Minimize SDK Usage**

Based on code reuse analysis, **direct HTTP calls are preferred** over SDK wrapper for most operations:

**Use Direct HTTP (FivePaisaXTS Pattern) For:**
- ✅ Authentication (`authenticate_direct()` - already implemented in Story 1.0-1)
- ✅ Order placement (existing `place_order_api()` - 85% reusable)
- ✅ Market data (existing `data.py` functions - 85% reusable)
- ✅ Funds/positions (existing functions - 90% reusable)
- ✅ HTTP client (`get_httpx_client()` - 100% reusable)

**Use XTS Pro SDK Only For:**
- ⚠️ Pro-specific features (dealer operations, bracket/cover orders)
- ⚠️ Streaming/WebSocket (if SDK provides better implementation)
- ⚠️ Features not available via direct HTTP

**Rationale:**
1. **Simpler:** Direct HTTP calls are easier to maintain than SDK wrapper
2. **Proven:** FivePaisaXTS uses direct HTTP successfully (production broker)
3. **Flexible:** Direct HTTP gives more control over requests/responses
4. **Testable:** Easier to mock HTTP calls than SDK objects
5. **Maintainable:** No SDK version dependencies for core functionality

**Reference:**
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 3
- **Authentication:** Story 1.0-1 (uses direct HTTP, not SDK)
- **FivePaisaXTS:** `broker/fivepaisaxts/api/auth_api.py` (direct HTTP pattern)

### SDK Wrapper Scope (Minimal)

**Create SDK wrapper ONLY for:**
1. **Pro-specific features** that require SDK (dealer operations)
2. **Streaming/WebSocket** (if SDK provides better implementation)
3. **Features not available via direct HTTP**

**Do NOT create SDK wrapper for:**
- ❌ Authentication (use direct HTTP - Story 1.0-1)
- ❌ Order placement (use direct HTTP - existing code)
- ❌ Market data (use direct HTTP - existing code)
- ❌ Funds/positions (use direct HTTP - existing code)

### Relevant Source Tree
- `broker/jainam_prop/api/sdk.py` – New SDK wrapper module (minimal scope - Pro features only)
- `broker/jainam_prop/_sample_strategy/xts_PRO_SDK/` – Vendor-provided SDK files
- `broker/jainam_prop/_sample_strategy/xts_connect.py` – Reference for Pro-specific patterns
- `broker/jainam_prop/api/auth_api.py` – ✅ Uses direct HTTP (Story 1.0-1)
- `broker/jainam_prop/api/order_api.py` – ✅ Uses direct HTTP (existing)
- `broker/jainam_prop/streaming/jainam_websocket.py` – ⚠️ May need SDK for WebSocket
- `broker/jainam_prop/api/config.py` – Configuration module (80% reusable)

### Integration Approach
- Centralize SDK imports in `api/sdk.py` with factory functions wrapping `XTSConnect` initialization.
- Inject configuration (base URL, SSL flags, source identifier) from config module into SDK constructors.
- Encapsulate custom behaviors (logging, retry logic, data transforms) in separate helpers that call SDK methods.
- Enforce wrapper usage via linting rules and code review checklists.

### Existing Pattern Reference
- **SDK Integration Strategy:** Implementation plan Section 7 (Phase 3.4, Task 3.5) describes import standardization and upgrade procedures (lines 352–378).
- **Sample SDK Usage:** Reference sample demonstrates interactive/market login, Socket.IO initialization, and order placement patterns (implementation plan lines 83–86, 214–254).
- **Configuration Integration:** Wrapper module must consume base URL and SSL flags from config module (Task 3.4, lines 329–350).

### Key Constraints
- SDK source files in `_sample_strategy/xts_PRO_SDK/` must never be modified; all customizations encapsulated in wrappers/helpers.
- Wrapper module must remain thin: no business logic, only SDK initialization and configuration injection.
- SDK version detection must not fail if version manifest is missing; emit warning and proceed with default behavior.
- Upgrade procedure must include rollback plan in case of incompatible SDK changes.

### Example Wrapper Implementation

```python
# broker/jainam_prop/api/sdk.py
"""
SDK wrapper providing centralized SDK initialization and configuration injection.
All production modules MUST import SDK clients via this wrapper, not directly from SDK.
"""
from broker.jainam_prop._sample_strategy.xts_PRO_SDK.Connect import XTSConnect
from broker.jainam_prop.api.config import get_jainam_base_url, get_ssl_verify
from utils.logging import get_logger

logger = get_logger(__name__)

def build_interactive_client(api_key: str, api_secret: str, source: str = "WEBAPI"):
    """
    Build configured XTS interactive client.

    Args:
        api_key: Interactive API key
        api_secret: Interactive API secret
        source: Source identifier (default: WEBAPI)

    Returns:
        Configured XTSConnect client for interactive API
    """
    root_url = get_jainam_base_url()
    logger.info("Initializing interactive SDK client", extra={"root_url": root_url, "source": source})
    return XTSConnect(api_key, api_secret, source, root=root_url)

def build_market_client(api_key: str, api_secret: str, source: str = "WEBAPI"):
    """
    Build configured XTS market data client.

    Args:
        api_key: Market data API key
        api_secret: Market data API secret
        source: Source identifier (default: WEBAPI)

    Returns:
        Configured XTSConnect client for market data API
    """
    root_url = get_jainam_base_url()
    logger.info("Initializing market data SDK client", extra={"root_url": root_url, "source": source})
    return XTSConnect(api_key, api_secret, source, root=root_url)
```

## Testing

- **Unit Tests:** Wrapper factory functions, configuration injection, SDK version detection, error handling.
- **Integration Tests:** Wrapper-provided clients authenticate successfully, execute operations, propagate config changes.
- **Linting Tests:** Verify direct SDK imports prohibited outside wrapper module.
- **Upgrade Simulation:** Swap SDK files, run smoke tests, validate upgrade procedure.

## Dependencies

- **Story 1.6-1**: Configuration Management – Config module must provide base URL and SSL flags for SDK initialization.
- **Story 1.2-5**: Token Lifecycle Management Enhancement – Authentication flows consume SDK wrapper for login operations.
- **Task 3.4**: Configuration Management (Phase 3.4) – SDK wrapper requires config module for base URL injection.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-08 | 0.1 | Initial draft: SDK integration strategy story created from Phase 3.4 implementation plan | Sarah (PO) |

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
