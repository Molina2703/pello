"""Read-only MCP discovery through Pello's real retained Codex SDK worker."""
from pathlib import Path
import json
from athis_autopilot.ai_supervisor import SDKBackend

project = Path(__file__).resolve().parents[2]
out = Path(__file__).resolve().parent
workspace = project / 'runtime/phase3b/preflight/workspace'
workspace.mkdir(parents=True, exist_ok=True)
backend = SDKBackend()
try:
    inventory = backend.mcp(workspace=workspace, out_dir=out / 'preflight/inventory', request={'action':'inventory'})
    (out / 'preflight/inventory.json').write_text(json.dumps(inventory, indent=2), encoding='utf-8')
    search = backend.mcp(workspace=workspace, out_dir=out / 'preflight/search',
        request={'action':'call', 'tool':'search_workflows', 'arguments':{'query':'PELLO-3B-', 'limit':10}})
    (out / 'preflight/search.json').write_text(json.dumps(search, indent=2), encoding='utf-8')
    print(json.dumps({'inventory':[{
        'name':s['name'], 'authStatus':s['authStatus'], 'runtimeStatus':s.get('runtimeStatus'),
        'serverInfo':s.get('serverInfo'), 'tools':list(s['tools']), 'toolsError':s.get('toolsError')
        } for s in inventory['result']['data']], 'search':search['result']}, indent=2))
finally:
    backend.close()
