# Phase 3C-1 implementation plan

## Objective

Add a local natural-language Markdown ingestion path that returns a schema-validated, source-traceable product interpretation. Preserve the source byte-for-byte. Treat the document as untrusted task data and keep planning tools/network/MCP disabled.

## Bounded changes

- Add typed Pydantic records for source segments, requirements, assumptions, and blocking/non-blocking issues.
- Segment Markdown deterministically with heading paths and 1-based line spans; calculate source hashes and stable requirement IDs in Core.
- Add an additive planning-project/version/operation store under the phase-specific SQLite runtime. Keep old Phase 2/3A/3B databases separate and untouched.
- Reuse the existing Python Core, SQLite, Git, Codex SDK worker, model catalog validation, role sessions, STOP pattern, and evidence folders.
- Add the existing CLI surface as `pello plan-spec` with `create`, `understand`, `status`, `review`, and `revalidate` actions; no manual manifest input.
- Record proposed outputs separately from Reviewer acceptance. A source change creates a new version; it cannot overwrite an accepted version.

## Verification

- Tests for complete/incomplete Markdown, section-spanning and repeated requirements, conflict/ambiguity, absent integration details, exclusions, hostile model-directed text, invalid source anchors, and unchanged source bytes.
- Tests for model response schema, ID stability, SQLite restart/replay, STOP, turn/deadline limits, stale-source detection, reviewer independence, and preservation of prior versions.
- Run focused tests, request independent review, then rerun the complete 126-test regression before checkpoint.

## Acceptance boundary

3C-1 is accepted only after real SDK ingestion, deterministic source/schema validation, independent Reviewer PASS, regression PASS, and a Git checkpoint. It does not yet claim autonomous decomposition, protected tests, or a completed business product.
