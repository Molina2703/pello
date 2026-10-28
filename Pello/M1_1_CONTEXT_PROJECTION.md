# M1.1 — Offline context projection

Baseline: `codex/pello-phase3c`, commit `cceb94cb374f40b20774265d9f02b2e978ca2286`. Existing untracked files were left untouched. M0 diagnostics: 8 tests pass; 8/9 analyses and 26 original prompts are available. Historical rejected prompt lengths are unavailable.

## Data flow and boundary

`create_project` ingests and stores the complete Markdown, hash and deterministic `MarkdownSource` segment map (IDs, headings, line ranges, text and hashes). `understand` supplies the source and map to the Planner; `normalize_analysis` validates references/dependencies and persists a structured analysis. `review_analysis` supplies original source, source map and interpretation to the Reviewer. Its persisted `input.json` is an evidence envelope, not the submitted prompt: existing packing may factor an identical nested map and, if still oversized, source text by lines. `planner_input` requires accepted review, checks source identity and supplies the complete structured analysis. Architecture receives it and its objective; increments also receive work nodes/global IDs; contracts receive increments/global IDs and may batch; model selection receives bounded task fields and capabilities. Their validators use the canonical analysis and stage outputs, not the transport projection. `manifest_from_contracts` and `_compile_product_plan` preserve requirement/task associations, dependencies and planning blockers; `IncrementalPipeline.inspect_planned_manifest` evaluates readiness.

`_invoke` serializes the prompt through `_prompt` and passes that string to `backend.run`; its canonical `input.json` and persisted analysis remain separate. The selected boundary is `understand`: its actual preserved prompts repeat source text both in the full Markdown and in each segment. Only a map identical to a freshly parsed canonical map is projected. Segment text is represented by its existing inclusive line range and reconstruction instructions; all IDs, headings, hashes and other fields remain. The projection is used only if shorter; malformed, changed, incomplete or conflicting inputs retain their prior representation. No business text is summarized or merged. The model must interpret the line references, so deterministic reconstruction is not proof of model behavior.

## Measurements

Character counts use the same compact JSON serialization. Original is the persisted original `codex_prompt.txt`; baseline reconstructed from its persisted input equals that original for every row. Optimized is reconstructed offline from that same input, not a historical submitted request. Full payload equality after deterministic reconstruction holds for every row; no coverage failures occurred.

| Held-out | Original persisted / reconstructed | Optimized reconstructed | Reduction | Reduction % |
|---|---:|---:|---:|---:|
| A | 19,648 | 12,506 | 7,142 | 36.35 |
| B | 22,230 | 14,004 | 8,226 | 37.00 |
| C | 22,045 | 14,043 | 8,002 | 36.30 |
| D | 21,915 | 13,857 | 8,058 | 36.77 |
| E | 22,662 | 14,534 | 8,128 | 35.87 |
| F | 22,201 | 13,951 | 8,250 | 37.16 |
| G | 22,739 | 14,521 | 8,218 | 36.14 |
| H | 21,162 | 13,783 | 7,379 | 34.87 |
| I | 18,883 | 12,362 | 6,521 | 34.53 |

## Verification and limits

`tests/test_m11_context_projection.py` checks exact round trip, shared references, similar and contradictory text, arbitrary structured fields, determinism, no mutation, malformed maps, unresolved IDs, marker collision, whitespace, line endings and fallback. M0 diagnostic tests pass (8); planning regression suite passes (67); complete offline suite passes (274). An independent Reviewer returned PASS, independently reproducing the measurements and identifying two defects corrected before the verdict. M0's deterministic FolioPay classification failure and ParcelProof C13 blocker behavior remain unchanged; C13 is not fixed. No historical evidence, SQLite state, validators or scheduler rules were changed.

This proves a deterministic reduction at one model-bound boundary and exact reconstruction of the supplied data on these fixtures. It does not establish model accuracy, successful inference, or resolution of the five historical context-limit failures. Remaining risks include large requirement representations and later-stage context growth. A suitable next increment is to measure one later actual model-bound stage and identify a separately reversible projection, retaining validation and blocker semantics.
