# Pello: Windows installation

Pello is a local command-line prototype. Use the isolated environment created by
`setup.ps1`; virtual-environment activation is unnecessary. The original archive
remains in Downloads. See `reports/INSTALLATION.md` for this machine's measured results.

## Install or repair

Open PowerShell in the Pello project folder and run:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1
```

This process-scoped execution-policy option does not change your computer's
execution policy. The script supports Windows PowerShell 5.1 and PowerShell 7.

The script finds 64-bit Python 3.10+ and Git, creates `.venv`, installs exact
dependencies from `requirements-lock.txt`, installs the editable local package,
creates missing configuration and SQLite tables, and runs dependency, entry-point,
unit-test, and offline-demo checks. Existing configuration and jobs are preserved.
It reads the SDK account status without printing credentials or running a model.
Logs are saved under `evidence/setup-*` and `evidence/setup-check-*`.

If Python or Git is missing, setup attempts a silent per-user WinGet installation
from the official WinGet catalog. It stops if this is unavailable or blocked;
it does not elevate automatically. Python 3.12 x64 is the tested baseline.
Missing-prerequisite installation branches were not exercised on this computer
because the prerequisites were already installed. Internet is required for packages.
Node.js and a separate global Codex CLI are not required: the Python SDK installs
its version-matched CLI runtime. The first download includes a large runtime wheel.

Select a particular interpreter when needed:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\setup.ps1 -PythonExe 'C:\path\to\python.exe'
```

Exit codes: `0` = requested checks passed; `1` = local setup/check failure;
`2` = local checks completed but authentication is blocked. A requested smoke test
failure is propagated as setup failure. Local checks alone never establish a
working model connection.

## Use Pello

```powershell
.\pello.cmd --help
.\pello.cmd doctor
.\pello.cmd doctor --check-auth
.\pello.cmd demo
.\pello.cmd status JOB_ID
```

The installed console entry point is `.\.venv\Scripts\pello.exe`. The module
entry point is `.\.venv\Scripts\python.exe -m athis_autopilot`.
`pello.cmd` also works when invoked by its absolute path from another directory.
No system-wide PATH edit is necessary.

`config/pello.json` is created from `config/pello.example.json`. It contains only
`runtime_root`, a path relative to this project (or an absolute path). The global
`--root` argument overrides it and goes before the command:

```powershell
.\pello.cmd --root 'C:\PelloData\runtime' demo
```

SQLite lives at `<runtime_root>/jobs.sqlite3`; each job has its own workspace,
copied acceptance tests, logs, and reports. Job-level timeouts/correction limits
are in the product specification, such as `examples/clinica/spec.json`.
No database server is needed. Avoid running simultaneous writers against one job.

## Codex authentication and one real test

The installer reuses existing Codex authentication. It never copies `auth.json`
into the project. Model workers require ChatGPT authentication and remove API-key
environment overrides to avoid an unintended API-billing fallback.

If the authentication check is blocked, run:

```powershell
.\pello.cmd login
# Alternative for a headless browser flow:
.\pello.cmd login --device
```

Complete the displayed browser flow yourself. Do not put credentials in project
files or send them in chat. `-SkipAuthenticationCheck` permits local-only setup;
it does not validate the Codex connection. Login is the only expected interactive
step on a computer without an existing authenticated session.

A real smoke test consumes account usage and makes **one model turn**:

```powershell
.\.venv\Scripts\python.exe -m athis_autopilot.sdk_smoke --timeout 120
```

Or request it during setup with `-RunSdkSmoke`. Default setup never runs a model.
The smoke test creates a fresh directory under `runtime/sdk-smoke/`, persists the
thread ID before the turn, asks Codex to write one arithmetic module, checks its
entire AST before importing it, and executes six independent tests outside the
worker workspace. Inspect `result.json`, `sdk/codex_result.json`, and
`independent-tests.log`. Only `REAL INTEGRATION VERIFIED` means this test passed.
A timeout kills the worker process tree and records a blocker; it does not prove
the remote turn was cancelled. Do not blindly repeat an interrupted turn.

The existing clinic `start --mode codex` command can run multiple development
turns. It is beyond the one-turn installation check and was not exercised here.

## Reproduce on another Windows computer

Copy the source folder with `pyproject.toml`, both requirements files,
`setup.ps1`, `pello.cmd`, `athis_autopilot`, `tests`, `examples`, and the example
configuration. Omit `.venv`, `runtime`, `*.egg-info`, local configuration, and
credentials. Run setup to create a new virtual environment; do not copy `.venv`
between computers. Authenticate if needed, then explicitly run one smoke test.
The lock pins package versions; it is not an offline wheel bundle or a guarantee
that future package registries remain available. Other Python/CPU/OS combinations
need their own verification.

## Limits

Successful installation and a small real SDK test do not establish full autonomous
V1 behavior. The current supervisor is deterministic, and the offline correction
is preprogrammed. General generated code and acceptance tests run as local Python
processes; they require a stronger OS isolation boundary for untrusted projects.
The AST restriction applies specifically to the installation probe. Keep runtime
data out of simultaneous OneDrive synchronization if file locking causes problems.

Official references checked for this installation:

- [Codex SDK](https://learn.chatgpt.com/docs/codex-sdk)
- [Codex authentication](https://learn.chatgpt.com/docs/auth)
