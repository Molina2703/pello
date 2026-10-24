# Current scope

## Phase 2 (current authorized work)

Implement one AI planning -> separate executor -> independent verification -> AI
review cycle, coordinated by Python through validated messages and existing
SQLite. Persist role sessions, bounded context, task states and evidence; extend
the CLI. Maximum three nested turns, one live demonstration, no automatic retry
of a blocked demonstration. No Phase 3 rotation or Phase 4 repair loops. See
`PHASE2.md` and `reports/PHASE2.md` for actual validation status.

## Initial installation scope (historical)

User-authorized objective: first-time local installation of the supplied Pello
prototype, reproducible Windows setup, actual baseline tests, and one real SDK
integration check when existing authentication permits it.

The supplied master specification is product reference material. Its broader
autonomous-supervisor roadmap is not implemented by this installation work.
Passing the installation probe does not satisfy the full V1 acceptance criteria.

Python, Git, SQLite, a virtual environment, the official Codex Python SDK, durable
logs, and executable command-line entry points are the installation requirements.
No deployment or external service mutation is part of this scope.
