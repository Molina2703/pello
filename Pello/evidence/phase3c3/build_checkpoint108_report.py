"""Report the bounded continuation honestly; never promote the retained FAIL."""
import hashlib,json,re,subprocess
from pathlib import Path
out=Path('evidence/phase3c3')
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
s=read('checkpoint-108-state.json');e=read('heldout-i-evaluation.json');f=read('heldout-i-freeze.json')
assert e['verdict']=='FAIL' and s['phase3c3']==s['overall_phase3c']=='PARTIAL'
review=read('partial-i-final-review.json');assert review['review']['verdict']=='PASS' and not review['Phase3C_accepted']
engineering=read('model-capacity-correction/accepted-regression-checkpoint.json');assert engineering['status']=='ACCEPTED_ENGINEERING_CORRECTION_ONLY'
p=read('heldout-i-plan.json')['plan'];a=p['requirements'];st=p['stages'];semantic=read('heldout-i-semantic-review.json')
mapping=read('criteria-coverage-i.json')['criteria'];assert len(mapping)==23
main=Path('PELLO_PHASE3C3_EVALUATION_REPORT.md');archive=out/'interim-reports/before-continuation114-evaluation-report.md'
if not archive.exists():archive.write_bytes(main.read_bytes())
impl=s['accepted_engineering_checkpoint']['implementation_HEAD']
models={r['task_id']:r for r in st['models']['records']}
task_rows=[]
for node in st['architecture']['proposal']['nodes']:
    m=models[node['task_id']]
    task_rows.append('| '+node['task_id']+' | '+node['objective'].split(' [SRC-')[0].replace('|','/')+' | '+(', '.join(node['depends_on']) or 'None')+' | '+m['selected_model_profile']+' / '+m['selected_reasoning_effort']+' |')
issues='\n'.join('| '+i['issue_id']+' | '+i['severity']+' | '+i['description'].replace('|','/')+' |' for i in a['issues'])
criteria='\n'.join('| '+r['id']+' | '+r['status']+' | '+r['evidence_or_limitation']+' |' for r in mapping)
names={'a':'CanalShare','b':'ArchiveLedger','c':'KilnBook','d':'FolioPay','e':'StackProof','f':'AssemblyCount','g':'StageMark','h':'CueConform','i':'ParcelProof'}
stops={'a':'Interpretation-review context','b':'Interpretation authorization invariant','c':'Interpretation-review context','d':'Architecture requirement/resource classification','e':'Increment context','f':'Contract context','g':'Interpretation-review context','h':'Architecture prerequisite validation','i':'Complete plan; critical semantic scope C13'}
old_rows='\n'.join('| '+names[k]+' | FAIL | '+stops[k]+' | '+('23/24 critical;24/25 total' if k=='i' else 'Not scored: plan incomplete')+' |' for k in names)
report=f'''# Pello V1.3 — Phase 3C-3 Evaluation Report

Reference date: October25,2026. Continuation closeout: {s['at']}.

**Phase3C-3: PARTIAL. Overall Phase3C: PARTIAL. Blind generalization: UNVERIFIED.** C1 and C2 remain ACCEPTED. ParcelProof produced the first complete held-out planning artifact, but independent evaluation found a critical semantic error. A96% total rubric score cannot override a failed critical criterion. Nine original blind FAILs remain preserved.

This report describes planning and Pello engineering evidence. No business software was implemented, published, tested or delivered. Phase3D was not started. Paths below are relative to the Pello directory.

## A. Initial state and authorization

Read-only verification began at branch `codex/pello-phase3c`, HEAD `0ab160e9c50397780a0dcf6f568ccca5992aafa1`. Git root was the parent DESARROLLO PELLO directory. No reset occurred. The accepted engineering implementation was `94c2bb9b8f7174bf06afe8758df5b11926421b88`; delivery checkpoint `6020a3d0640f5d115200aee19dc85ab9a2046be5` and later preservation-only commits were retained. Preexisting unrelated/untracked artifacts were preserved.

SQLite integrity was `ok`, STOP absent, all25 historical SQLite checkpoint Git objects present, no uncertain/in-flight operation, and1493/1493 historical hashes matched. The ledger held88 charged reservations,84 completed SDK calls, and four retained historical failure/non-submission charges. Author usage was14/14. The last full accepted regression was257/257; C2 protected baseline63/63. The first28 operation rows and four original projects were unchanged. The accepted C2 digest reconstructed unchanged: `7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87`.

The earlier proposal114/author18 had been declined. The new explicit user reply, **“Autorizo114 globales, autor18 y ese plazo”**, authorized one bounded fresh case and justified localized correction/review until **October27,2026,06:30 UTC /01:30 Colombia**. `authorization-extension-114.json` and the append-only SQLite grant record this approval, preserving88 global and14 author charges. Other project caps remained12. No replacement author project or counter reset occurred. This grant superseded the previous preservation decision only for the newly approved scope.

Initial verification reran40 existing focused checks. One runner invocation failed to import a top-level test helper; its transcript remains `continuation114-focused-runner-FAIL.log`. Correcting the invocation's search path yielded40/40 PASS without implementation changes. The unchanged-validator AST and C2 reconstruction evidence is in `continuation114-recovery-verification.json`. The master v1.3 byte hash remains `6bca1e0b8d871201601e83b6cdbeadb0554fa52be18a8d624a29ca46ca44674d`.

## B. Independent evaluation preparation

**ParcelProof**, identity `{f['evaluation_id']}`, version1, was independently authored in the existing authorized evaluation-author SDK context. That context is separate from Pello Planner and evaluation Reviewer and received no Planner outputs or technical solution. The business domain is survey-point validation, exact parcel geometry, disputes, approval and cadastral submission. It differs from the eight consumed cases, Vendor Return Desk and HMP/ADSA demos. It contains meaningful rules, exclusions, dependencies, two independent local branches, external integration gaps, a genuine P-7 contradiction, reversible assumptions and exact-package authorization restrictions.

Source: `heldout-i-spec.md`,6662 characters. Frozen at `{f['created_at']}`. Source SHA-256: `{f['specification_sha256']}`. Original private rubric SHA-256: `{f['rubric_sha256']}`. All24 critical criteria and at least90% of25 total criteria must pass. Critical failures include missing mandatory capabilities, exclusion violations, unauthorized assumptions/effects, ignored contradictions, invalid dependencies, executable blocked work, manifest incompatibility and false product-test claims.

The private rubric stayed outside Planner's working surface in the existing denied evaluation directory. Native profile `pello_supplied_context` extends read-only, denies key/author/ledger/evaluation/Reviewer/transcript paths, and disables network access. Supplied-context SDK roles also disable command, image, host-code, browser, computer, app/plugin/MCP and automatic project-document/skill/memory surfaces. The worker verifies effective profile identity before inference. Actual submitted contexts contain no evaluator-key fields.

All15 native root checks passed: one readable public control and14 denied roots. Both exact-key Windows alias checks denied reads, with same-file and hash proof. All eight real Pello SDK submission receipts passed the actual isolation audit. Evidence: `full-boundary-i-objective.json`, `rubric-i-alias-proof.json`, `heldout-i-actual-isolation-audit.json`, `isolation/` and runtime submission receipts. Official documentation describes the [Codex Python SDK](https://learn.chatgpt.com/docs/codex-sdk) and [filesystem deny permissions](https://learn.chatgpt.com/docs/permissions); the local probes establish this evaluation's actual boundary.

Independent preparation review PASS preceded Planner creation. Source/rubric expectations, structural checks and semantic grading source were registered at `batch1-i-checkpoint.json` and committed in **`ba9380e`** before the first Planner invocation. The original rubric and grading gates were not rewritten after seeing results. The consumed rubric was exported unchanged only after the semantic FAIL, with timing/hash evidence in `consumed-rubrics-i-publication.json`; the private original remains intact.

## C. Actual autonomous planning run

Existing `ProductPlanningCore.plan_product` ran through the real authorized SDK: understand → independent interpretation review → architecture → increments → three contract batches → model decisions → durable plan/manifest. Eight Pello SDK invocations completed. The Planner received the original source, authorized inventory/constraints and its own preceding structured outputs; no manually prepared architecture, increments, contracts or manifest were supplied.

The complete result contains **35 requirements,6 issues,5 unapproved assumptions,8 architecture nodes,8 functional increments,8 contracts and86 proposed acceptance criteria**. Exclusions, source IDs, permissions and proposed completion conditions remain inspectable in `heldout-i-plan.json`. Issues:

| Issue | Severity | Description |
|---|---|---|
{issues}

| Increment | Autonomous objective | Dependencies | Proposed Coder configuration |
|---|---|---|---|
{chr(10).join(task_rows)}

Initial planning readiness was W01 and W02; **first actionable increment W01**. This means ready to prepare protected tests and request execution authorization. It is not permission to execute. Two external-operation branches remain unauthorized/unavailable. The graph is acyclic and structurally covers the source, but its enforced blocker scope is semantically wrong as described below.

The architecture passed structural validation on its first attempt. **The bounded architecture retry was not exercised through this SDK run.** Its prior controlled-engine evidence remains accepted; real SDK recovery efficacy is still unverified. No artificial error was injected to force that path.

The existing context mechanism split contract generation into3/3/2 increments. Each request retained the full original requirements and exact supplied increment fields. Exact comparison proved submitted prompts match generated prompts, all eight increment records survive batching unchanged, and the merged eight contracts equal the complete ordered batch responses. Existing aggregate validation and PipelineManifest conversion passed. Evidence: `heldout-i-actual-contract-batching.json` and runtime `contracts-context-batches.json`.

Models were selected adaptively from the actual catalog: Luna Low/Medium/High and specifically justified initial Sol High for exact topology. These are future Coder assignments, not executed Coder calls. The original model request advertised17 available turns while validation/reporting used16; the original plan truthfully retains the resulting one-turn shortfall. This accounting defect was corrected later for new requests, without editing the failed plan.

Plan digest: `{e['plan_sha256']}`. SQLite history has one plan row; a separate CLI process reconstructed the same plan without additional inference. Existing `IncrementalPipeline.inspect_planned_manifest` consumed the generated manifest without manual technical translation. Stable IDs, stage hashes and plan identity survived restart and the later engineering correction. Approval remains **PROPOSED**, execution authorization **false**. No business-product Python implementation exists in the project workspace. All86 criteria remain proposed; product tests are not generated, protected or executed.

## D. Independent semantic and structural evaluation

Frozen structural checks: **10/10 PASS**. They establish source/rubric identity, traceability, coverage, valid manifest/DAG, ineligible blocked/external work, at least two independent local tasks, proposed-only criteria lifecycle, typed model availability, restart idempotence and no implementation/effects. They do not prove all business semantics.

The full semantic packet was235746 canonical characters. Initial alias packing needed eight parts, leaving insufficient Reviewer-project capacity for closure. These preflights reserved no SDK call. Existing row transport and exact shared-node references reduced repeated labels/identical fields to194120 characters. Six candidate parts of at most34000 characters each produced actual requests between27330 and36063, all below45000. Composition of both reversible encoders was asserted to reconstruct every original field/value. The original frozen driver remained unchanged; a separate transport driver differs only by encoder import and candidate part size. Hashes, complete preflights and proof are in `review-transport-i-protocol.json` and capacity-preflight records. No source, rubric, grading threshold or Pello implementation was changed during this evaluation. No Planner rerun occurred.

All six parts entered the SAME independent Reviewer SDK session before grading. Receipts were explicitly not verdicts. The Reviewer then evaluated the complete original source, unchanged rubric and all plan artifacts. Criterion identity and citations were verified. Result: **23/24 critical PASS;24/25 total PASS (96%); FAIL**. This percentage is only the held-out rubric score, not global V1 completion.

Critical criterion **C13** failed. The persisted graph/manifest attaches P-7's unresolved dispute to all W04, preventing unrelated parcel review. It also attaches unresolved positive recovery policy to W05, blocking its independent local authorization/history/overview/refusal safeguards. The prose and contracts promise these capabilities remain available, but enforced blockers prevail. After W01,W02,W03 are hypothetically completed, scheduler readiness is empty. W04-AC04 and W05-AC11 conflict with those eligibility decisions.

Reproduction: reconstruct the unchanged plan; call `IncrementalPipeline.inspect_planned_manifest(plan['manifest'], completed={{'W01','W02','W03'}})`; inspect W04's `specification:ISS-f1ee3142ec14` and W05's `specification:ISS-bf95e4f6bde7`. Compare the original source and cited criteria. This is artifact/scheduler inspection, not an executed business-product test.

Independent diagnosis classified the cause as mixed: earliest semantic mismatch in requirement/issue scope granularity, then architecture references; the validator correctly applies its conservative intersection rule. No validator weakening is justified. It separately confirmed the deterministic model-budget context mismatch. Evidence: `heldout-i-semantic-review.json`, `heldout-i-evaluation.json`, `heldout-i-independent-failure-diagnosis.json`. Original FAIL and score were committed in **`06a6cb6`** before implementation correction.

## E. Localized engineering correction and preserved failures

Only the demonstrated capacity mismatch was corrected in `ProductPlanningCore.propose_models`. New requests compute post-selection capacity once and expose that same value to model selection, validation and aggregate reporting. A context marker distinguishes new capacity semantics from legacy pre-reservation inputs. Stored completed requests replay their original payload; old shortfalls are retained. No usable post-selection capacity blocks before a new reservation. Model policy, aggregate-warning behavior, validators, PipelineManifest and authorization rules remain unchanged.

Four new checks were hashed/copied outside implementation scope before code modification. Baseline:4 tests,3 FAIL; original transcript preserved. Corrected code:40 focused PASS,4/4 protected-copy PASS,261/261 full PASS and independent engineering Reviewer PASS. New/missing-stage/legacy replay use real Core/SQLite with a controlled engine; **they are not a real SDK efficacy demonstration**. Accepted engineering implementation/checkpoint: **`{impl}`**, supported by `model-capacity-correction/accepted-regression-checkpoint.json` and its full review input/output.

This engineering change does **not** fix C13, constitute autonomous Pello self-repair or accept the failed plan. Neither the original I source/rubric/plan nor any earlier FAIL was altered. I was not rerun after the change and cannot be reused as untouched blind evidence. Another complete fresh evaluation needs more capacity than remains; no case J was prepared or launched.

| Case | Original verdict | Earliest stopping point | Semantic score |
|---|---|---|---|
{old_rows}

Earlier localized corrections and their original FAIL/BLOCKED evidence remain in their committed records and archived reports. The complete pre-continuation report is preserved at `interim-reports/before-continuation114-evaluation-report.md`. Current review/transport size rejections were stopped before reservation; their packets/logs remain. They were not reclassified as successful planning results.

## F. Current regression, integrity, accounting and checkpoints

Actual complete regression: **261/261 PASS**, exit0,261.297 seconds. C2 protected suites: **63/63 PASS** with original source and protected-copy hashes intact. C3 now has44 protected defect checks across12 source files, including the four new capacity checks. The63 and44 overlap the full261; they are not additional unique tests. See `model-capacity-regression.json`, `model-capacity-protected.json`, `model-capacity-integrity.json` and complete logs.

Historical hashes: **1493/1493 matching**. First28 operations, four original projects, and all first88 pre-continuation operation rows remain unchanged. All27 SQLite checkpoint Git objects exist. Master, frozen objective script, rubric/source identities and protected tests are intact. SQLite integrity is `ok`; no uncertain/in-flight operation remains. C2 digest and rejected I digest reconstruct unchanged with no additional SDK call. I has no accepted-plan checkpoint.

Final accounting: **{s['charged_reservations']}/114 charged reservations**, **{s['completed_SDK_calls']} completed SDK calls**, one retained provider-quota failure, two retained active-writer rejections and one retained context-rejected historical reservation. **{s['remaining_global_slots']} global slots remain**; author15/18. Deadline remains October27,06:30 UTC. All20 new SDK calls completed within authorization; counters were not reset. STOP remains absent. Snapshot: `{s['backup_path']}`, SHA-256 `{s['snapshot_sha256']}`. Complete state: `checkpoint-108-state.json`.

The final independent preservation review returned **PASS for partial-checkpoint preservation only**, with Phase3C acceptance explicitly prohibited. It did not override the semantic FAIL. Evidence: `partial-i-final-review.json`, bound to its actual input hash and SDK thread/turn. Oversized preservation metadata was stopped before SDK submission; repeated already-received verdict prose and duplicate Git references were factored without removing new code/test evidence.

External business operations: **zero**. Business Coder calls: **zero**. No n8n workflow operations, webhooks, messages, customer data, Railway provisioning, config/MCP changes or Phase3D work occurred. Real integration evidence is the Codex SDK and existing local planning pipeline. No live cadastral integration is claimed.

## G. Final verdict and limitations

**Phase3C-3 PARTIAL; overall Phase3C PARTIAL.** The first complete autonomous held-out plan is durable and inspectable, but no genuinely accepted blind plan exists. The original critical semantic defect remains unresolved. The budget-context engineering correction is accepted within its narrow tested scope. Fresh real SDK efficacy after that correction remains unverified, as does real SDK architecture recovery.

Final implementation HEAD: `{impl}`. Original blind FAIL checkpoint: `06a6cb6`. Final state/checkpoint receipt: `checkpoint-108-state.json`; the subsequent reporting-only delivery HEAD is recorded in the companion delivery receipt and final response. Existing accepted C1/C2 checkpoints remain valid. The repository was not reset and historical results were not rewritten.

`PELLO_PHASE3C_FINAL_REPORT.md` remains the earlier historical document; no new accepted Phase3C consolidation is generated because the acceptance condition is unmet. No global V1 percentage is inferred from rubric scores or engineering test counts. **V1-20 remains NOT COMPLETE.**

The next necessary Phase3C work is to resolve structured blocker scope against the consumed regression evidence, preserve conservative safety semantics, independently review any justified small change, and then fund/freeze a different unseen complete evaluation. Do not tune I and call it blind. No further case can be completed with the six-slot reserve. The later multi-increment business implementation milestone remains a recommendation conditional on valid Phase3C acceptance; no Phase3D files or execution were started.

## H. Evidence mapping to all23 V1.3 criteria

Scoped Phase3C evidence only. Previous milestones retain their own historical evidence. No row below declares the entire V1 complete.

| Criterion | Current evidence scope | Evidence or limitation |
|---|---|---|
{criteria}
'''
report=report.replace('Phase3C','Phase 3C').replace('Phase3D','Phase 3D').replace('A96%','A 96%').replace('genuinely accepted','accepted')
report=re.sub(r'\b(October|all|All|and|of|held|preserving|author|autor|Autorizo|version|first|full|The)(?=\d)',r'\1 ',report)
report=re.sub(r',(?=\S)',', ',report)
main.write_text(report,encoding='utf-8')
snapshot=out/'interim-reports/checkpoint-108-reservations-PARTIAL.md';assert not snapshot.exists();snapshot.write_bytes(main.read_bytes())
print(json.dumps({'status':'PARTIAL','report':str(main),'report_sha256':hashlib.sha256(main.read_bytes()).hexdigest(),'engineering_HEAD':impl,'criteria_mapped':len(mapping)},indent=2))
