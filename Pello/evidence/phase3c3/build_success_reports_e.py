"""Only emit ACCEPTED reports after existing Core accepted the independently reviewed plan."""
import hashlib,json,subprocess
from pathlib import Path
out=Path('evidence/phase3c3')
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
accepted=read('accepted-plan-checkpoint.json');assert accepted['accepted']['approval']=='ACCEPTED'
evaluation=read('heldout-e-evaluation.json');assert evaluation['verdict']=='PASS'
assert read('final-review.json')['verdict']=='PASS'
state=read('closure-state.json');reg=read('final-regression.json');integrity=read('final-integrity.json')
assert reg['exit_code']==0 and integrity['historical_hashes_matching']==1493
plan=accepted['accepted']['plan'];analysis=plan['requirements'];st=plan['stages'];inspection=accepted['inspection']
f=read('heldout-e-freeze.json');semantic=read('heldout-e-semantic-review.json');obj=read('heldout-e-objective.json')
digest=accepted['accepted']['plan_sha256'];count=reg['tests_run']
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
implementation_head=subprocess.check_output(['git','log','-1','--format=%H','--','athis_autopilot'],text=True).strip()
case_names={'a':'CanalShare','b':'ArchiveLedger','c':'KilnBook','d':'FolioPay','e':'StackProof'}
case_rows=[];hash_rows=[]
for letter,name in case_names.items():
    freeze=read(f'heldout-{letter}-freeze'+('-v2' if letter=='a' else '')+'.json')
    verdict=read(f'heldout-{letter}-evaluation.json')['verdict']
    case_rows.append(f"| {name} | {freeze['evaluation_id']} | {verdict} | {freeze['created_at']} |")
    hash_rows.append(f"| {name} | `{freeze['specification_sha256']}` | `{freeze['rubric_sha256']}` |")
issue_rows=[]
for issue in analysis['issues']:
    issue_rows.append(f"| {issue['issue_id']} | {issue['severity']} | {str(issue.get('description',issue.get('summary',issue))).replace('|','/')} |")
nodes=st['architecture']['proposal']['nodes'];increments=st['increments']['proposal']['increments'];contracts=st['contracts']['proposal']['contracts']
task_rows=[]
models={r['task_id']:r for r in st['models']['records']}
for inc in increments:
    m=models[inc['task_id']]
    task_rows.append(f"| {inc['task_id']} | {inc.get('title',inc.get('name',''))} | {', '.join(inc['depends_on']) or '—'} | {m['selected_model_profile']} / {m['selected_reasoning_effort']} |")
cp=[x for x in state['checkpoints'] if x['project_id']=='phase3c3-heldout-e' and x['phase']=='plan-accepted']
assert len(cp)==1
checkpoint=cp[0]['commit_sha']
tests=sum(len(c['criteria']) for c in contracts)
minor='; '.join(semantic['minor_findings']) or 'No minor finding reported.'
critical='; '.join(semantic['critical_failures']) or 'None in the accepted StackProof evaluation.'
semantic_passed=sum(c['verdict']=='PASS' for c in semantic['criteria'])
report=f'''# Pello V1.3 — Phase 3C-3 Evaluation Report

Reference date: October 25, 2026. Evidence closeout: {state['at']}.

**Phase 3C-3: ACCEPTED. Overall Phase 3C: ACCEPTED at planning level.** StackProof passed the genuinely new, independently prepared blind evaluation, all mandatory objective gates and independent final review. Four earlier blind FAILs remain FAIL. No business product was implemented or delivered. Phase 3D was not started.

Paths below are relative to the Pello directory. Full structured artifacts remain authoritative; counts of engineering tests do not represent product implementation.

## A. Initial state

Branch `codex/pello-phase3c`; initial HEAD `c1bb076e7059100f0c4b5abf623625d2843f0be2`, reporting successor to accepted C2 implementation `90ea13053fa31bf12b4031b45e5f5e620bc86331`. Git history was inspected without reset. Three unrelated untracked context artifacts were preserved.

Initial SQLite integrity was `ok`, fourteen prior checkpoint commits existed, STOP was absent, and the ledger contained 28 completed SDK turns against the historical cap 30. That historical authorization expired October 25 at 21:14:29 UTC. Accepted C1/C2 reports, project chat, journal, authorization rows and historical evidence were reconciled. Baseline recomputed 1493/1493 hashes and reran 63/63 protected checks. Historical full-suite count was 217.

The user explicitly authorized 60 cumulative turns until October 26 00:45 UTC, then 75 until 03:30 UTC, and finally extended only the deadline to **October 26 06:30 UTC / 01:30 Colombia**. Append-only grants are preserved in `authorization.json`, `authorization-extension-75.json` and `authorization-deadline-0630.json`; no counters were reset. At closure: **{state['sdk_charged_reservations']}/75 charged reservations**, comprising {state['actual_completed_sdk_calls']} completed actual SDK calls, one terminal provider-quota failure and one conservatively retained never-submitted reservation. Remaining authorized slots: {state['remaining_authorized_slots']}. STOP stayed absent; no external business operations were authorized or executed. Evidence: `initial-state.json`, `baseline-protected.json`, `closure-state.json` and the hashed SQLite backup.

## B. Evaluation preparation

An independent SDK author session created each synthetic business source and private outcome rubric without receiving Planner outputs, technical designs or manual increments. Separate Reviewer sessions assessed preparation and results. Every new case used the existing ledger and per-project limit 12. Projects were never recreated to evade consumption.

| Case | Frozen identity | Actual planning verdict | Frozen at UTC |
|---|---|---|---|
{chr(10).join(case_rows)}

| Case | Specification SHA-256 | Rubric SHA-256 |
|---|---|---|
{chr(10).join(hash_rows)}

StackProof has {f['total_criteria']} frozen criteria, including {f['critical_criteria']} critical. All critical criteria and at least 90% overall must pass. Mandatory failures include omitted capabilities, violated exclusions, unauthorized assumptions/effects, ignored contradictions, invalid dependencies, executable blocked work, incompatible PipelineManifest and false product-test claims. Source quotes, timestamps and hashes were frozen before Planner creation. Structural checks and the semantic-grading source were registered at `batch1-e-checkpoint.json`, committed before inference at `cdf7166`.

CanalShare preparation v1 failed for evaluator defects; independently revised v2 was frozen before its Planner run, with source unchanged. ArchiveLedger preparation required additional Windows alias proof. Their earlier records remain. No rubric was changed after observing that case's Planner result.

Read-only access alone was insufficient, so a reviewed opt-in adapter correction selected the existing native named permission profile. It denies the private key directory, author artifacts, SQLite, evaluator evidence, Reviewer workspaces and Codex transcripts. Supplied-context reasoning roles also lose command/image/browser/computer/app/plugin/host-code and automatic project/skill/memory reading surfaces. The worker verifies the actual returned profile and instruction-source receipt before inference and enforces profile identity on resume. Ordinary executor behavior remains unchanged. `shell_tool=false` is the effective command gate; `unified_exec=false` alone is not treated as enforcement.

Native positive controls read public data; all eleven E boundary controls passed, and exact frozen rubric paths plus their packaged/normal Windows aliases returned PermissionError. Parent same-file/hash checks establish alias identity. Reviewer preparation PASS records the limits of independently rerunning private checks. Raw native transcripts and actual SDK profile receipts support the boundary. Merely asking Planner not to read was not used as blindness. Private E material was not added to Git before the Planner completed. Evidence: `isolation/`, `full-boundary-e-objective.json`, `rubric-e-alias-proof.json`, freeze/preparation/checkpoint records and actual submission receipts.

## C. Actual planning run

The existing `ProductPlanningCore.plan_product` executed understand → independent interpretation review → architecture → increments → contracts → model decisions → persistence, using real authorized SDK calls. Inputs were only StackProof source, existing inventory and constraints. No hand-written technical manifest or business Coder call was supplied.

The result contains **{len(analysis['requirements'])} requirements, {len(analysis['issues'])} issues, {len(analysis['assumptions'])} assumptions, {len(nodes)} architecture nodes, {len(increments)} functional increments, {len(contracts)} contracts and {tests} proposed criteria**. Source references and exclusions remain in `heldout-e-plan.json`. Architecture components and graph are in `plan.stages.architecture`; contracts define concrete inputs/outputs, edge/error behavior and observable criteria. Model decisions include actual backend availability snapshots, typed efforts and per-task risk/context/budget justifications. No fixed escalation ladder was added.

| Increment | Functional capability | Prerequisites | Proposed Coder model / effort |
|---|---|---|---|
{chr(10).join(task_rows)}

The existing PipelineManifest consumed the generated plan without manual translation. First actionable increment: **{inspection['first_actionable']}**. Full readiness and blocked reasons: `heldout-e-pipeline-inspection.json` and objective scheduler-state proof. NOx policy/limits and unavailable portal contract/permissions remain scoped blockers; independent local work remains actionable. The full generated manifest is persisted under the project's `planning/execution-manifest.json`. Plan SHA-256: `{digest}`.

The first architecture request terminated with provider `usageLimitExceeded` and no assistant output. Read-only thread inspection reconciled it; its charge remains. An attempted recovery was stopped by the expired deadline before reserving a new turn. After the explicit 06:30 extension, a separately charged recovery invoked existing `_invoke` with identical input/schema hashes, same model policy and unchanged architecture validator, then resumed ordinary `plan_product`. No source/rubric/design changed, no model switch or quota reset occurred, and no uncertain attempt was blindly repeated. Receipts: `sdk-provider-block-reconciliation.json`, `provider-recovery-renewed-authorization.json`, `resumed-planning-e.log`.

All business acceptance criteria remain **proposed**; product tests are not generated, protected or executed. Execution authorization remains false even after planning acceptance. No business implementation automatically starts.

## D. Independent evaluation

Structural objective results: **{obj['checks_passed']}/{obj['checks_run']} PASS**. They check frozen identities/source anchors, requirement coverage, real manifest and DAG, every reachable scheduler state for unauthorized/blocked work, useful local progress, contract lifecycle, actual typed model catalog, separate-process restart/idempotence and absence of business implementation.

Frozen semantic evaluation: **{sum(c['verdict']=='PASS' for c in semantic['criteria'])}/{len(semantic['criteria'])} PASS**, all critical criteria PASS, valid criterion identities and evidence citations. The Reviewer evaluated the original StackProof source and exact frozen expectations, not merely Pello's summary. Numerical and business-rule coverage, contradictions, narrow blockers, permissions, graph, contracts, models and persistence were assessed. Critical defects: {critical} Minor findings: {minor}

Semantic and final Reviewers used a separate session from Planner and received no private Planner reasoning. The evaluation packet factors repeated quotes and IDs losslessly, with exact reconstruction proof; it does not edit expectations or invent results. Mandatory objective failures cannot be overridden. Final Engineering Reviewer verdict: **PASS**, followed by existing Core's hash-bound `approve_plan`, which saved `PLAN_ACCEPTED` and its checkpoint.

Evidence: `heldout-e-objective.json`, `heldout-e-semantic-review.json`, `heldout-e-evaluation.json`, `heldout-e-review-packing.json`, `final-review-input.json`, `final-review.json`, `accepted-plan-checkpoint.json`. Reproduce deterministic checks with the recorded `.venv/Scripts/python.exe -X utf8 -B evidence/phase3c3/objective_checks_e.py`; it consumes no SDK turn. Do not rerun a consumed case as a new blind demonstration.

## E. Corrections and preserved failures

1. CanalShare FAIL: duplicated original source overflowed the interpretation-review context after a charged but never-submitted reservation. Preserve FAIL and charge. Correction validates context before reservation and factors identical repeated source segments losslessly. Four protected defect checks and independent PASS.
2. ArchiveLedger FAIL: an authorization-category requirement emitted false `authorization_required`, violating an existing invariant. Correction clarifies the existing schema rule; no coercion or validator relaxation. Three protected checks and independent PASS.
3. KilnBook FAIL: review context remained too large after first factoring. Correction references only exactly matching source line ranges, retaining complete original source once; divergent text stays visible and the cap remains. Three protected checks and independent PASS.
4. FolioPay FAIL: architecture globalized business rules and treated available local inputs as separately missing resources. Correction changes only two schema descriptions to explain existing category/resource semantics; `validate_architecture` source is identical to C2. Three protected checks, 55 targeted PASS, independent PASS and exact C2 reconstruction without inference.

Before these cases, six protected isolation/profile tests verified the necessary opt-in blind boundary. Corrections were small engineering changes, not autonomous self-repair by Pello. Each consumed fixture remained FAIL; StackProof was independently authored and frozen afterward. Failure reproduction is in each original run log and raw rejected SDK output, with defect regression tests under `tests/`. Context preflight failures reserve no new turn; the older charged slot was retained and explicitly reconciled as never submitted. The prior 49-slot PARTIAL report is preserved under `interim-reports/`.

## F. Regression, integrity and checkpoints

Complete current local suite: **{count}/{count} PASS**, exit 0. C2 protected suites: **63/63 PASS**, with original source and protected-copy hashes intact. The 63 overlap the full suite; they are not additional unique tests. Nineteen new protected Phase 3C-3 defect checks are included in the full suite. Full run command and duration: `final-regression.json`; logs preserve actual unittest counts.

Historical integrity: **1493/1493 hashes match**. First 28 SDK operation rows and all four original project rows match their initial identities. Master specification, C1/C2 evidence, old FAIL/BLOCKED records and checkpoint history were preserved. SQLite integrity `ok`; every checkpoint Git object verified. Accepted C2 plan reconstructs with the same digest and no extra SDK turn or duplicate plan. Separate-process StackProof reconstruction also preserves digest, history count and budget. New protected-test hashes and frozen objective source remain intact. Evidence: `final-integrity.json`, `final-protected.json`, C2 reconstruction records and `closure-state.json`.

STOP and hard-budget tests remain in the full suite; actual SDK submissions retained their authoritative gates. Final acceptance checkpoint in StackProof workspace: `{checkpoint}`. Source implementation HEAD: `{implementation_head}`. Code/evidence closure HEAD: `{head}`; the subsequent report-only Git commit is identified by the final delivery receipt. SQLite backup SHA-256: `{state['snapshot_sha256']}`.

External business operations: **zero**. No n8n workflow mutations/readbacks, production webhook requests, messages, customer-data changes, Railway provisioning, new servers or `config.toml`/MCP reconfiguration occurred. Protected workflow IDs were never operated. Real integration evidence here means the Codex backend and existing local Pello planning pipeline; no live regulator portal integration is claimed.

## G. Final verdict and limitations

**Phase 3C-3 ACCEPTED; overall Phase 3C ACCEPTED within planning scope.** Evidence is one valid fresh blind PASS after four retained FAILs, not universal reliability. The accepted plan, objective and semantic gates, complete regression, historical preservation and independent final review support this bounded conclusion.

The complete enterprise business product, production publishing, business-product testing, broad long-running delivery and runtime adaptive recovery remain unproven by this phase. V1-20 is not complete. The consolidated `PELLO_PHASE3C_FINAL_REPORT.md` maps all 23 criteria without promoting planning-level evidence into global product acceptance. No Phase 3D files or implementation work were created.

Recommended next milestone only: a small local business product such as supplier invoice discrepancy tracking with dependent intake/validation, matching, approval and evidence/report increments. Connect the existing plan directly to protected tests, Coder, Tester, independent Reviewer, localized corrections and integration. Use synthetic data and local effects first; require a verified multi-increment result without human prompt transfers. This recommendation grants no execution authorization.
'''
Path('PELLO_PHASE3C3_EVALUATION_REPORT.md').write_text(report,encoding='utf-8')
old=Path('PELLO_PHASE3C_FINAL_REPORT.md');archive=out/'interim-reports/phase3c2-original-final-report.md'
if not archive.exists():archive.write_bytes(old.read_bytes())
mapping=[
('01','Specification understanding','Scoped real evidence','C1 interpretation; C2 familiar plan; E fresh blind requirements/architecture and manifest, no manual translation.'),
('02','Autonomous decomposition','Scoped real evidence',f'E {len(increments)} increments, DAG, {len(contracts)} contracts/{tests} proposed criteria; existing PipelineManifest.'),
('03','Independent testing','Supporting, incomplete','Pello engineering tests protected before code; business-product tests remain ungenerated/unexecuted.'),
('04','Incremental pipeline','Supporting, incomplete','Existing pipeline consumes generated plan and inspects readiness; no multi-increment business Coder/Tester execution in C3.'),
('05','Autonomous correction','Not established by C3','Engineering session corrected real defects; do not label this autonomous Pello repair.'),
('06','Adaptive escalation','Scoped policy evidence','Typed task-specific model/effort choices, actual backend catalog, evidence-based adaptation invariants; no rigid ladder. No runtime business repair escalation demonstrated.'),
('07','n8n integration','No new C3 evidence','Prior milestones retain their own results; no n8n operations here.'),
('08','Autonomous publishing','No new C3 evidence','No product publishing occurred.'),
('09','Real integration testing','No business integration evidence','Real SDK/local pipeline only; no live business integration test.'),
('10','Auxiliary integration','Not established by C3','External business integration unavailable and blocked; no verified external effects.'),
('11','Change control','Supporting local evidence','Accepted Git checkpoints, immutable plan history and preserved original failures; no production configuration restore claim.'),
('12','Memory and sessions','Scoped real evidence','SQLite and separate-process reconstruction keep plan identity, models and one history row without new inference; independent sessions persist.'),
('13','Recovery','Supporting, incomplete','Never-submitted reservation reconciled conservatively; no blindly repeated uncertain business effect. Broader recovery not proved.'),
('14','Long-running execution','Supporting, incomplete','Actual planning stages chained under ledger; full business delivery without human transfers not demonstrated.'),
('15','Automated reporting','Not established by C3','Local evidence reports only; no daily emails sent.'),
('16','MCP permissions','Preserved, no new live proof','No MCP mutations or alternative customer access; blind evaluation uses native local deny profile.'),
('17','Budgets','Scoped verified evidence','Append-only 60/75 authorizations, preserved historical charges, deadline/STOP/hard-cap regression and actual guarded submissions.'),
('18','Requirement validation','Scoped real evidence','Original-source frozen evaluation of contradiction, critical missing limits/integration, assumptions and independently actionable local work.'),
('19','Independent review','Scoped real evidence','Distinct non-writing Reviewer contexts, source+frozen rubric, native key isolation, objective failures cannot be overridden; final hash-bound acceptance.'),
('20','Complete delivery','NOT COMPLETE','No full enterprise business product implemented, published, tested or delivered in Phase 3C.'),
('21','STOP and recovery','Supporting local evidence','Enforced STOP/budget tests and preserved state; no new live STOP incident or production-workflow lifecycle demonstration.'),
('22','Production test-data management','No new C3 evidence','Only local synthetic data; no production test resources created.'),
('23','MCP access lifecycle','No new C3 evidence','No workflow creation/exposure/access handoff; historical evidence unchanged.')]
rows='\n'.join(f'| V1-{n} | {title} | {scope} | {evidence} |' for n,title,scope,evidence in mapping)
final=f'''# Pello V1.3 — Phase 3C Final Report

Reference date October 25, 2026. Closeout {state['at']}. **Phase 3C ACCEPTED at planning level. Pello V1 is not globally complete. V1-20 is NOT COMPLETE.**

Phase 3C-1 and 3C-2 retain their accepted historical results. Phase 3C-3 now adds a genuinely fresh blind planning PASS, with frozen independent expectations and enforced answer-key isolation. No enterprise business product was implemented or delivered, and Phase 3D was not started.

## Consolidated milestones without rewriting history

| Milestone | Historical/current evidence | Verdict |
|---|---|---|
| C1 | 13 interpretation items; 16 source segments; 6 blockers/2 nonblocking; 2 assumptions; 28 targeted/154 full tests at that checkpoint | ACCEPTED |
| C2 | Six sequential batches; 217 full and 63 protected; seven increments/contracts and 34 proposed criteria; 1493 preserved hashes; familiar Vendor Return Desk fixture | ACCEPTED |
| C3 | Four original held-out FAILs retained; fresh StackProof {obj['checks_passed']}/{obj['checks_run']} objectives, {semantic_passed}/{len(semantic['criteria'])} semantic criteria; {count} current full/63 protected;1493 hashes; final independent PASS | ACCEPTED within planning scope |

Original reports and evidence remain in Git and under `evidence/phase3c/`. The exact earlier PARTIAL final report is archived at `evidence/phase3c3/interim-reports/phase3c2-original-final-report.md`; the 49-reservation C3 PARTIAL checkpoint is separately preserved. Failed trials were not relabeled, deleted or retried as blind successes.

The autonomous path now demonstrates specification → traceable requirements/issues/assumptions → architecture/DAG → functional increments/contracts/proposed criteria → typed adaptive model decisions → durable existing PipelineManifest → first actionable increment. Existing pipeline inspection and separate-process reconstruction consume the generated artifact without manual technical translation or new inference. Source/runtime evidence and exact limits are in `PELLO_PHASE3C3_EVALUATION_REPORT.md`.

Accepted fresh plan: `{digest}`. First actionable increment: `{inspection['first_actionable']}`. SQLite `PLAN_ACCEPTED` and workspace checkpoint `{checkpoint}` follow objective gates and an independent final Reviewer PASS. Product execution authorization remains false. Proposed business criteria must not be credited as generated, protected or executed tests.

## Mapping to the 23 authoritative V1 acceptance criteria

These are scoped evidence mappings, not new global acceptance declarations. Historical non-C3 capabilities retain their previous reports; absence of new evidence does not rewrite them.

| Criterion | Capability | Scope established here | Verified evidence or limitation |
|---|---|---|---|
{rows}

## Verification, authorization and remaining limits

Current complete regression: {count}/{count} PASS. Protected C2 checks: 63/63 PASS, overlapping the full suite. Historical hashes:1493/1493. Original operation/project rows and protected source/copy identities preserved. Actual C2 and E reconstruction keeps digest/history without extra SDK usage. All recorded checkpoint Git objects verified. Final independent review and objective evidence are bound to the accepted plan identity.

Budget: {state['sdk_charged_reservations']}/75 charged reservations, {state['actual_completed_sdk_calls']} actual completed SDK calls plus one terminal provider rejection and one retained never-submitted slot; deadline October 26 06:30 UTC. All explicit extensions were recorded without resetting historical counters. The failed provider turn was reconciled before same-payload recovery; the intervening expired-deadline attempt was blocked before submission. Zero external business effects, no n8n operations, no config/MCP mutations and no Phase 3D execution. Source implementation HEAD `{implementation_head}`; accepted code/evidence HEAD `{head}` precedes the report-only delivery commit identified in the delivery receipt.

One successful independent held-out result supports bounded generalization, not universal reliability. The four earlier FAILs show real reliability limitations and justify the small recorded corrections. No autonomous business self-repair, full enterprise delivery, production publication or long-running product implementation is claimed.

## Next milestone recommendation only

Use a small realistic local supplier-invoice discrepancy product with dependent intake/validation, matching, approval and report increments. Have existing Pello coordinate specification, autonomous planning, independently protected tests, Coder, Tester, independent Reviewer, evidence-based localized corrections and integrated verified behavior without human prompt transfers. Keep data synthetic and effects local initially. Define observable business examples and an explicit authorization boundary. This is a recommendation, not permission to start; no Phase 3D implementation files or work were created.
'''
old.write_text(final,encoding='utf-8')
print(json.dumps({'report':'PELLO_PHASE3C3_EVALUATION_REPORT.md','consolidated':'PELLO_PHASE3C_FINAL_REPORT.md','status':'ACCEPTED','criteria_mapped':len(mapping),'old_final_report_sha256':hashlib.sha256(archive.read_bytes()).hexdigest()},indent=2))
