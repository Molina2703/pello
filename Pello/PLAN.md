# Current Phase 2 plan

The AI supervisor, structured bridge, separate sessions, persistent task/exchange
records, one-cycle CLI, and objective verification gates are implemented. Local
tests and SDK session preparation are verified. The real AI cycle remains
IMPLEMENTED / UNVERIFIED: the only attempt, `phase2-leads-first`, blocked during
preparation before any model turn. The configuration defect was fixed, but the
user's explicit no-retry boundary prevents automatically repeating that cycle.

Immediate next task: obtain authorization for one new three-turn demonstration
using the corrected configuration. Run plan, execute, verify the 12 lead tests,
review and stop; preserve the original blocked project's history.

Exact next Phase 3 engineering task, after Phase 2 live verification succeeds:
add configurable per-role session rotation, reconstruct bounded context from
stored specs/tasks/decisions/tests, and test continuation across replacement
threads without repeating completed tasks. Do not begin it automatically.

## Original post-installation roadmap (historical)

Installation and the one-turn SDK probe are complete. The following are future
development tasks, not work completed during installation.

1. Audit reporting and failure classification. Distinguish attempted turns from
   completed turns and verified work; preserve structured authentication/quota
   blockers. Add focused regression cases for failed SDK results and interruptions.
2. Introduce typed supervisor/executor/verification messages and a persistent
   multi-task plan. Preserve the existing deterministic state guards and tests.
3. Add an actual AI supervisor, separately managed from the executor. Verify that
   Python transfers bounded tasks/results between the two roles.
4. Persist and reconstruct both sessions, with rotation and interrupted-operation
   reconciliation. Do not equate saved thread IDs with verified resume behavior.
5. Establish OS-level isolation for general generated code and protected tests.
6. Verify real dependent tasks, independent verification, automatic diagnosis and
   correction, bounded retries, pause, and recovery.
7. Run measured evaluations against the master specification's V1 acceptance
   criteria. Report each criterion's evidence level independently.

The reporting defect above is now fixed: attempted turns alone do not establish
completed Codex execution. The current next action is the bounded live
demonstration described at the top of this file.
