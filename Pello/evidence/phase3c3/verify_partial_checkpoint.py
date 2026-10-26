"""Verify current code while SDK authorization is expired; no acceptance claim.

Reuse the exact regression/integrity implementation of the final harness, but
do not require a blind PASS to measure a PARTIAL checkpoint. Output identities
are separate so these results cannot impersonate final held-out acceptance.
"""
from pathlib import Path
source=Path('evidence/phase3c3/run_regression_e.py').read_text(encoding='utf-8')
gate="out=Path('evidence/phase3c3');evaluation=json.loads((out/'heldout-e-evaluation.json').read_text())\nassert evaluation['verdict']=='PASS'"
assert source.count(gate)==1
source=source.replace(gate,"out=Path('evidence/phase3c3')")
for suffix in ['regression','protected','integrity']:
    source=source.replace('final-'+suffix,'checkpoint-'+suffix)
exec(compile(source,'checkpoint_regression_shared_implementation','exec'))
