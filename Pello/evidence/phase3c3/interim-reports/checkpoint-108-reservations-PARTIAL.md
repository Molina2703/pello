# Pello V1.3 — Phase 3C-3 Evaluation Report

Reference date: October 25, 2026. Continuation closeout: 2026-10-27T04:14:35.498698+00:00.

**Phase 3C-3: PARTIAL. Overall Phase 3C: PARTIAL. Blind generalization: UNVERIFIED.** C1 and C2 remain ACCEPTED. ParcelProof produced the first complete held-out planning artifact, but independent evaluation found a critical semantic error. A 96% total rubric score cannot override a failed critical criterion. Nine original blind FAILs remain preserved.

This report describes planning and Pello engineering evidence. No business software was implemented, published, tested or delivered. Phase 3D was not started. Paths below are relative to the Pello directory.

## A. Initial state and authorization

Read-only verification began at branch `codex/pello-phase3c`, HEAD `0ab160e9c50397780a0dcf6f568ccca5992aafa1`. Git root was the parent DESARROLLO PELLO directory. No reset occurred. The accepted engineering implementation was `94c2bb9b8f7174bf06afe8758df5b11926421b88`; delivery checkpoint `6020a3d0640f5d115200aee19dc85ab9a2046be5` and later preservation-only commits were retained. Preexisting unrelated/untracked artifacts were preserved.

SQLite integrity was `ok`, STOP absent, all 25 historical SQLite checkpoint Git objects present, no uncertain/in-flight operation, and 1493/1493 historical hashes matched. The ledger held 88 charged reservations, 84 completed SDK calls, and four retained historical failure/non-submission charges. Author usage was14/14. The last full accepted regression was257/257; C2 protected baseline63/63. The first 28 operation rows and four original projects were unchanged. The accepted C2 digest reconstructed unchanged: `7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87`.

The earlier proposal114/author 18 had been declined. The new explicit user reply, **“Autorizo 114 globales, autor 18 y ese plazo”**, authorized one bounded fresh case and justified localized correction/review until **October 27, 2026, 06:30 UTC /01:30 Colombia**. `authorization-extension-114.json` and the append-only SQLite grant record this approval, preserving 88 global and 14 author charges. Other project caps remained12. No replacement author project or counter reset occurred. This grant superseded the previous preservation decision only for the newly approved scope.

Initial verification reran40 existing focused checks. One runner invocation failed to import a top-level test helper; its transcript remains `continuation114-focused-runner-FAIL.log`. Correcting the invocation's search path yielded40/40 PASS without implementation changes. The unchanged-validator AST and C2 reconstruction evidence is in `continuation114-recovery-verification.json`. The master v1.3 byte hash remains `6bca1e0b8d871201601e83b6cdbeadb0554fa52be18a8d624a29ca46ca44674d`.

## B. Independent evaluation preparation

**ParcelProof**, identity `phase3c3-heldout-i-v1`, version 1, was independently authored in the existing authorized evaluation-author SDK context. That context is separate from Pello Planner and evaluation Reviewer and received no Planner outputs or technical solution. The business domain is survey-point validation, exact parcel geometry, disputes, approval and cadastral submission. It differs from the eight consumed cases, Vendor Return Desk and HMP/ADSA demos. It contains meaningful rules, exclusions, dependencies, two independent local branches, external integration gaps, a genuine P-7 contradiction, reversible assumptions and exact-package authorization restrictions.

Source: `heldout-i-spec.md`, 6662 characters. Frozen at `2026-10-27T03:04:49.333667+00:00`. Source SHA-256: `d481313540b5f2959c4a8e10308262d08b920bb6dd8a33918ff48094ada91211`. Original private rubric SHA-256: `2fa06bf103a54a03ab57148fcdce47bcdb7e25a1d92388ea412332e010150735`. All 24 critical criteria and at least90% of 25 total criteria must pass. Critical failures include missing mandatory capabilities, exclusion violations, unauthorized assumptions/effects, ignored contradictions, invalid dependencies, executable blocked work, manifest incompatibility and false product-test claims.

The private rubric stayed outside Planner's working surface in the existing denied evaluation directory. Native profile `pello_supplied_context` extends read-only, denies key/author/ledger/evaluation/Reviewer/transcript paths, and disables network access. Supplied-context SDK roles also disable command, image, host-code, browser, computer, app/plugin/MCP and automatic project-document/skill/memory surfaces. The worker verifies effective profile identity before inference. Actual submitted contexts contain no evaluator-key fields.

All 15 native root checks passed: one readable public control and 14 denied roots. Both exact-key Windows alias checks denied reads, with same-file and hash proof. All eight real Pello SDK submission receipts passed the actual isolation audit. Evidence: `full-boundary-i-objective.json`, `rubric-i-alias-proof.json`, `heldout-i-actual-isolation-audit.json`, `isolation/` and runtime submission receipts. Official documentation describes the [Codex Python SDK](https://learn.chatgpt.com/docs/codex-sdk) and [filesystem deny permissions](https://learn.chatgpt.com/docs/permissions); the local probes establish this evaluation's actual boundary.

Independent preparation review PASS preceded Planner creation. Source/rubric expectations, structural checks and semantic grading source were registered at `batch1-i-checkpoint.json` and committed in **`ba9380e`** before the first Planner invocation. The original rubric and grading gates were not rewritten after seeing results. The consumed rubric was exported unchanged only after the semantic FAIL, with timing/hash evidence in `consumed-rubrics-i-publication.json`; the private original remains intact.

## C. Actual autonomous planning run

Existing `ProductPlanningCore.plan_product` ran through the real authorized SDK: understand → independent interpretation review → architecture → increments → three contract batches → model decisions → durable plan/manifest. Eight Pello SDK invocations completed. The Planner received the original source, authorized inventory/constraints and its own preceding structured outputs; no manually prepared architecture, increments, contracts or manifest were supplied.

The complete result contains **35 requirements, 6 issues, 5 unapproved assumptions, 8 architecture nodes, 8 functional increments, 8 contracts and 86 proposed acceptance criteria**. Exclusions, source IDs, permissions and proposed completion conditions remain inspectable in `heldout-i-plan.json`. Issues:

| Issue | Severity | Description |
|---|---|---|
| ISS-f1ee3142ec14 | blocking | P-7 has two different mandatory western-boundary claims, A–B and C–D, with no authoritative precedence or resolution. |
| ISS-69a8509a76a6 | blocking | The agency endpoint, authentication contract, required reference-system identification, coordinate precision, package schema and duplicate-lodgement behavior are unknown. |
| ISS-34ee2e748ce4 | blocking | External accounts, credentials and submission authorizations are absent, and the firm's agency permissions are unknown. The brief supplies no execution permission. |
| ISS-bf95e4f6bde7 | blocking | Documented resolution is required after an unknown timeout outcome, but acceptable resolution evidence, the responsible resolver and its relationship to agency duplicate-lodgement handling are unspecified. |
| ISS-c70edf298df8 | non_blocking | Users prefer different initial grouping keys, but the source explicitly accepts either client reference or parcel identifier. |
| ISS-e8b835f8a7df | non_blocking | Edge lengths require three decimal places, but the exact-half rounding convention is specified only for area. |

| Increment | Autonomous objective | Dependencies | Proposed Coder configuration |
|---|---|---|---|
| W01 | Propose the local point workflow and reusable role enforcement: preview required fields, atomically reject invalid files, preserve project-scoped uniqueness, make identical reimports no-ops, retain reasoned revisions and expose licensed-surveyor point approvals and unapproved points. Use available synthetic inputs and proposed durable local storage; this creates neither external credentials nor execution authority. | None | gpt-6-luna / medium |
| W02 | Propose the independent geometry module using explicit synthetic point snapshots: capture ordered outlines, enforce project/reference-system consistency, validate without repair, calculate exact area and displayed measurements, record adjoining chains, compare reversed chains with collinear subdivisions and detect all positive-area project overlaps. Its planning does not require W01 or agency access. | None | gpt-6.1-sol / high |
| W03 | Propose local dispute records and candidate checks: preserve both mandatory P-7 claims and their sources without precedence, record authoritative conveyancer resolution when supplied and permit candidate geometry checks only with disputed/unapproved labels. No resolution is required to preserve claims or check labeled candidates. | W02 | gpt-6-luna / low |
| W04 | Propose versioned local schedule review using point, geometry, adjoining and dispute results. Enforce licensed-surveyor approval and all prerequisites; refuse unresolved P-7 approval while allowing other parcels; stale affected approvals after supporting changes; preserve submitted snapshots and require newly reviewed linked amendments. The unresolved P-7 decision does not block implementation or synthetic verification of these gates. | W01, W02, W03 | gpt-6-luna / high |
| W05 | Propose local package-authority controls, submission history and overview. Bind principal authorization to exact approved package details, invalidate changes, perform immediate preflight without rebuilding, preserve linked outcomes and registration evidence, classify timeouts as unknown and deny automatic or unresolved repeat attempts. Expose all overview conditions and viewer schedule access. Use synthetic attempt history independently of the agency and unresolved positive recovery branch; grouping remains provisional. | W04 | gpt-6-luna / high |
| W06 | Conditional P-7 positive review branch, blocked by ISS-f1ee3142ec14: after an actual authoritative conveyancer resolution is supplied as input, record it without deciding ownership and review the resulting P-7 schedule through all ordinary approval prerequisites. Do not choose A–B or C–D, fabricate a resolution or claim this branch complete while the contradiction remains. This node performs no submission. | W03, W04 | gpt-6-luna / medium |
| W07 | Propose the first eligible live lodgement of a schedule or amendment and capture its outcome. This external-operation node is blocked by ISS-69a8509a76a6 and ISS-34ee2e748ce4: require a confirmed agency contract, actual agency access and firm permissions, and separately supplied principal-surveyor execution authorization matching the exact approved package, project, parcel set and destination. Invoke W05 preflight immediately before sending. Exclude unresolved P-7 and any repeat attempt after unknown outcome; the latter belongs to W08. Planning does not perform this operation. | W05 | gpt-6-luna / medium |
| W08 | Conditional live recovery branch following an unknown attempted lodgement. In addition to W07's integration/access blockers, ISS-bf95e4f6bde7 blocks acceptance until the responsible resolver, acceptable documented outcome-resolution evidence and agency duplicate-lodgement behavior are established. Only then may a subsequent attempt be considered, with current approval, matching separate principal authorization and immediate preflight; never retry automatically. W05's local unknown-outcome and refusal safeguards do not depend on this branch. Planning performs no recovery contact or subsequent transmission. | W05, W07 | gpt-6-luna / medium |

Initial planning readiness was W01 and W02; **first actionable increment W01**. This means ready to prepare protected tests and request execution authorization. It is not permission to execute. Two external-operation branches remain unauthorized/unavailable. The graph is acyclic and structurally covers the source, but its enforced blocker scope is semantically wrong as described below.

The architecture passed structural validation on its first attempt. **The bounded architecture retry was not exercised through this SDK run.** Its prior controlled-engine evidence remains accepted; real SDK recovery efficacy is still unverified. No artificial error was injected to force that path.

The existing context mechanism split contract generation into3/3/2 increments. Each request retained the full original requirements and exact supplied increment fields. Exact comparison proved submitted prompts match generated prompts, all eight increment records survive batching unchanged, and the merged eight contracts equal the complete ordered batch responses. Existing aggregate validation and PipelineManifest conversion passed. Evidence: `heldout-i-actual-contract-batching.json` and runtime `contracts-context-batches.json`.

Models were selected adaptively from the actual catalog: Luna Low/Medium/High and specifically justified initial Sol High for exact topology. These are future Coder assignments, not executed Coder calls. The original model request advertised17 available turns while validation/reporting used16; the original plan truthfully retains the resulting one-turn shortfall. This accounting defect was corrected later for new requests, without editing the failed plan.

Plan digest: `b0199c77c21c1e0b66ffd2f2b6217a011c95760bb87f0cc4957b930233c5a722`. SQLite history has one plan row; a separate CLI process reconstructed the same plan without additional inference. Existing `IncrementalPipeline.inspect_planned_manifest` consumed the generated manifest without manual technical translation. Stable IDs, stage hashes and plan identity survived restart and the later engineering correction. Approval remains **PROPOSED**, execution authorization **false**. No business-product Python implementation exists in the project workspace. All 86 criteria remain proposed; product tests are not generated, protected or executed.

## D. Independent semantic and structural evaluation

Frozen structural checks: **10/10 PASS**. They establish source/rubric identity, traceability, coverage, valid manifest/DAG, ineligible blocked/external work, at least two independent local tasks, proposed-only criteria lifecycle, typed model availability, restart idempotence and no implementation/effects. They do not prove all business semantics.

The full semantic packet was235746 canonical characters. Initial alias packing needed eight parts, leaving insufficient Reviewer-project capacity for closure. These preflights reserved no SDK call. Existing row transport and exact shared-node references reduced repeated labels/identical fields to194120 characters. Six candidate parts of at most34000 characters each produced actual requests between27330 and 36063, all below45000. Composition of both reversible encoders was asserted to reconstruct every original field/value. The original frozen driver remained unchanged; a separate transport driver differs only by encoder import and candidate part size. Hashes, complete preflights and proof are in `review-transport-i-protocol.json` and capacity-preflight records. No source, rubric, grading threshold or Pello implementation was changed during this evaluation. No Planner rerun occurred.

All six parts entered the SAME independent Reviewer SDK session before grading. Receipts were explicitly not verdicts. The Reviewer then evaluated the complete original source, unchanged rubric and all plan artifacts. Criterion identity and citations were verified. Result: **23/24 critical PASS;24/25 total PASS (96%); FAIL**. This percentage is only the held-out rubric score, not global V1 completion.

Critical criterion **C13** failed. The persisted graph/manifest attaches P-7's unresolved dispute to all W04, preventing unrelated parcel review. It also attaches unresolved positive recovery policy to W05, blocking its independent local authorization/history/overview/refusal safeguards. The prose and contracts promise these capabilities remain available, but enforced blockers prevail. After W01, W02, W03 are hypothetically completed, scheduler readiness is empty. W04-AC04 and W05-AC11 conflict with those eligibility decisions.

Reproduction: reconstruct the unchanged plan; call `IncrementalPipeline.inspect_planned_manifest(plan['manifest'], completed={'W01', 'W02', 'W03'})`; inspect W04's `specification:ISS-f1ee3142ec14` and W05's `specification:ISS-bf95e4f6bde7`. Compare the original source and cited criteria. This is artifact/scheduler inspection, not an executed business-product test.

Independent diagnosis classified the cause as mixed: earliest semantic mismatch in requirement/issue scope granularity, then architecture references; the validator correctly applies its conservative intersection rule. No validator weakening is justified. It separately confirmed the deterministic model-budget context mismatch. Evidence: `heldout-i-semantic-review.json`, `heldout-i-evaluation.json`, `heldout-i-independent-failure-diagnosis.json`. Original FAIL and score were committed in **`06a6cb6`** before implementation correction.

## E. Localized engineering correction and preserved failures

Only the demonstrated capacity mismatch was corrected in `ProductPlanningCore.propose_models`. New requests compute post-selection capacity once and expose that same value to model selection, validation and aggregate reporting. A context marker distinguishes new capacity semantics from legacy pre-reservation inputs. Stored completed requests replay their original payload; old shortfalls are retained. No usable post-selection capacity blocks before a new reservation. Model policy, aggregate-warning behavior, validators, PipelineManifest and authorization rules remain unchanged.

Four new checks were hashed/copied outside implementation scope before code modification. Baseline:4 tests, 3 FAIL; original transcript preserved. Corrected code:40 focused PASS, 4/4 protected-copy PASS, 261/261 full PASS and independent engineering Reviewer PASS. New/missing-stage/legacy replay use real Core/SQLite with a controlled engine; **they are not a real SDK efficacy demonstration**. Accepted engineering implementation/checkpoint: **`8e70f3ed7be79f91380095ce1334b2379915a40e`**, supported by `model-capacity-correction/accepted-regression-checkpoint.json` and its full review input/output.

This engineering change does **not** fix C13, constitute autonomous Pello self-repair or accept the failed plan. Neither the original I source/rubric/plan nor any earlier FAIL was altered. I was not rerun after the change and cannot be reused as untouched blind evidence. Another complete fresh evaluation needs more capacity than remains; no case J was prepared or launched.

| Case | Original verdict | Earliest stopping point | Semantic score |
|---|---|---|---|
| CanalShare | FAIL | Interpretation-review context | Not scored: plan incomplete |
| ArchiveLedger | FAIL | Interpretation authorization invariant | Not scored: plan incomplete |
| KilnBook | FAIL | Interpretation-review context | Not scored: plan incomplete |
| FolioPay | FAIL | Architecture requirement/resource classification | Not scored: plan incomplete |
| StackProof | FAIL | Increment context | Not scored: plan incomplete |
| AssemblyCount | FAIL | Contract context | Not scored: plan incomplete |
| StageMark | FAIL | Interpretation-review context | Not scored: plan incomplete |
| CueConform | FAIL | Architecture prerequisite validation | Not scored: plan incomplete |
| ParcelProof | FAIL | Complete plan; critical semantic scope C13 | 23/24 critical;24/25 total |

Earlier localized corrections and their original FAIL/BLOCKED evidence remain in their committed records and archived reports. The complete pre-continuation report is preserved at `interim-reports/before-continuation114-evaluation-report.md`. Current review/transport size rejections were stopped before reservation; their packets/logs remain. They were not reclassified as successful planning results.

## F. Current regression, integrity, accounting and checkpoints

Actual complete regression: **261/261 PASS**, exit0, 261.297 seconds. C2 protected suites: **63/63 PASS** with original source and protected-copy hashes intact. C3 now has44 protected defect checks across12 source files, including the four new capacity checks. The 63 and 44 overlap the full 261; they are not additional unique tests. See `model-capacity-regression.json`, `model-capacity-protected.json`, `model-capacity-integrity.json` and complete logs.

Historical hashes: **1493/1493 matching**. First28 operations, four original projects, and all first 88 pre-continuation operation rows remain unchanged. All 27 SQLite checkpoint Git objects exist. Master, frozen objective script, rubric/source identities and protected tests are intact. SQLite integrity is `ok`; no uncertain/in-flight operation remains. C2 digest and rejected I digest reconstruct unchanged with no additional SDK call. I has no accepted-plan checkpoint.

Final accounting: **108/114 charged reservations**, **104 completed SDK calls**, one retained provider-quota failure, two retained active-writer rejections and one retained context-rejected historical reservation. **6 global slots remain**; author 15/18. Deadline remains October 27, 06:30 UTC. All 20 new SDK calls completed within authorization; counters were not reset. STOP remains absent. Snapshot: `evidence\phase3c3\checkpoint-108-jobs.sqlite3`, SHA-256 `5bc52b75f573f672d90d2e9558e0b32994e1bfec2b1f6603d8d9c675871cb68f`. Complete state: `checkpoint-108-state.json`.

The final independent preservation review returned **PASS for partial-checkpoint preservation only**, with Phase 3C acceptance explicitly prohibited. It did not override the semantic FAIL. Evidence: `partial-i-final-review.json`, bound to its actual input hash and SDK thread/turn. Oversized preservation metadata was stopped before SDK submission; repeated already-received verdict prose and duplicate Git references were factored without removing new code/test evidence.

External business operations: **zero**. Business Coder calls: **zero**. No n8n workflow operations, webhooks, messages, customer data, Railway provisioning, config/MCP changes or Phase 3D work occurred. Real integration evidence is the Codex SDK and existing local planning pipeline. No live cadastral integration is claimed.

## G. Final verdict and limitations

**Phase 3C-3 PARTIAL; overall Phase 3C PARTIAL.** The first complete autonomous held-out plan is durable and inspectable, but no accepted blind plan exists. The original critical semantic defect remains unresolved. The budget-context engineering correction is accepted within its narrow tested scope. Fresh real SDK efficacy after that correction remains unverified, as does real SDK architecture recovery.

Final implementation HEAD: `8e70f3ed7be79f91380095ce1334b2379915a40e`. Original blind FAIL checkpoint: `06a6cb6`. Final state/checkpoint receipt: `checkpoint-108-state.json`; the subsequent reporting-only delivery HEAD is recorded in the companion delivery receipt and final response. Existing accepted C1/C2 checkpoints remain valid. The repository was not reset and historical results were not rewritten.

`PELLO_PHASE3C_FINAL_REPORT.md` remains the earlier historical document; no new accepted Phase 3C consolidation is generated because the acceptance condition is unmet. No global V1 percentage is inferred from rubric scores or engineering test counts. **V1-20 remains NOT COMPLETE.**

The next necessary Phase 3C work is to resolve structured blocker scope against the consumed regression evidence, preserve conservative safety semantics, independently review any justified small change, and then fund/freeze a different unseen complete evaluation. Do not tune I and call it blind. No further case can be completed with the six-slot reserve. The later multi-increment business implementation milestone remains a recommendation conditional on valid Phase 3C acceptance; no Phase 3D files or execution were started.

## H. Evidence mapping to all 23 V1.3 criteria

Scoped Phase 3C evidence only. Previous milestones retain their own historical evidence. No row below declares the entire V1 complete.

| Criterion | Current evidence scope | Evidence or limitation |
|---|---|---|
| V1-01 | PARTIAL | C1/C2 remain accepted. ParcelProof generated a complete plan but failed critical semantic scope C13; generalization is unverified. |
| V1-02 | PARTIAL | Eight autonomous increments, valid DAG, eight contracts and 86 proposed criteria; enforced blocker scope is semantically wrong. |
| V1-03 | SUPPORTING | 261 engineering tests, 63 protected C2 checks and 44 protected C3 checks; these overlap. No business-product tests generated/protected/executed. |
| V1-04 | PARTIAL | Real SDK planning stages chained into existing PipelineManifest. No multi-increment business Coder/Tester implementation. |
| V1-05 | NOT_ESTABLISHED_BY_C3 | Architecture retry has controlled-engine tests; initial ParcelProof architecture was structurally valid, so retry was not exercised. Budget repair was made by the engineering session. |
| V1-06 | SCOPED_POLICY_EVIDENCE | Typed task-specific Luna Low/Medium/High and justified initial Sol High with actual catalog. No real runtime business escalation demonstrated. |
| V1-07 | NO_NEW_C3_EVIDENCE | No n8n operations in C3; historical accepted integration results retain their own evidence. |
| V1-08 | NO_NEW_C3_EVIDENCE | No publishing in this phase. |
| V1-09 | PARTIAL | Real Codex SDK and local planning/persistence integration verified; no live business integration tests. |
| V1-10 | NOT_ESTABLISHED_BY_C3 | External cadastral operations were unavailable and unauthorized, with no verified business effects. |
| V1-11 | SUPPORTING_LOCAL_EVIDENCE | Git checkpoints, 27 SQLite checkpoint objects, original FAILs and immutable source/plan identities preserved; no new production configuration restoration. |
| V1-12 | SCOPED_REAL_EVIDENCE | C2 accepted plan and ParcelProof proposed plan reconstruct with stable digests and no extra inference or duplicate plan history. |
| V1-13 | SUPPORTING_INCOMPLETE | Historical provider/writer reconciliation retained. Controlled-engine new/legacy model replay preserves reservations; broader business recovery remains unproven. |
| V1-14 | PARTIAL | Eight actual planning invocations chained without human technical manifest transfer. Long-running enterprise implementation/delivery remains unverified. |
| V1-15 | NOT_ESTABLISHED_BY_C3 | Local reports only; no daily emails sent. |
| V1-16 | PRESERVED_NO_NEW_LIVE_MCP_PROOF | Native SDK evaluation deny profiles verified; no MCP business operations or alternative production access. |
| V1-17 | SCOPED_VERIFIED_EVIDENCE | Explicit append-only114/author 18 authorization, conserved charges/deadline/STOP controls; post-reservation capacity mismatch corrected with protected replay tests. No product execution budget granted. |
| V1-18 | PARTIAL_CRITICAL_GAP | P-7 contradiction, missing agency details and unapproved assumptions identified; scope granularity wrongly blocks unrelated local work. |
| V1-19 | SCOPED_REAL_EVIDENCE | Separate author/Planner/Reviewer contexts, native rubric denial, frozen criteria and independently preserved semantic FAIL. Reviewer PASS cannot override a critical FAIL. |
| V1-20 | NOT_COMPLETE | No complete business software product implemented, integrated, tested or delivered in C3. |
| V1-21 | SUPPORTING_LOCAL_EVIDENCE | STOP/budget regression preserved, STOP remains absent. No new production STOP/lifecycle incident demonstrated. |
| V1-22 | NO_NEW_C3_EVIDENCE | Synthetic local data only; no production test resources created. |
| V1-23 | NO_NEW_C3_EVIDENCE | No workflow creation, MCP exposure or access handoff. Earlier milestones retain their own evidence. |
