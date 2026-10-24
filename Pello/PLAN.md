# Current plan

Phase 2 is REAL SDK VERIFIED for one bounded development cycle: AI planning,
a separate executor, independent local verification, and AI review coordinated
by Python. Project `phase2-leads-retained` ended with COMPLETE after 12 passing
acceptance tests. Three real SDK turns were used; 43 local tests passed.

## Next Phase 3 engineering task (not started)

Implement a configurable rotation policy independently for supervisor and
executor. Reconstruct a bounded prompt from stored specification, plan, task,
architecture decisions, verified outcomes and unresolved issues. Verify that a
replacement session continues unfinished work without repeating completed tasks.
Persist replacement lineage and handle unavailable/active-writer sessions as
explicit blockers. Preserve the bridge's operation reservations and correlation.
Do not automatically start this work without a new user request.

## Later phases

- Phase 4: bounded AI diagnosis/repair, dependent-task continuation, cancellation
  and safe reconciliation of interrupted effects.
- Strengthen the verifier's OS isolation before accepting untrusted projects.
- Phase 5: measured evaluations and full V1 acceptance coverage.

The original installation and both pre-inference blocked Phase 2 attempts remain
in historical reports/evidence. They are not substitutes for the final real
cycle; see `reports/PHASE2.md` for current evidence and limits.
