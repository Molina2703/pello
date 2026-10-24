# Remaining product work

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

Recommended next task: fix the existing `codex_executed` reporting field, which
currently derives execution from attempted-turn counters; add failed-turn and
quota-blocker regression cases before expanding the orchestrator. This can be
tested without spending additional model turns.
