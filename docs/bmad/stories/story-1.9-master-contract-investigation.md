# Story 1.9 - Master Contract Download Investigation

**Date:** 2025-10-09  
**Status:** Under Investigation  
**Priority:** Medium (Non-blocking for Phase 1)

---

## Executive Summary

The master contract download functionality for Jainam Prop broker is failing with HTTP 404 errors across all 6 exchanges (NSECM, NSEFO, NSECD, BSECM, BSEFO, MCXFO). Investigation reveals potential server configuration mismatch between development/production environments.

**Current Status:**
- ✅ Basic broker functionality working (auth, orders, positions, funds)
- ❌ Master contract download failing with HTTP 404
- ⚠️ May not be critical for Phase 1 MVP

---

## Problem Statement

### Error Description
```
[2025-10-09 20:56:03,086] INFO in master_contract_db: Master contract API response status: 404
[2025-10-09 20:56:03,086] ERROR in master_contract_db: HTTP 404 error for NSECM: <html>
<head><title>404 Not Found</title></head>
<body>
<center><h1>404 Not Found</h1></center>
<hr><center>nginx</center>
</body>
</html>
```

### Endpoint Details
- **URL:** `https://smpb.jainam.in:4143/apimarketdata/instruments/master`
- **Method:** POST
- **Payload:** `{"exchangeSegmentList": ["NSECM"]}`
- **Headers:** `Authorization: {market_token}`, `Content-Type: application/json`
- **Response:** HTTP 404 with nginx error page

---

## Investigation Findings

### 1. Server Configuration Analysis

**Current Environment (OpenAlgo):**
- Base URL: `https://smpb.jainam.in:4143`
- Source: `.env` file `JAINAM_BASE_URL`
- Server: Jainam Production Server (Symphony B)

**Reference Implementation (XTS SDK):**
- Base URL (config.ini): `http://ctrade.jainam.in:3001/`
- Base URL (Example.py): `https://developers.symphonyfintech.in`
- Server: Symphony Development/Demo Server

**Key Finding:** Multiple different base URLs exist for Jainam XTS API:
1. `https://smpb.jainam.in:4143` (Current - Production)
2. `http://ctrade.jainam.in:3001/` (SDK config.ini)
3. `https://developers.symphonyfintech.in` (SDK examples)

### 2. Endpoint Path Verification

**Verified from XTS SDK (`Connect.py` line 123):**
```python
"market.instruments.master": "/apimarketdata/instruments/master"
```

**Verified from working implementation (`xts_connect.py` line 362):**
```python
"market.instruments.master": "/apimarketdata/instruments/master"
```

**Conclusion:** The endpoint path `/apimarketdata/instruments/master` is correct according to official SDK.

### 3. Request Format Analysis

**Task 16 Fix Applied:**
- Changed from `json=payload` to `content=json.dumps(payload)`
- Matches working implementation pattern
- Still returns HTTP 404

**Conclusion:** Request format is correct, issue is server-side.

### 4. Possible Root Causes

1. **Server Configuration Difference:**
   - Production server (`smpb.jainam.in:4143`) may not have master contract endpoint enabled
   - Development server (`developers.symphonyfintech.in`) has the endpoint
   - Different Jainam server instances may have different API capabilities

2. **API Version Mismatch:**
   - Production server may use older/newer API version
   - Endpoint may have been deprecated or moved

3. **Authentication/Authorization:**
   - Market data token may not have permissions for master contract download
   - Different API keys may have different endpoint access

4. **Network/Proxy Issues:**
   - nginx reverse proxy may be blocking the endpoint
   - Firewall rules may prevent access

---

## Fixes Implemented

### Task 13: JSON Parsing Error Handling (COMPLETE)
- Added HTTP status code validation
- Added Content-Type header validation
- Added JSON parsing error handling with try/except
- Added detailed logging for debugging

**File:** `broker/jainam_prop/database/master_contract_db.py` (lines 138-156)

### Task 16: Request Format Fix (COMPLETE - Did not resolve issue)
- Changed from `httpx.post(json=payload)` to `httpx.post(content=json.dumps(payload))`
- Matches working XTS Connect implementation pattern
- Added comprehensive documentation

**File:** `broker/jainam_prop/database/master_contract_db.py` (lines 122-138)

### Phase 2: Enhanced Logging (COMPLETE)
- Added detailed request logging (URL, headers, payload)
- Added detailed response logging (status, headers, body)
- Logs show exact request/response for debugging

**File:** `broker/jainam_prop/database/master_contract_db.py` (lines 142-181)

---

## BREAKTHROUGH: Binary Market Data API Discovery

### Evidence Found in Codebase

**Critical Finding:** The codebase already contains references to Binary Market Data API!

1. **`broker/jainam_prop/api/auth_api.py` (line 109):**
   ```python
   endpoints = [
       f"{base_url}/apimarketdata/auth/login",
       f"{base_url}/marketdata/auth/login",
       f"{base_url}/apibinarymarketdata/auth/login",  # ← Binary Market Data!
   ]
   ```

2. **`broker/ibulls/baseurl.py` (line 7):**
   ```python
   MARKET_DATA_URL = f"{BASE_URL}/apibinarymarketdata"  # ← iBulls uses Binary!
   ```

3. **`broker/jainam_prop/get_jainam_tokens.py` (line 165):**
   ```python
   candidate_paths = [
       "/apimarketdata/auth/login",
       "/marketdata/auth/login",
       "/apibinarymarketdata/auth/login",  # ← Binary Market Data!
   ]
   ```

### Hypothesis

**The master contract endpoint should use `/apibinarymarketdata/` instead of `/apimarketdata/`**

- **Current (failing):** `https://smpb.jainam.in:4143/apimarketdata/instruments/master` → HTTP 404
- **Proposed (likely correct):** `https://smpb.jainam.in:4143/apibinarymarketdata/instruments/master` → To be tested

### Fix Implemented (Task 18) ✅ VERIFIED WORKING

**File:** `broker/jainam_prop/database/master_contract_db.py`

**Changes:**
1. Added retry logic to try both endpoints:
   - Primary: `/apibinarymarketdata/instruments/master` (Binary Market Data API)
   - Fallback: `/apimarketdata/instruments/master` (Standard Market Data API)

2. Enhanced logging to show which endpoint succeeded

3. Graceful fallback if binary endpoint fails

**Result:** ✅ **SUCCESS!** Binary endpoint returns HTTP 200 with valid data.

**Verification:**
- NSEFO: Downloaded 85,367 instruments successfully
- BSEFO: Downloaded 4,964 instruments successfully
- NSECD: 0 instruments (empty, expected)
- MCXFO: 0 instruments (empty, expected)

---

## Additional Fixes Required (Task 19)

### Issue 1: DataFrame Column Mismatch ✅ FIXED

**Problem:** NSECM and BSECM failing with "23 columns passed, data had 22 columns"

**Root Cause:**
- Equity exchanges (NSECM, BSECM) have **22 columns**
- F&O exchanges (NSEFO, BSEFO, NSECD, MCXFO) have **23 columns**
- Code was using same 23-column structure for all exchanges

**Evidence:**
- NSECM sample: 22 pipe-delimited fields
- NSEFO sample: 23 pipe-delimited fields (includes expiry_date, strike_price, option_type)

**Fix Implemented:**
```python
if exchange in ['NSECM', 'BSECM']:
    # Equity exchanges: 22 columns
    columns = [22 equity-specific columns]
else:
    # F&O exchanges: 23 columns
    columns = [23 derivative-specific columns]
```

**Reference:** `broker/fivepaisaxts/database/master_contract_db.py` lines 86-87

---

### Issue 2: Missing Database Table ✅ FIXED

**Problem:** `sqlite3.OperationalError: no such table: symbol_token`

**Root Cause:**
- Code was using table name `symbol_token`
- Actual table name is `symtoken` (defined in `database/symbol.py` line 33)

**Fix Implemented:**
- Updated DELETE query: `DELETE FROM symtoken WHERE broker = :broker`
- Updated INSERT query: `INSERT INTO symtoken (...) VALUES (...)`
- Updated index creation: `CREATE INDEX ... ON symtoken (...)`

**Files Modified:**
- `broker/jainam_prop/database/master_contract_db.py` (lines 596-622)

---

## Next Steps

### Option 1: Test Binary Market Data API Fix (RECOMMENDED - IN PROGRESS)
**Action:** Escalate to Jainam technical support with specific questions:
1. Is `/apimarketdata/instruments/master` endpoint available on `smpb.jainam.in:4143`?
2. What is the correct base URL for production master contract downloads?
3. Are there different API endpoints for different server instances?
4. Do we need special permissions/API keys for master contract access?

**Timeline:** 2-5 business days for response

### Option 2: Make Master Contract Optional (WORKAROUND)
**Action:** Implement configuration flag to disable master contract download
1. Add `JAINAM_ENABLE_MASTER_CONTRACT_DOWNLOAD=false` to `.env`
2. Modify `master_contract_db.py` to skip download if disabled
3. Document limitation in user guide
4. Note: Symbol lookup functionality may be limited

**Timeline:** 1-2 hours implementation

### Option 3: Use Alternative Data Source (WORKAROUND)
**Action:** Download master contract from alternative source
1. Use static CSV files from Jainam website (if available)
2. Use NSE/BSE official master contract files
3. Implement manual upload functionality

**Timeline:** 4-8 hours implementation

---

## Impact Assessment

### Critical for Phase 1? **NO**

**Working Functionality:**
- ✅ Authentication (Interactive + Market Data)
- ✅ Order placement, modification, cancellation
- ✅ Order book retrieval
- ✅ Trade book retrieval
- ✅ Position book retrieval
- ✅ Holdings retrieval (with error handling)
- ✅ Funds/margin retrieval
- ✅ Logout

**Limited Functionality:**
- ⚠️ Master contract download (failing)
- ⚠️ Symbol-to-token lookup (depends on master contract)
- ⚠️ Token-based order placement (may need manual token entry)

**Recommendation:** Proceed to Checkpoint 1 Review with master contract documented as known limitation.

---

## Documentation References

1. **XTS SDK:** `/broker/jainam_prop/_sample_strategy/xts_PRO_SDK/`
2. **Working Implementation:** `/broker/jainam_prop/_sample_strategy/xts_connect.py`
3. **Config Example:** `/broker/jainam_prop/_sample_strategy/xts_PRO_SDK/config.ini`
4. **API Examples:** `/broker/jainam_prop/_sample_strategy/xts_PRO_SDK/Example.py`

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-10-09 | Implemented Task 16 fix (json.dumps) | Match working implementation pattern |
| 2025-10-09 | Added comprehensive logging | Debug exact request/response |
| 2025-10-09 | Pending: Contact Jainam support | Need official confirmation of endpoint availability |

---

## Appendix: Server URLs Comparison

| Server | Base URL | Port | Protocol | Purpose |
|--------|----------|------|----------|---------|
| Production (Current) | `smpb.jainam.in` | 4143 | HTTPS | Live trading |
| Development (SDK) | `ctrade.jainam.in` | 3001 | HTTP | Testing |
| Symphony Demo | `developers.symphonyfintech.in` | 443 | HTTPS | Demo/Examples |

**Question for Jainam:** Which server should be used for production master contract downloads?

