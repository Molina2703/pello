"""Full contract-batch correction regression; separate immutable records."""
from pathlib import Path
source=Path('evidence/phase3c3/run_regression_f.py').read_text(encoding='utf-8')
gate="out=Path('evidence/phase3c3');evaluation=json.loads((out/'heldout-f-evaluation.json').read_text())\nassert evaluation['verdict']=='PASS'"
assert source.count(gate)==1
source=source.replace(gate,"out=Path('evidence/phase3c3')")
for suffix in ['regression','protected','integrity']:source=source.replace('final-'+suffix,'contract-'+suffix)
source=source.replace('count>=240','count>=245')
old="out/'planning-context-correction/protection.json']";assert old in source
source=source.replace(old,"out/'planning-context-correction/protection.json',out/'contract-context-correction/protection.json']")
exec(compile(source,'contract_regression_shared_implementation','exec'))
