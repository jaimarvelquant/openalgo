# Story 1.6-1: Configuration Management

## Status
Draft

## Estimated Effort
**4-6 hours** (High code reuse from existing config patterns)

## Code Reuse Summary

**Reuse Breakdown:**
- ✅ Config module pattern: 80% reusable from other broker config modules
- ✅ Environment variable handling: 90% reusable from standard patterns
- ✅ Validation logic: 85% reusable from existing validation patterns
- ✅ Documentation: 70% reusable from other broker docs

**Reference:**
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 5
- **Existing Config:** `broker/jainam_prop/api/config.py` (already exists, needs enhancement)
- **Pattern:** Other broker config modules (80% reusable)

**Effort Reduction:** ~50% (from 8-12 hours to 4-6 hours)

## Story

**As a** deployment engineer responsible for multi-environment Jainam Prop integration,
**I want** centralized configuration management for base URLs, SSL flags, and retry tuning via a dedicated config module,
**so that** environment-specific settings are isolated from code, deployment tiers (development, staging, production) can be configured independently, and configuration drift is eliminated.

## Acceptance Criteria

1. **AC1**: Extend or create `broker/jainam_prop/api/config.py` to centralize base URLs (`JAINAM_BASE_URL`), SSL verification flags (`JAINAM_DISABLE_SSL`), and HTTP retry parameters (`JAINAM_HTTP_RETRIES`, `JAINAM_HTTP_BACKOFF_BASE`, `JAINAM_HTTP_BACKOFF_FACTOR`).
2. **AC2**: Implement configuration precedence: environment variable → `.env` file → deployment secret → documented fallback constant, ensuring explicit configuration source logging.
3. **AC3**: Provide getter functions (`get_jainam_base_url()`, `get_ssl_verify()`, `get_retry_config()`) that load settings lazily and cache results for performance.
4. **AC4**: Remove all hard-coded base URLs and SSL flags from `api/auth_api.py`, `api/http.py`, `streaming/jainam_websocket.py`, and SDK initialization points.
5. **AC5**: Document required environment variables in `docs/bmad/research/` or broker README with example `.env` file covering local development, staging, and production configurations.
6. **AC6**: Add configuration validation on module load: emit warnings for missing required variables, fail fast for critical misconfigurations (e.g., invalid URL format, out-of-range retry counts).
7. **AC7**: Support environment-specific overrides for testing: allow tests to inject mock configurations without polluting global state or environment variables.

## Integration Verification

**IV1**: Verify all modules (`auth_api`, `http`, streaming adapter, SDK wrappers) consume configuration via config module rather than hard-coded values or direct environment variable reads.
**IV2**: Confirm configuration changes (base URL, SSL flag, retry tuning) propagate correctly across local development, CI/CD test environments, and production deployments without code changes.
**IV3**: Ensure test suites can inject mock configurations and restore original settings after test execution without side effects.

## Tasks / Subtasks

- [ ] Task 1: Config module implementation (AC: 1, 2, 3, 6)
  - [ ] Subtask 1.1: Create or extend `broker/jainam_prop/api/config.py` with configuration loader functions.
  - [ ] Subtask 1.2: Define configuration keys: `JAINAM_BASE_URL`, `JAINAM_DISABLE_SSL`, `JAINAM_HTTP_RETRIES`, `JAINAM_HTTP_BACKOFF_BASE`, `JAINAM_HTTP_BACKOFF_FACTOR`.
  - [ ] Subtask 1.3: Implement precedence logic: `os.getenv()` → `.env` parser (via `python-dotenv`) → fallback constants.
  - [ ] Subtask 1.4: Add lazy loading with caching (module-level variables or `@lru_cache` decorator) for performance.
  - [ ] Subtask 1.5: Implement configuration validation: check URL format (regex), SSL flag type (bool), retry counts (1-10 range).
  - [ ] Subtask 1.6: Emit structured logs indicating configuration source (env var, .env file, fallback) during load.

- [ ] Task 2: Refactor modules to use config (AC: 4)
  - [ ] Subtask 2.1: Update `api/auth_api.py` to call `get_jainam_base_url()` and `get_ssl_verify()` instead of hard-coded values.
  - [ ] Subtask 2.2: Refactor `api/http.py` (Task 2.4 from Phase 2.5) to consume retry configuration via `get_retry_config()`.
  - [ ] Subtask 2.3: Update streaming adapter initialization to load base URL and SSL flags from config module.
  - [ ] Subtask 2.4: Modify SDK wrapper (`api/sdk.py` from Task 3.5) to pass config-derived root URL to `XTSConnect` constructor.
  - [ ] Subtask 2.5: Audit codebase for remaining hard-coded URLs or SSL flags using grep; migrate all instances to config module.

- [ ] Task 3: Documentation and examples (AC: 5)
  - [ ] Subtask 3.1: Create example `.env` file (`config/jainam_example.env`) with documented variables and recommended values per environment.
  - [ ] Subtask 3.2: Document configuration precedence and validation rules in broker README or `docs/bmad/research/configuration-guide.md`.
  - [ ] Subtask 3.3: Provide deployment-specific examples: local development (sandbox URL, SSL disabled), staging (test URL, SSL enabled), production (live URL, strict SSL).
  - [ ] Subtask 3.4: Add troubleshooting section covering common misconfigurations and error messages.

- [ ] Task 4: Testing and validation (AC: 7, IV1, IV2, IV3)
  - [ ] Subtask 4.1: Create `test_config.py` with unit tests for configuration loading, precedence, validation, and fallback behavior.
  - [ ] Subtask 4.2: Implement test fixture for injecting mock configurations (using `monkeypatch` or context managers) and restoring state.
  - [ ] Subtask 4.3: Add integration tests verifying modules consume config correctly (auth API, HTTP helper, streaming adapter).
  - [ ] Subtask 4.4: Test configuration changes across environments (simulate env var overrides, .env file presence/absence).
  - [ ] Subtask 4.5: Run regression tests confirming existing functionality unaffected by config refactor.

## Dev Notes

### Code Reuse Guidance - Configuration Management

**Existing Config Module:** `broker/jainam_prop/api/config.py` already exists (80% complete)

**Current Implementation:**
```python
# broker/jainam_prop/api/config.py (existing)
import os

def get_jainam_base_url():
    """Get Jainam API base URL from environment"""
    return os.getenv('JAINAM_BASE_URL', 'https://xts.jainam.in')

def get_ssl_verify():
    """Get SSL verification flag"""
    return os.getenv('JAINAM_DISABLE_SSL', 'false').lower() != 'true'
```

**Enhancement Needed (20%):**
1. Add retry configuration getters (30 min)
2. Add configuration validation (30 min)
3. Add configuration logging (15 min)
4. Add caching for performance (15 min)

**Enhanced Implementation Pattern:**
```python
# broker/jainam_prop/api/config.py (enhanced)
import os
from functools import lru_cache
from utils.logging import get_logger

logger = get_logger(__name__)

@lru_cache(maxsize=1)
def get_jainam_base_url():
    """Get Jainam API base URL with validation"""
    url = os.getenv('JAINAM_BASE_URL', 'https://xts.jainam.in')
    logger.info(f"Jainam base URL: {url}")
    return url

@lru_cache(maxsize=1)
def get_ssl_verify():
    """Get SSL verification flag"""
    disable_ssl = os.getenv('JAINAM_DISABLE_SSL', 'false').lower() == 'true'
    ssl_verify = not disable_ssl
    logger.info(f"SSL verification: {ssl_verify}")
    return ssl_verify

@lru_cache(maxsize=1)
def get_retry_config():
    """Get HTTP retry configuration"""
    config = {
        'retries': int(os.getenv('JAINAM_HTTP_RETRIES', '3')),
        'backoff_base': float(os.getenv('JAINAM_HTTP_BACKOFF_BASE', '1.0')),
        'backoff_factor': float(os.getenv('JAINAM_HTTP_BACKOFF_FACTOR', '2.0'))
    }
    logger.info(f"Retry config: {config}")
    return config

def validate_config():
    """Validate configuration on module load"""
    url = get_jainam_base_url()
    if not url.startswith('http'):
        logger.warning(f"Invalid base URL format: {url}")

    retry_config = get_retry_config()
    if not 1 <= retry_config['retries'] <= 10:
        logger.warning(f"Retry count out of range: {retry_config['retries']}")

# Validate on module load
validate_config()
```

**Reuse Percentages:**
- Existing config module: 80% complete
- Enhancement needed: 20%
- Pattern reuse from other brokers: 90%
- Overall effort: 4-6 hours (vs 8-12 hours from scratch)

### Relevant Source Tree
- `broker/jainam_prop/api/config.py` – ✅ Already exists (80% complete, needs enhancement)
- `broker/jainam_prop/api/auth_api.py` – ✅ Already uses `get_jainam_base_url()`
- `broker/jainam_prop/api/http.py` – ⚠️ Needs retry config integration
- `broker/jainam_prop/streaming/jainam_websocket.py` – ⚠️ Needs config integration
- Other broker config modules – ✅ Reference for patterns (90% reusable)

### Integration Approach
- ✅ Config module already exists (80% complete)
- ⚠️ Enhance with retry config, validation, logging (20% work)
- ✅ Most modules already use config getters
- ⚠️ Add retry config to HTTP helper
- ✅ Document configuration keys and precedence

### Existing Pattern Reference
- **Configuration Precedence:** Implementation plan Section 7 (Phase 3.4, Task 3.4) describes environment variable → `.env` → fallback flow (lines 329–350).
- **SDK Configuration:** Sample SDK expects `config.ini` for base URL and SSL settings (implementation plan line 332).
- **Retry Tuning:** HTTP helper (Task 2.4) requires configurable retry counts and backoff parameters (lines 138–209).

### Key Constraints
- Configuration validation must fail fast for critical errors (invalid URLs, out-of-range values) during module load.
- Configuration caching must be thread-safe and respect environment changes in test contexts.
- Sensitive credentials (API keys, secrets) must never be logged; only non-sensitive config keys should appear in logs.
- Configuration precedence must be consistent across all deployment tiers (local, staging, production).

### Example Configuration

```ini
# config/jainam_example.env (reference)
# Base URL for Jainam XTS API (interactive and market data)
JAINAM_BASE_URL=https://smpb.jainam.in:4143

# Disable SSL verification for development environments (set to 'false' for production)
JAINAM_DISABLE_SSL=false

# HTTP retry configuration
JAINAM_HTTP_RETRIES=3
JAINAM_HTTP_BACKOFF_BASE=0.25
JAINAM_HTTP_BACKOFF_FACTOR=2.0

# WebSocket configuration
JAINAM_WS_RECONNECT_MAX_ATTEMPTS=10
JAINAM_WS_RECONNECT_MAX_DELAY=60
```

## Testing

- **Unit Tests:** Configuration loading, precedence logic, validation rules, fallback behavior, cache consistency.
- **Integration Tests:** Module consumption of config (auth, HTTP, streaming), environment variable overrides, `.env` file parsing.
- **Regression Tests:** Verify existing functionality unaffected by config centralization.
- **Deployment Tests:** Validate configuration across local, staging, and production environments with different `.env` files.

## Dependencies

- **Task 2.4**: HTTP Helper with Retry Logic (Phase 2.5) – HTTP helper requires retry configuration from config module.
- **Task 3.5**: SDK Integration Strategy (Phase 3.4) – SDK wrapper requires base URL configuration from config module.
- **Story 1.5-1**: Streaming Adapter Refactor – Streaming adapter requires base URL and SSL configuration from config module.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-08 | 0.1 | Initial draft: configuration management story created from Phase 3.4 implementation plan | Sarah (PO) |

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
