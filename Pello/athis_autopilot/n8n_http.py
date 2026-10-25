"""Four journaled POSTs to the owned QA webhook; no administrative HTTP API."""
import http.client
import json
from urllib.parse import urlsplit
from .engines import CodexBlocked
from .n8n_mcp import ORIGIN
from .n8n_operations import check_stop, digest, encoded, no_secrets
from .supervisor import now


def webhook_post(path,payload):
    host=urlsplit(ORIGIN)
    connection=http.client.HTTPSConnection(host.hostname,timeout=20)
    try:
        connection.request('POST',path,body=encoded(payload).encode('utf-8'),headers={'Content-Type':'application/json'})
        response=connection.getresponse();raw=response.read(65537)
        if len(raw)>65536: raise ValueError('QA HTTP response exceeds bounded size')
        text=raw.decode('utf-8')
        try: body=json.loads(text)
        except ValueError: body={'unparsed_response':text}
        # http.client does not follow redirects or use environment proxies.
        return {'status':response.status,'body':body}
    finally: connection.close()


class QAHttpJournal:
    MAX_CALLS=4
    def __init__(self,core,transport=None):
        self.core=core;self.transport=transport or webhook_post;self.simulated=transport is not None
        with core.db() as cx:
            cx.execute('''CREATE TABLE IF NOT EXISTS pello_n8n_http(
                project_id TEXT NOT NULL,op_key TEXT NOT NULL,request_hash TEXT NOT NULL,
                request TEXT NOT NULL,status TEXT NOT NULL,response TEXT,created TEXT NOT NULL,modified TEXT NOT NULL,
                PRIMARY KEY(project_id,op_key))''')

    def operations(self,pid):
        with self.core.db() as cx:
            return [dict(r) for r in cx.execute('SELECT * FROM pello_n8n_http WHERE project_id=? ORDER BY rowid',(pid,))]

    def post(self,pid,key,payload):
        no_secrets(payload)
        if set(payload)!={'request_id','value','op'} or not isinstance(payload['request_id'],str) or not payload['request_id'].startswith('pello-3b-'):
            raise CodexBlocked('Only scoped synthetic QA payloads are authorized')
        resource=self.core.journal.resource(pid)
        request={'url':ORIGIN+'/webhook/'+resource['webhook_path'],'method':'POST','body':payload}
        existing=next((r for r in self.operations(pid) if r['op_key']==key),None)
        if existing:
            if existing['request_hash']!=digest(request): raise CodexBlocked('HTTP operation intent differs')
            if existing['status']=='CONFIRMED': return json.loads(existing['response'])
            raise CodexBlocked('Uncertain HTTP execution must not be repeated')
        with self.core.db() as cx:
            cx.execute('BEGIN IMMEDIATE');check_stop(self.core.db_path,resource)
            published=any(r['tool']=='publish_workflow' and r['status']=='CONFIRMED' and
                json.loads(r['request']).get('versionId')==resource['reviewed_version'] for r in self.core.journal.operations(pid))
            if not resource['workflow_id'] or not published: raise CodexBlocked('QA HTTP requires confirmed publication of the reviewed owned workflow')
            rows=cx.execute('SELECT status FROM pello_n8n_http WHERE project_id=?',(pid,)).fetchall()
            if any(r['status']!='CONFIRMED' for r in rows):raise CodexBlocked('Uncertain HTTP execution blocks additional POSTs')
            if len(rows)>=self.MAX_CALLS:raise CodexBlocked('QA HTTP call budget exhausted')
            cx.execute('INSERT INTO pello_n8n_http VALUES(?,?,?,?,?,NULL,?,?)',
                (pid,key,digest(request),encoded(request),'SUBMITTED',now(),now()))
        try:
            response=self.transport('/webhook/'+resource['webhook_path'],payload)
        except Exception as exc:
            with self.core.db() as cx:cx.execute("UPDATE pello_n8n_http SET status='UNCERTAIN',modified=? WHERE project_id=? AND op_key=?",(now(),pid,key))
            raise CodexBlocked('HTTP result uncertain; no automatic repetition: '+type(exc).__name__) from exc
        with self.core.db() as cx:
            cx.execute("UPDATE pello_n8n_http SET status='CONFIRMED',response=?,modified=? WHERE project_id=? AND op_key=?",
                (encoded(response),now(),pid,key))
        return response
