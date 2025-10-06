# Story 1.9: Add Jainam Prop to Broker Selection UI

**Epic:** Complete Jainam Prop Broker Integration for Production Readiness
**Story ID:** 1.9
**Story Type:** UI Enhancement
**Priority:** High
**Estimated Effort:** 1 day
**Dependencies:** Story 1.2 (Security Hardening - needs API key for OAuth URL)

## Status
Draft

## Story
**As a** trader wanting to use Jainam Prop with OpenAlgo,
**I want** Jainam Prop to appear in the broker selection dropdown,
**so that** I can select and authenticate with my Jainam Prop account.

## Tasks / Subtasks
- [ ] Add Jainam Prop option to broker dropdown in templates/broker.html
- [ ] Add JavaScript case handler for Jainam Prop OAuth routing
- [ ] Configure XTS OAuth URL with proper parameters
- [ ] Implement enable/disable logic based on configuration
- [ ] Add verification for dropdown display and OAuth redirect

## Dev Notes
### Relevant Source Tree
- Frontend: templates/broker.html - broker selection dropdown
- JavaScript: Static JS files handling broker selection
- Backend: blueprints/brlogin.py - OAuth callback handling

### Technical Context
- Follow Compositedge pattern for XTS OAuth integration
- OAuth URL: https://xts.jainam.in/interactive/thirdparty?appKey={{broker_api_key}}&returnURL={{redirect_url}}
- Dropdown value: 'jainam_prop'
- Display text: 'Jainam Prop'

### Testing Standards
- Browser compatibility testing (Chrome, Firefox, Safari)
- OAuth redirect verification
- Dropdown rendering validation
- JavaScript error checking

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

## Dev Agent Record
### Agent Model Used
GPT-4

### Debug Log References
- N/A (pre-implementation)

### Completion Notes List
- N/A (not yet implemented)

### File List
- Modified: templates/broker.html
- Modified: static/js/broker-selection.js (if exists)

## QA Results
- N/A (not yet implemented)

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

### AC2: Add OAuth URL Routing
Add switch case in JavaScript form submission handler to route Jainam Prop authentication to appropriate OAuth URL

**Implementation Details:**
- Add case statement in broker selection form handler
- Route to Jainam XTS OAuth endpoint
- Follow same pattern as Compositedge and Definedge

**Verification:**
- [ ] JavaScript switch statement includes `case 'jainam_prop':`
- [ ] Form submission routes to correct OAuth URL
- [ ] No JavaScript errors in browser console

---

### AC3: Configure XTS OAuth URL
Follow XTS OAuth pattern similar to Compositedge: `loginUrl = 'https://xts.jainam.in/interactive/thirdparty?appKey={{broker_api_key}}&returnURL={{ redirect_url }}'`

**Implementation Details:**
- Use XTS OAuth URL format
- Include `appKey` parameter with Interactive API key
- Include `returnURL` parameter for callback
- Confirm actual URL with Jainam documentation

**Verification:**
- [ ] OAuth URL matches XTS pattern
- [ ] `appKey` parameter uses `{{broker_api_key}}` template variable
- [ ] `returnURL` parameter uses `{{ redirect_url }}` template variable
- [ ] URL is properly URL-encoded

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

### AC6: Test OAuth Redirect
Test that clicking "Connect Account" button with Jainam Prop selected redirects to correct OAuth URL

**Implementation Details:**
- Select Jainam Prop from dropdown
- Click "Connect Account" button
- Verify redirect to Jainam OAuth page
- Verify URL parameters are correct

**Verification:**
- [ ] Button click triggers redirect
- [ ] Redirect goes to Jainam OAuth URL
- [ ] URL includes correct `appKey` parameter
- [ ] URL includes correct `returnURL` parameter
- [ ] OAuth page loads successfully

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

### IV3: Verify OAuth URL Parameters
Verify OAuth URL includes correct API key and return URL parameters

**Test Steps:**
1. Select Jainam Prop and click "Connect Account"
2. Inspect redirect URL in browser
3. Verify `appKey` parameter is present and correct
4. Verify `returnURL` parameter is present and correct

**Expected Results:**
- URL includes `appKey` parameter
- `appKey` value matches configured Interactive API key
- URL includes `returnURL` parameter
- `returnURL` points to correct callback endpoint

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

### OAuth URL Format
Confirm actual Jainam XTS OAuth URL with Jainam documentation. The expected format is:
```
https://xts.jainam.in/interactive/thirdparty?appKey={API_KEY}&returnURL={CALLBACK_URL}
```

### Template Variables
- **`{{broker_api_key}}`** - Use for Interactive API key (not Market Data API key)
- **`{{ redirect_url }}`** - Use for OAuth callback URL

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

