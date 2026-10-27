# M0 offline planning diagnostics

From the Pello repository root in PowerShell, run:

```powershell
.\.venv\Scripts\python.exe -m athis_autopilot.planning_diagnostics
```

Add `--json` for structured output. `--database`, `--evidence`, and `--runtime`
can point to another local snapshot. The SQLite connection is opened read-only;
the tool does not call the SDK, network, or production integrations and does not
write generated reports into the evidence directories.

Character counts are Unicode Python string lengths. A stage prompt is reported
as measured only when its persisted `codex_prompt.txt` exists. A JSON request
envelope, result file, or later reconstruction is not substituted for that
original prompt. The tool separately measures preserved `input.json` envelopes
and identifies exactly repeated source maps there; those sizes are not submitted
prompt measurements. Evaluation failures identify reported over-limit stages
where available, even when the original prompt text was rejected before persistence.

Planning inspection delegates manifest readiness to
`IncrementalPipeline.inspect_planned_manifest` and uses the existing architecture
and increment validators only when their persisted inputs are complete. Missing
artifacts are reported as insufficient evidence. The ParcelProof C13 scenario is
replayed only from a persisted ParcelProof manifest; a missing plan is reported
as unreproducible, without synthesizing identifiers or blockers.
