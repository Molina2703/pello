# Initial installation: observed results

Date: **2026-10-23, America/Bogota**. Machine-readable evidence uses UTC on
2026-10-24. Scope: first local setup and one real SDK development turn.

## Outcome

The local prototype is installed in an isolated virtual environment. The four
original unit tests pass after a Windows SQLite fix. The offline demo passes its
eight acceptance tests after its intentional failing attempt. A real authenticated
Codex SDK turn wrote a module that passed six independent tests.

**This verifies installation and the small real SDK integration. Full autonomous
Pello V1 remains unfinished and unverified.**

## Environment and dependencies

| Item | Observed |
| --- | --- |
| OS | Windows 11 Pro x64, 10.0.26300 |
| Python used | 3.12.6, isolated `.venv` |
| Other Python found | 3.13 launcher entry; not used or verified |
| Git | 2.51.0.windows.2 |
| Node / npm | 22.22.0 / 10.9.4; not required by the Python setup |
| PowerShell | Host 7.6.5; setup also executed in Windows PowerShell 5.1 |
| SQLite | Python standard library, SQLite 3.45.3; no server |
| Official SDK / pinned runtime | openai-codex 0.163.0 / openai-codex-cli-bin 0.163.0 |
| Local package | pello-autopilot 0.1.0, editable install |

Python and Git already existed; no system installation was necessary. No Pello
environment, configuration, database, or dependency installation was reused.
`openai-codex` was absent from the initially selected Python. Its eight resolved
packages were installed inside `.venv` and pinned in `requirements-lock.txt`.
Build tooling is separately pinned in `pyproject.toml`. No API key was requested.

SDK signatures were checked against the installed package and the
[official SDK documentation](https://learn.chatgpt.com/docs/codex-sdk).
Its original `thread_start`, `thread_resume`, and `thread.run` calls match this
SDK. The SDK account API confirmed `chatgpt` authentication; no credential file
contents, account email, or tokens were printed. See the
[official authentication documentation](https://learn.chatgpt.com/docs/auth).

## Archive audit and reusable components

Original archive: `C:\Users\USUARIO\Downloads\ATHIS-DEV-AUTOPILOT-V1.zip`.

SHA-256: `7607e3afc6e011142bc18ffc79ae5ad7aafc6ebb7fc305f5890b75a2169da86e`.

The ZIP contained 18 files, no installed environment or database, and an unpinned
optional SDK requirement. It was extracted without overwriting files into this
dedicated `Pello` directory. It remains unchanged in Downloads. Per-file hashes
are in `evidence/original-manifest.json`.

Reusable components: SQLite job/event storage, deterministic supervisor state
machine, Git workspace checkpoints, bounded execution adapter, CLI, fixture
specification, and independent acceptance tests. The original tests and acceptance
suite were preserved unchanged. `example_evidence` contains inherited material;
it is not evidence from this installation.

## Actual baseline and corrections

| Check | Actual outcome |
| --- | --- |
| Original code, four unit tests | Exit 1: 4 cleanup errors, Windows `WinError 32` on `jobs.sqlite3` |
| Original offline demo | Exit 0: 2 attempts, 1 correction, 8 tests in each cycle |
| Intentional first mock implementation | 8 failures; correctly detected |
| Second mock implementation | 8 passes |
| Four unit tests after SQLite repair | All pass |
| Dependency consistency | `pip check` passes |
| Entry points | Module, installed `pello.exe`, and `pello.cmd` verified |
| SDK authentication | Existing ChatGPT account recognized |
| Real SDK probe | One completed turn; generated source exists and matches safe AST; 6 tests pass |
| Windows timeout cleanup | Parent and child processes both stopped in an actual process-tree check |
| Fresh-environment setup | Windows PowerShell 5.1 setup exit 0: new venv, packages, configuration, database, all 6 local checks passed |

The SQLite connection context manager committed/rolled back transactions but did
not close its connections. Windows then prevented test-directory cleanup. The
replacement context manager now closes every connection in `finally`.

The original adapter's API methods were compatible. It was hardened to require
ChatGPT login, decode subprocess output as UTF-8, and stop the worker process tree
on timeout. The previous timeout only stopped the Python worker, potentially
leaving its app-server child alive. No timeout was needed during the real probe.

The login command now returns failure when authentication fails. `doctor` can
optionally check SDK authentication without a model turn. Configuration, package
metadata, launcher, pinned dependencies, initializer, setup checks, and a one-turn
probe were added. The setup script was repaired for PowerShell variable parsing
and Windows PowerShell's handling of harmless native stderr output.

## Real integration evidence

Evidence: `evidence/first-sdk-smoke/` (copied from the original runtime run).

- SDK result: `completed`; test classification: `REAL INTEGRATION VERIFIED`.
- Thread: `01a16c1a-1fb1-7b70-877f-b7a52c96f575`.
- Turn: `01a16c1a-2557-7ec3-a55d-7c85f14b8b43`.
- Generated source: `pello_probe.py`, containing the requested `add(a, b)` function.
- Source SHA-256: `ba1a531f581d2e6094e978ed6f7aca7a8d92eeb62c6e7ad73ee692f7f18bc772`.
- Six independent tests passed after checking the complete generated AST.
- SDK reported total usage: 34,842 input tokens, 87 output tokens, 34,929 total;
  30,720 input tokens were cached. These are SDK counters, not a verified USD bill.
- Exactly one real model turn was requested. No automatic retries were run.

The raw changed-files list also includes verifier-generated bytecode; see
`ARTIFACT_NOTE.md`. The source file was authored by Codex. Future probe runs
disable bytecode generation in the verifier. The saved raw result is unchanged.

The probe is recorded separately from product jobs; it does not claim to be an
autonomous project run or an AI supervisor/executor exchange.

## Files and evidence

Modified original files: `.gitignore`, `README.md`, `requirements-codex.txt`, and
`athis_autopilot/{cli,codex_worker,engines,supervisor}.py`.

New executable/setup files: `setup.ps1`, `pello.cmd`, `pyproject.toml`,
`requirements-lock.txt`, `athis_autopilot/installation.py`,
`athis_autopilot/sdk_smoke.py`, and `config/pello.example.json`.

New local state: `.venv`, `config/pello.json`, SQLite database and runtime folders.
Instructions and durable context: `INSTALL.md`, `SPEC.md`, `STATE.md`, `PLAN.md`,
and this report.

Evidence includes `baseline-tests.log`, `baseline-demo.log`, `environment.json`,
`sdk-auth.json`, `original-manifest.json`, `timeout-process-tree.json`, SDK probe
artifacts, timestamped setup logs, and `setup-check-*/result.json` with individual
check logs. Local runtime and credentials are excluded from source distribution.

The final `setup.ps1` was also executed from a separate source copy with no
virtual environment, configuration, or runtime directory. It created all three,
installed the locked dependencies, and passed every local check with exit 0.
Authentication was deliberately skipped for this second setup, and no second
model turn was run. Its logs are in `evidence/clean-room-setup/evidence/`.
Automatic approval review rejected recursive cleanup of the temporary
`.setup-repro` folder; it remains excluded from Git and source distribution.
This verifies setup on a fresh Pello environment on this machine; it does not
test installing missing system prerequisites or setup on another computer.

## Remaining limitations and next step

The supervisor is deterministic; mock correction is preprogrammed. AI planning,
two-role message transfer, session rotation, robust interrupted-work recovery,
and real multi-task correction have not been validated. Thread persistence was
observed; resume and rotation were not exercised. General generated code still
needs stronger OS-level isolation than a subprocess timeout and test hashes.

An audit also found that the existing `codex_executed` report field is computed
from mode and attempted-turn count, so a failed attempt could be reported as
execution. It was not used as proof for the installation probe. The exact next
recommended task is to correct this evidence classification and add failed-turn
and quota-blocker regression tests before expanding orchestration. See `PLAN.md`.
