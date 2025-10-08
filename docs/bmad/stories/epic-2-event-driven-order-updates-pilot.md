# Epic 2: Event-Driven Order Updates Pilot (Jainam + Zerodha)

**Epic Goal:**
Implement event-driven order updates for Jainam and Zerodha brokers using Vn.py's proven EventEngine architecture to provide real-time order status updates (<100ms latency) as a pilot program, with clear success criteria for data-driven go/no-go decision on expansion to additional brokers.

**Status:** Proposed (Pending Epic 1 Completion)

**Dependencies:**
- **HARD DEPENDENCY:** Epic 1 must be COMPLETE and STABLE
- REST API foundation required for fallback mechanism
- Jainam and Zerodha broker integrations must be production-ready

**Timeline Estimate:** 9 weeks total
- Development: 12 days (2.4 weeks)
- Evaluation: 30 days (6.6 weeks)
- Engineering Hours: 96 hours (12 days × 8 hours)

**Scope Boundaries:**
- ✅ **In Scope:** Jainam + Zerodha only (2 brokers)
- ✅ **In Scope:** EventEngine adaptation from Vn.py
- ✅ **In Scope:** WebSocket/postback integration
- ✅ **In Scope:** Monitoring and metrics infrastructure
- ✅ **In Scope:** Feature flags and rollback mechanism
- ❌ **Out of Scope:** Other brokers (expansion requires separate approval)
- ❌ **Out of Scope:** Removing REST API (maintained as fallback)
- ❌ **Out of Scope:** Market data WebSocket (already implemented)

---

## Strategic Context

### Why Event-Driven Architecture?

**Current Limitation:**
- Order status updates require manual refresh or polling
- Latency: 1-2 seconds for status updates
- No automated risk management possible
- Poor user experience for active traders

**Proposed Solution:**
- Real-time order updates via WebSocket/postback
- Latency: <100ms for status updates
- Enables automated stop-loss adjustments
- Enhanced UX with instant notifications

### Why Pilot Approach?

**Risk Mitigation:**
- Limited scope (2 brokers) reduces blast radius
- Proven code (Vn.py) reduces implementation risk
- Feature flags enable instant rollback
- Data-driven decision before expansion

**Learning Opportunity:**
- Validate latency improvements (claimed 10-100x)
- Measure user satisfaction impact
- Identify unforeseen issues
- Build team expertise in event-driven patterns

---

## Story Sequence Overview

**Phase 1: EventEngine Foundation (Story 2.1-2.2)** — 4 days, 32 hours
- Story 2.1: EventEngine Implementation (3 days)
- Story 2.2: BrokerAdapter Refactoring (1 day)

**Phase 2: Broker Integration (Story 2.3-2.4)** — 4.5 days, 36 hours
- Story 2.3: Jainam WebSocket Integration (2.5 days)
- Story 2.4: Zerodha Postback Integration (2 days)

**Phase 3: Infrastructure & Deployment (Story 2.5-2.7)** — 3.5 days, 28 hours
- Story 2.5: Monitoring Infrastructure (1.5 days)
- Story 2.6: Feature Flag & Rollback (1 day)
- Story 2.7: Evaluation & Documentation (1 day)

**Dependency Chain:**
```
2.1 (EventEngine) → 2.2 (BrokerAdapter) → 2.3, 2.4 (Broker Integration)
2.5 (Monitoring) → 2.6 (Feature Flags) → 2.7 (Documentation)
All stories → Evaluation Period (6.6 weeks)
```

---

## Success Criteria

### Primary Metrics (Must Achieve)

| Metric | Current Baseline | Target | Measurement Method |
|--------|------------------|--------|-------------------|
| **Order Status Latency** | 1-2 seconds | <500ms | Timestamp: order placed → UI update |
| **System Stability** | 99.9% uptime | >99.9% | WebSocket uptime, event queue health |
| **Error Rate** | <0.1% | <0.1% | Event processing errors, WebSocket failures |

### Secondary Metrics (Nice to Have)

| Metric | Current Baseline | Target | Measurement Method |
|--------|------------------|--------|-------------------|
| **API Call Reduction** | Baseline | -50% | Order status API calls per hour |
| **User Satisfaction** | Baseline | +20% | Survey: "How satisfied with order updates?" |
| **Feature Adoption** | N/A | >50% | % of Jainam/Zerodha users using real-time |

### Go/No-Go Decision Framework

**After 1 month of production evaluation:**

✅ **EXPAND to more brokers IF:**
- Latency <500ms achieved consistently
- Stability maintained (no degradation)
- User satisfaction improved (survey data)
- No critical bugs in 1 month
- Team comfortable with event-driven patterns

⚠️ **REFINE and re-evaluate IF:**
- Latency 500-1000ms (marginal improvement)
- User satisfaction +10% (modest improvement)
- Minor stability issues (occasional disconnections)
- Some bugs but manageable

❌ **ROLLBACK to REST only IF:**
- Latency >1000ms (no improvement)
- User satisfaction unchanged/negative
- Stability issues (frequent disconnections)
- Critical bugs or high maintenance burden

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **WebSocket disconnections** | Medium | High | Auto-reconnect with exponential backoff (from Vn.py) |
| **Event queue backlog** | Low | Medium | Monitor queue size, alert if >1000 events |
| **Broker API changes** | Low | High | Version API calls, graceful degradation |
| **Performance degradation** | Low | High | Feature flag for instant rollback |
| **User confusion** | Medium | Low | Clear UI indicator (real-time vs. manual) |

**Overall Risk Level:** MEDIUM (well-mitigated)

---

## Story Definitions

### Story 2.1: EventEngine Implementation

**As a** platform architect,
**I want** to adapt Vn.py's EventEngine for OpenAlgo,
**so that** we have a production-proven event processing system for order updates.

**Acceptance Criteria:**
1. EventEngine class adapted from Vn.py with thread-safe queue
2. EventType enum created with trading-specific events (ORDER_UPDATE, TRADE_UPDATE, etc.)
3. Timer events firing every 1 second for periodic tasks
4. Handler registration/unregistration working correctly
5. Integration with Flask-SocketIO for UI updates
6. Unit tests for thread safety and queue management
7. No memory leaks after 24-hour stress test

**Effort:** 3 days, 24 hours

---

### Story 2.2: BrokerAdapter Refactoring

**As a** broker integration developer,
**I want** to add event methods to BrokerAdapter base class,
**so that** brokers can emit order updates to the event engine.

**Acceptance Criteria:**
1. BrokerAdapter has `on_order()`, `on_trade()`, `on_position()` methods
2. Event methods are optional (backward compatible)
3. Events are properly formatted and emitted to EventEngine
4. Existing REST-based brokers continue working unchanged
5. Documentation updated with event-driven patterns
6. Unit tests for event emission

**Effort:** 1 day, 8 hours

---

### Story 2.3: Jainam WebSocket Integration

**As a** Jainam Prop user,
**I want** real-time order updates via WebSocket,
**so that** I see order status changes instantly without manual refresh.

**Acceptance Criteria:**
1. Jainam WebSocket API researched and documented
2. WebSocket client implemented with connection management
3. Order updates parsed and emitted as events
4. Automatic reconnection with exponential backoff
5. Fallback to REST polling if WebSocket fails
6. Integration tests with Jainam paper trading account
7. Latency <500ms measured end-to-end

**Effort:** 2.5 days, 20 hours

---

### Story 2.4: Zerodha Postback Integration

**As a** Zerodha user,
**I want** real-time order updates via postback/webhook,
**so that** I see order status changes instantly without manual refresh.

**Acceptance Criteria:**
1. Zerodha postback/webhook API researched and documented
2. Webhook endpoint implemented with signature verification
3. Order updates parsed and emitted as events
4. Fallback to REST polling if webhook fails
5. Integration tests with Zerodha paper trading account
6. Latency <500ms measured end-to-end

**Effort:** 2 days, 16 hours

---

### Story 2.5: Monitoring Infrastructure

**As a** platform operator,
**I want** comprehensive monitoring for the event engine,
**so that** I can detect and respond to issues proactively.

**Acceptance Criteria:**
1. Event queue size metrics collected
2. Event processing latency tracked
3. WebSocket connection health monitored
4. Alerts configured (queue >1000, latency >100ms, disconnected >10s)
5. Metrics dashboard created
6. Runbook for common issues documented

**Effort:** 1.5 days, 12 hours

---

### Story 2.6: Feature Flag & Rollback

**As a** platform operator,
**I want** feature flags and rollback mechanism,
**so that** I can disable event-driven updates instantly if issues arise.

**Acceptance Criteria:**
1. `USE_EVENT_DRIVEN_ORDERS` environment variable implemented
2. Gradual rollout mechanism (10% → 25% → 50% → 100%)
3. Instant rollback procedure documented
4. Feature flag tested (enable/disable without code deployment)
5. User opt-in/opt-out mechanism (optional)

**Effort:** 1 day, 8 hours

---

### Story 2.7: Evaluation & Documentation

**As a** product owner,
**I want** evaluation framework and documentation,
**so that** we can make data-driven decision on expansion.

**Acceptance Criteria:**
1. Success criteria clearly defined
2. Metrics collection automated
3. User survey created and deployed
4. Architecture documentation written
5. Deployment guide updated with Epic 2 configuration
6. Evaluation report template created

**Effort:** 1 day, 8 hours

---

## Evaluation Period (6.6 weeks)

**Week 1-2: Deployment & Stabilization**
- Deploy to 10% of Jainam/Zerodha users
- Monitor metrics closely
- Fix critical bugs
- Collect initial feedback

**Week 3-4: Gradual Rollout**
- Expand to 25% of users (if stable)
- Continue monitoring
- Refine based on feedback
- Document learnings

**Week 5-6: Full Rollout & Data Collection**
- Expand to 100% of users (if successful)
- Collect comprehensive metrics
- Survey users
- Prepare evaluation report

**Week 7: Evaluation & Decision**
- Review metrics vs. success criteria
- Analyze user feedback
- Team retrospective
- Go/No-Go decision

---

## Handoff Plan

**After Epic 2 Completion:**

**If EXPAND decision:**
- Hand off to PM for Epic 3 planning (additional brokers)
- Provide lessons learned and implementation playbook
- Recommend broker prioritization based on user demand

**If REFINE decision:**
- Hand off to Dev team for refinement work
- Provide specific improvement areas
- Re-evaluate after refinements

**If ROLLBACK decision:**
- Hand off to Ops team for rollback execution
- Document reasons for failure
- Recommend alternative approaches (polling + webhooks)

---

## Notes

**Code Reuse Strategy:**
- Vn.py EventEngine: https://github.com/vnpy/vnpy/blob/master/vnpy/event/engine.py
- Proven in production since 2015
- Battle-tested in high-frequency trading environments
- Reduces implementation risk significantly

**Broker API Documentation:**
- Jainam WebSocket: To be researched in Story 2.3
- Zerodha Postback: https://kite.trade/docs/connect/v3/postbacks/

**Reference Implementation:**
- Vn.py Gateway Pattern: https://github.com/vnpy/vnpy/tree/master/vnpy/gateway
- OpenAlgo WebSocket Proxy: `websocket_proxy/` (for market data)

---

**Epic Created:** 2025-10-08
**Epic Owner:** Sarah (PO Agent)
**Status:** Proposed (Pending Epic 1 Completion & User Approval)
**Approved By:** User (2025-10-08)

