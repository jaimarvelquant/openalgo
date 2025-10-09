# Story 1.9: Add Jainam Prop to Broker Selection UI

**Epic:** Complete Jainam Prop Broker Integration for Production Readiness
**Story ID:** 1.9
**Story Type:** UI Enhancement
**Priority:** High
**Estimated Effort:** 2-3 hours (reduced from 1 day due to pattern reuse)
**Dependencies:** Story 1.10 (Authentication Callback - direct login, not OAuth)

## Status
**Ready for Implementation** (Backend authentication complete in Story 1.0-1)

## Code Reuse Summary

**Reuse Breakdown:**
- ✅ Broker dropdown: 95% reusable from other broker UI patterns
- ✅ JavaScript handler: 90% reusable from FivePaisaXTS (direct login pattern)
- ❌ OAuth routing: NOT APPLICABLE (Jainam uses direct login, not OAuth)

**Reference:**
- **Analysis:** `docs/bmad/research/jainam-code-reuse-analysis.md` Section 6
- **FivePaisaXTS UI:** Direct login pattern (90% reusable)
- **Story 1.10:** Authentication callback (direct login, not OAuth)

**Effort Reduction:** ~70% (from 8 hours to 2-3 hours)

**⚠️ CRITICAL:** Jainam uses **direct login**, NOT OAuth. No OAuth URL needed.

## Story
**As a** trader wanting to use Jainam Prop with OpenAlgo,
**I want** Jainam Prop to appear in the broker selection dropdown,
**so that** I can select and authenticate with my Jainam Prop account using direct login.

## Tasks / Subtasks

### Task 1: Add Broker Dropdown Option (15 minutes)
- [ ] Subtask 1.1: Add `<option value="jainam_prop">Jainam Prop</option>` to `templates/broker.html` (5 min)
- [ ] Subtask 1.2: Place alphabetically between "Groww" and "Ibulls" (2 min)
- [ ] Subtask 1.3: Add enable/disable logic based on `broker_name` variable (5 min)
- [ ] Subtask 1.4: Verify dropdown renders correctly in browser (3 min)

### Task 2: Add JavaScript Direct Login Handler (15 minutes)
- [ ] Subtask 2.1: Add `case 'jainam_prop':` to switch statement in `templates/broker.html` (5 min)
- [ ] Subtask 2.2: Set `loginUrl = '/jainam_prop/callback';` (following FivePaisaXTS pattern) (5 min)
- [ ] Subtask 2.3: Add `break;` statement (1 min)
- [ ] Subtask 2.4: Test JavaScript routing in browser console (4 min)

### Task 3: Add Backend Callback Handler (30 minutes)
- [ ] Subtask 3.1: Add `elif broker == 'jainam_prop':` case to `blueprints/brlogin.py` (10 min)
- [ ] Subtask 3.2: Call `auth_function()` to get tokens (follows FivePaisaXTS pattern) (5 min)
- [ ] Subtask 3.3: Extract `auth_token`, `feed_token`, `user_id`, `error_message` from response (5 min)
- [ ] Subtask 3.4: Set `forward_url = 'broker.html'` (2 min)
- [ ] Subtask 3.5: Test callback handler with mock authentication (8 min)

### Task 4: Add Database Token Storage (15 minutes)
- [ ] Subtask 4.1: Verify `auth_function` is registered in `app.broker_auth_functions` (5 min)
- [ ] Subtask 4.2: Confirm token storage uses existing `upsert_auth()` call (5 min)
- [ ] Subtask 4.3: Test end-to-end flow with database persistence (5 min)

### Task 5: Integration Testing (15 minutes)
- [ ] Subtask 5.1: Test broker selection dropdown displays Jainam Prop (3 min)
- [ ] Subtask 5.2: Test clicking "Connect Account" routes to callback (3 min)
- [ ] Subtask 5.3: Test authentication flow with valid credentials (5 min)
- [ ] Subtask 5.4: Test error handling with invalid credentials (4 min)

**Total Effort:** 1.5 hours (reduced from 2-3 hours due to backend completion)

## Dev Notes

### Code Reuse Guidance - UI Integration

**⚠️ CRITICAL: Jainam Uses Direct Login, NOT OAuth**

**Pattern to Follow:** FivePaisaXTS (direct login broker)
**Pattern to AVOID:** Zerodha/Upstox/Compositedge (OAuth brokers)

**UI Changes Needed (95% reusable):**

**1. Add to Broker Dropdown (10 minutes):**
```html
<!-- templates/broker.html -->
<option value="jainam_prop">Jainam Prop</option>
```

**2. Add JavaScript Handler (15 minutes):**
```javascript
// Follow FivePaisaXTS pattern (direct login)
case 'jainam_prop':
    // Direct login - no OAuth redirect
    window.location.href = '/broker_callback?broker=jainam_prop';
    break;
```

**3. Backend Already Complete (Story 1.10):**
```python
# blueprints/brlogin.py (already implemented in Story 1.10)
elif broker == 'jainam_prop':
    logger.debug(f'Jainam Prop broker - direct login')
    auth_token, feed_token, user_id, error_message = auth_function()
    forward_url = 'broker.html'
```

**Reuse Percentages:**
- Broker dropdown: 95% (just add one option)
- JavaScript handler: 90% (copy FivePaisaXTS pattern)
- Backend: 100% (already complete in Story 1.10)
- Overall: 95%

**Total Effort:** 2-3 hours (vs 8 hours for OAuth broker)

### Relevant Source Tree
- `templates/broker.html` – ⚠️ Add Jainam option to dropdown (line ~163) and JavaScript handler (line ~32)
- `blueprints/brlogin.py` – ⚠️ Add callback handler (after line ~136, following FivePaisaXTS pattern)
- `broker/jainam_prop/api/auth_api.py` – ✅ Backend authentication complete (Story 1.0-1)
- `database/auth_db.py` – ✅ Token persistence functions ready
- **Reference Pattern:** FivePaisaXTS (lines 130-136 in brlogin.py, lines 32-34 in broker.html)

### Technical Context
- **⚠️ CRITICAL CORRECTION:** Jainam uses **DIRECT LOGIN**, NOT OAuth
- **Authentication Method:** Direct API key/secret authentication (like FivePaisaXTS)
- **Pattern to Follow:** FivePaisaXTS (direct login)
- **Pattern to AVOID:** Compositedge/Zerodha (OAuth-based)
- **Dropdown value:** `'jainam_prop'`
- **Display text:** `'Jainam Prop'`
- **Callback URL:** `/jainam_prop/callback`
- **Backend Function:** `authenticate_direct()` returns `(auth_token, feed_token, user_id, error_message)`
- **No OAuth URL needed** - Direct callback to backend

### Testing Standards
- Browser compatibility testing (Chrome, Firefox, Safari)
- Direct login callback verification (NOT OAuth redirect)
- Dropdown rendering validation
- JavaScript error checking
- End-to-end authentication flow testing

## Testing
### Test Scenarios
- Dropdown displays Jainam Prop option when configured
- JavaScript routes to correct OAuth URL
- OAuth page loads successfully
- Callback handling works properly
- Error cases handled gracefully

## Change Log
| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-06 | 1.0 | Initial story creation | AI Assistant |
| 2025-10-09 | 2.0 | Major corrections: Changed from OAuth to direct login pattern | Augment Agent |
| 2025-10-09 | 2.1 | Updated with backend completion status from Story 1.0-1 | Augment Agent |
| 2025-10-09 | 2.2 | Added detailed implementation guidance and corrected acceptance criteria | Augment Agent |

## Dev Agent Record
### Agent Model Used
- **Story Analysis:** Claude Sonnet 4.5 (Augment Agent)
- **Implementation:** Pending

### Debug Log References
- Backend authentication tests: `broker/jainam_prop/test_auth.py`
- Reference implementation: `broker/fivepaisaxts/api/auth_api.py`
- Reference UI pattern: `templates/broker.html` (FivePaisaXTS lines 32-34, 163)
- Reference callback: `blueprints/brlogin.py` (FivePaisaXTS lines 130-136)

### Completion Notes List

#### Backend Prerequisites (Story 1.0-1) ✅ COMPLETE
- ✅ `authenticate_direct()` implemented in `broker/jainam_prop/api/auth_api.py`
- ✅ Returns `(auth_token, feed_token, user_id, error_message)` tuple
- ✅ Database integration ready via `database/auth_db.py`
- ✅ Unit tests passing
- ✅ Helper script available for testing

#### UI Implementation ⚠️ PENDING
- [ ] Dropdown option not yet added to `templates/broker.html`
- [ ] JavaScript handler not yet added
- [ ] Backend callback not yet added to `blueprints/brlogin.py`
- [ ] End-to-end web login flow not yet tested

#### Critical Corrections Made
1. **OAuth → Direct Login:** Original story incorrectly specified OAuth pattern
   - Corrected to follow FivePaisaXTS direct login pattern
   - Removed OAuth URL configuration (not applicable)
   - Updated all acceptance criteria to reflect direct login

2. **Dependency Clarification:** Story 1.9 depends on Story 1.0-1 backend
   - Backend authentication complete
   - UI integration is the remaining work

3. **Pattern Reference:** Changed from Compositedge to FivePaisaXTS
   - Compositedge uses OAuth (wrong pattern)
   - FivePaisaXTS uses direct login (correct pattern)

### File List

#### Files to Modify:
1. **`templates/broker.html`** (2 changes)
   - Add dropdown option (line ~163)
   - Add JavaScript case handler (line ~32)

2. **`blueprints/brlogin.py`** (1 change)
   - Add callback handler (after line ~136)

#### Files Already Complete (Story 1.0-1):
1. **`broker/jainam_prop/api/auth_api.py`** - Authentication backend
2. **`database/auth_db.py`** - Token persistence
3. **`broker/jainam_prop/get_jainam_tokens.py`** - Testing helper

## QA Results

### Pre-Implementation Validation ✅ PASSED
- Backend authentication verified working (Story 1.0-1)
- Database schema supports dual-token storage
- FivePaisaXTS pattern confirmed as correct reference
- Implementation plan validated against codebase

### Implementation Testing ⚠️ PENDING
- Dropdown rendering: Not yet tested
- JavaScript routing: Not yet tested
- Backend callback: Not yet tested
- End-to-end flow: Not yet tested
- Browser compatibility: Not yet tested

### Blockers Resolved
- ✅ Backend authentication complete (was blocking UI work)
- ✅ Correct pattern identified (FivePaisaXTS, not OAuth)
- ✅ Implementation locations identified
- ✅ Code examples provided

### Ready for Implementation
- All prerequisites met
- Clear implementation guidance provided
- Reference code identified
- Estimated effort: 1.5 hours

---

## Acceptance Criteria

### AC1: Add Broker Option to Dropdown
Add Jainam Prop option to broker dropdown in `templates/broker.html` with value `jainam_prop` and display text "Jainam Prop"

**Implementation Details:**
- Add `<option value="jainam_prop">Jainam Prop</option>` to broker dropdown
- Place alphabetically in dropdown list
- Ensure option is visible and selectable

**Verification:**
- [ ] Jainam Prop appears in broker dropdown
- [ ] Option value is exactly `jainam_prop` (lowercase with underscore)
- [ ] Display text is "Jainam Prop" (proper capitalization)

---

### AC2: Add Direct Login Routing (CORRECTED)
Add switch case in JavaScript form submission handler to route Jainam Prop authentication to direct login callback

**⚠️ CORRECTION:** Jainam uses direct login, NOT OAuth

**Implementation Details:**
- Add case statement in broker selection form handler
- Route to `/jainam_prop/callback` (direct callback, not OAuth URL)
- Follow FivePaisaXTS pattern (NOT Compositedge/Zerodha OAuth pattern)

**Verification:**
- [ ] JavaScript switch statement includes `case 'jainam_prop':`
- [ ] Form submission routes to `/jainam_prop/callback`
- [ ] No JavaScript errors in browser console

---

### AC3: Add Backend Callback Handler (NEW)
Add callback handler in `blueprints/brlogin.py` to process Jainam authentication

**Implementation Details:**
- Add `elif broker == 'jainam_prop':` case after FivePaisaXTS handler (line ~136)
- Call `auth_function()` which maps to `authenticate_direct()` from Story 1.0-1
- Extract `auth_token`, `feed_token`, `user_id`, `error_message` from response
- Set `forward_url = 'broker.html'`
- Follow exact pattern from FivePaisaXTS (lines 130-136)

**Verification:**
- [ ] Callback handler added to `blueprints/brlogin.py`
- [ ] Handler calls correct authentication function
- [ ] Tokens extracted and stored correctly
- [ ] Error handling follows existing pattern

---

### AC4: Enable/Disable Based on Configuration
Ensure Jainam Prop option is enabled/disabled based on broker configuration (follows same pattern as other brokers)

**Implementation Details:**
- Check if Jainam Prop credentials are configured
- Disable option if credentials missing
- Show appropriate message if disabled
- Follow same pattern as other brokers

**Verification:**
- [ ] Option is enabled when credentials configured
- [ ] Option is disabled when credentials missing
- [ ] Disabled state is visually indicated
- [ ] Tooltip or message explains why disabled (if applicable)

---

### AC5: Verify Dropdown Display
Verify dropdown displays "Jainam Prop" and is selectable when broker is configured

**Implementation Details:**
- Test dropdown rendering in multiple browsers
- Verify text is readable and properly formatted
- Ensure option is clickable/selectable

**Verification:**
- [ ] Dropdown displays correctly in Chrome
- [ ] Dropdown displays correctly in Firefox
- [ ] Dropdown displays correctly in Safari
- [ ] Option is selectable with mouse and keyboard

---

### AC6: Test Direct Login Flow (CORRECTED)
Test that clicking "Connect Account" button with Jainam Prop selected triggers direct login callback

**⚠️ CORRECTION:** Test direct login flow, NOT OAuth redirect

**Implementation Details:**
- Select Jainam Prop from dropdown
- Click "Connect Account" button
- Verify redirect to `/jainam_prop/callback`
- Verify backend authentication is triggered
- Verify tokens are stored in database

**Verification:**
- [ ] Button click triggers redirect to callback
- [ ] Redirect goes to `/jainam_prop/callback` (NOT external OAuth URL)
- [ ] Backend `authenticate_direct()` function is called
- [ ] Tokens are successfully stored in database
- [ ] User is redirected to dashboard on success

---

## Integration Verification

### IV1: Verify Other Brokers Continue to Work
Verify other broker options continue to work correctly after adding Jainam Prop

**Test Steps:**
1. Select each existing broker from dropdown
2. Click "Connect Account" for each
3. Verify redirect to correct OAuth URL
4. Verify no JavaScript errors

**Expected Results:**
- All existing brokers still work
- No regression in broker selection functionality
- No JavaScript errors in console

---

### IV2: Test Jainam Prop Selection
Test Jainam Prop selection displays correctly in dropdown and routes to correct URL

**Test Steps:**
1. Open broker selection page
2. Click broker dropdown
3. Verify Jainam Prop appears in list
4. Select Jainam Prop
5. Click "Connect Account"
6. Verify redirect to Jainam OAuth URL

**Expected Results:**
- Jainam Prop appears in dropdown
- Selection works correctly
- Redirect goes to correct URL
- OAuth page loads

---

### IV3: Verify Direct Login Authentication (CORRECTED)
Verify direct login authentication flow works end-to-end

**⚠️ CORRECTION:** Test direct login, NOT OAuth URL parameters

**Test Steps:**
1. Select Jainam Prop and click "Connect Account"
2. Verify redirect to `/jainam_prop/callback`
3. Verify backend calls `authenticate_direct()`
4. Verify tokens are stored in database
5. Verify user is redirected to dashboard

**Expected Results:**
- Callback handler is triggered
- `authenticate_direct()` is called with environment credentials
- Interactive and market data tokens are generated
- Tokens are stored in `auth` table with `broker='jainam_prop'`
- User session is established
- User is redirected to dashboard

---

## Technical Notes

### Pattern Reference
Follow Compositedge implementation in `templates/broker.html` (lines 38-40)

**Compositedge Example:**
```html
<option value="compositedge">Compositedge</option>
```

**JavaScript Example:**
```javascript
case 'compositedge':
    loginUrl = 'https://xts.compositedge.com/interactive/thirdparty?appKey=' + apiKey + '&returnURL=' + redirectUrl;
    break;
```

### Direct Login Implementation (CORRECTED)

**⚠️ CRITICAL:** Jainam does NOT use OAuth. Follow direct login pattern.

**Step 1: Add to Dropdown (`templates/broker.html` line ~163)**
```html
<option value="jainam_prop" {{ 'disabled' if broker_name != 'jainam_prop' }}>Jainam Prop {{ '(Disabled)' if broker_name != 'jainam_prop' }}</option>
```

**Step 2: Add JavaScript Handler (`templates/broker.html` line ~32)**
```javascript
case 'jainam_prop':
    loginUrl = '/jainam_prop/callback';
    break;
```

**Step 3: Add Backend Callback (`blueprints/brlogin.py` after line ~136)**
```python
elif broker == 'jainam_prop':
    code = 'jainam_prop'
    logger.debug(f'Jainam Prop broker - code: {code}')

    # Fetch auth token, feed token and user ID
    auth_token, feed_token, user_id, error_message = auth_function(code)
    forward_url = 'broker.html'
```

### Environment Variables Required
- **`JAINAM_INTERACTIVE_API_KEY`** - Interactive API key
- **`JAINAM_INTERACTIVE_API_SECRET`** - Interactive API secret
- **`JAINAM_MARKET_API_KEY`** - Market data API key
- **`JAINAM_MARKET_API_SECRET`** - Market data API secret
- **`REDIRECT_URL`** - Should include `/jainam_prop/callback`

### Browser Compatibility
Test in:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

---

## Definition of Done

- [ ] All acceptance criteria (AC1-AC6) met
- [ ] All integration verification (IV1-IV3) passed
- [ ] Code reviewed and approved
- [ ] No JavaScript errors in browser console
- [ ] Tested in multiple browsers
- [ ] Documentation updated (if needed)
- [ ] Changes committed to version control

---

## Related Stories

- **Story 1.2:** Security Hardening (provides API key for OAuth URL)
- **Story 1.10:** Authentication Callback Handler (handles OAuth callback)
- **Story 1.8:** Error Handling & Testing (validates UI integration)

---

## Notes

- This story focuses on UI changes only
- Backend authentication is handled in Story 1.10
- OAuth URL should be confirmed with Jainam documentation before implementation
- Consider adding Jainam logo/icon to dropdown (optional enhancement)

