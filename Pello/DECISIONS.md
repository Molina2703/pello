# Engineering decisions

1. **Reuse the prototype.** `SupervisedCycle` extends the existing supervisor's
   SQLite lifecycle and Git initialization. Additive `pello_*` tables preserve
   legacy jobs/events. The existing SDK worker/adapter gains role, model, effort,
   schema and session-only options; no message broker or service is added.
2. **Python owns authority.** Pydantic rejects malformed/incomplete/mismatched
   exchanges and invalid plans. Tasks have IDs, sequential dependencies and
   completion criteria. Agent summaries remain claims; Python observes source
   changes and independent tests. Failed or unexecuted tests cannot be approved.
3. **Bounded durable operations.** Unique `plan`, `execute`, `review` reservations
   cap each project at three turns. Requests, responses, messages, task states
   and sessions persist. Completed output can be replayed locally; uncertain
   effects block. This is not an exactly-once/concurrent execution guarantee.
4. **Separate roles and permissions.** The roles must have distinct thread IDs.
   Supervisors request read-only access; executors request workspace writes.
   External tools and additional agents are disabled for nested roles only.
5. **Explicit economical configuration.** Actual catalog-confirmed `gpt-6-luna`
   with low reasoning is the tiny fixture's default. SDK 0.163.0 signatures were
   checked for `output_schema`, `effort`, thread start and resume. No higher-model
   routing, repair loop, or paid API-key fallback is introduced.
6. **Owner-controlled acceptance.** Tests live outside the executor workspace,
   with a pinned expected count and hashes. Source hashes detect later drift.
   The verifier subprocess remains an incomplete malicious-code boundary.
7. **Retain failed evidence.** The first live command blocked before any model
   turn. CLI `-c` paths require bare normal MCP identifiers; quoting them created
   an invalid separate entry. The corrected path was verified without inference;
   unusual names fail closed. Original blocked records/logs are preserved.
8. **Respect the run boundary.** The user prohibited automatically repeating a
   blocked live demonstration. Each subsequent attempt received explicit human
   authorization. The final cycle completed with exactly three real turns in
   total. Rotation/compaction and repair remain later phases.
9. **Retain SDK role handles through a cycle.** An explicitly authorized second
   attempt exposed that a fresh empty thread cannot be resumed from a different
   process. The first turn now follows creation in the same worker, with its
   SQLite session record committed first. The worker caches the distinct role
   handles for planning/execution/review and closes at the cycle boundary. A
   no-inference SDK roundtrip tested this correction before the subsequently
   authorized real cycle passed. Both blocked attempts were preserved. The final
   suite has 43 passing tests, including correct aggregation of failing subtests.
