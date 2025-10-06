# Story 1.10: Implement Authentication Callback Handler

**Epic:** Complete Jainam Prop Broker Integration for Production Readiness
**Story ID:** 1.10
**Story Type:** Backend Integration
**Priority:** High
**Estimated Effort:** 1 day
**Dependencies:** Story 1.2 (Security Hardening), Story 1.9 (Broker Selection UI)

## Status
Draft

## Story
**As a** trader authenticating with Jainam Prop,
**I want** the OAuth callback to be handled correctly,
**so that** I can successfully log in and use OpenAlgo with my Jainam Prop account.

## Tasks / Subtasks
- [ ] Add elif case for 'jainam_prop' in blueprints/brlogin.py broker_callback function
- [ ] Extract request_token from OAuth callback parameters
- [ ] Call authenticate_broker() from jainam_prop.api.auth_api
- [ ] Handle successful authentication and store access_token
- [ ] Handle authentication errors with appropriate user feedback
- [ ] Add comprehensive logging for debugging
- [ ] Test end-to-end OAuth flow

## Dev Notes
### Relevant Source Tree
- Backend: blueprints/brlogin.py - broker_callback function
- Broker: broker/jainam_prop/api/auth_api.py - authenticate_broker function
- Database: token storage and user association

### Technical Context
- Follow Compositedge pattern for XTS OAuth callback handling
- Request token parameter: request.args.get('request_token')
- Authentication function: authenticate_broker(request_token)
- Success handler: handle_auth_success(access_token, session['user'], broker)
- Error handler: handle_auth_failure(error_message, forward_url='broker.html')

### Security Considerations
- Validate request_token format before processing
- Never log sensitive tokens in application logs
- Use HTTPS for all OAuth redirects
- Sanitize error messages before displaying to users

### Testing Standards
- Unit tests for callback handler
- Integration tests with mock Jainam API
- End-to-end OAuth flow testing
- Error scenario testing (invalid tokens, network failures)

## Testing
### Test Scenarios
- Successful OAuth callback with valid request_token
- Invalid request_token handling
- Authentication API failures
- Network connectivity issues
- Session management across OAuth flow
- Error message sanitization

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
- Modified: blueprints/brlogin.py
- Verified: broker/jainam_prop/api/auth_api.py

## QA Results
- N/A (not yet implemented)

---

## Acceptance Criteria

### AC1: Add Broker Case to Callback Handler
Add `elif broker == 'jainam_prop':` case to `blueprints/brlogin.py` broker_callback function

**Implementation Details:**
- Add case statement in `broker_callback()` function
- Place after existing broker cases
- Follow same pattern as Compositedge/Definedge

**Verification:**
- [ ] Case statement added to `broker_callback()` function
- [ ] Condition checks for `broker == 'jainam_prop'`
- [ ] Code follows existing pattern

---

### AC2: Extract Request Token
Extract `request_token` from OAuth callback query parameters (similar to Compositedge pattern)

**Implementation Details:**
- Use `request.args.get('request_token')` or similar
- Handle missing request_token gracefully
- Log request_token extraction for debugging

**Verification:**
- [ ] Request token extracted from query parameters
- [ ] Missing token handled with error message
- [ ] Token extraction logged at DEBUG level

---

### AC3: Exchange Token for Access Token
Call `authenticate_broker(request_token)` from `broker.jainam_prop.api.auth_api` to exchange request_token for access_token

**Implementation Details:**
- Import `authenticate_broker` from `broker.jainam_prop.api.auth_api`
- Call function with extracted request_token
- Handle authentication response
- Log authentication attempt

**Verification:**
- [ ] `authenticate_broker()` function imported correctly
- [ ] Function called with request_token parameter
- [ ] Response captured and processed
- [ ] Authentication attempt logged

---

### AC4: Handle Successful Authentication
Handle authentication response: if successful, store access_token via `handle_auth_success(auth_token, session['user'], broker)`

**Implementation Details:**
- Check authentication response for success
- Extract access_token from response
- Call `handle_auth_success()` with token, user, and broker
- Redirect user to dashboard or broker page

**Verification:**
- [ ] Success response detected correctly
- [ ] Access token extracted from response
- [ ] `handle_auth_success()` called with correct parameters
- [ ] User redirected to appropriate page

---

### AC5: Handle Authentication Errors
Handle authentication errors: if failed, return error message via `handle_auth_failure(error_message, forward_url='broker.html')`

**Implementation Details:**
- Catch authentication exceptions
- Extract error message from exception
- Call `handle_auth_failure()` with error and forward URL
- Log error for debugging

**Verification:**
- [ ] Authentication errors caught with try-except
- [ ] Error message extracted and sanitized
- [ ] `handle_auth_failure()` called with error message
- [ ] Error logged at ERROR level

---

### AC6: Set Forward URL
Set `forward_url = 'broker.html'` for redirect after authentication

**Implementation Details:**
- Set forward_url variable to 'broker.html'
- Use in both success and failure cases
- Ensure consistent redirect behavior

**Verification:**
- [ ] `forward_url` variable set to 'broker.html'
- [ ] Used in success redirect
- [ ] Used in failure redirect

---

### AC7: Log Authentication Events
Log authentication attempts and results for debugging

**Implementation Details:**
- Log authentication start (INFO level)
- Log request_token extraction (DEBUG level)
- Log authentication success (INFO level)
- Log authentication failure (ERROR level)
- Include broker name and user in logs

**Verification:**
- [ ] Authentication start logged
- [ ] Token extraction logged
- [ ] Success logged with user and broker
- [ ] Failure logged with error details
- [ ] No sensitive data (tokens, passwords) in logs

---

## Integration Verification

### IV1: Verify Existing Brokers Continue to Work
Verify existing broker authentication flows continue to work

**Test Steps:**
1. Test authentication with Zerodha
2. Test authentication with Angel
3. Test authentication with Compositedge
4. Verify no regression in existing flows

**Expected Results:**
- All existing brokers authenticate successfully
- No errors in authentication flow
- No impact on existing functionality

---

### IV2: Test Jainam Prop OAuth Callback
Test Jainam Prop OAuth callback successfully exchanges request_token for access_token

**Test Steps:**
1. Select Jainam Prop and click "Connect Account"
2. Complete OAuth flow on Jainam page
3. Verify callback to OpenAlgo
4. Verify request_token extracted
5. Verify access_token obtained
6. Verify user redirected to dashboard

**Expected Results:**
- OAuth callback received
- Request token extracted successfully
- Access token obtained from Jainam API
- User authenticated and redirected

---

### IV3: Verify Token Storage
Verify access_token is stored in database and user is redirected to dashboard

**Test Steps:**
1. Complete Jainam Prop authentication
2. Check database for stored access_token
3. Verify token is associated with correct user
4. Verify token is associated with correct broker
5. Verify user can make API calls with stored token

**Expected Results:**
- Access token stored in database
- Token associated with correct user
- Token associated with 'jainam_prop' broker
- Token works for API calls

---

## Technical Notes

### Pattern Reference
Follow Compositedge implementation in `blueprints/brlogin.py` (lines 138-210)

**Compositedge Example:**
```python
elif broker == 'compositedge':
    try:
        request_token = request.args.get('request_token')
        if not request_token:
            return handle_auth_failure("No request token received", forward_url='broker.html')

        # Authenticate with broker
        auth_response = authenticate_broker(request_token)

        if auth_response.get('status') == 'success':
            access_token = auth_response.get('token')
            return handle_auth_success(access_token, session['user'], broker)
        else:
            error_msg = auth_response.get('message', 'Authentication failed')
            return handle_auth_failure(error_msg, forward_url='broker.html')

    except Exception as e:
        logger.error(f"Compositedge authentication error: {e}")
        return handle_auth_failure(str(e), forward_url='broker.html')
```

### Request Token Parameter
Extract from `request.args.get('request_token')` or similar parameter name. Confirm actual parameter name with Jainam XTS documentation.

### Error Handling
Use try-except blocks to catch:
- Missing request_token
- Authentication API failures
- Network errors
- Invalid responses

### Session Management
Ensure user session is maintained through OAuth flow:
- Session should persist during redirect to Jainam
- Session should be available in callback
- User ID should be retrievable from session

### Security Considerations
- Validate request_token format before using
- Sanitize error messages before displaying to user
- Never log access_tokens or API secrets
- Use HTTPS for all OAuth redirects

---

## Definition of Done

- [ ] All acceptance criteria (AC1-AC7) met
- [ ] All integration verification (IV1-IV3) passed
- [ ] Code reviewed and approved
- [ ] Error handling comprehensive
- [ ] Logging implemented correctly
- [ ] No sensitive data in logs
- [ ] Tested with real Jainam OAuth flow
- [ ] Documentation updated (if needed)
- [ ] Changes committed to version control

---

## Related Stories

- **Story 1.2:** Security Hardening (provides credentials for authentication)
- **Story 1.9:** Broker Selection UI (triggers OAuth flow)
- **Story 1.1:** Database Integration (stores access_token)
- **Story 1.8:** Error Handling & Testing (validates authentication flow)

---

## Test Scenarios

### Happy Path
1. User selects Jainam Prop
2. User clicks "Connect Account"
3. User redirected to Jainam OAuth page
4. User enters credentials on Jainam page
5. User approves access
6. Callback received with request_token
7. Request token exchanged for access_token
8. Access token stored in database
9. User redirected to dashboard
10. User can place orders

### Error Scenarios
1. **Missing Request Token:** Callback without request_token → Error message displayed
2. **Invalid Request Token:** Invalid token → Authentication fails gracefully
3. **Network Error:** Jainam API unreachable → Error message with retry option
4. **Authentication Denied:** User denies access → Error message displayed
5. **Token Exchange Failure:** Exchange fails → Error logged and user notified

---

## Notes

- Confirm actual OAuth parameter names with Jainam documentation
- Test with real Jainam test account before production
- Consider adding retry logic for transient failures
- Monitor authentication success rate in production
