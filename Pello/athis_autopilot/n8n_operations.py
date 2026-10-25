"""Small project-scoped external journal. Native MCP is the only admin transport."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import time

from .engines import CodexBlocked
from .n8n_mcp import PROTECTED_IDS, READ_TOOLS, RESOURCE_READS
from .supervisor import now

MUTATIONS = {'create_workflow_from_code', 'update_workflow', 'publish_workflow', 'execute_workflow', 'test_workflow'}


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(encoded(value).encode()).hexdigest()


def mcp_data(response):
    raw = response.get('result', response)
    if isinstance(raw.get('structuredContent'), dict): return raw['structuredContent']
    for item in raw.get('content', []):
        if item.get('type') == 'text':
            try: return json.loads(item['text'])
            except (ValueError, TypeError): pass
    return {}


def no_secrets(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if child and any(word in key.lower() for word in ('password', 'api_key', 'access_token', 'authorization', 'credential', 'private_key', 'secret')):
                raise CodexBlocked('Credential/secret material is outside the QA operation scope')
            no_secrets(child)
    elif isinstance(value, list):
        for item in value: no_secrets(item)


def authorize(resource, tool, arguments):
    if tool not in READ_TOOLS | MUTATIONS:
        raise CodexBlocked('Tool is outside the n8n QA allowlist')
    no_secrets(arguments)
    if tool == 'search_workflows' and arguments.get('query') != resource['name']:
        raise CodexBlocked('Search must use this project unique QA name')
    if 'workflowId' in arguments and (not resource['workflow_id'] or
            arguments['workflowId'] != resource['workflow_id'] or arguments['workflowId'] in PROTECTED_IDS):
        raise CodexBlocked('Workflow ID is outside this project')
    if tool in RESOURCE_READS and 'workflowId' not in arguments:
        raise CodexBlocked('Resource reads must identify the project-owned workflow')
    if tool in MUTATIONS - {'create_workflow_from_code'} and 'workflowId' not in arguments:
        raise CodexBlocked('A project-owned workflow ID is required')
    if tool == 'create_workflow_from_code' and (resource['workflow_id'] or arguments.get('name') != resource['name']):
        raise CodexBlocked('Only one new workflow with the authorized unique name may be created')
    if tool == 'publish_workflow' and (not resource['reviewed_version'] or
            arguments.get('versionId') != resource['reviewed_version']):
        raise CodexBlocked('Publication requires the exact independently reviewed version')
    if tool == 'update_workflow':
        for operation in arguments.get('operations', []):
            if operation.get('type') not in {'updateNodeParameters', 'setNodeParameter', 'setWorkflowMetadata', 'setWorkflowSettings'}:
                raise CodexBlocked('Update operation exceeds the narrow pilot scope')
            if 'errorWorkflow' in operation.get('settings', {}):
                raise CodexBlocked('Other workflow invocations are not authorized')


def check_stop(db_path, resource):
    stop = Path(db_path).parent / 'supervised' / resource['project_id'] / 'STOP'
    if stop.exists(): raise CodexBlocked('Emergency STOP is set; no new external operation')
    if time.time() >= resource['deadline']: raise CodexBlocked('External project time budget exhausted')


def authorize_in_db(cx, resource, tool, arguments):
    authorize(resource, tool, arguments)
    if tool == 'get_workflow_execution':
        known=cx.execute('SELECT 1 FROM pello_n8n_executions WHERE project_id=? AND execution_id=?',
                         (resource['project_id'],arguments.get('executionId'))).fetchone()
        if not known: raise CodexBlocked('Execution ID has not been observed for this project-owned workflow')


def claim_operation(proof, tool, arguments, thread_id):
    """Atomic submission boundary inside the SDK worker, before native MCP call."""
    with closing(sqlite3.connect(proof['db'], timeout=15)) as cx, cx:
        cx.row_factory = sqlite3.Row; cx.execute('BEGIN IMMEDIATE')
        resource = dict(cx.execute('SELECT * FROM pello_n8n_projects WHERE project_id=?', (proof['project_id'],)).fetchone())
        check_stop(proof['db'], resource); authorize_in_db(cx, resource, tool, arguments)
        op = cx.execute('SELECT * FROM pello_n8n_operations WHERE project_id=? AND op_key=?',
                        (proof['project_id'], proof['key'])).fetchone()
        if not op or op['status'] != 'IN_FLIGHT' or op['tool'] != tool or op['request_hash'] != digest(arguments):
            raise CodexBlocked('No matching unsubmitted authorized operation; do not repeat')
        cx.execute("UPDATE pello_n8n_operations SET status='SUBMITTED',thread_id=?,modified=? WHERE project_id=? AND op_key=?",
                   (thread_id, now(), proof['project_id'], proof['key']))


def finish_operation(proof, response):
    """Capture returned IDs in SQLite before writing response files or returning."""
    data = mcp_data(response)
    with closing(sqlite3.connect(proof['db'], timeout=15)) as cx, cx:
        cx.row_factory = sqlite3.Row; cx.execute('BEGIN IMMEDIATE')
        op = cx.execute('SELECT * FROM pello_n8n_operations WHERE project_id=? AND op_key=?',
                        (proof['project_id'], proof['key'])).fetchone()
        if not op: raise CodexBlocked('Missing external operation record')
        if op['status'] == 'CONFIRMED': return
        failed = response.get('isError') is True or data.get('success') is False or bool(data.get('error'))
        status = 'FAILED' if failed else 'CONFIRMED'
        if op['tool'] == 'create_workflow_from_code':
            workflow_id = data.get('workflowId') or (data.get('workflow') or {}).get('id')
            if not workflow_id or workflow_id in PROTECTED_IDS: status = 'UNCERTAIN'
            else:
                existing = cx.execute('SELECT workflow_id FROM pello_n8n_projects WHERE project_id=?', (proof['project_id'],)).fetchone()[0]
                if existing and existing != workflow_id: raise CodexBlocked('Unexpected second workflow ID')
                cx.execute('UPDATE pello_n8n_projects SET workflow_id=? WHERE project_id=?', (workflow_id, proof['project_id']))
        if op['tool'] in ('execute_workflow','search_workflow_executions') and not failed:
            own=cx.execute('SELECT workflow_id FROM pello_n8n_projects WHERE project_id=?',(proof['project_id'],)).fetchone()[0]
            records=data.get('executions',data.get('data',data.get('results',[])))
            if not isinstance(records,list): records=[]
            execution=data.get('execution') or {}
            if isinstance(execution,dict) and (data.get('executionId') or execution.get('id')):
                records=[{'id':data.get('executionId') or execution.get('id'),'workflowId':own},*records]
            for record in records:
                if record.get('workflowId',own)!=own: raise CodexBlocked('MCP returned execution metadata from a different workflow')
                execution_id=record.get('id')
                if isinstance(execution_id,(str,int)):
                    cx.execute('INSERT OR IGNORE INTO pello_n8n_executions VALUES(?,?)',(proof['project_id'],str(execution_id)))
        cx.execute('UPDATE pello_n8n_operations SET status=?,response=?,modified=? WHERE project_id=? AND op_key=?',
                   (status, encoded(response), now(), proof['project_id'], proof['key']))


class N8nJournal:
    def __init__(self, core):
        self.core = core
        with core.db() as cx:
            cx.executescript('''CREATE TABLE IF NOT EXISTS pello_n8n_projects(
                project_id TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, webhook_path TEXT NOT NULL UNIQUE,
                workflow_id TEXT UNIQUE, deadline REAL NOT NULL, max_calls INTEGER NOT NULL,
                max_mutations INTEGER NOT NULL, reviewed_version TEXT, reviewed_hash TEXT);
                CREATE TABLE IF NOT EXISTS pello_n8n_operations(
                project_id TEXT NOT NULL, op_key TEXT NOT NULL, tool TEXT NOT NULL,
                request_hash TEXT NOT NULL, request TEXT NOT NULL, status TEXT NOT NULL,
                response TEXT, thread_id TEXT, created TEXT NOT NULL, modified TEXT NOT NULL,
                PRIMARY KEY(project_id,op_key));
                CREATE TABLE IF NOT EXISTS pello_n8n_executions(
                project_id TEXT NOT NULL, execution_id TEXT NOT NULL, PRIMARY KEY(project_id,execution_id));''')

    def configure(self, project_id, name, webhook_path, *, max_calls=40, max_mutations=6, seconds=2400):
        import re
        self.core.project(project_id)
        if not re.fullmatch(r'PELLO-3B-[A-Za-z0-9_-]{8,90}', name) or not re.fullmatch(r'pello-3b-[a-z0-9-]{8,80}', webhook_path):
            raise ValueError('Distinctive QA resource names are required')
        if not (1 <= max_calls <= 80 and 1 <= max_mutations <= 12 and 1 <= seconds <= 3600):
            raise ValueError('Invalid bounded external budget')
        with self.core.db() as cx:
            existing=cx.execute('SELECT * FROM pello_n8n_projects WHERE project_id=?',(project_id,)).fetchone()
            if existing:
                if (existing['name'],existing['webhook_path'],existing['max_calls'],existing['max_mutations']) != (name,webhook_path,max_calls,max_mutations):
                    raise CodexBlocked('Existing external scope/budget cannot be replaced')
                return
            cx.execute('INSERT INTO pello_n8n_projects VALUES(?,?,?,NULL,?,?,?,NULL,NULL)',
                       (project_id,name,webhook_path,time.time()+seconds,max_calls,max_mutations))

    def resource(self, project_id):
        with self.core.db() as cx:
            return dict(cx.execute('SELECT * FROM pello_n8n_projects WHERE project_id=?',(project_id,)).fetchone())

    def operations(self, project_id):
        with self.core.db() as cx:
            return [dict(r) for r in cx.execute('SELECT * FROM pello_n8n_operations WHERE project_id=? ORDER BY rowid',(project_id,))]

    def prepare(self, project_id, key, tool, arguments):
        resource=self.resource(project_id); authorize(resource,tool,arguments)
        with self.core.db() as cx:
            cx.execute('BEGIN IMMEDIATE'); check_stop(self.core.db_path,resource)
            authorize_in_db(cx,resource,tool,arguments)
            records=cx.execute('SELECT * FROM pello_n8n_operations WHERE project_id=?',(project_id,)).fetchall()
            if len(records)>=resource['max_calls']: raise CodexBlocked('MCP call budget exhausted')
            if tool in MUTATIONS:
                if any(r['status'] in ('IN_FLIGHT','SUBMITTED','UNCERTAIN') and r['tool'] in MUTATIONS for r in records):
                    raise CodexBlocked('Uncertain mutation must be reconciled before further writes')
                if sum(r['tool'] in MUTATIONS for r in records)>=resource['max_mutations']:
                    raise CodexBlocked('Mutation budget exhausted')
                if tool=='create_workflow_from_code':
                    if any(r['tool']==tool for r in records): raise CodexBlocked('Creation was already submitted; reconcile instead')
                    valid=any(r['tool']=='validate_workflow' and r['status']=='CONFIRMED' and
                        json.loads(r['request']).get('code')==arguments.get('code') and
                        mcp_data(json.loads(r['response'])).get('valid') is True for r in records)
                    if not valid: raise CodexBlocked('Exact workflow code must pass official validation before creation')
            cx.execute('INSERT INTO pello_n8n_operations VALUES(?,?,?,?,?,?,NULL,NULL,?,?)',
                (project_id,key,tool,digest(arguments),encoded(arguments),'IN_FLIGHT',now(),now()))

    def call(self, project_id, key, tool, arguments):
        existing=next((r for r in self.operations(project_id) if r['op_key']==key),None)
        if existing:
            if existing['tool']!=tool or existing['request_hash']!=digest(arguments): raise CodexBlocked('Operation key has different intent')
            if existing['status']=='CONFIRMED': return json.loads(existing['response'])
            raise CodexBlocked('Unresolved/failed operation cannot be blindly repeated')
        self.prepare(project_id,key,tool,arguments)
        proof={'db':str(self.core.db_path),'project_id':project_id,'key':key}
        try:
            raw=self.core.backend.mcp(workspace=self.core.folder(project_id)/'workspace',
                out_dir=self.core.folder(project_id)/'evidence/mcp'/key,
                request={'action':'call','tool':tool,'arguments':arguments,'operation':proof})
            finish_operation(proof,raw['result'])
        except Exception as exc:
            current=next(r for r in self.operations(project_id) if r['op_key']==key)
            if current['status']=='CONFIRMED': return json.loads(current['response'])
            with self.core.db() as cx:
                cx.execute("UPDATE pello_n8n_operations SET status='UNCERTAIN',modified=? WHERE project_id=? AND op_key=?",
                           (now(),project_id,key))
            raise CodexBlocked('External operation uncertain; reconcile before retrying: '+type(exc).__name__) from exc
        current=next(r for r in self.operations(project_id) if r['op_key']==key)
        if current['status']!='CONFIRMED': raise CodexBlocked('External result not confirmed; inspect saved evidence')
        return json.loads(current['response'])

    def reconcile_create(self, project_id, key):
        op=next(r for r in self.operations(project_id) if r['op_key']==key)
        if op['tool']!='create_workflow_from_code' or op['status'] not in ('IN_FLIGHT','SUBMITTED','UNCERTAIN'):
            raise CodexBlocked('No uncertain creation to reconcile')
        resource=self.resource(project_id)
        search=self.call(project_id,key+'-reconcile','search_workflows',{'query':resource['name'],'limit':20})
        matches=[r for r in mcp_data(search).get('data',[]) if r.get('name')==resource['name'] and r.get('id') not in PROTECTED_IDS]
        if len(matches)!=1: raise CodexBlocked('Creation reconciliation is ambiguous; writes remain blocked')
        response={'structuredContent':{'workflowId':matches[0]['id'],'reconciled':True},'isError':False,'content':[]}
        finish_operation({'db':str(self.core.db_path),'project_id':project_id,'key':key},response)

    def reviewed(self, project_id, version, fingerprint, *, tests_passed, review_passed):
        if not tests_passed or not review_passed or not version or not fingerprint:
            raise CodexBlocked('Mandatory tests and independent review are required before publication')
        with self.core.db() as cx:
            cx.execute('UPDATE pello_n8n_projects SET reviewed_version=?,reviewed_hash=? WHERE project_id=?',
                       (version,fingerprint,project_id))
