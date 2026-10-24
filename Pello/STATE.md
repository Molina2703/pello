# Persistent state

## Current state: Phase 3A verified

2026-10-24, America/Bogota. Branch codex/pello-phase3a, base 61f52e7.
Implementation checkpoint 30ed940. phase3a-quotes-first: COMPLETE,
VERIFIED THROUGH REAL CODEX SDK. Two dependent increments, one attempt each,
five gpt-6-luna/low turns: plan, execute/review T1, execute/review T2.
T1 pricing.py passed 6 tests; T2 quotes.py passed 6 plus the 6 T1 regression tests.
Two Git checkpoints; T2 consumes pricing.normalize_item unchanged. 69 automated
tests pass, including the original 43. Reopening added no operations/turns.
All baseline rows preserved, SQLite ok, original archive unchanged.
Evidence: evidence/phase3a/verified-live-pipeline/. Report: reports/PHASE3A.md;
machine summary: reports/phase3a-result.json. No external integration, rotation,
deployment or email claimed. Phase 3A stopped; next milestone requires a new
request: n8n DEV adapter with allowlist and operation reconciliation (PLAN.md).

## Historical state: Phase 2 verified

Verified on 2026-10-23, America/Bogota. Branch: `codex/pello-phase2`.
Pre-change checkpoint: `3a9b0fe`; earlier Phase 2 checkpoint: `0630125`.

- Project `phase2-leads-retained`, task `T1`: REAL SDK VERIFIED.
- Three real SDK turns: AI plan, separate executor development, AI review.
- Model: catalog-confirmed `gpt-6-luna`, low reasoning, existing ChatGPT login.
- Generated `leads.py`; all 12 owner-controlled acceptance tests passed.
- Supervisor decision: COMPLETE. Python independently enforced the success gate.
- Supervisor thread: `01a16c44-6047-7783-8696-388dd4198e63`.
- Executor thread: `01a16c44-820c-71c3-bd9c-54c7dfa3fa15`.
- Both role/session records and last successful turns are in `runtime/jobs.sqlite3`.
- 43 automated tests passed: 34 unit and 9 local integration, including originals.
- Completed project reopened from another CLI process without additional turns.
- Evidence: `evidence/phase2/verified-live-cycle/`; report: `reports/PHASE2.md`.
- Two earlier pre-inference blocked projects remain unchanged:
  `phase2-leads-first` and `phase2-leads-authorized`. Later attempts were explicitly
  authorized. No automatic retry or repair was executed.
- At that historical checkpoint there was no Phase 3 implementation, background
  service, deployment or remote push.

## Historical installation

Original ZIP is preserved in Downloads; hashes: `evidence/original-manifest.json`.
The isolated environment remains `.venv`; local configuration: `config/pello.json`.
Operational database backup before Phase 2: `evidence/phase2/jobs-before-phase2.sqlite3`.
Legacy jobs/events and original reports/tests were preserved. The original mock
job `clinica-reservas-demo-20261024040808-1a32bd` remains LISTO_PARA_REVISION.
Initial real SDK smoke remains in `evidence/first-sdk-smoke/`.

## Historical next task (superseded by the Phase 3A request)

Upon a new Phase 3 request, add configurable per-role session rotation and bounded
context reconstruction from the existing durable data, testing continuation
without duplicate execution of completed tasks. Full V1 is not complete.
