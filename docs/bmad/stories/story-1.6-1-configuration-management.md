# Story 1.6-1: Configuration Management

**Status:** Ready for Development  
**Priority:** MEDIUM (Maintainability improvement)  
**Effort:** 0.5 days (4 hours) - **Code Reuse: 60%**  
**Original Effort:** 1.5 days (12 hours)  
**Savings:** 67% (8 hours saved)

---

## Story

As a **developer maintaining Jainam Prop broker integration**,  
I want **all configuration centralized in a single module with environment variable overrides**,  
so that **base URLs, SSL flags, retry settings, and other config can be changed without modifying code**.

---

## Context

### Current State
- Configuration scattered across multiple files
- Hard-coded URLs in some modules
- Partial implementation in `broker/jainam_prop/api/config.py`
- No centralized retry configuration
- SSL flags not configurable

### Reference Implementation
**Source:** `broker/fivepaisaxts/baseurl.py`

FivePaisaXTS has clean configuration pattern:
- ✅ Environment variable pattern (lines 1-10)
- ✅ Default values with fallbacks
- ✅ Simple, readable structure
- ✅ Single source of truth

### Code Reuse Strategy
**60% can be copied from FivePaisaXTS**

**What to Copy:**
- Environment variable pattern
- Default value structure
- Configuration organization

**What to Adapt (Jainam-Specific):**
- Multi-server configuration (Symphony A/B/C)
- Dealer account configuration
- Retry settings
- SSL/timeout settings

---

## Acceptance Criteria

### AC1: Centralize Base URL Configuration ✅

**Pattern:** Copy from `broker/fivepaisaxts/baseurl.py`

**File:** `broker/jainam_prop/api/config.py`

**Current State (Partial):**
```python
# broker/jainam_prop/api/config.py (current)
# Some config exists, but incomplete
```

**Enhanced Configuration:**
```python
"""
Centralized configuration for Jainam Prop broker integration.

✅ COPY PATTERN FROM FivePaisaXTS baseurl.py
✏️ ADAPT for Jainam multi-server and dealer accounts
"""
import os
from typing import Dict

# ============================================================================
# Multi-Server Configuration (Symphony A/B/C)
# ============================================================================

# ✏️ JAINAM-SPECIFIC: Multi-server support
SYMPHONY_SERVER_URLS: Dict[str, str] = {
    'A': os.getenv('JAINAM_SYMPHONY_A_URL', 'https://smpa.jainam.in:6543'),
    'B': os.getenv('JAINAM_SYMPHONY_B_URL', 'https://smpb.jainam.in:4143'),
    'C': os.getenv('JAINAM_SYMPHONY_C_URL', 'https://smpc.jainam.in:14543')
}

# ✅ COPY PATTERN FROM FivePaisaXTS (env variable with default)
ACTIVE_SYMPHONY_SERVER = os.getenv('JAINAM_ACTIVE_SYMPHONY_SERVER', 'B')

def get_jainam_base_url() -> str:
    """
    Get the active Symphony server base URL.
    
    ✏️ JAINAM-SPECIFIC: Multi-server selection
    """
    return SYMPHONY_SERVER_URLS.get(ACTIVE_SYMPHONY_SERVER, SYMPHONY_SERVER_URLS['B'])

# ============================================================================
# Dealer Account Configuration
# ============================================================================

# ✏️ JAINAM-SPECIFIC: Dealer account type
ACTIVE_ACCOUNT_TYPE = os.getenv('JAINAM_ACTIVE_ACCOUNT_TYPE', 'PRO')

# Dealer account credentials (loaded from environment)
DEALER_CREDENTIALS = {
    'PRO': {
        'interactive_api_key': os.getenv('JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_KEY', ''),
        'interactive_api_secret': os.getenv('JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_SECRET', ''),
        'market_api_key': os.getenv('JAINAM_SYMPHONY_B_PRO_MARKET_API_KEY', ''),
        'market_api_secret': os.getenv('JAINAM_SYMPHONY_B_PRO_MARKET_API_SECRET', ''),
        'client_id': os.getenv('JAINAM_SYMPHONY_B_PRO_CLIENT_ID', 'ZZJ13048')
    },
    'NORMAL': {
        'interactive_api_key': os.getenv('JAINAM_SYMPHONY_B_NORMAL_INTERACTIVE_API_KEY', ''),
        'interactive_api_secret': os.getenv('JAINAM_SYMPHONY_B_NORMAL_INTERACTIVE_API_SECRET', ''),
        'market_api_key': os.getenv('JAINAM_SYMPHONY_B_NORMAL_MARKET_API_KEY', ''),
        'market_api_secret': os.getenv('JAINAM_SYMPHONY_B_NORMAL_MARKET_API_SECRET', ''),
        'client_id': os.getenv('JAINAM_SYMPHONY_B_NORMAL_CLIENT_ID', 'DLL7182')
    }
}

def get_active_credentials() -> dict:
    """Get credentials for active account type."""
    return DEALER_CREDENTIALS.get(ACTIVE_ACCOUNT_TYPE, DEALER_CREDENTIALS['PRO'])

# ============================================================================
# HTTP Configuration
# ============================================================================

# ✅ COPY PATTERN FROM FivePaisaXTS (env variables with defaults)
# ✏️ ADAPT: Jainam-specific settings

# Retry configuration (from Story 1.4-1)
RETRY_ATTEMPTS = int(os.getenv('JAINAM_RETRY_ATTEMPTS', '3'))
RETRY_BACKOFF_MIN = float(os.getenv('JAINAM_RETRY_BACKOFF_MIN', '0.25'))
RETRY_BACKOFF_MAX = float(os.getenv('JAINAM_RETRY_BACKOFF_MAX', '2.0'))

# Timeout configuration
REQUEST_TIMEOUT = float(os.getenv('JAINAM_REQUEST_TIMEOUT', '10.0'))
CONNECT_TIMEOUT = float(os.getenv('JAINAM_CONNECT_TIMEOUT', '5.0'))

# SSL configuration
VERIFY_SSL = os.getenv('JAINAM_VERIFY_SSL', 'true').lower() == 'true'

# ============================================================================
# WebSocket Configuration
# ============================================================================

# ✏️ JAINAM-SPECIFIC: WebSocket settings
WS_RECONNECT_DELAY = int(os.getenv('JAINAM_WS_RECONNECT_DELAY', '5'))
WS_MAX_RECONNECT_DELAY = int(os.getenv('JAINAM_WS_MAX_RECONNECT_DELAY', '60'))
WS_MAX_RECONNECT_ATTEMPTS = int(os.getenv('JAINAM_WS_MAX_RECONNECT_ATTEMPTS', '10'))

# ============================================================================
# API Endpoints
# ============================================================================

# ✏️ JAINAM-SPECIFIC: Endpoint paths
ENDPOINTS = {
    # Authentication
    'user.login': '/interactive/user/session',
    'user.logout': '/interactive/user/session',
    
    # Orders
    'orders.place': '/interactive/orders',
    'orders.modify': '/interactive/orders',
    'orders.cancel': '/interactive/orders',
    
    # Dealer-specific endpoints
    'dealer.orderbook': '/interactive/orders/dealerorderbook',
    'dealer.tradebook': '/interactive/orders/dealertradebook',
    'dealer.positions': '/interactive/portfolio/dealerpositions',
    
    # Portfolio
    'portfolio.holdings': '/interactive/portfolio/holdings',
    'user.balance': '/interactive/user/balance',
    
    # Market Data
    'market.login': '/apibinarymarketdata/auth/login'
}

def get_endpoint(key: str) -> str:
    """Get endpoint path by key."""
    return ENDPOINTS.get(key, '')

# ============================================================================
# Logging Configuration
# ============================================================================

# ✅ COPY PATTERN FROM FivePaisaXTS
LOG_LEVEL = os.getenv('JAINAM_LOG_LEVEL', 'INFO')
LOG_API_REQUESTS = os.getenv('JAINAM_LOG_API_REQUESTS', 'false').lower() == 'true'
LOG_API_RESPONSES = os.getenv('JAINAM_LOG_API_RESPONSES', 'false').lower() == 'true'
```

**Verification:**
- [ ] All base URLs centralized
- [ ] Environment variables with defaults
- [ ] Multi-server configuration working
- [ ] Dealer account credentials accessible
- [ ] Retry settings centralized
- [ ] SSL/timeout settings configurable

---

### AC2: Update All Modules to Use Centralized Config ✅

**Modules to Update:**

1. **`broker/jainam_prop/api/auth_api.py`**
```python
# Before
base_url = "https://smpb.jainam.in:4143"

# After
from broker.jainam_prop.api.config import get_jainam_base_url
base_url = get_jainam_base_url()
```

2. **`broker/jainam_prop/api/http_helper.py`**
```python
# Before
retries = 3
backoff_min = 0.25

# After
from broker.jainam_prop.api.config import RETRY_ATTEMPTS, RETRY_BACKOFF_MIN
retries = RETRY_ATTEMPTS
backoff_min = RETRY_BACKOFF_MIN
```

3. **`broker/jainam_prop/streaming/jainam_adapter.py`**
```python
# Before
reconnect_delay = 5
max_reconnect_attempts = 10

# After
from broker.jainam_prop.api.config import WS_RECONNECT_DELAY, WS_MAX_RECONNECT_ATTEMPTS
reconnect_delay = WS_RECONNECT_DELAY
max_reconnect_attempts = WS_MAX_RECONNECT_ATTEMPTS
```

**Verification:**
- [ ] No hard-coded URLs in any module
- [ ] All modules import from config
- [ ] Configuration changes work without code changes

---

### AC3: Document Configuration Options ✅

**Create:** `broker/jainam_prop/CONFIG.md`

```markdown
# Jainam Prop Configuration Guide

## Environment Variables

### Multi-Server Configuration
- `JAINAM_ACTIVE_SYMPHONY_SERVER` - Active server (A/B/C), default: B
- `JAINAM_SYMPHONY_A_URL` - Symphony A URL
- `JAINAM_SYMPHONY_B_URL` - Symphony B URL
- `JAINAM_SYMPHONY_C_URL` - Symphony C URL

### Dealer Account Configuration
- `JAINAM_ACTIVE_ACCOUNT_TYPE` - Account type (PRO/NORMAL), default: PRO
- `JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_KEY` - Pro interactive API key
- `JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_SECRET` - Pro interactive secret
- ... (all dealer credentials)

### HTTP Configuration
- `JAINAM_RETRY_ATTEMPTS` - Number of retry attempts, default: 3
- `JAINAM_RETRY_BACKOFF_MIN` - Min backoff delay (seconds), default: 0.25
- `JAINAM_RETRY_BACKOFF_MAX` - Max backoff delay (seconds), default: 2.0
- `JAINAM_REQUEST_TIMEOUT` - Request timeout (seconds), default: 10.0
- `JAINAM_VERIFY_SSL` - Verify SSL certificates, default: true

### WebSocket Configuration
- `JAINAM_WS_RECONNECT_DELAY` - Initial reconnect delay (seconds), default: 5
- `JAINAM_WS_MAX_RECONNECT_DELAY` - Max reconnect delay (seconds), default: 60
- `JAINAM_WS_MAX_RECONNECT_ATTEMPTS` - Max reconnect attempts, default: 10

### Logging Configuration
- `JAINAM_LOG_LEVEL` - Log level (DEBUG/INFO/WARNING/ERROR), default: INFO
- `JAINAM_LOG_API_REQUESTS` - Log API requests, default: false
- `JAINAM_LOG_API_RESPONSES` - Log API responses, default: false

## Usage Examples

### Switch Symphony Server
```bash
export JAINAM_ACTIVE_SYMPHONY_SERVER=A
```

### Switch Dealer Account
```bash
export JAINAM_ACTIVE_ACCOUNT_TYPE=NORMAL
```

### Enable Debug Logging
```bash
export JAINAM_LOG_LEVEL=DEBUG
export JAINAM_LOG_API_REQUESTS=true
```
```

**Verification:**
- [ ] All configuration options documented
- [ ] Usage examples provided
- [ ] Default values listed

---

## Implementation Steps

### Step 1: Copy Configuration Pattern (1 hour)
1. Review `broker/fivepaisaxts/baseurl.py`
2. Copy environment variable pattern
3. Create enhanced `config.py`
4. Add Jainam-specific sections

### Step 2: Update All Modules (2 hours)
1. Update `auth_api.py` to use config
2. Update `http_helper.py` to use config
3. Update `jainam_adapter.py` to use config
4. Update any other modules with hard-coded values
5. Test all modules

### Step 3: Create Documentation (1 hour)
1. Create `CONFIG.md`
2. Document all environment variables
3. Add usage examples
4. Update main README if needed

**Total Effort: ~4 hours (0.5 days)**

---

## Testing Strategy

### Configuration Tests
```python
# broker/jainam_prop/api/test_config.py

def test_get_base_url():
    """Test base URL retrieval"""
    # Test default server
    # Test server switching

def test_get_active_credentials():
    """Test credential retrieval"""
    # Test PRO credentials
    # Test NORMAL credentials

def test_environment_overrides():
    """Test environment variable overrides"""
    # Test URL override
    # Test retry override
```

---

## Dependencies

**Requires:**
- ✅ Story 1.4-1 (HTTP Helper) - uses retry config
- ✅ Story 1.5-1 (Streaming Adapter) - uses WS config

**Blocks:**
- None (enhancement to existing functionality)

---

## Success Metrics

- [ ] All configuration centralized in config.py
- [ ] No hard-coded URLs in any module
- [ ] All environment variables documented
- [ ] Configuration changes work without code changes
- [ ] All modules use centralized config
- [ ] Tests verify configuration loading

---

## Code Reuse Summary

**Reused from FivePaisaXTS:**
- ✅ Environment variable pattern (100%)
- ✅ Default value structure (100%)
- ✅ Configuration organization (100%)

**Jainam-Specific Additions:**
- ✏️ Multi-server configuration (new)
- ✏️ Dealer account configuration (new)
- ✏️ Retry settings (new)
- ✏️ WebSocket settings (new)
- ✏️ Endpoint mapping (new)

**Overall Code Reuse: 60%**  
**Effort Savings: 67% (8 hours saved)**

---

## Related Stories

- **Enhances:** All stories (provides centralized config)
- **Related:** Story 1.4-1 (HTTP Helper), Story 1.5-1 (Streaming)

---

**Ready for Development** ✅

