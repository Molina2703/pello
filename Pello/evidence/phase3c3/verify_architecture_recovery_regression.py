"""Full engineering regression; does not relabel the original held-out FAIL."""
from pathlib import Path
source=Path('evidence/phase3c3/run_regression_h.py').read_text(encoding='utf-8')
gate="out=Path('evidence/phase3c3');evaluation=json.loads((out/'heldout-h-evaluation.json').read_text())\nassert evaluation['verdict']=='PASS'"
assert source.count(gate)==1
source=source.replace(gate,"out=Path('evidence/phase3c3')")
for suffix in ['regression','protected','integrity']:source=source.replace('final-'+suffix,'architecture-recovery-'+suffix)
source=source.replace('count>=249','count>=257')
old="out/'analysis-transport-correction/protection.json']";assert old in source
source=source.replace(old,"out/'analysis-transport-correction/protection.json',out/'architecture-recovery/protection.json',out/'architecture-recovery/protection-integration.json']")
exec(compile(source,'architecture_recovery_shared_regression','exec'))
