# JAINAM PROP AUTHENTICATION GUIDE

**Date:** October 8, 2025  
**Purpose:** Enable live API testing for Jainam Prop broker integration  
**Status:** Complete Guide with Helper Scripts

---

## EXECUTIVE SUMMARY

### The Good News: Direct Login is Supported! ✅

**You do NOT need a request token or OAuth flow!**

The Jainam XTS API supports **direct programmatic login** using only your API key and secret. This is the pattern used in the sample code (`_sample_strategy/xts_connect.py`) and is the recommended approach.

### Current Authentication Architecture

**Two Separate Authentication Flows:**

1. **Interactive API** (for orders, portfolio, positions)
   - Endpoint: `POST {base_url}/interactive/user/session`
   - Credentials: `appKey` + `secretKey` + `source`
   - Returns: `interactive_token` + `userID` + `isInvestorClient`

2. **Market Data API** (for quotes, historical data, depth)
   - Endpoint: `POST {base_url}/apimarketdata/auth/login`
   - Credentials: `appKey` + `secretKey` + `source`
   - Returns: `market_token` + `userID`

### What You Have vs What You Need

| Item | Status | Location |
|------|--------|----------|
| **API Credentials** | ✅ Have | `.env` file |
| **Base URL** | ✅ Have | `.env` file |
| **Interactive Token** | ❌ Need | Generated via login |
| **Market Token** | ❌ Need | Generated via login |
| **Request Token** | ❌ NOT NEEDED | N/A |

---

## ANSWER TO YOUR QUESTIONS

### 1. How do we obtain the initial JAINAM_REQUEST_TOKEN?

**Answer:** ❌ **YOU DON'T NEED IT!**

The `authenticate_broker(request_token)` function in `auth_api.py` is designed for **OAuth-based brokers** (like Zerodha, Upstox) that require a web-based login flow. 

**Jainam XTS API uses DIRECT LOGIN** - you can obtain session tokens programmatically using only your API key and secret.

---

### 2. What is the authentication flow we should implement?

**Answer:** ✅ **Option B: Automated Direct Login**

**Recommended Flow:**

```
1. Call Interactive API Login
   ├─ Input: API Key + API Secret + Source
   └─ Output: Interactive Token + User ID

2. Call Market Data API Login
   ├─ Input: API Key + API Secret + Source
   └─ Output: Market Token + User ID

3. Store Tokens
   ├─ In session (for web app)
   └─ In .env (for scripts/testing)

4. Use Tokens for API Calls
   ├─ Interactive Token → Order/Portfolio APIs
   └─ Market Token → Market Data APIs
```

**This is exactly what the sample code does** (see `xts_connect.py` lines 44-54).

---

### 3. Can we generate session tokens programmatically using only the API key/secret?

**Answer:** ✅ **YES! Absolutely!**

**Interactive API Login:**
```python
POST http://smpb.jainam.in:4143/interactive/user/session
Content-Type: application/json

{
    "appKey": "753d09b5c21762b4e24239",
    "secretKey": "Riof561$ws",
    "source": "WEBAPI"
}

Response:
{
    "type": "success",
    "code": "s-login-200",
    "description": "User session created successfully",
    "result": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "userID": "DLL11594",
        "isInvestorClient": false
    }
}
```

**Market Data API Login:**
```python
POST http://smpb.jainam.in:4143/apimarketdata/auth/login
Content-Type: application/json

{
    "appKey": "753d09b5c21762b4e24239",
    "secretKey": "Riof561$ws",
    "source": "WEBAPI"
}

Response:
{
    "type": "success",
    "code": "s-login-200",
    "description": "User session created successfully",
    "result": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "userID": "DLL11594"
    }
}
```

---

### 4. What is the recommended approach for the implementation plan?

**Answer:** ✅ **Create a Helper Script + Update auth_api.py**

**Recommended Implementation:**

1. **Create `get_jainam_tokens.py` helper script** (see below)
   - Obtains both tokens programmatically
   - Saves to `.env` file
   - Can be run anytime to refresh tokens

2. **Update `auth_api.py` to support direct login** (Phase 2 enhancement)
   - Add `authenticate_direct()` function
   - Keep existing `authenticate_broker()` for OAuth compatibility
   - Use direct login as primary method

3. **Implement automatic token refresh** (Phase 2 enhancement)
   - Detect token expiry (401 errors)
   - Automatically re-authenticate
   - Update stored tokens

---

### 5. For immediate testing, what is the quickest path forward?

**Answer:** ✅ **Run the helper script I'm providing below**

**Quickest Path (5 minutes):**

1. Run `get_jainam_tokens.py` script (provided below)
2. Script will:
   - Read credentials from `.env`
   - Call both login APIs
   - Display tokens
   - Optionally save to `.env`
3. Use tokens for live API testing

---

## HELPER SCRIPT: get_jainam_tokens.py

**Location:** `/Users/maruth/projects/openalgo/broker/jainam_prop/get_jainam_tokens.py`

**Purpose:** Obtain interactive and market data tokens programmatically

**Usage:**
```bash
cd /Users/maruth/projects/openalgo
python broker/jainam_prop/get_jainam_tokens.py
```

**Features:**
- ✅ Reads credentials from `.env`
- ✅ Calls both login APIs
- ✅ Displays tokens with expiry info
- ✅ Optionally saves to `.env`
- ✅ Validates token format
- ✅ Comprehensive error handling

---

## TOKEN LIFECYCLE

### Token Validity

**Interactive Token:**
- **Validity:** Typically 24 hours (check API docs)
- **Expiry Behavior:** Returns 401 Unauthorized
- **Refresh:** Call `interactive_login()` again

**Market Token:**
- **Validity:** Typically 24 hours (check API docs)
- **Expiry Behavior:** Returns 401 Unauthorized
- **Refresh:** Call `marketdata_login()` again

### Token Storage

**For Web Application (OpenAlgo):**
- Store in Flask session: `session['jainam_prop_auth_token']`
- Store in Flask session: `session['marketdata_token']`
- Tokens are user-specific and session-specific

**For Scripts/Testing:**
- Store in `.env` file: `JAINAM_INTERACTIVE_SESSION_TOKEN`
- Store in `.env` file: `JAINAM_MARKET_TOKEN`
- Tokens are shared across all script runs

---

## AUTHENTICATION ENDPOINTS

### Interactive API Login

**Endpoint:** `POST {base_url}/interactive/user/session`

**Request:**
```json
{
    "appKey": "your_api_key",
    "secretKey": "your_api_secret",
    "source": "WEBAPI"
}
```

**Response (Success):**
```json
{
    "type": "success",
    "code": "s-login-200",
    "description": "User session created successfully",
    "result": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "userID": "DLL11594",
        "isInvestorClient": false
    }
}
```

**Response (Error):**
```json
{
    "type": "error",
    "code": "e-login-400",
    "description": "Invalid credentials"
}
```

---

### Market Data API Login

**Endpoint:** `POST {base_url}/apimarketdata/auth/login`

**Request:**
```json
{
    "appKey": "your_api_key",
    "secretKey": "your_api_secret",
    "source": "WEBAPI"
}
```

**Response (Success):**
```json
{
    "type": "success",
    "code": "s-login-200",
    "description": "User session created successfully",
    "result": {
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "userID": "DLL11594"
    }
}
```

---

## USING TOKENS IN API CALLS

### Interactive API Calls (Orders, Portfolio)

**Headers:**
```python
headers = {
    'Authorization': interactive_token,
    'Content-Type': 'application/json'
}
```

**Example - Get Order Book:**
```python
GET http://smpb.jainam.in:4143/interactive/orders
Headers:
    Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    Content-Type: application/json
```

---

### Market Data API Calls (Quotes, Historical Data)

**Headers:**
```python
headers = {
    'Authorization': market_token,
    'Content-Type': 'application/json'
}
```

**Example - Get Quotes:**
```python
POST http://smpb.jainam.in:4143/apimarketdata/instruments/quotes
Headers:
    Authorization: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    Content-Type: application/json
Body:
{
    "instruments": [
        {
            "exchangeSegment": 1,
            "exchangeInstrumentID": 2885
        }
    ],
    "xtsMessageCode": 1501,
    "publishFormat": "JSON"
}
```

---

## COMPARISON: auth_api.py vs Sample Code

### Current auth_api.py (OAuth-based)

```python
def authenticate_broker(request_token):
    # Expects a request_token from OAuth flow
    # Generates checksum: SHA256(api_key + request_token + api_secret)
    # Calls: POST /interactive/user/session
    # Returns: access_token
```

**Problem:** Requires `request_token` which Jainam doesn't use for direct login

---

### Sample Code (Direct Login)

```python
def interactive_login(self):
    params = {
        "appKey": self.apiKey,
        "secretKey": self.secretKey,
        "source": self.source
    }
    response = self._post("user.login", params)
    return response['result']['token']
```

**Advantage:** Direct login without request token

---

## RECOMMENDED UPDATES TO auth_api.py

### Add Direct Login Function

```python
def authenticate_direct():
    """
    Direct authentication with Jainam XTS API (no request token needed)
    
    Returns:
        dict: {
            'interactive_token': str,
            'market_token': str,
            'user_id': str,
            'is_investor_client': bool
        }
    
    Raises:
        ValueError: If credentials are missing
        Exception: If authentication fails
    """
    # Get credentials
    interactive_api_key = os.getenv('JAINAM_INTERACTIVE_API_KEY')
    interactive_api_secret = os.getenv('JAINAM_INTERACTIVE_API_SECRET')
    market_api_key = os.getenv('JAINAM_MARKET_API_KEY')
    market_api_secret = os.getenv('JAINAM_MARKET_API_SECRET')
    
    # Validate
    if not all([interactive_api_key, interactive_api_secret, market_api_key, market_api_secret]):
        raise ValueError("Missing required credentials")
    
    # Login to Interactive API
    interactive_token, user_id, is_investor = _login_interactive(
        interactive_api_key, interactive_api_secret
    )
    
    # Login to Market Data API
    market_token = _login_market_data(
        market_api_key, market_api_secret
    )
    
    return {
        'interactive_token': interactive_token,
        'market_token': market_token,
        'user_id': user_id,
        'is_investor_client': is_investor
    }
```

---

## NEXT STEPS

### Immediate (For Testing)

1. ✅ **Run the helper script** (provided in next file)
   ```bash
   python broker/jainam_prop/get_jainam_tokens.py
   ```

2. ✅ **Copy tokens to `.env`**
   ```bash
   JAINAM_INTERACTIVE_SESSION_TOKEN=<token_from_script>
   JAINAM_MARKET_TOKEN=<token_from_script>
   ```

3. ✅ **Run live validation scripts**
   ```bash
   python broker/jainam_prop/test_live_api.py
   ```

### Phase 2 (Enhancement)

1. Update `auth_api.py` to add `authenticate_direct()` function
2. Implement automatic token refresh on 401 errors
3. Add token expiry detection and proactive refresh
4. Update OpenAlgo web app to use direct login

---

## TROUBLESHOOTING

### Error: "Invalid credentials"

**Cause:** Wrong API key or secret

**Solution:**
- Verify credentials in `.env` match Jainam portal
- Check for extra spaces or quotes
- Ensure base URL is correct

---

### Error: "Token expired"

**Cause:** Token validity period exceeded

**Solution:**
- Run `get_jainam_tokens.py` again to get fresh tokens
- Implement automatic token refresh

---

### Error: "Connection refused"

**Cause:** Base URL is incorrect or Jainam server is down

**Solution:**
- Verify `JAINAM_BASE_URL=http://smpb.jainam.in:4143/`
- Check if server is accessible: `curl http://smpb.jainam.in:4143/`

---

## CONCLUSION

✅ **You have everything you need to start testing!**

**Summary:**
- ❌ No request token needed
- ✅ Direct login with API key/secret
- ✅ Two separate tokens (interactive + market)
- ✅ Helper script provided
- ✅ Tokens valid for ~24 hours
- ✅ Can refresh anytime

**Next Action:** Run the helper script to obtain tokens and start live testing!

---

**Status:** ✅ GUIDE COMPLETE - READY TO OBTAIN TOKENS

