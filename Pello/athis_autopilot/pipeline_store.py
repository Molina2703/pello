"""Additive Phase 3A storage, preserving every Phase 2 row and contract."""
import json
from contextlib import contextmanager
from .supervised import SupervisedCycle
from .pipeline_contracts import PipelinePolicy, PipelineManifest
from .supervisor import now
from .engines import CodexBlocked


class PipelineStore(SupervisedCycle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with self.db() as cx:
            cx.executescript('''
            CREATE TABLE IF NOT EXISTS pello_pipeline_projects(
              project_id TEXT PRIMARY KEY, manifest TEXT NOT NULL, policy TEXT NOT NULL,
              plan TEXT, capabilities TEXT, initial_head TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pello_pipeline_attempts(
              project_id TEXT NOT NULL, task_id TEXT NOT NULL, attempt INTEGER NOT NULL,
              stage TEXT NOT NULL, before_snapshot TEXT, after_snapshot TEXT,
              feedback TEXT NOT NULL DEFAULT '', created TEXT NOT NULL,
              PRIMARY KEY(project_id,task_id,attempt));
            CREATE TABLE IF NOT EXISTS pello_pipeline_exchanges(
              seq INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL,
              task_id TEXT NOT NULL, attempt INTEGER NOT NULL, kind TEXT NOT NULL,
              origin TEXT NOT NULL, payload TEXT NOT NULL, created TEXT NOT NULL,
              UNIQUE(project_id,task_id,attempt,kind));
            CREATE TABLE IF NOT EXISTS pello_pipeline_operations(
              project_id TEXT NOT NULL, phase TEXT NOT NULL, status TEXT NOT NULL,
              request TEXT NOT NULL, response TEXT, created TEXT NOT NULL, modified TEXT NOT NULL,
              PRIMARY KEY(project_id,phase));
            CREATE TABLE IF NOT EXISTS pello_pipeline_checkpoints(
              project_id TEXT NOT NULL, task_id TEXT NOT NULL, attempt INTEGER NOT NULL,
              parent_head TEXT NOT NULL, commit_sha TEXT, snapshot TEXT NOT NULL,
              stage TEXT NOT NULL, created TEXT NOT NULL, PRIMARY KEY(project_id,task_id));
            ''')
            cx.execute('INSERT OR IGNORE INTO pello_migrations VALUES(3,?)', (now(),))

    def pipeline_config(self, project_id):
        with self.db() as cx:
            row = cx.execute('SELECT * FROM pello_pipeline_projects WHERE project_id=?', (project_id,)).fetchone()
        if row is None:
            raise ValueError('Not a Phase 3A pipeline project; use supervised for Phase 2')
        return dict(row)

    def manifest(self, project_id):
        return PipelineManifest.model_validate_json(self.pipeline_config(project_id)['manifest'])

    def policy(self, project_id):
        return PipelinePolicy.model_validate_json(self.pipeline_config(project_id)['policy'])

    def attempts(self, project_id, task_id=None):
        with self.db() as cx:
            return [dict(r) for r in cx.execute('SELECT * FROM pello_pipeline_attempts WHERE project_id=?'
                + (' AND task_id=?' if task_id else '') + ' ORDER BY rowid',
                (project_id, task_id) if task_id else (project_id,))]

    def pipeline_exchanges(self, project_id, task_id=None, attempt=None):
        query = 'SELECT * FROM pello_pipeline_exchanges WHERE project_id=?'
        args = [project_id]
        for key, val in (('task_id', task_id), ('attempt', attempt)):
            if val is not None:
                query += ' AND ' + key + '=?'; args.append(val)
        with self.db() as cx:
            rows = cx.execute(query + ' ORDER BY seq', args).fetchall()
        return [{**dict(r), 'payload': json.loads(r['payload'])} for r in rows]

    def exchange(self, cx, project_id, task_id, attempt, kind, origin, payload):
        cx.execute('INSERT INTO pello_pipeline_exchanges(project_id,task_id,attempt,kind,origin,payload,created) VALUES(?,?,?,?,?,?,?)',
                   (project_id, task_id, attempt, kind, origin, json.dumps(payload, ensure_ascii=False), now()))

    def operation(self, project_id, phase):
        with self.db() as cx:
            row = cx.execute('SELECT * FROM pello_pipeline_operations WHERE project_id=? AND phase=?', (project_id, phase)).fetchone()
        return dict(row) if row else None

    def reserve(self, project_id, phase, request):
        policy = self.policy(project_id)
        with self.db() as cx:
            cx.execute('BEGIN IMMEDIATE')
            count = cx.execute('SELECT count(*) FROM pello_pipeline_operations WHERE project_id=?', (project_id,)).fetchone()[0]
            if count >= policy.max_turns:
                raise CodexBlocked('Configured model turn budget reached; no operation submitted')
            request['selection'] = self.current_selection
            cx.execute('INSERT INTO pello_pipeline_operations VALUES(?,?,?, ?,NULL,?,?)',
                       (project_id, phase, 'IN_FLIGHT', json.dumps(request), now(), now()))

    def save_response(self, project_id, phase, response):
        with self.db() as cx:
            cx.execute('UPDATE pello_pipeline_operations SET status=?,response=?,modified=? WHERE project_id=? AND phase=?',
                       ('COMPLETED', json.dumps(response), now(), project_id, phase))

    def checkpoints(self, project_id):
        with self.db() as cx:
            return [dict(r) for r in cx.execute('SELECT * FROM pello_pipeline_checkpoints WHERE project_id=? ORDER BY rowid', (project_id,))]

    @contextmanager
    def project_lock(self, project_id):
        """OS releases this single-writer lock even after process death."""
        import os
        lock = (self.folder(project_id) / 'pipeline.lock').open('a+b')
        try:
            lock.seek(0, 2)
            if lock.tell() == 0:
                lock.write(b'0'); lock.flush()
            lock.seek(0)
            try:
                if os.name == 'nt':
                    import msvcrt
                    msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as exc:
                raise CodexBlocked('Another pipeline writer holds this project') from exc
            yield
        finally:
            lock.close()
