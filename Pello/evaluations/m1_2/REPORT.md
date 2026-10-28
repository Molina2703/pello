# M1.2 — Controlled semantic smoke test

Baseline: `codex/pello-phase3c`, M1.1 commit `7ac436378c85821b8864ba5f2054f381dbc98d43`. Three new synthetic specifications and their expected checkpoints were independently reviewed and frozen before inference. The frozen `cases.json` SHA-256 is `62671fa8cc373490fb4c8c7849fb27960676be5fe56582ae9edc30bea69bdf19`. The expected inventories guide review; source citations, dependencies and blocker scopes were assessed independently against the specifications, not inferred from the inventories alone.

The actual configured and available Planner was `gpt-6.1-sol` / `high`; account authentication and rate limits were checked before runs. Six primary calls used distinct new sessions, isolated temporary projects and databases, the same role instructions, schema and source within each pair, and no prior answers. A was the original serialized payload; B was the M1.1 projection. A always preceded B. SQLite operation requests confirm the actual model and effort; input, schema and role-instruction file hashes match inside each pair. All sessions completed and all six outputs passed existing normalization and `validate_planning_input`. Identical deterministic reconstruction does not itself prove model understanding. Raw inference traces and temporary databases are not committed.

## Observations

The independent Reviewer assessed each pair against the original source and frozen inventory before proceeding to the next pair. The Reviewer found no critical regression in the three observed pairs, with the following qualifications:

- **WhatsApp:** both covered all seven checkpoints and cited matching source segments. Both preserved opt-in and explicit authorization as separate gates. A classified uncertainty around matching the word `URGENT` as blocking; B described a provisional case-sensitive standalone-word interpretation as a non-blocking assumption. B marked all requirements customer-approved although the source has no explicit approval record. It did not treat that label as permission to send.
- **CRM:** both covered the eight checkpoints, including local storage during outage, contact match and consent before task creation, error recording, no false synchronization and explicit write authorization. B's acceptance implications for task creation expressed the prohibitions more explicitly than the positive success case. B also treated unresolved matching rules as blocking more broadly than A; local recording and error handling remained independent.
- **Claims:** both preserved the eleven checkpoints, the mutually conflicting current refund instructions and their blocking contradiction, unknown provider and refund authorization, and independent local recording and status. A marked requirements customer-approved without an explicit approval record; neither variant treated that label as refund authorization.

These approval-label observations are a provenance concern in both directions, not evidence that projection alone caused them. They should not be hidden by an aggregate PASS. One sample per variant cannot distinguish representation effects from ordinary sampling variation. No actual external actions were authorized or performed.

## Recorded resources

Prompt characters measure only the `understand` prompt. Tokens are SDK-reported usage for the full turn, including context beyond that prompt; output token counts include the reported reasoning tokens. Latency includes project setup and the model call, and is not a controlled benchmark.

| Case | Variant | Prompt chars | Input tokens | Output tokens | Total tokens | Seconds |
|---|---|---:|---:|---:|---:|---:|
| WhatsApp | A | 2,516 | 11,773 | 3,523 | 15,296 | 92.80 |
| WhatsApp | B | 2,268 | 11,721 | 3,642 | 15,363 | 93.41 |
| CRM | A | 3,200 | 11,940 | 5,887 | 17,827 | 145.74 |
| CRM | B | 2,716 | 11,845 | 4,368 | 16,213 | 93.33 |
| Claims | A | 3,855 | 12,072 | 3,577 | 15,649 | 80.97 |
| Claims | B | 3,089 | 11,936 | 5,140 | 17,076 | 112.11 |

Total reported usage: 97,424 tokens. No cost estimate is available. Account windows reported 13% used for the five-hour window and 31% for the weekly window at initial inspection; limits can change during execution.

## Verification and next boundary

Independent semantic Reviewer verdict: **PASS for this focused sample, with the provenance concern and limits above**. Targeted M1.2, M1.1 and M0 tests passed (15); complete offline regression suite passed (276). No protected strategic document, historical evidence or production database was changed. The tool requires a fresh output directory outside the repository and refuses altered case data; it does not automatically retry uncertain submissions. An independent semantic Reviewer assessed each pair before proceeding; the runner does not enforce review between separate invocations.

M0 diagnostics report the largest preserved later planning prompts as architecture E at 54,043 characters, increments I at 53,834, and contracts I batch 1 at 51,736. These are persisted original prompts, not reconstructed candidates; rejected historical prompt lengths remain unknown. The increment-planning boundary is a promising next measurement target because it carries full structured analysis plus work nodes, but this increment does not modify it. Later-stage context amplification and historical context-limit failures remain unresolved.

This is evidence of semantic coverage in three controlled pairs, not statistical proof of equivalence or model accuracy in general. The fixed ordering, limited sample, unresolved provenance-label inconsistency and model nondeterminism constrain the conclusion. M1 remains open.
