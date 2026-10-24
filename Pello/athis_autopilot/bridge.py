"""Additive SQLite storage for one supervised cycle, reusing Supervisor's DB."""
import json
from .supervisor import Supervisor, now


class Bridge(Supervisor):
    def __init__(self, root):
        super().__init__(root)
        with self.db() as cx:
            cx.executescript('''
            CREATE TABLE IF NOT EXISTS pello_migrations(version INTEGER PRIMARY KEY, applied TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pello_projects(
                id TEXT PRIMARY KEY, spec TEXT NOT NULL, stage TEXT NOT NULL,
                suite_hash TEXT NOT NULL, expected_tests INTEGER NOT NULL,
                model TEXT NOT NULL, effort TEXT NOT NULL, created TEXT NOT NULL,
                modified TEXT NOT NULL, task_id TEXT, blocker TEXT NOT NULL DEFAULT '',
                evidence_class TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS pello_tasks(
                project_id TEXT NOT NULL, task_id TEXT NOT NULL, position INTEGER NOT NULL,
                definition TEXT NOT NULL, state TEXT NOT NULL,
                PRIMARY KEY(project_id,task_id));
            CREATE TABLE IF NOT EXISTS pello_sessions(
                project_id TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('supervisor','executor')),
                thread_id TEXT NOT NULL UNIQUE, created TEXT NOT NULL,
                last_successful_turn TEXT, task_id TEXT, status TEXT NOT NULL,
                PRIMARY KEY(project_id,role));
            CREATE TABLE IF NOT EXISTS pello_exchanges(
                seq INTEGER PRIMARY KEY AUTOINCREMENT, project_id TEXT NOT NULL,
                task_id TEXT NOT NULL, kind TEXT NOT NULL, origin TEXT NOT NULL,
                payload TEXT NOT NULL, created TEXT NOT NULL,
                UNIQUE(project_id,kind));
            CREATE TABLE IF NOT EXISTS pello_operations(
                project_id TEXT NOT NULL, phase TEXT NOT NULL, status TEXT NOT NULL,
                request TEXT NOT NULL, response TEXT, created TEXT NOT NULL, modified TEXT NOT NULL,
                PRIMARY KEY(project_id,phase));
            ''')
            cx.execute('INSERT OR IGNORE INTO pello_migrations VALUES(2,?)', (now(),))
        # SQLite cannot widen a CHECK constraint with ALTER COLUMN. Rebuild only
        # this small table, atomically, preserving all seven columns and old roles.
        with self.db() as cx:
            cx.execute('BEGIN IMMEDIATE')
            if not cx.execute('SELECT 1 FROM pello_migrations WHERE version=4').fetchone():
                cx.execute('ALTER TABLE pello_sessions RENAME TO pello_sessions_before_v4')
                cx.execute('''CREATE TABLE pello_sessions(
                    project_id TEXT NOT NULL,
                    role TEXT NOT NULL CHECK(role IN ('supervisor','executor','planner','reviewer','tester')),
                    thread_id TEXT NOT NULL UNIQUE, created TEXT NOT NULL,
                    last_successful_turn TEXT, task_id TEXT, status TEXT NOT NULL,
                    PRIMARY KEY(project_id,role))''')
                cx.execute('INSERT INTO pello_sessions SELECT * FROM pello_sessions_before_v4')
                cx.execute('DROP TABLE pello_sessions_before_v4')
                cx.execute('INSERT INTO pello_migrations VALUES(4,?)', (now(),))

    def project(self, project_id):
        with self.db() as cx:
            row = cx.execute('SELECT * FROM pello_projects WHERE id=?', (project_id,)).fetchone()
        if row is None:
            raise ValueError('Unknown supervised project: ' + project_id)
        return dict(row)

    def folder(self, project_id):
        # Resolve only a previously validated/database-backed ID.
        self.project(project_id)
        return self.root / 'supervised' / project_id

    def tasks(self, project_id):
        with self.db() as cx:
            return [dict(x) for x in cx.execute('SELECT * FROM pello_tasks WHERE project_id=? ORDER BY position', (project_id,))]

    def sessions(self, project_id):
        with self.db() as cx:
            return [dict(x) for x in cx.execute('SELECT * FROM pello_sessions WHERE project_id=? ORDER BY role', (project_id,))]

    def exchanges(self, project_id):
        with self.db() as cx:
            rows = cx.execute('SELECT * FROM pello_exchanges WHERE project_id=? ORDER BY seq', (project_id,)).fetchall()
        return [{**dict(row), 'payload': json.loads(row['payload'])} for row in rows]

    def operation(self, project_id, phase):
        with self.db() as cx:
            row = cx.execute('SELECT * FROM pello_operations WHERE project_id=? AND phase=?', (project_id, phase)).fetchone()
        return dict(row) if row else None

    def reserve(self, project_id, phase, request):
        with self.db() as cx:
            cx.execute('BEGIN IMMEDIATE')
            count = cx.execute('SELECT count(*) FROM pello_operations WHERE project_id=?', (project_id,)).fetchone()[0]
            if count >= 3:
                raise ValueError('Three-turn limit reached')
            cx.execute('INSERT INTO pello_operations VALUES(?,?,?, ?,NULL,?,?)',
                       (project_id, phase, 'IN_FLIGHT', json.dumps(request), now(), now()))

    def save_response(self, project_id, phase, response):
        with self.db() as cx:
            cx.execute('UPDATE pello_operations SET status=?,response=?,modified=? WHERE project_id=? AND phase=?',
                       ('COMPLETED', json.dumps(response), now(), project_id, phase))

    @staticmethod
    def add_exchange(cx, project_id, task_id, kind, origin, payload):
        cx.execute('INSERT INTO pello_exchanges(project_id,task_id,kind,origin,payload,created) VALUES(?,?,?,?,?,?)',
                   (project_id, task_id, kind, origin, json.dumps(payload, ensure_ascii=False), now()))

    @staticmethod
    def set_stage(cx, project_id, stage, **fields):
        allowed = {'task_id', 'blocker'}
        if not set(fields) <= allowed:
            raise ValueError('Unexpected project field')
        values = {'stage': stage, 'modified': now(), **fields}
        cx.execute('UPDATE pello_projects SET ' + ','.join(key + '=?' for key in values) + ' WHERE id=?',
                   (*values.values(), project_id))

    def block(self, project_id, reason):
        with self.db() as cx:
            self.set_stage(cx, project_id, 'BLOCKED', blocker=reason[:4000])
            cx.execute("UPDATE pello_sessions SET status='RECONCILIATION_REQUIRED' WHERE project_id=? AND status='IN_FLIGHT'", (project_id,))
