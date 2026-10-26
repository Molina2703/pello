"""Refresh generated reporting metadata, never changes evaluation expectations."""
from pathlib import Path
p=Path('evidence/phase3c3/build_success_reports_f.py');s=p.read_text(encoding='utf-8')
s=s.replace("case_names={'a':'CanalShare','b':'ArchiveLedger','c':'KilnBook','d':'FolioPay','e':'StackProof','f':'NEW_CASE'}", "fresh_name=analysis['product_name']\nboundary_count=len(read('full-boundary-f-objective.json')['native_checks'])\ncase_names={'a':'CanalShare','b':'ArchiveLedger','c':'KilnBook','d':'FolioPay','e':'StackProof','f':fresh_name}")
lines=s.splitlines(keepends=True)
for index,line in enumerate(lines):
 if not line.startswith('case_names='):lines[index]=line.replace('StackProof','{fresh_name}')
s=''.join(lines)
s=s.replace('all eleven E boundary controls','all {boundary_count} F boundary controls').replace('all eleven F boundary controls','all {boundary_count} F boundary controls')
s=s.replace('All11','All{boundary_count}').replace('all eleven','all {boundary_count}')
s=s.replace('**{state[\'sdk_charged_reservations\']}/75','**{state[\'sdk_charged_reservations\']}/{state[\'cumulative_limit\']}')
s=s.replace("{state['sdk_charged_reservations']}/75", "{state['sdk_charged_reservations']}/{state['cumulative_limit']}")
s=s.replace('and finally extended only the deadline to **October 26 06:30 UTC / 01:30 Colombia**.', 'then extended the deadline to **October 26 06:30 UTC / 01:30 Colombia**, and finally explicitly raised the cumulative cap to85 without changing that deadline.')
s=s.replace('and `authorization-deadline-0630.json`;', '`authorization-deadline-0630.json` and `authorization-extension-85.json`;')
s=s.replace('The first architecture request terminated with provider', 'During the earlier StackProof run, its first architecture request terminated with provider')
s=s.replace('Four initial blind FAILs','Five initial blind FAILs')
needle='Before these cases, six protected isolation/profile tests'
addition='5. StackProof FAIL: increment planning context exceeded55,000 before reservation despite valid architecture. The localized correction limits increment active architecture to exact nodes/global IDs, retains the full original requirements/issues/assumptions and immutable architecture for validation, and uses reversible column/row transport for oversized plan inputs. Four protected defect tests,53 targeted PASS, independent correction PASS and240 full regression PASS. E remains FAIL; the current held-out was independently prepared afterward.\n\n'
assert needle in s;s=s.replace(needle,addition+needle)
s=s.replace('Six protected defect-test sources','Seven protected defect-test sources')
p.write_text(s,encoding='utf-8');print('Updated reporting metadata only; ACCEPTED output remains gated on actual Core acceptance.')
