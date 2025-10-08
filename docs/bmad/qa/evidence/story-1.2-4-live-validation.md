# Story 1.2-4 — Jainam Live Integration Validation Evidence

**Run Date:** _pending (credentials unavailable in repo workspace)_  
**Operator:** _pending_  
**Environment:** Production Jainam API (requires interactive + market sessions)

## 1. Pre-checks

- Virtual environment activated? ☐
- `SQLAlchemy` import check passed? ☐
- Regression tests executed?
  - `python -m pytest broker/jainam_prop/test_position_holdings_unit.py -q` → _pending_
  - `python -m pytest broker/jainam_prop/test_trade_book.py -q` → _pending_

## 2. Credential Source

```
python -m scripts.jainam_keyring_helper export --format env
```

> **Note:** Do not paste secrets in this document. Confirm the command was run
> locally and the session environment held the expected variables.

## 3. Live API Runs

| Flow | Command | Started At (UTC) | Duration (s) | Status | Notes |
|------|---------|------------------|--------------|--------|-------|
| Positions | `python -m scripts.live_fetch_jainam --fetch positions` | _pending_ | _pending_ | _blocked_ | Workspace lacks production credentials; live run deferred to release team. |
| Holdings  | `python -m scripts.live_fetch_jainam --fetch holdings`  | _pending_ | _pending_ | _blocked_ | Same as above. |
| Trade Book | `python -m scripts.live_fetch_jainam --fetch tradebook` | _pending_ | _pending_ | _blocked_ | Same as above. |

## 4. Observations / Findings

- Holdings P&L alignment (expects non-zero delta): _pending_
- Token propagation through `map_portfolio_data`: _pending_
- Anomalies or API errors: _pending_

## 5. Sanitisation Checklist

- Sensitive IDs redacted from stored JSON? ☐
- Credentials omitted from logs and artifacts? ☐
- Evidence stored under `docs/bmad/qa/evidence/` only? ☐

## 6. Follow-up Actions

- Acquire production credentials via secure channel before rerunning live validation.
- Once executed, update this sheet with actual metrics and mark story change log accordingly.

