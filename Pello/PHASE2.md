# Phase 2: one supervised cycle

This command extends the existing installation without replacing legacy jobs:

Current result: **REAL SDK VERIFIED** for `phase2-leads-retained`: three real
turns, 12 passing independent tests, supervisor decision COMPLETE, and 43 passing
local automated tests. Full V1 is unfinished. The earlier blocked attempts below
are preserved historical evidence; each subsequent attempt was explicitly authorized.

The SDK worker stays alive for one cycle and retains two distinct role handles.
Each new thread is persisted to SQLite before inference and receives its first
turn in that same process. A completed supervisor handle is reused for review.
This avoids trying to reopen an empty, not-yet-materialized thread from another
process. A thread held by an external writer still requires reconciliation.

```powershell
.\pello.cmd supervised --spec examples\leads\SPEC.md --suite examples\leads\acceptance
```

It creates a project, asks the AI supervisor to plan, delivers the selected typed
task to a separate executor thread, runs external acceptance tests, sends the
observations back to the supervisor, persists its review, reports, and stops.
At most **three** model turns are reserved: plan, execute, review. There are no
workflow retries, automatic model escalation, repair loops, or background service.
The default `gpt-6-luna` and low reasoning were confirmed in this account's actual
catalog. An unavailable configuration blocks instead of silently substituting.
Existing ChatGPT authentication is reused without paid API-key fallback.

The independent suite needs `test_*.py` and `manifest.json` declaring a positive
`expected_tests` count. Python requires exactly that many successful tests, with
no skips, before accepting success. AI cannot lower this count, replace the plan
during review, or override failed tests. Agent file claims are stored separately
from Python's observed source hashes.

```powershell
.\pello.cmd supervised --status PROJECT_ID
.\pello.cmd supervised --resume PROJECT_ID
```

`--status` reads without inference. `--resume` continues unfinished stages without
repeating completed operations. Blocked projects stay blocked. A saved SDK result
can be reconciled without another model turn; missing or ambiguous in-flight
results require human reconciliation. Use one process at a time, not concurrent
runs. Reusing an existing project ID for a new run is rejected.

Exit `0`: independent verification passed and the review consistently chose
`COMPLETE`/`CONTINUE`. Exit `2`: blocked work, invalid input, `REPAIR`,
`NEEDS_HUMAN`, or failed verification. Repair and subsequent tasks are never
executed in this phase. `COMPLETE` is rejected if any planned task is unverified.

Artifacts: `<runtime_root>/supervised/<project_id>/` contains `SPEC.md`,
`workspace/`, external copied `acceptance/`, role thread IDs, `evidence/`, and
`report.json`/`report.md`. Additive `pello_*` tables in the existing `jobs.sqlite3`
store projects, tasks, exchanges, sessions, and operation reservations. Legacy
tables and historical evidence are preserved.

Nested supervisors request read-only access; executors request workspace write
access without added writable roots. Inherited MCP servers, apps/plugins, web
search and additional agents are disabled without changing global configuration.
Shell environments do not inherit secrets; the SDK process receives a small
runtime/auth environment and still needs its normal credential store. Phase 2
uses standard-library `tomllib` (Python 3.11+); tested environment: Python 3.12.6.

The verifier uses Python `-I`, a limited environment, source/suite hash checks,
and machine-readable unittest counts. This is not a strong OS isolation boundary
against malicious generated Python. Use a restricted OS account, VM, or container
before accepting untrusted projects. A timeout does not prove remote cancellation
or absence of side effects; inspect persisted state before further work.

This run's only live attempt, `phase2-leads-first`, blocked during session setup
with **zero model turns**, due to an MCP override syntax defect. The defect was
fixed and both role presets initialized successfully without inference. The
blocked live cycle was not repeated. See `reports/PHASE2.md` for observed evidence.

Update: a second attempt was explicitly authorized and blocked before inference
on the empty-thread lifecycle defect described above. That defect is now fixed,
42 tests pass, and the retained-worker RPC path was verified without inference.
No further model cycle was launched without authorization. A subsequent explicitly
authorized cycle passed after this correction; see the current report for proof.
