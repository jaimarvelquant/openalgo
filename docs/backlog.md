# Engineering Backlog

This backlog collects cross-cutting or future action items that emerge from reviews and planning.

Routing guidance:

- Use this file for non-urgent optimizations, refactors, or follow-ups that span multiple stories/epics.
- Must-fix items to ship a story belong in that story’s `Tasks / Subtasks`.
- Same-epic improvements may also be captured under the epic Tech Spec `Post-Review Follow-ups` section.

| Date | Story | Epic | Type | Severity | Owner | Status | Notes |
| ---- | ----- | ---- | ---- | -------- | ----- | ------ | ----- |
| 2025-10-12 | 1.4-1 | 1.4 | Bug | High | TBD | Open | Repair `cancel_order_api` to unpack `_parse_auth_token` results correctly and add regression coverage for the cancel flow. |
| 2025-10-12 | 1.4-1 | 1.4 | Bug | High | TBD | Open | Align `.env.example` and setup docs with the new `JAINAM_SYMPHONY_*` credentials (or restore compatibility) so `get_jainam_credentials` succeeds for default installs. |
| 2025-10-12 | 1.4-1 | 1.4 | Bug | Medium | TBD | Open | Restore `BaseAPIClient` support for custom base URL overrides and add regression coverage so staging/test endpoints remain configurable. |
