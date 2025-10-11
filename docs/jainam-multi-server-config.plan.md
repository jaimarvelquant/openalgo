<!-- c8ed21e9-e75f-44cf-8b8f-f730a64d6bc7 01e367cf-e9fe-45d0-a008-c9a9d60df15d -->
# Jainam Multi-Server and Dealer Account Configuration - Implementation Plan

## Current State Analysis

### What EXISTS in the codebase:

1. **config.py**: Basic `get_jainam_base_url()` reading legacy `JAINAM_BASE_URL` env var
2. **auth_api.py**: Hardcoded credential loading from `JAINAM_INTERACTIVE_API_KEY` etc.
3. **order_api.py**: Already accepts `client_id` parameter (optional) for all methods
4. **brlogin.py** (line 588): Sets `clientID = user_id` in auth_token (INCORRECT for our use case)

### What's MISSING:

1. ✗ No multi-server support (Symphony A, B, C)
2. ✗ No account type configuration (Pro vs Normal)  
3. ✗ No dynamic credential loading based on server + account type
4. ✗ ClientID not loaded from configuration (uses userID from API response)
5. ✗ No `.env` file with proper credentials

## Key Understanding (from PDFs)

**Both Pro and Normal are DEALER accounts:**

- **Pro Dealer**: clientID `ZZJ13048`, credentials for Interactive/Market APIs
- **Normal Dealer**: clientID `DLL7182`, different credentials
- **Same endpoints**: Both use `/dealerorderbook`, `/dealertradebook`, `/dealerpositions`
- **Same base URL** depends on Symphony server (A/B/C), not account type
- **Both require** `clientID` parameter in ALL API calls

## Implementation Steps

### Step 1: Create/Update .env File

**IMPORTANT: Copy `.sample.env` to `.env` first if it doesn't exist:**

```bash
cp .sample.env .env
```

**Then APPEND the following Jainam configuration to the END of `/Users/maruth/projects/openalgo/.env`:**

This preserves ALL existing OpenAlgo configuration and adds Jainam-specific settings:

```bash
# ============================================================================
# Jainam Symphony Server Configuration
# ============================================================================
# Reference: broker/jainam_prop/_sample_strategy/pro-dealer-api.md
# Reference: broker/jainam_prop/_sample_strategy/normal-dealer-api.md

# IMPORTANT: Both PRO and NORMAL are dealer accounts (require clientID)
# The ONLY differences:
# - Different credentials (API keys/secrets)
# - Different clientID values (ZZJ13048 vs DLL7182)
# - Same endpoints, same base URLs (server-dependent)

# Symphony A: https://smpa.jainam.in:6543
#   Dashboard: https://smpa.jainam.in:6543/dashboard#!/login
#   Interactive: https://smpa.jainam.in:6543/interactive
#   Docs: https://smpa.jainam.in:6543/doc/interactive

# Symphony B: https://smpb.jainam.in:4143 (CURRENTLY ACTIVE)
#   Dashboard: https://smpb.jainam.in:4143/dashboard#!/login
#   Interactive: https://smpb.jainam.in:4143/interactive
#   Docs: https://smpb.jainam.in:4143/doc/interactive

# Symphony C: https://smpc.jainam.in:14543
#   Dashboard: https://smpc.jainam.in:14543/dashboard#!/login
#   Interactive: https://smpc.jainam.in:14543/interactive
#   Docs: https://smpc.jainam.in:14543/doc/interactive

# ============================================================================
# Active Configuration - CHANGE THESE TO SWITCH
# ============================================================================
JAINAM_ACTIVE_SYMPHONY_SERVER='B'  # Options: A, B, C
JAINAM_ACTIVE_ACCOUNT_TYPE='PRO'   # Options: PRO, NORMAL

# ============================================================================
# Symphony B - Pro Dealer Account
# ============================================================================
# ClientID: ZZJ13048
# Interactive API Key: 753d09b5c21762b4e24239
JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_KEY='753d09b5c21762b4e24239'
JAINAM_SYMPHONY_B_PRO_INTERACTIVE_API_SECRET='Riof561$ws'

# Market Data API Key: d4a77bc14c550effbbb423
JAINAM_SYMPHONY_B_PRO_MARKET_API_KEY='d4a77bc14c550effbbb423'
JAINAM_SYMPHONY_B_PRO_MARKET_API_SECRET='Pqoa026@Eg'

# ClientID (REQUIRED for all dealer API calls)
JAINAM_SYMPHONY_B_PRO_CLIENT_ID='ZZJ13048'

# ============================================================================
# Symphony B - Normal Dealer Account
# ============================================================================
# ClientID: DLL7182
# Interactive API Key: d229ee8bc6be3d81d35946
JAINAM_SYMPHONY_B_NORMAL_INTERACTIVE_API_KEY='d229ee8bc6be3d81d35946'
JAINAM_SYMPHONY_B_NORMAL_INTERACTIVE_API_SECRET='Qiet271#eJ'

# Market Data API Key: 511c4265c2869ab1f54180
JAINAM_SYMPHONY_B_NORMAL_MARKET_API_KEY='511c4265c2869ab1f54180'
JAINAM_SYMPHONY_B_NORMAL_MARKET_API_SECRET='Lypl445#sR'

# ClientID (REQUIRED for all dealer API calls)
JAINAM_SYMPHONY_B_NORMAL_CLIENT_ID='DLL7182'

# ============================================================================
# Symphony A / C - Placeholders (Add when needed)
# ============================================================================
# JAINAM_SYMPHONY_A_PRO_INTERACTIVE_API_KEY=''
# JAINAM_SYMPHONY_A_PRO_INTERACTIVE_API_SECRET=''
# JAINAM_SYMPHONY_A_PRO_MARKET_API_KEY=''
# JAINAM_SYMPHONY_A_PRO_MARKET_API_SECRET=''
# JAINAM_SYMPHONY_A_PRO_CLIENT_ID=''
#
# JAINAM_SYMPHONY_A_NORMAL_INTERACTIVE_API_KEY=''
# JAINAM_SYMPHONY_A_NORMAL_INTERACTIVE_API_SECRET=''
# JAINAM_SYMPHONY_A_NORMAL_MARKET_API_KEY=''
# JAINAM_SYMPHONY_A_NORMAL_MARKET_API_SECRET=''
# JAINAM_SYMPHONY_A_NORMAL_CLIENT_ID=''

# ============================================================================
# Legacy Variables (DEPRECATED - will trigger warnings)
# ============================================================================
# JAINAM_INTERACTIVE_API_KEY=''
# JAINAM_INTERACTIVE_API_SECRET=''
# JAINAM_MARKET_API_KEY=''
# JAINAM_MARKET_API_SECRET=''
# JAINAM_BASE_URL=''
```

### Step 2: Update broker/jainam_prop/api/config.py

**Replace entire file:**

```python
import os
from typing import Tuple
from utils.logging import get_logger

logger = get_logger(__name__)

# Symphony server URL mapping
SYMPHONY_SERVERS = {
    'A': 'https://smpa.jainam.in:6543',
    'B': 'https://smpb.jainam.in:4143',
    'C': 'https://smpc.jainam.in:14543',
}

DEFAULT_SYMPHONY_SERVER = 'B'
DEFAULT_ACCOUNT_TYPE = 'PRO'


def get_jainam_base_url() -> str:
    """
    Get Jainam API base URL for active Symphony server.
    
    Reads JAINAM_ACTIVE_SYMPHONY_SERVER environment variable.
    Falls back to Symphony B if not set.
    
    Returns:
        Base URL (e.g., 'https://smpb.jainam.in:4143')
    
    Raises:
        ValueError: If server not supported
    """
    server = os.getenv('JAINAM_ACTIVE_SYMPHONY_SERVER', DEFAULT_SYMPHONY_SERVER).strip().upper()
    
    if server not in SYMPHONY_SERVERS:
        raise ValueError(
            f"Invalid Symphony server '{server}'. "
            f"Supported: {', '.join(SYMPHONY_SERVERS.keys())}"
        )
    
    url = SYMPHONY_SERVERS[server]
    logger.debug(f"Using Jainam Symphony Server {server}: {url}")
    return url


def get_jainam_credentials() -> Tuple[str, str, str, str, str, str, str]:
    """
    Get credentials for active Symphony server and account type.
    
    IMPORTANT: Both PRO and NORMAL are dealer accounts requiring clientID.
    - PRO: clientID = ZZJ13048
    - NORMAL: clientID = DLL7182
    
    Returns:
        Tuple: (interactive_key, interactive_secret, market_key, market_secret,
                server, account_type, client_id)
    
    Raises:
        ValueError: If configuration invalid or credentials missing
    """
    server = os.getenv('JAINAM_ACTIVE_SYMPHONY_SERVER', DEFAULT_SYMPHONY_SERVER).strip().upper()
    account_type = os.getenv('JAINAM_ACTIVE_ACCOUNT_TYPE', DEFAULT_ACCOUNT_TYPE).strip().upper()
    
    # Validate server
    if server not in SYMPHONY_SERVERS:
        raise ValueError(
            f"Invalid Symphony server '{server}'. "
            f"Supported: {', '.join(SYMPHONY_SERVERS.keys())}"
        )
    
    # Validate account type
    if account_type not in ('PRO', 'NORMAL'):
        raise ValueError(
            f"Invalid account type '{account_type}'. "
            f"Supported: PRO (Dealer clientID=ZZJ13048), NORMAL (Dealer clientID=DLL7182)"
        )
    
    # Build credential env var names dynamically
    prefix = f"JAINAM_SYMPHONY_{server}_{account_type}"
    
    interactive_key = os.getenv(f"{prefix}_INTERACTIVE_API_KEY")
    interactive_secret = os.getenv(f"{prefix}_INTERACTIVE_API_SECRET")
    market_key = os.getenv(f"{prefix}_MARKET_API_KEY")
    market_secret = os.getenv(f"{prefix}_MARKET_API_SECRET")
    client_id = os.getenv(f"{prefix}_CLIENT_ID")
    
    # Check for missing credentials
    missing = []
    if not interactive_key:
        missing.append(f"{prefix}_INTERACTIVE_API_KEY")
    if not interactive_secret:
        missing.append(f"{prefix}_INTERACTIVE_API_SECRET")
    if not market_key:
        missing.append(f"{prefix}_MARKET_API_KEY")
    if not market_secret:
        missing.append(f"{prefix}_MARKET_API_SECRET")
    if not client_id:
        missing.append(f"{prefix}_CLIENT_ID")
    
    if missing:
        raise ValueError(
            f"Missing Jainam credentials for Symphony {server} {account_type} account.\n"
            f"Required environment variables:\n  " + "\n  ".join(missing) +
            f"\n\nNote: Both PRO and NORMAL are dealer accounts requiring clientID"
        )
    
    expected_client_id = 'ZZJ13048' if account_type == 'PRO' else 'DLL7182'
    
    logger.info(
        f"Loaded Jainam credentials: Symphony {server}, Account: {account_type}, "
        f"ClientID: {client_id}"
    )
    
    if client_id != expected_client_id:
        logger.warning(
            f"⚠️  ClientID mismatch! Configured '{client_id}' "
            f"does not match expected '{expected_client_id}' for {account_type} account"
        )
    
    return interactive_key, interactive_secret, market_key, market_secret, server, account_type, client_id
```

### Step 3: Update broker/jainam_prop/api/auth_api.py

**Update `_validate_credentials()` function (lines 95-124):**

```python
def _validate_credentials(
    *,
    require_interactive: bool = True,
    require_market: bool = True,
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """Validate Jainam credentials using dynamic configuration."""
    from broker.jainam_prop.api.config import get_jainam_credentials
    
    # Check for legacy environment variables
    legacy_vars = [
        'JAINAM_INTERACTIVE_API_KEY',
        'JAINAM_INTERACTIVE_API_SECRET',
        'JAINAM_MARKET_API_KEY',
        'JAINAM_MARKET_API_SECRET',
    ]
    
    found_legacy = [var for var in legacy_vars if os.getenv(var)]
    if found_legacy:
        logger.warning(
            f"⚠️  Legacy Jainam environment variables detected: {', '.join(found_legacy)}. "
            f"Please migrate to JAINAM_SYMPHONY_* format in .env file. "
            f"See .env template or documentation."
        )
    
    try:
        i_key, i_secret, m_key, m_secret, server, account_type, client_id = get_jainam_credentials()
    except ValueError as exc:
        raise ValueError(str(exc)) from exc
    
    # Partial credential support
    if not require_interactive:
        return None, None, m_key, m_secret
    if not require_market:
        return i_key, i_secret, None, None
    
    return i_key, i_secret, m_key, m_secret
```

**Update `authenticate_direct()` function to return clientID (lines 174-214):**

```python
def authenticate_direct() -> Tuple[Optional[str], Optional[str], Optional[str], Optional[bool], Optional[str], Optional[str]]:
    """
    Authenticate with Jainam XTS using configured credentials.
    
    IMPORTANT: Both PRO and NORMAL are dealer accounts.
    Both require clientID in all API calls.
    The difference is the clientID value (ZZJ13048 vs DLL7182).
    
    Returns:
        tuple: (interactive_token, market_token, user_id, is_investor_client, client_id, error_message)
    """
    from broker.jainam_prop.api.config import get_jainam_credentials
    
    try:
        interactive_key, interactive_secret, market_key, market_secret = _validate_credentials()
    except ValueError as exc:
        logger.error(str(exc))
        return None, None, None, None, None, str(exc)
    
    # Get configuration info for logging and clientID
    try:
        _, _, _, _, server, account_type, client_id = get_jainam_credentials()
    except:
        server, account_type, client_id = "Unknown", "Unknown", None
    
    base_url = get_jainam_base_url()
    
    logger.info(
        f"🔐 Authenticating Jainam Symphony {server} - {account_type} dealer account "
        f"(clientID: {client_id})"
    )

    try:
        # Authenticate Interactive API
        interactive_client = InteractiveAuthClient(base_url=base_url)
        interactive_response = interactive_client.login(interactive_key, interactive_secret)
        interactive_token, user_id, is_investor = _extract_token_from_response(
            interactive_response, "Interactive"
        )

        # Authenticate Market Data API
        market_client = MarketDataAuthClient(base_url=base_url)
        market_response = market_client.login(market_key, market_secret)
        market_token, _, _ = _extract_token_from_response(market_response, "Market data")

        # Log authentication success
        logger.info(
            f"✅ Jainam authentication SUCCESS - Symphony {server}, "
            f"Account: {account_type}, ClientID: {client_id}, UserID: {user_id}, "
            f"isInvestorClient: {bool(is_investor)}"
        )
        
        # Verify isInvestorClient flag (both should be False for dealer accounts)
        if is_investor:
            logger.warning(
                f"⚠️  Unexpected isInvestorClient=True for {account_type} dealer account! "
                f"Dealer accounts should return isInvestorClient=False."
            )
        else:
            logger.info(f"✓ Dealer account confirmed: clientID '{client_id}' will be used in all API calls")
        
        return interactive_token, market_token, user_id, is_investor, client_id, None
        
    except Exception as exc:
        error_message = (
            f"❌ Jainam authentication FAILED for Symphony {server} {account_type} account: {exc}"
        )
        logger.error(error_message)
        return None, None, None, None, None, error_message
```

**Update `authenticate_broker()` wrapper (lines 217-224):**

```python
def authenticate_broker(*_args, **_kwargs):
    """
    Backwards-compatible wrapper to support plugin loader expectations.

    Returns:
        tuple: (interactive_token, market_token, user_id, is_investor_client, client_id, error_message)
    """
    return authenticate_direct()
```

### Step 4: Update blueprints/brlogin.py

**Update line 142-143 to handle new return value:**

```python
# Line 142-143: Update to receive client_id
# Old: auth_token, feed_token, user_id, is_investor_client, error_message = auth_function()
# New:
auth_token, feed_token, user_id, is_investor_client, client_id, error_message = auth_function()
```

**Update lines 585-590 to use configured clientID:**

```python
# Lines 585-590: Use configured clientID instead of user_id
# Old code:
#     auth_token_json = json.dumps({
#         'token': auth_token,
#         'user_id': user_id,
#         'clientID': user_id,  # WRONG - uses userID from API
#         'isInvestorClient': is_investor_client
#     })

# New code:
if broker == 'jainam_prop' and user_id:
    import json
    # CRITICAL: Use configured clientID (ZZJ13048 or DLL7182), NOT user_id
    configured_client_id = client_id if client_id else user_id  # Fallback to user_id if not configured
    auth_token_json = json.dumps({
        'token': auth_token,
        'user_id': user_id,
        'clientID': configured_client_id,  # Use configured clientID from environment
        'isInvestorClient': is_investor_client
    })
    logger.info(
        f"Jainam Prop: Storing auth token with configured clientID: {configured_client_id}, "
        f"userID: {user_id}, isInvestorClient: {is_investor_client}"
    )
    # Store JSON version in database
    return handle_auth_success(auth_token_json, session['user'], broker, feed_token=feed_token, user_id=user_id)
```

### Step 5: Testing Plan

**Test 1: Pro Dealer Authentication**

```bash
# In .env:
JAINAM_ACTIVE_SYMPHONY_SERVER='B'
JAINAM_ACTIVE_ACCOUNT_TYPE='PRO'

# Expected:
# - Symphony B URL used
# - Pro credentials loaded
# - ClientID ZZJ13048 in auth_token
# - isInvestorClient=False
```

**Test 2: Normal Dealer Authentication**

```bash
# In .env:
JAINAM_ACTIVE_ACCOUNT_TYPE='NORMAL'

# Expected:
# - Symphony B URL used
# - Normal credentials loaded
# - ClientID DLL7182 in auth_token
# - isInvestorClient=False
```

**Test 3: Server Switching**

```bash
# In .env:
JAINAM_ACTIVE_SYMPHONY_SERVER='A'  # Assuming credentials configured

# Expected:
# - Symphony A URL used
# - Proper credentials loaded for server A
```

**Test 4: API Calls with ClientID**

```bash
# Place order, check positions, etc.
# Verify clientID parameter is sent correctly
# Verify dealer endpoints work
```

## Summary of Changes

| File | Lines | Change |

|------|-------|--------|

| `.env` | New file | Create with all Symphony servers and credentials |

| `broker/jainam_prop/api/config.py` | Entire file | Add SYMPHONY_SERVERS, get_jainam_credentials() |

| `broker/jainam_prop/api/auth_api.py` | 95-124 | Update _validate_credentials() to use dynamic loading |

| `broker/jainam_prop/api/auth_api.py` | 174-214 | Update authenticate_direct() to return client_id |

| `broker/jainam_prop/api/auth_api.py` | 217-224 | Update authenticate_broker() signature |

| `blueprints/brlogin.py` | 142-143 | Update to receive client_id from auth_function() |

| `blueprints/brlogin.py` | 585-590 | Use configured client_id instead of user_id |

## Success Criteria

- ✅ Switch accounts by changing 1 env var: `JAINAM_ACTIVE_ACCOUNT_TYPE`
- ✅ Switch servers by changing 1 env var: `JAINAM_ACTIVE_SYMPHONY_SERVER`
- ✅ Correct clientID used in all API calls (ZZJ13048 or DLL7182)
- ✅ Clear logging shows active server, account, and clientID
- ✅ Backward compatibility warnings for legacy variables
- ✅ Both dealer accounts work with same endpoints