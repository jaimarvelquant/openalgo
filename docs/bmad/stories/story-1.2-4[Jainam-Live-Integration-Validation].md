# Story 1.2-4: Jainam Live Integration Validation

## Status
Approved

## Story

**As a** release readiness owner for the Jainam Prop integration,  
**I want** to validate positions, holdings, and trade book flows against the live Jainam API with production-grade credentials,  
**so that** we can confirm latency targets, market token propagation, and UI data accuracy before launch.

## Acceptance Criteria

1. **AC1**: Capture at least one live API run for positions, holdings, and trade book using operational credentials and record raw request/response timestamps.
2. **AC2**: Document observed end-to-end latency for each flow (API + transform + service) and confirm they meet IV targets (<5 s positions/holdings, <5 s trade book).
3. **AC3**: Verify live holdings data returns non-zero P&L by confirming market/feed token propagation through `services/holdings_service` → `map_portfolio_data`.
4. **AC4**: Update `docs/bmad/qa/evidence/` with captured telemetry and summary findings, including any deviations or mitigations.
5. **AC5**: Extend project setup documentation to include SQLAlchemy/venv requirements so tests and scripts run without ad-hoc steps.
6. **AC6**: Log validation outcomes in the story Dev Notes and change log, flagging any residual risks or follow-up items.

## Integration Verification

**IV1**: Verify the live validation does not regress existing automated tests (`pytest broker/jainam_prop/test_position_holdings_unit.py`, `test_trade_book.py`).  
**IV2**: Confirm UI endpoints (positions, holdings, trade book) display updated data immediately after live fetches.  
**IV3**: Ensure no sensitive credentials are persisted in logs or artifacts generated during validation.

## Tasks / Subtasks

- [ ] Task 1: Prepare live validation environment (AC: 1, 2, 3, 5)  
  - [ ] Subtask 1.1: Provision secure storage for Jainam interactive and market tokens (no plaintext in repo).  
  - [x] Subtask 1.2: Configure `.venv` with SQLAlchemy and document activation steps.  
  - [x] Subtask 1.3: Re-run baseline automated tests to confirm clean state.
- [ ] Task 2: Execute live API validation (AC: 1, 2, 3)  
  - [ ] Subtask 2.1: Run positions/holdings/trade book fetches capturing timestamps and payload samples.  
  - [ ] Subtask 2.2: Confirm holdings P&L reflects live LTP values; troubleshoot market token propagation if zero.  
  - [ ] Subtask 2.3: Aggregate latency metrics and compare to IV thresholds.
- [ ] Task 3: Publish evidence and documentation updates (AC: 4, 5, 6)  
  - [ ] Subtask 3.1: Store sanitized logs and timing data under `docs/bmad/qa/evidence/`.  
  - [x] Subtask 3.2: Update setup/deployment docs with venv + dependency instructions.  
  - [ ] Subtask 3.3: Record outcomes, risks, and next steps in this story’s Dev Notes and change log.

## Dev Notes

- **Relevant Source Tree:**  
  - `broker/jainam_prop/api/order_api.py` – Live API entry points (`get_positions`, `get_holdings`, `get_trade_book`).  
  - `broker/jainam_prop/mapping/order_data.py` – Portfolio/trade transformations and market token handling.  
  - `services/holdings_service.py`, `services/positionbook_service.py` – Auth payload propagation and service latency measurement hooks.  
  - `scripts/measure_jainam_portfolio_latency.py` – Use as reference for capturing live timings (adapt for real credentials).  
  - `docs/bmad/qa/evidence/` – Location for latency artifacts.
- **Integration Approach:** Run live calls via secured environment variables, capture timings with minimal instrumentation, and compare outputs against unit-test expectations.
- **Existing Pattern Reference:** Mirror benchmarking/validation approach from `story-1.2-1` QA evidence; follow logging/error patterns already in `order_api.py`.
- **Key Constraints:**  
  - Credentials must remain outside version control (use env vars / secrets manager).  
  - Avoid persisting raw payloads containing sensitive data; redact before archiving.  
  - Validation should not exceed rate limits or disrupt production clients.

## Testing

- Manual live validation scripts for positions, holdings, trade book (with timestamps).  
- Automated regression: `python -m pytest broker/jainam_prop/test_position_holdings_unit.py -q` and `python -m pytest broker/jainam_prop/test_trade_book.py -q`.  
- Optional sanity: rerun `scripts/measure_jainam_portfolio_latency.py` with live data if safe.

## Change Log

| Date | Version | Description | Author |
|------|---------|-------------|--------|
| 2025-10-07 | 0.1 | Initial draft: live integration validation story created | Sarah (PO) |
| 2025-10-08 | 0.2 | Added secure credential helper, live fetch harness, and documentation updates; live validation pending production credentials | James (dev) |

## Dev Agent Record

### Agent Model Used
GPT-5 Codex (2025-10-08)

### Debug Log References
- 2025-10-08: `.venv/bin/python -m pytest broker/jainam_prop/test_position_holdings_unit.py -q` (pass, 25 tests, SQLAlchemy deprecation warning)
- 2025-10-08: `.venv/bin/python -m pytest broker/jainam_prop/test_trade_book.py -q` (pass, 6 tests, SQLAlchemy deprecation warning)
- 2025-10-08: Created documentation scaffolding at `docs/bmad/qa/evidence/story-1.2-4-live-validation.md` noting credential blocker

### Completion Notes List
- Authored `scripts/jainam_keyring_helper.py` to capture Jainam interactive/market credentials via OS keyring so tokens never land in the repo.
- Implemented `scripts/live_fetch_jainam.py` CLI to pull positions, holdings, and trade book data while capturing latency metrics and redacting identifiers.
- Documented virtualenv + SQLAlchemy requirements in `INSTALL.md` and produced `docs/bmad/qa/live-validation-runbook.md` so release teams can repeat the validation flow.
- Added evidence template `docs/bmad/qa/evidence/story-1.2-4-live-validation.md` capturing current blocker (no production credentials in workspace).
- Live API validation remains blocked pending secure delivery of production tokens; no changes made to broker runtime behaviour.

### File List
- INSTALL.md (updated virtualenv / SQLAlchemy section)
- scripts/jainam_keyring_helper.py (new secure credential helper)
- scripts/live_fetch_jainam.py (new live validation harness)
- docs/bmad/qa/live-validation-runbook.md (new runbook)
- docs/bmad/qa/evidence/story-1.2-4-live-validation.md (new evidence template)
