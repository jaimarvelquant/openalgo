# Story 1.11: Create Deployment Strategy and Documentation

**Epic:** Complete Jainam Prop Broker Integration for Production Readiness
**Story ID:** 1.11
**Story Type:** Documentation & DevOps
**Priority:** High
**Estimated Effort:** 1 day
**Dependencies:** Stories 1.1-1.7, 1.9-1.10 (all implementation complete)

## Status
Draft

## Story
**As a** DevOps engineer or system administrator,
**I want** comprehensive deployment documentation for the Jainam Prop integration,
**so that** I can safely deploy and troubleshoot the integration in production.

## Tasks / Subtasks
- [ ] Create docs/bmad/deployment-guide.md with deployment instructions
- [ ] Document all required environment variables with descriptions
- [ ] Document step-by-step deployment procedure
- [ ] Document rollback procedure for issue recovery
- [ ] Document troubleshooting guide for common issues
- [ ] Document monitoring and alerting recommendations
- [ ] Document CI/CD integration requirements
- [ ] Test deployment guide in development environment

## Dev Notes
### Relevant Source Tree
- Configuration: .env file and environment variables
- Database: symbol_token table for master contract storage
- Documentation: docs/bmad/ directory structure
- Broker: broker/jainam_prop/ integration files

### Technical Context
- Environment variables: JAINAM_MARKET_API_KEY, JAINAM_MARKET_API_SECRET, JAINAM_INTERACTIVE_API_KEY, JAINAM_INTERACTIVE_API_SECRET
- Master contract: POST /api/v1/master_contract/jainam_prop
- API endpoints: positions, holdings, trade book, orders
- Database: symbol_token table with broker='jainam_prop'

### Security Considerations
- Never commit .env files to version control
- Use strong, unique API credentials
- Rotate credentials periodically
- Restrict file permissions on configuration files
- Use HTTPS for all API communications

### Testing Standards
- Documentation accuracy testing (step-by-step verification)
- Environment validation testing
- Rollback procedure testing
- Troubleshooting guide validation
- Monitoring configuration verification

## Testing
### Test Scenarios
- Deployment guide accuracy verification
- Rollback procedure validation
- Troubleshooting guide effectiveness testing
- Environment variable validation
- Master contract download testing
- API endpoint availability verification

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
- Created: docs/bmad/deployment-guide.md
- Modified: .env.example (if needed)

## QA Results
- N/A (not yet implemented)

---

## Acceptance Criteria

### AC1: Create Deployment Guide
Create `docs/bmad/deployment-guide.md` with comprehensive deployment instructions

**Implementation Details:**
- Create new markdown file at specified location
- Include table of contents
- Use clear headings and formatting
- Include code examples where appropriate

**Verification:**
- [ ] File created at `docs/bmad/deployment-guide.md`
- [ ] Table of contents included
- [ ] All sections present and complete
- [ ] Markdown formatting correct

---

### AC2: Document Environment Variables
Document all required environment variables with descriptions and examples

**Required Variables:**
- `JAINAM_MARKET_API_KEY` - Market Data API key from Jainam
- `JAINAM_MARKET_API_SECRET` - Market Data API secret from Jainam
- `JAINAM_INTERACTIVE_API_KEY` - Interactive Order API key from Jainam
- `JAINAM_INTERACTIVE_API_SECRET` - Interactive Order API secret from Jainam

**Optional Variables:**
- `JAINAM_API_TIMEOUT` - API request timeout in seconds (default: 10)
- `JAINAM_RATE_LIMIT` - Maximum orders per second (default: 10)
- `JAINAM_RETRY_COUNT` - Number of retry attempts for failed requests (default: 3)

**Verification:**
- [ ] All 4 required variables documented
- [ ] All 3 optional variables documented
- [ ] Description provided for each variable
- [ ] Example values provided
- [ ] Security warnings included

---

### AC3: Document Deployment Steps
Document step-by-step deployment procedure

**Deployment Steps:**
1. **Update Environment Variables**
   - Add credentials to `.env` file
   - Verify all 4 required variables are set
   - Optionally configure timeout, rate limit, retry count

2. **Download Master Contract**
   - Via API: `POST /api/v1/master_contract/jainam_prop`
   - Via Admin UI: Navigate to Admin → Master Contract → Download
   - Verify download completes successfully
   - Check database for Jainam Prop symbols

3. **Restart Application**
   - Development: `python app.py`
   - Production (systemd): `sudo systemctl restart openalgo`
   - Production (supervisor): `sudo supervisorctl restart openalgo`
   - Production (Docker): `docker-compose restart openalgo`

4. **Verify Broker Availability**
   - Check broker list: `GET /api/v1/brokers`
   - Verify `jainam_prop` appears in response
   - Check UI: Jainam Prop appears in broker dropdown
   - Test authentication flow

**Verification:**
- [ ] All 4 deployment steps documented
- [ ] Commands provided for each step
- [ ] Multiple deployment methods covered
- [ ] Verification steps included

---

### AC4: Document Rollback Procedure
Document how to rollback deployment if issues occur

**Rollback Steps:**
1. **Disable Jainam Prop Broker**
   - Remove from broker list configuration
   - Or set `JAINAM_ENABLED=false` in environment

2. **Revert Database Changes**
   - Delete Jainam records: `DELETE FROM symbol_token WHERE broker='jainam_prop'`
   - Or restore database backup

3. **Restore Previous Application Version**
   - Git: `git checkout <previous-commit>`
   - Docker: `docker-compose down && docker-compose up -d`
   - Systemd: Restore previous binary/code

4. **Verify Rollback**
   - Check broker list no longer includes Jainam Prop
   - Verify existing brokers still work
   - Check logs for errors

**Verification:**
- [ ] All 4 rollback steps documented
- [ ] Commands provided for each step
- [ ] Multiple rollback methods covered
- [ ] Verification steps included

---

### AC5: Document Troubleshooting Guide
Document common issues and solutions

**Common Issues:**

1. **Authentication Errors**
   - Symptom: "Invalid credentials" or "Authentication failed"
   - Cause: Incorrect API keys or secrets
   - Solution: Verify credentials in `.env` file, check Jainam dashboard

2. **Symbol Lookup Failures**
   - Symptom: "Token not found for symbol"
   - Cause: Master contract not downloaded or outdated
   - Solution: Download master contract, verify database records

3. **API Rate Limiting**
   - Symptom: "Rate limit exceeded" errors
   - Cause: Too many orders placed too quickly
   - Solution: Reduce order frequency, increase `JAINAM_RATE_LIMIT`

4. **Network Connectivity Problems**
   - Symptom: "Connection timeout" or "Network error"
   - Cause: Firewall blocking Jainam API, network issues
   - Solution: Check firewall rules, verify Jainam API is reachable

**Verification:**
- [ ] At least 4 common issues documented
- [ ] Symptoms described for each issue
- [ ] Root causes identified
- [ ] Solutions provided with commands/steps

---

### AC6: Document Monitoring and Alerting
Document key metrics to monitor and alerting recommendations

**Key Metrics:**
- **API Response Time:** Track average response time for Jainam API calls
- **Error Rate:** Track percentage of failed API calls
- **Order Success Rate:** Track percentage of successful order placements
- **Authentication Failures:** Track failed authentication attempts
- **Token Lookup Failures:** Track symbol-to-token lookup failures

**Log Locations:**
- Application logs: `/var/log/openalgo/app.log` (or configured location)
- Error logs: `/var/log/openalgo/error.log`
- Access logs: `/var/log/openalgo/access.log`

**Recommended Alerting Thresholds:**
- Error rate > 5%: Warning
- Error rate > 10%: Critical
- API response time > 5 seconds: Warning
- API response time > 10 seconds: Critical
- Authentication failures > 3 in 5 minutes: Warning

**Verification:**
- [ ] At least 5 key metrics documented
- [ ] Log locations specified
- [ ] Alerting thresholds recommended
- [ ] Monitoring tools mentioned (if applicable)

---

### AC7: Document CI/CD Integration
Document automated testing and deployment pipeline requirements (if applicable)

**CI/CD Requirements:**

1. **Automated Testing**
   - Unit tests for all new functions
   - Integration tests with mock Jainam API
   - End-to-end tests with test account

2. **Quality Gates**
   - All tests must pass
   - Code coverage > 80%
   - No critical security vulnerabilities
   - No linting errors

3. **Deployment Pipeline**
   - Build application
   - Run automated tests
   - Deploy to staging environment
   - Run smoke tests
   - Deploy to production (manual approval)

**Verification:**
- [ ] Automated testing requirements documented
- [ ] Quality gates specified
- [ ] Deployment pipeline steps outlined
- [ ] Manual approval points identified

---

## Integration Verification

### IV1: Verify Deployment Guide Accuracy
Verify deployment guide is complete and accurate by following it in test environment

**Test Steps:**
1. Set up clean test environment
2. Follow deployment guide step-by-step
3. Verify each step works as documented
4. Note any missing steps or unclear instructions
5. Update guide based on findings

**Expected Results:**
- All steps work as documented
- No missing steps
- Instructions are clear and unambiguous
- Deployment completes successfully

---

### IV2: Test Rollback Procedure
Test rollback procedure works as documented

**Test Steps:**
1. Deploy Jainam Prop integration
2. Verify integration works
3. Follow rollback procedure step-by-step
4. Verify rollback completes successfully
5. Verify existing brokers still work

**Expected Results:**
- Rollback procedure works as documented
- Jainam Prop broker disabled
- Database changes reverted
- Existing brokers unaffected
- No errors in logs

---

### IV3: Verify Troubleshooting Guide
Verify troubleshooting guide addresses common issues encountered during testing

**Test Steps:**
1. Intentionally create each documented issue
2. Follow troubleshooting steps
3. Verify issue is resolved
4. Note any additional issues encountered
5. Update guide with new issues

**Expected Results:**
- All documented issues can be reproduced
- Troubleshooting steps resolve issues
- Guide is comprehensive
- Additional issues documented (if found)

---

## Technical Notes

### Deployment Methods
Document multiple deployment methods:
- **Development:** `python app.py` (Flask development server)
- **Production (systemd):** `sudo systemctl restart openalgo`
- **Production (supervisor):** `sudo supervisorctl restart openalgo`
- **Production (Docker):** `docker-compose restart openalgo`

### Master Contract Refresh
Explain when to refresh master contract:
- **Daily:** For active trading (recommended)
- **Weekly:** For less active trading
- **On-demand:** When symbol lookup failures occur
- **After market hours:** To avoid disrupting trading

### Security Best Practices
Emphasize security:
- Never commit `.env` file to version control
- Use strong, unique API keys
- Rotate credentials periodically
- Restrict file permissions on `.env` file (chmod 600)
- Use HTTPS for all API calls

### Testing Recommendations
Recommend testing approach:
- Test in sandbox/test environment first
- Use small order quantities initially
- Monitor logs closely during initial deployment
- Have rollback plan ready
- Test during off-market hours if possible

---

## Definition of Done

- [ ] All acceptance criteria (AC1-AC7) met
- [ ] All integration verification (IV1-IV3) passed
- [ ] Deployment guide created and complete
- [ ] Guide tested in real environment
- [ ] Rollback procedure tested
- [ ] Troubleshooting guide validated
- [ ] Documentation reviewed and approved
- [ ] Changes committed to version control

---

## Related Stories

- **All Stories 1.1-1.7, 1.9-1.10:** Deployment guide covers all implemented functionality
- **Story 1.8:** Error Handling & Testing (validates deployment procedures)

---

## Deliverables

1. **`docs/bmad/deployment-guide.md`** - Complete deployment documentation
2. **Updated `.env.example`** - Template with all Jainam variables
3. **Rollback script** (optional) - Automated rollback procedure
4. **Monitoring dashboard** (optional) - Grafana/Prometheus dashboard for metrics

---

## Notes

- Deployment guide should be living document, updated as issues are discovered
- Consider creating video walkthrough of deployment process
- Share guide with DevOps team for review before finalizing
- Include screenshots where helpful (broker dropdown, admin UI, etc.)
