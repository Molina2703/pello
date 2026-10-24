# Persistent state

## Current state: Phase 2 verified

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
- No Phase 3 implementation, background service, deployment or remote push.

## Historical installation

Original ZIP is preserved in Downloads; hashes: `evidence/original-manifest.json`.
The isolated environment remains `.venv`; local configuration: `config/pello.json`.
Operational database backup before Phase 2: `evidence/phase2/jobs-before-phase2.sqlite3`.
Legacy jobs/events and original reports/tests were preserved. The original mock
job `clinica-reservas-demo-20261024040808-1a32bd` remains LISTO_PARA_REVISION.
Initial real SDK smoke remains in `evidence/first-sdk-smoke/`.

## Exact next task

Upon a new Phase 3 request, add configurable per-role session rotation and bounded
context reconstruction from the existing durable data, testing continuation
without duplicate execution of completed tasks. Full V1 is not complete.
