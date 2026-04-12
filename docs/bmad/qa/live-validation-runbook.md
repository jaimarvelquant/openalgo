# Jainam Live Validation Runbook

This runbook documents the repeatable steps required to execute the Story 1.2‑4
live validation against the production Jainam API without leaking credentials.
Use it as the authoritative checklist before every release rehearsal.

## 1. Secure Credential Storage

- Install the Python `keyring` helper inside your project virtual environment:
  ```
  python -m pip install keyring
  ```
- Store the Jainam tokens in the operating system keychain (input is hidden):
  ```
  python -m scripts.jainam_keyring_helper store
  ```
  Fields left blank are skipped and can be added later with the same command.
- Load the credentials into the shell session when running validation scripts:
  ```
  eval "$(python -m scripts.jainam_keyring_helper export --format env)"
  ```
  The helper only emits environment exports; nothing is written to disk.

## 2. Virtual Environment Requirements

1. Create or reuse the project virtualenv documented in `INSTALL.md`:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m pip install SQLAlchemy
   ```
   (The explicit `SQLAlchemy` install guarantees ORM availability for the
   holdings/positions tests even if requirements installation skipped it.)
2. Double-check the ORM is importable:
   ```
   python -c "import sqlalchemy, flask_sqlalchemy"
   ```

## 3. Baseline Regression Tests

- Run the automated safety net before touching live systems:
  ```
  python -m pytest broker/jainam_prop/test_position_holdings_unit.py -q
  python -m pytest broker/jainam_prop/test_trade_book.py -q
  ```
- Capture the command output and attach it to the evidence sheet (Section 4).

## 4. Live Validation Evidence Checklist

Capture one run for each API with production credentials. Redact account IDs
before storing artifacts under `docs/bmad/qa/evidence/`.

| Flow | Command | Evidence to Save | Latency Target |
|------|---------|------------------|----------------|
| Positions | `python -m scripts.live_fetch_jainam --fetch positions` | Raw request/response timestamps (ISO8601), pretty JSON sample with PII masked | < 5 seconds |
| Holdings  | `python -m scripts.live_fetch_jainam --fetch holdings`  | Same as above + proof that P&L uses live LTP | < 5 seconds |
| Trade Book | `python -m scripts.live_fetch_jainam --fetch trades`   | Aggregated trade entries, exchange trade IDs masked | < 5 seconds |

> **Note:** `scripts/live_fetch_jainam.py` is a placeholder for the operational
> script used by the release team. If the executable name changes, update this
> table so that evidence capture stays in sync.

## 5. Data Sanitisation Rules

- Remove account numbers, order IDs, and client codes from all artifacts.
- Retain timestamps, latency measurements, and anonymised symbol data.
- Confirm no bearer tokens/headers are present before committing evidence.

## 6. Handoff Summary Template

When validation is complete, document findings in the story (`Dev Notes`,
`Change Log`) and summarise here for QA sign-off:

- ✅ Positions latency (avg/max):
- ✅ Holdings latency (avg/max):
- ✅ Trade book latency (avg/max):
- ✅ Holdings P&L reflects live LTP:
- ⚠️ Deviations / mitigation steps:
- 🛡 Sanitisation check performed by:

