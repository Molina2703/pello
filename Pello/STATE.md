# Persistent state

## Current Phase 2 state

- Branch: `codex/pello-phase2`; pre-change checkpoint: `3a9b0fe`.
- Implemented: AI role prompts, typed message bridge, additive SQLite tables,
  separate sessions, bounded context, independent verification, `supervised` CLI.
- Pre-migration database backup: `evidence/phase2/jobs-before-phase2.sqlite3`
  (local and ignored by Git).
- Only live cycle: `phase2-leads-first`; `BLOCKED` during session preparation.
  Zero model turns; no real plan, executor implementation, lead acceptance
  execution, or supervisor review was produced in Phase 2.
- Cause: quoted MCP override names created an invalid server entry. Fixed and
  regression-tested. The blocked cycle was not retried.
- Corrected diagnostic preparation: supervisor
  `01a16c33-4748-72c1-b37d-99643b131943` (`read-only`) and executor
  `01a16c33-56a7-7323-b480-46a54b7c220c` (`workspace-write`). Both ready, distinct
  IDs; these diagnostic sessions have no successful model turn.
- Configuration: catalog-confirmed `gpt-6-luna`, low reasoning; existing ChatGPT
  authentication. No API key introduced.
- Next action: authorize one new bounded real demonstration before Phase 3.
  See `reports/PHASE2.md`, `DECISIONS.md`, and `PLAN.md`.

## Installation state (preserved historical evidence)

Verified on 2026-10-23, America/Bogota (evidence timestamps use UTC).

- Project: this Pello source folder; isolated Python environment: `.venv`.
- Original ZIP preserved in `C:\Users\USUARIO\Downloads`; archive and file hashes:
  `evidence/original-manifest.json`.
- Default configuration: `config/pello.json`; operational database:
  `runtime/jobs.sqlite3`.
- Original mock job: `clinica-reservas-demo-20261024040808-1a32bd`.
  Final state: `LISTO_PARA_REVISION`, 2 attempts, 1 correction, 8 passing tests.
  This is deterministic MOCK VERIFIED evidence.
- SDK smoke: `runtime/sdk-smoke/first-install/result.json` and portable evidence
  under `evidence/first-sdk-smoke/`. Status: REAL INTEGRATION VERIFIED.
- SDK thread: `01a16c1a-1fb1-7b70-877f-b7a52c96f575`.
- SDK turn: `01a16c1a-2557-7ec3-a55d-7c85f14b8b43`.
- One real turn completed; its generated module passed 6 independent tests.
- Existing ChatGPT authentication reused; credentials remain outside this project.
- No product Codex job or complete autonomous V1 loop has been validated.

Use `pello.cmd doctor --check-auth` for current prerequisites/account state. The
saved authentication result is historical evidence, not a promise of future access.
See `reports/INSTALLATION.md` for exact setup verification and `PLAN.md` for the
next development task. No background service or scheduled process is installed.
