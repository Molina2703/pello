# Phase 3C planning interface

Use the existing CLI and the official SDK. A project requires an explicit operational allowance and a valid deadline. The continuation grant for this development run is recorded under evidence/phase3c; it is not a standing authorization for future product implementation.

```powershell
.\pello.cmd --root runtime plan-spec --create --spec .\product.md --project-id product-plan --max-turns 12 --duration-minutes 60
.\pello.cmd --root runtime plan-spec --plan --project-id product-plan
.\pello.cmd --root runtime plan-spec --inspect-plan --project-id product-plan
```

`--plan` reuses an accepted interpretation, or performs understanding and independent analysis review first. It generates architecture, bounded functional increments, contracts, objective acceptance proposals and catalog-validated task model decisions. Core deterministically checks references, coverage, graphs, blockers and the resulting existing PipelineManifest. It persists one source-version plan in SQLite, with structured artifacts under the project's evidence/version-N/planning directory. No human-written technical manifest is needed. The SDK turn budget is enforced across projects when a run ledger is installed.

The manifest carries source requirement IDs, specification/resource/authorization blockers, the selected Coder profile and decision hash. The existing pipeline reads these fields, skips blocked work and honors task-specific profiles without a retry-count ladder. Legacy manifests retain their old defaults. Actual future execution still requires protected suites, project authorization, available tools and budgets. The generated `expected_tests` is a planning estimate, not an observed executable-test count.

`--inspect-plan` reconstructs persisted state, restores missing artifacts and asks the existing pipeline to identify ready work without invoking a Coder. Conflicting artifacts fail closed. Changed source requires `--revalidate`; it creates a new version and preserves the previous plan. A proposed plan is not marked accepted until a recorded independent Reviewer PASS is bound to its hash and passing objective verification. Core can recover a missing acceptance checkpoint after interruption without another model turn.

Model decisions retain typed complexity/risk/context assessments, catalog snapshots, rationale, evidence, budget estimates and adaptation history references. Luna Low/Medium/High are all allowed initial choices; ordinary failures with progress do not justify automatic Sol escalation. Aggregate estimates are reported separately from available capacity. Product implementation turns are not reserved by planning.

See PELLO_PHASE3C2_REPORT.md for actual measured acceptance and limitations. Phase 3C-3 requires separate remaining capacity after C2 acceptance; Phase 3D is outside this work.
