"""Preserve five blind FAILs and a verified correction; no blind PASS claim."""
import hashlib,json,sqlite3,subprocess
from datetime import datetime,timezone
from pathlib import Path
out=Path('evidence/phase3c3')
def read(p):return json.loads((out/p).read_text(encoding='utf-8'))
reg=read('transport-regression.json');integrity=read('transport-integrity.json');protected=read('transport-protected.json')
assert reg['tests_run']==240 and reg['exit_code']==0 and integrity['historical_hashes_matching']==1493
assert read('planning-context-correction/review.json')['verdict']=='PASS'
c=sqlite3.connect('runtime/phase3c/jobs.sqlite3');c.row_factory=sqlite3.Row
assert c.execute('select sum(used_turns) from pello_product_projects').fetchone()[0]==62
assert c.execute("select count(*) from pello_product_projects where project_id='phase3c3-heldout-f'").fetchone()[0]==0
auth=dict(c.execute('select * from pello_product_run_authorizations order by rowid desc limit 1').fetchone())
assert auth['max_turns']==75 and auth['deadline']=='2026-10-26T06:30:00+00:00'
statuses=[dict(r) for r in c.execute('select status,count(*) as count from pello_product_operations group by status')]
dest=out/'checkpoint-62-jobs.sqlite3';backup=sqlite3.connect(dest);c.backup(backup);backup.close()
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
state={'at':datetime.now(timezone.utc).isoformat(),'status':'PARTIAL','gate':'INSUFFICIENT_PRACTICAL_CAPACITY_FOR_FRESH_EVALUATION_AND_RESERVE','HEAD':head,'charged_reservations':62,'cumulative_limit':75,'remaining_slots':13,'deadline':auth['deadline'],'statuses':statuses,'STOP':False,'sqlite_integrity':c.execute('pragma integrity_check').fetchone()[0],'five_original_blind_FAILs_preserved':True,'correction_review':'PASS','full_tests':240,'protected_tests':63,'historical_hashes':1493,'fresh_F_started':False,'SDK_during_budget_request':False,'proposed_cumulative_limit':85,'proposed_available_slots':23,'proposed_allocation':{'new_specification_planning_and_bounded_reviews':14,'failure_reserve':9},'snapshot_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'external_business_operations':0,'Phase3D_started':False}
(out/'checkpoint-62-state.json').write_text(json.dumps(state,indent=2),encoding='utf-8');c.close()
rows=[]
for letter,name in [('a','CanalShare'),('b','ArchiveLedger'),('c','KilnBook'),('d','FolioPay'),('e','StackProof')]:
 f=read(f'heldout-{letter}-freeze'+('-v2' if letter=='a' else '')+'.json');assert read(f'heldout-{letter}-evaluation.json')['verdict']=='FAIL'
 rows.append(f"| {name} | {f['evaluation_id']} | `{f['specification_sha256']}` | `{f['rubric_sha256']}` | FAIL |")
report=f'''# Pello V1.3 — Phase 3C-3 Evaluation Report

Reference date October25,2026. Checkpoint {state['at']}.

**Phase 3C-3 PARTIAL; overall Phase 3C PARTIAL; blind generalization UNVERIFIED.** Five original blind runs failed. Small engineering corrections are independently reviewed and the current code passes regression, but no complete new held-out PASS exists. A further fresh evaluation requires enough authorized capacity. Phase3D was not started.

## A. Initial and current state

Repository branch `codex/pello-phase3c`; initial HEAD `c1bb076e7059100f0c4b5abf623625d2843f0be2`, reporting successor to accepted C2 implementation `90ea13053fa31bf12b4031b45e5f5e620bc86331`. Actual history was verified without reset. Three unrelated pre-existing context artifacts remain preserved. Initial SQLite integrity was `ok`, fourteen old checkpoints existed, STOP was absent and the ledger held28 completed SDK turns. Accepted C1/C2 reports, previous project chat, journal, grants, protected sources and historical evidence were reconciled. Baseline actually reran63 protected tests and1493 hashes; historical full-suite count was217.

The user explicitly authorized60 cumulative turns until October26 00:45 UTC, then75 until03:30 UTC, then extended only the deadline to **October26 06:30 UTC / 01:30 Colombia**. All grants remain append-only: `authorization.json`, `authorization-extension-75.json`, `authorization-deadline-0630.json`. Historical counters were never reset. Only the necessary E/Reviewer project deadlines were renewed; original accepted projects remain byte-equivalent in SQLite.

Current usage: **62/75 charged reservations**:60 completed SDK calls, one terminal provider-quota rejection and one retained never-submitted historical reservation. Thirteen slots remain. STOP is absent, SQLite integrity `ok`, and no external business effects occurred. The current capacity estimate for a fresh specification, planning and bounded independent reviews is about14 calls before reserve. The pending explicit request proposes **85 cumulative, same06:30 deadline**, giving23 available:14 planned and9 reserve. No new grant is inferred and the next fixture has not been authored or evaluated.

## B. Frozen independent evaluations

Each source and private rubric was authored in a separate SDK evaluation session without Planner outputs or manual architecture, dependency graph or increments. Independent Reviewers assessed preparation. All cases used the same authoritative ledger and per-project limit12. New projects were not created to bypass consumption.

| Case | Frozen identity | Specification SHA-256 | Rubric SHA-256 | Result |
|---|---|---|---|---|
{chr(10).join(rows)}

Freeze files retain creation times, versions, exact source quotes and acceptance thresholds: every critical criterion must pass and at least90% overall must pass. Critical failures include omitted mandatory capabilities, violated exclusions, invented authorization, ignored blockers, invalid dependencies, executable blocked work, unauthorized effects, incompatible manifests and fabricated product-test executions. Objective scripts were registered before Planner creation. No frozen rubric changed after observing its result.

CanalShare evaluator v1 FAIL remains; independently corrected v2 was frozen before Planner, source unchanged. ArchiveLedger's additional Windows-alias proof was obtained before its Planner without modifying its rubric. Each consumed correction required the next genuinely new case. StackProof preparation froze27 criteria,26 critical, and obtained independent PASS before commit `cdf7166` and inference.

Blindness uses an existing native named filesystem profile denying the private key directory, author artifacts, SQLite, evaluator evidence, Reviewer workspaces and Codex transcripts. Supplied-context roles also disable shell/image/browser/computer/app/plugin/host-code and automatic project/skill/memory reading surfaces. Actual returned profile/instruction-source receipts are checked before inference and on resume. Ordinary executor behavior is preserved. Read-only access alone was not credited as isolation.

Public positive controls passed; E's11 native boundary controls and exact rubric/Windows aliases verified PermissionError, with parent same-file/hash proof. Sources and private rubrics were never placed in Planner input or Git before that case was consumed. Raw receipts and preparation records remain. `shell_tool=false` is the effective command gate; `unified_exec=false` alone is not sufficient. See `isolation/`, `full-boundary-e-objective.json`, `rubric-e-alias-proof.json`, freeze/preparation/checkpoint artifacts.

## C. Actual autonomous runs

The existing `ProductPlanningCore.plan_product` C1→C2 pipeline used actual authorized SDK calls with source/resource/constraint inputs only. Mocks did not replace the demonstration. No hand-written technical manifest or business Coder increment was supplied.

CanalShare extracted37 requirements then failed review-context preparation. ArchiveLedger emitted33 raw requirements but violated the existing authorization flag invariant. KilnBook produced39 typed requirements,8 issues and4 assumptions before another review-context overflow. FolioPay produced38 requirements,8 issues,4 assumptions and8 architecture nodes; interpretation passed but architecture validation rejected globalized business rules and available-input declarations blocked local work.

StackProof produced **40 requirements,7 issues,3 assumptions and21 source segments** with independent interpretation PASS. Its first architecture request was rejected by provider quota. Read-only thread inspection proved terminal `usageLimitExceeded`, userMessage only, no assistant output; the charge remains. A recovery request encountered the expired deadline and was blocked before reservation. After the explicit06:30 renewal, identical input/schema hashes and the same model policy passed through existing guarded `_invoke`. The generated architecture passed unchanged validation.

The ordinary pipeline then failed preparing increment context: **76,177 compact JSON characters** exceeded the unchanged55,000 cap before another SDK reservation. Architecture is durable, but no complete increments, contracts, model assignments, PipelineManifest or first actionable increment were produced. Full semantic correctness, plan reconstruction and pipeline consumption therefore remain unverified for E. All business tests remain ungenerated/unprotected/unexecuted. No business implementation occurred.

## D. Independent evaluation and reproduction

All five planning results are **FAIL**, not overridden by interpretation or repair-review PASS. Missing mandatory complete planning artifacts is an objective critical failure. No final independent phase-closure review or PLAN_ACCEPTED checkpoint exists for a held-out case. Structural validity of E architecture alone does not establish semantic correctness.

Original frozen expectations, raw model results, logs and exact failed input are preserved. E's reproduction is `resumed-planning-e.log` plus `planning-context-correction/original-increments-input.json`. The original unmodified `_prompt` rejects that76,177-character context; its guard reserved no additional SDK turn. Corrections must not be demonstrated on E and relabeled blind. `heldout-e-evaluation.json` records FAIL and the fresh-case requirement.

Independent correction review now reports PASS against the actual diff, protected defect tests, source/graph preservation and objective results. It explicitly accepts only the engineering repair, not autonomous generalization or autonomous Pello self-repair. See `planning-context-correction/review-input.json`, `review.json`, `objective-proof.json` and accepted checkpoints.

## E. Small corrections and preserved failures

Before authoring cases, six protected checks verified the opt-in native isolation/profile correction. A's four protected checks cover source-map deduplication and preflight before reservation. B's three cover the existing authorization schema rule without coercing raw output. C's three cover exact source-line references and CRLF/nonmatching-text preservation. D's three cover schema descriptions for category/global requirements and missing-resource semantics, with validator source unchanged from C2. Every correction obtained independent PASS; old results remain unchanged.

E's correction adds **four protected checks**, frozen before implementation. Increment active context retains exact validated nodes, global IDs and the complete accepted source/requirement/issue/assumption set. Verbose architecture stays in its immutable artifact and full validation still uses it. Oversized plan-* contexts may encode homogeneous object lists as ordered columns/rows, preserving every field/value; reserved-marker collisions and irreducible oversize fail closed. Small context serialization and the55,000 cap remain unchanged.

Actual corrected E package: **49,387 characters**. Exact decode proves all remaining input fields unchanged; every node/global field and complete requirements payload match original. No source/rubric, validator, budget or permission was weakened. C2 reconstructs its accepted hash without inference. Targeted tests: **53/53 PASS**; independent Reviewer PASS. An earlier wrong-module test invocation is retained as setup FAIL, then corrected without test edits. Raw unittest subtest whitespace in FAIL logs is preserved; source/test whitespace checks pass.

## F. Regression, integrity and checkpoint

Complete current suite: **240/240 PASS**, exit0, actual duration {reg['seconds']} seconds. C2 protected suites: **63/63 PASS**, original source/protected-copy hashes intact. These63 overlap the240. Twenty-three new protected C3 defect checks are included in the full suite. This is engineering regression, not a held-out business-product result.

Historical preservation: **1493/1493 hashes match**. First28 SDK operation rows, four original project rows, master v1.3 specification, C1/C2 reports, old FAIL/BLOCKED records and checkpoints are intact. SQLite integrity `ok`; all recorded checkpoint Git objects verify. Accepted C2 plan digest stays `7d9b1b7d59d711ff5c892d9844aedfd0f99125bf0fbf2c276e50606a94abea87`; reconstruction uses no extra SDK call or duplicate history. New protected test hashes and frozen E objective source remain intact. STOP and hard-budget regression pass; the actual expiry gate also stopped a new reservation.

Evidence: `transport-regression.json/log`, `transport-protected.json`, six protected-suite logs, `transport-integrity.json`, `planning-context-correction/accepted-regression-checkpoint.json` and `checkpoint-62-state.json`. Accepted correction implementation/evidence HEAD: `{head}`. SQLite backup SHA-256: `{state['snapshot_sha256']}`. Final reporting-only HEAD is recorded by Git and the delivery receipt after commit. Earlier49- and60-reservation PARTIAL reports remain under `interim-reports/`.

External business effects: **zero**. No n8n mutation/readback, production webhook, WhatsApp/message, customer-data operation, Railway provisioning, new server or config.toml/MCP reconfiguration occurred. Protected workflow IDs were never operated. Only local synthetic data and the Codex backend were used. No Phase3D implementation files or work were created.

## G. Final checkpoint verdict

**Phase3C-3 PARTIAL; overall Phase3C PARTIAL.** C1/C2 remain ACCEPTED. Generalization is unverified despite the accepted engineering repair. No final consolidated ACCEPTED report is generated and V1-20 remains incomplete.

Next required work, after sufficient explicit budget: independently author/freeze a new business source and hidden rubric; verify enforced isolation and checkpoint before Planner; run the complete real pipeline; independently assess every frozen criterion against original source and actual full outputs; run final regression and independent hash-bound closure review. Evaluation evidence may be delivered in ordered bounded parts within the same independent Reviewer context, with exact concatenation hashes and no missing facts/criteria. Receipts are not PASS verdicts. A semantic FAIL cannot be overridden. Any further correction consumes that fixture and requires another genuinely new case and enough authorization.

Recommendation only after valid Phase3C acceptance: a small realistic local business product with multiple dependent increments, protected tests, Coder, Tester, independent Reviewer, localized corrections and integration coordinated without manual prompt transfers. No next-phase execution is authorized here.
'''
Path('PELLO_PHASE3C3_EVALUATION_REPORT.md').write_text(report,encoding='utf-8')
(out/'interim-reports/checkpoint-62-reservations-PARTIAL.md').write_text(report,encoding='utf-8')
print(json.dumps(state,indent=2))
