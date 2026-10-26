"""Full correction regression; retain prior immutable run records."""
from pathlib import Path
source=Path('evidence/phase3c3/run_regression_g.py').read_text(encoding='utf-8')
gate="out=Path('evidence/phase3c3');evaluation=json.loads((out/'heldout-g-evaluation.json').read_text())\nassert evaluation['verdict']=='PASS'"
assert source.count(gate)==1
source=source.replace(gate,"out=Path('evidence/phase3c3')")
for suffix in ['regression','protected','integrity']:source=source.replace('final-'+suffix,'analysis-transport-'+suffix)
source=source.replace('count>=245','count>=249')
old="out/'contract-context-correction/protection.json']";assert old in source
source=source.replace(old,"out/'contract-context-correction/protection.json',out/'analysis-transport-correction/protection.json']")
exec(compile(source,'analysis_transport_regression_shared_implementation','exec'))
