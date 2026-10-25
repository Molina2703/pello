# Pello V1.3 — Phase 3C-3 Evaluation Report

Checkpoint date: 2026-10-25T23:04:22+00:00. **Phase 3C-3: PARTIAL. Overall Phase 3C: PARTIAL. Blind generalization: UNVERIFIED.**

Three genuinely new, independently authored held-out specifications were frozen and attempted through the real SDK pathway. All three autonomous runs failed before producing a complete plan. Their FAILs remain unchanged. Localized engineering corrections passed independent review and regression, but no valid held-out PASS exists and Phase 3C cannot be accepted. No business product was implemented or delivered; Phase 3D was not started.

Paths are relative to the Pello product directory unless stated otherwise.

## A. Initial state and authorization

Initial branch: `codex/pello-phase3c`. Initial HEAD: `c1bb076e7059100f0c4b5abf623625d2843f0be2`, the reporting-only successor to accepted C2 implementation `90ea13053fa31bf12b4031b45e5f5e620bc86331`. History was inspected, never reset. Three unrelated, pre-existing untracked context artifacts were preserved and excluded from commits.

SQLite integrity was `ok`; all fourteen existing checkpoint commits were present. STOP was absent and remained absent. The authoritative ledger had 28 completed SDK model operations, a cumulative limit of 30 and the historical deadline 2026-10-25 21:14:29 UTC. The previous project chat and accepted C2 report were read and reconciled against actual rows and artifacts.

The user explicitly approved **60 cumulative SDK turns until 2026-10-26 00:45 UTC** (October 25, 19:45 Colombia). `authorization.json` records that reply; its append-only authorization row preserves all 28 prior operations and project counters. Per-project limit 12, STOP, available-model checks and zero external business operations remain enforced. No additional grant is inferred from this report.

Initial preservation recomputed 1493/1493 historical hashes, all six protected test-source registrations and the five C2 delivery hashes. Baseline protected suites were actually rerun: 63/63 PASS. Historical 217/217 regression is distinguished from the new 233/233 run below. Evidence: `initial-state.json`, `authorization.json`, `baseline-protected.json`, and prior `evidence/phase3c/closeout/`.

## B. Evaluation preparation and blindness

The evaluation author used a separate SDK tester session with no Pello Planner output or private reasoning. It produced business specifications and outcome rubrics, not architectures, task graphs or technical manifests. Evaluation Reviewers used separate sessions. Each Planner was a new bounded project under the same cumulative ledger; projects were not recreated to evade a limit.

| Held-out case | Identity | Frozen at UTC | Acceptance rubric |
|---|---|---|---|
| A: CanalShare | `phase3c3-heldout-a-v2` | 2026-10-25T22:02:51.683315+00:00 | 25 critical + 1 minor |
| B: ArchiveLedger | `phase3c3-heldout-b-v1` | 2026-10-25T22:21:52.758992+00:00 | 26 critical + 1 minor |
| C: KilnBook | `phase3c3-heldout-c-v1` | 2026-10-25T22:40:08.994765+00:00 | 27 critical + 1 minor |

**A specification:** `9ade6c83162fcf07f3d959ff59343c5804934c59c2d89c3cdd68268370845b2c`  
**A rubric:** `8f8cca8054c6bed730e9ccfddf5d1913cd41a1a6f7eae52ccba521097a434db4`

**B specification:** `7a692ecfd1f947401e5a72875775be0ce6ce5ed1b4c8c4d64c4af99f13a82bc1`  
**B rubric:** `5445b18a88010996556d8ccdfc5a04bfc8db40b370eaad874eb09bce43cb7523`

**C specification:** `ab227a640a8a4e25fdadbf3c3c9900873549b26eaaeaffe4fb7a2ebad4c624b7`  
**C rubric:** `3674c9e42de22b346e4d7d6d93fb0772b04b04b998cb70c13eb8174feaccd20e`

All critical criteria must PASS and at least 90% of all criteria must PASS. Frozen critical failures include omitted mandatory capabilities, exclusion violations, invented authorization, ignored blockers, invalid graphs, executable blocked work, unauthorized effects, incompatible manifests and false claims of executed/protected product tests. Structural objective-check scripts were hashed before each Planner project was created.

CanalShare preparation v1 failed review because all criteria were critical and one prescribed a backend architecture. Its original rubric, hashes and FAIL remain. Independently authored rubric v2 corrected those evaluator defects **before the Planner saw the specification**; the business source stayed byte-identical. ArchiveLedger preparation required additional exact-path isolation proof; no source or rubric was changed. KilnBook preparation passed with complete frozen records. Preparation PASS never counted as planning PASS.

Read-only sandboxing alone was insufficient. Before any case was authored, a localized adapter correction disabled reading surfaces for supplied-context roles and selected an existing named native filesystem profile with `deny` roots. Explicit legacy sandbox selection was removed only for this opt-in boundary because it discarded the named profile. The worker confirms actual `activePermissionProfile`, denied roots, absent automatic instruction sources and read-only/no-network provenance before inference; resumed/shared handles preserve or verify the same configuration. Ordinary executor permissions are unchanged.

Native positive controls read a public synthetic file. Negative controls returned `PermissionError` for the private key area, author artifacts, SQLite ledger, evaluator evidence, reviewer copies and Codex transcript area. The exact declared rubric paths and their Windows packaged/normal-user aliases were also tested. Parent file-identity and hash checks proved the alias relationship; denial was verified on both names. Residual metadata/orchestration tools are not presented as an empty tool inventory. External MCP/app access stayed disabled.

Private rubrics stayed outside Planner context and behind the enforced boundary. Only public specification, existing resource constraints and pipeline-generated context were supplied. Rubrics were exported for audit under `consumed-rubrics/` only after their respective cases had been consumed; their original bytes/hashes remain intact. No expected solution was added to Git before that case's Planner run.

Evidence: `isolation/`, the three freeze and preparation-review records, `full-boundary-*-objective.json`, exact-rubric path proofs, `objective-registration*.json`, `batch1*-checkpoint.json`, and `consumed-rubric-publication.json`. Profile behavior references: [official configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference) and [command-tool feature documentation](https://learn.chatgpt.com/docs/config-file/config-basic). Runtime enforcement is supported by native transcripts, not those links alone.

## C. Actual autonomous planning runs

The real `ProductPlanningCore.plan_product` C1 → C2 path was invoked, with existing SDK reservation, model availability, role isolation and persistent source mechanisms. No human-authored technical plan was supplied.

| Case | Actual observed output | Failure boundary | Durable outcome |
|---|---|---|---|
| A — CanalShare irrigation allocation/reconciliation | 37 normalized requirements, 6 issues, 3 assumptions | Duplicated interpretation-review context exceeded 55,000 characters; reservation preceded rejection | Interpretation and original SDK response saved; no complete plan |
| B — ArchiveLedger records custody/storage/disposition | 33 raw requirement candidates; typed validation rejected one | An authorization-category local role rule set `authorization_required=false`, violating the accepted cross-field contract | Completed SDK response and ValidationError saved; no accepted interpretation |
| C — KilnBook timber intake/kiln capacity/recovery/certification | 39 typed-valid normalized requirements, 8 issues, 4 assumptions | Review context still exceeded 55,000 after first-level map deduplication | Interpretation saved; preflight correctly made no review reservation |

**For all three held-outs:** architecture not reached; functional increments not generated; dependency graph not generated; technical contracts not generated; task model decisions not generated; existing PipelineManifest not produced; persistent plan reconstruction and first actionable increment not reached. Source acceptance examples and interpretation implications are not generated, protected or executed product tests.

Actual Planner invocations used the approved Sol High profile. No business Coder, integration publication, customer operation, n8n mutation or message was executed. Existing adaptive policy remains; there is no forced retry ladder or automatic escalation after these failures. No held-out Coder assignments are credited.

Separately, the accepted C2 development plan was reconstructed under the corrected Core: hash `7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87`, approval ACCEPTED, first actionable N01, one plan-history row, seven decision rows and project SDK counter 8 → 8. This preserves C2; it is not a new blind PASS. See `c2-reconstruction-regression.json`.

## D. Independent evaluation and critical findings

**A: FAIL. B: FAIL. C: FAIL.** None satisfied the mandatory complete-pipeline condition. Full semantic/architecture/contract grading was not reached and remains unverified. Preparation or engineering Reviewer PASS cannot override these objective failures. There is no independent final Phase 3C acceptance verdict.

The original failures are reproducible from saved model outputs, source/hash records, exception transcripts and deterministic defect regressions. A retained reservation alone is not evidence of a model invocation. Case B's rejection is a typed-contract failure; it is not evidence that an unauthorized external operation occurred. Case C demonstrates that the pre-reservation correction worked even though context capacity still failed.

Use the original code checkpoints and `before-FAIL.log` transcripts to reproduce pre-correction behavior; current corrected code is intentionally different. Canonical failed inputs are preserved in `context-correction/initial-failed-operations.json` and `source-context-correction/original-failed-review-payload.json`. The SDK result for each understand operation remains in the authoritative SQLite journal and runtime artifacts. Per-case evaluation JSON records contain verdict, reproduction boundary and evidence references.

## E. Localized corrections and retained failures

| Engineering batch | Small correction | Verification | Independent result |
|---|---|---|---|
| Pre-evaluation isolation | Existing SDK native deny-read profile; supplied-context tool restrictions; actual profile confirmation; resume/shared-profile identity | 17 targeted unit tests + native controls | Initial BLOCKED retained, corrected PASS |
| After A | Check bounded context before reserving a turn; factor byte-equivalent duplicated source maps | 53 targeted tests; original 63,632-character input losslessly packed into a 52,395-character prompt | PASS |
| After B | Expose existing authorization-category invariant and non-grant meaning in the model-facing Field description | 56 targeted tests; existing validator unchanged | PASS |
| After C | Replace segment text only when it exactly reconstructs from source lines; retain the complete original Markdown once | 59 targeted tests; CRLF and mismatching-text negative coverage; actual 71,399-character payload round-trips exactly in a 51,204-character prompt | PASS |

These test groups overlap and are not added together as unique tests. All defect checks were frozen before their implementation changes; original red transcripts and Reviewer FAIL/BLOCKED records remain. No frozen business expectation was changed after observing that case's Planner result. Corrections were made by this engineering session, not autonomously by Pello.

Case A's never-submitted review reservation was reconciled as `NOT_SUBMITTED_CONTEXT_REJECTED` using absence of prompt/submission/result/thread/session plus the deterministic failure location. The original row is archived and its used-turn charge remains. No counters were decremented. Cases B/C remain blocked, with their completed outputs retained.

A fresh case was used after each earlier repair. The latest source-reference correction has **not** been demonstrated by another untouched SDK planning run; local reconstruction of a consumed payload is regression evidence only. Another new independent frozen case is required for any subsequent blind claim.

## F. Regression, integrity and consumption

* Complete corrected-source regression: **233/233 PASS**, exit 0, 259.984 seconds (`correction-regression.json`/`.log`). This is correction verification, not a final acceptance run following a held-out PASS.
* Existing six protected C2 suites: **63/63 PASS**; registered source and protected-copy hashes match. These overlap the complete local suite.
* **1493/1493 historical hashes match**. First 28 SDK operation rows and the four pre-existing project records remain unchanged. Historical FAILs and the known separately corrected C1 manifest self-hash issue are not rewritten.
* All five new protected regression source files match their pre-change registrations; sixteen new unit tests bring the local count from 217 to 233.
* SQLite integrity `ok`; existing checkpoint commits remain present. `interim-planning-state.sqlite3` is a hashed recovery/audit snapshot, not a replacement ledger.
* Cumulative ledger: **49/60 reserved/charged slots**, comprising **48 completed SDK model invocations and one never-submitted reservation retained conservatively**. There are no uncertain or in-flight operations. Remaining authorized slots: **11**. The 28 historical completed calls are included, never reset.
* The temporary quota block occurred before reservation; its exception and later quota recovery remain recorded. No reset credit was consumed. Models/account probes and thread-start diagnostics without inference are distinct from model turns. Raw SDK usage is retained; cumulative per-thread totals must not be summed repeatedly. No monetary amount or live billing control is claimed.
* Zero external business operations: no n8n/MCP mutations, production HTTP requests, customer access, messages, new workflows or Railway provisioning. Protected IDs `dFoCUpXVrP9gc9rY`, `I4qwL8MuXvTotZKU`, `Tbuvwcxde8MEMYcJ` were not operated on. No `config.toml` or MCP reconfiguration occurred. Remote workflow state was not queried as a substitute for local evidence.

Evidence: `correction-protected.json`, `correction-integrity.json`, `interim-state.json`, all accepted engineering-review records and checkpoint manifests. Planning contracts, pipeline/model-policy source and protected accepted behaviors were preserved; Pello was not rebuilt and no orchestrator, database platform, MCP server or cloud service was added.

## G. Verdict, checkpoint and remaining work

**Phase 3C-3: PARTIAL. Overall Phase 3C: PARTIAL. Phase 3C-1 and 3C-2 remain ACCEPTED in their recorded scopes.** No accepted C3/generalization checkpoint exists. The latest accepted engineering correction checkpoint is **`8b714e2c9c25a32de703587d2bd5f7e1593a6eee`** on `codex/pello-phase3c`; the report-only delivery commit is identified separately in Git/chat to avoid a self-referential commit hash.

Remaining requirements include a complete real SDK plan on another untouched case, independent original-source/rubric semantic PASS, coherent generated architecture/increments/contracts/models, durable compatible manifest reconstruction, correct first-actionable selection, final regression after that PASS and independent final acceptance review. The current 55,000-character limit still fails closed for irreducible contexts; it is not proof of arbitrary large-document support.

V1-01/V1-02 generalization remains unverified; V1-06 preserves typed adaptive-policy support without a new runtime escalation claim; V1-18 has accepted development-fixture support but no complete new held-out demonstration. V1-03/V1-04/V1-12/V1-17/V1-19 have relevant scoped engineering evidence, not global completion. **V1-20 is not complete.** No enterprise business product was implemented or delivered and no product-completion percentage is inferred from tests.

No new accepted consolidated `PELLO_PHASE3C_FINAL_REPORT.md` is generated: its acceptance prerequisite is unmet, and prior C2 reports remain unchanged as historical records.

### Proposed continuation authorization — NOT YET GRANTED

One further fresh evaluation needs approximately 10 turns including preparation, the six-call planning path, semantic evaluation and final review. A minimal five-turn failure reserve would require 15 available slots, exceeding the current 11. After three real failures, the defensible proposed allowance is **75 cumulative slots**: preserve 49, provide up to 26 (10 fresh evaluation, 2 localized correction/review, 10 for another fresh case if necessary, 4 failure reserve). Proposed deadline: **2026-10-26 03:30 UTC** (October 25, 22:30 Colombia). All external-effect prohibitions remain; no reset or project-limit bypass is proposed.

Sections 3 and 8 of the user's task require explicit authorization before increasing these hard limits or starting a new evaluation without enough capacity. Further SDK execution for another held-out is pending that approval. Until then, preserve this corrected, independently reviewed and regression-tested checkpoint.

The next action remains completing Phase 3C-3. An end-to-end implementation milestone is a recommendation only after valid C acceptance: connect generated contracts to an independent Tester that writes/protects suites, then use the existing pipeline for several dependent increments in a bounded local business product, correction on a real FAIL and independent integrated verification. No Phase 3D files or execution were created.
