"""Full correction checkpoint; separate records, no blind acceptance claim."""
from pathlib import Path
source=Path('evidence/phase3c3/run_regression_e.py').read_text(encoding='utf-8')
gate="out=Path('evidence/phase3c3');evaluation=json.loads((out/'heldout-e-evaluation.json').read_text())\nassert evaluation['verdict']=='PASS'"
assert source.count(gate)==1
source=source.replace(gate,"out=Path('evidence/phase3c3')")
for suffix in ['regression','protected','integrity']:source=source.replace('final-'+suffix,'transport-'+suffix)
source=source.replace('count>=236','count>=240')
old="out/'architecture-contract-correction/protection.json']"
assert old in source
source=source.replace(old,"out/'architecture-contract-correction/protection.json',out/'planning-context-correction/protection.json']")
exec(compile(source,'transport_regression_shared_implementation','exec'))
