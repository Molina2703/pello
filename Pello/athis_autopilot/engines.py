"""Replaceable execution engines. Mock is a deterministic orchestration test, NOT AI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import queue
import threading


class EngineError(Exception):
    pass


class CodexBlocked(EngineError):
    pass


def worker_environment(restricted=False):
    env = os.environ.copy()
    if restricted:
        permitted = {'PATH', 'PATHEXT', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'TEMP', 'TMP',
                     'USERPROFILE', 'HOME', 'LOCALAPPDATA', 'APPDATA', 'PROGRAMFILES',
                     'PROGRAMFILES(X86)', 'CODEX_HOME', 'CODEX_CA_CERTIFICATE', 'SSL_CERT_FILE'}
        env = {key: value for key, value in env.items() if key.upper() in permitted}
    env.pop('OPENAI_API_KEY', None)
    env.pop('CODEX_API_KEY', None)
    project_root = str(Path(__file__).resolve().parent.parent)
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
    env['PYTHONUTF8'] = '1'
    return env


class CodexWorkerProcess:
    """One local SDK process for a whole cycle, retaining both role handles."""
    def __init__(self, evidence_dir):
        evidence_dir.mkdir(parents=True, exist_ok=True)
        self.responses = queue.Queue()
        self.proc = subprocess.Popen([sys.executable, '-m', 'athis_autopilot.codex_worker', '--serve'],
            cwd=Path(__file__).resolve().parent.parent, env=worker_environment(True),
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding='utf-8', start_new_session=(os.name != 'nt'))
        def read_responses():
            for line in self.proc.stdout:
                self.responses.put(line)
            self.responses.put(None)
        def save_stderr():
            with (evidence_dir / 'sdk-worker-stderr.log').open('a', encoding='utf-8') as output:
                for line in self.proc.stderr:
                    output.write(line); output.flush()
        self.reader = threading.Thread(target=read_responses, daemon=True)
        self.stderr_reader = threading.Thread(target=save_stderr, daemon=True)
        self.reader.start(); self.stderr_reader.start()

    def execute(self, argv, timeout):
        self.proc.stdin.write(json.dumps(argv) + '\n'); self.proc.stdin.flush()
        try:
            line = self.responses.get(timeout=timeout)
        except queue.Empty as exc:
            from .installation import stop_process_tree
            stop_process_tree(self.proc)
            raise CodexBlocked('SDK worker timeout; reconcile operation effects before retrying') from exc
        if line is None:
            raise EngineError('SDK worker closed before responding; inspect sdk-worker-stderr.log')
        reply = json.loads(line)
        return reply['exit_code'], '', reply.get('error', '')

    def close(self):
        if self.proc.poll() is None:
            self.proc.stdin.close()
            try:
                self.proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                from .installation import stop_process_tree
                stop_process_tree(self.proc)
        self.reader.join(timeout=2); self.stderr_reader.join(timeout=2)
        for pipe in (self.proc.stdout, self.proc.stderr):
            pipe.close()


BROKEN = '''"""Intentional faulty starting implementation for offline smoke test."""
class ClinicBooking:
    def __init__(self):
        self.bookings = {}
    def reserve(self, slot, customer_id, request_id, confirmed):
        booking = {"slot": slot, "customer_id": customer_id, "request_id": request_id}
        self.bookings[request_id] = booking
        return booking
    def cancel(self, request_id):
        return self.bookings.pop(request_id, None) is not None
    def slots(self, candidates):
        return list(candidates)
'''

FIXED = '''"""Correct demo appointment engine, NOT a production Google Calendar integration."""
from threading import RLock

class ClinicBooking:
    def __init__(self):
        self._lock = RLock()
        self._by_request = {}
        self._by_slot = {}

    def reserve(self, slot, customer_id, request_id, confirmed):
        if not all(isinstance(x, str) and x.strip() for x in (slot, customer_id, request_id)):
            raise ValueError("Missing booking field")
        with self._lock:
            if request_id in self._by_request:
                previous = self._by_request[request_id]
                if previous["slot"] != slot or previous["customer_id"] != customer_id:
                    raise ValueError("Request key collision")
                return previous.copy()
            if not confirmed:
                raise ValueError("Booking requires confirmation")
            if slot in self._by_slot:
                raise ValueError("Slot already reserved")
            booking = {"slot": slot, "customer_id": customer_id, "request_id": request_id}
            self._by_request[request_id] = booking
            self._by_slot[slot] = request_id
            return booking.copy()

    def cancel(self, request_id):
        with self._lock:
            booking = self._by_request.pop(request_id, None)
            if booking is None:
                return False
            self._by_slot.pop(booking["slot"], None)
            return True

    def slots(self, candidates):
        with self._lock:
            return [slot for slot in candidates if slot not in self._by_slot]
'''


def run_mock(workspace: Path, *, fixing: bool) -> dict:
    (workspace / 'booking.py').write_text(FIXED if fixing else BROKEN, encoding='utf-8')
    (workspace / 'IMPLEMENTATION.md').write_text(
        'Demo local in-memory con datos ficticios. No integra WhatsApp, n8n ni Calendar.\n'
        'El ejecutor mock utiliza una corrección preprogramada; no genera decisiones de IA.\n',
        encoding='utf-8'
    )
    return {"engine": "mock", "phase": "fix" if fixing else "initial", "usage": None}


def run_codex(workspace: Path, prompt: str, thread_file: Path, out_dir: Path, timeout_s: int,
              *, role=None, model=None, effort=None, output_schema=None, prepare_only=False,
              instructions='', session_db=None, project_id=None, task_id=None, runner=None) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = out_dir / 'codex_prompt.txt'
    result_file = out_dir / 'codex_result.json'
    prompt_file.write_text(prompt, encoding='utf-8')
    command = [sys.executable, '-m', 'athis_autopilot.codex_worker',
               '--workspace', str(workspace), '--prompt', str(prompt_file),
               '--thread-file', str(thread_file), '--result', str(result_file)]
    for flag, value in (('--role', role), ('--model', model), ('--effort', effort),
                        ('--session-db', session_db), ('--project-id', project_id), ('--task-id', task_id)):
        if value is not None:
            command.extend([flag, str(value)])
    if prepare_only:
        command.append('--prepare-only')
    if output_schema is not None:
        schema_file = out_dir / 'output-schema.json'
        schema_file.write_text(json.dumps(output_schema), encoding='utf-8')
        command.extend(['--schema', str(schema_file)])
    if instructions:
        instructions_file = out_dir / 'role-instructions.txt'
        instructions_file.write_text(instructions, encoding='utf-8')
        command.extend(['--instructions', str(instructions_file)])
    if runner is not None:
        returncode, stdout, stderr = runner.execute(command[3:], timeout_s)
    else:
        from .installation import stop_process_tree
        worker = subprocess.Popen(command, cwd=workspace, env=worker_environment(bool(role)), stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True, encoding='utf-8',
                                  start_new_session=(os.name != 'nt'))
        try:
            stdout, stderr = worker.communicate(timeout=timeout_s)
        except subprocess.TimeoutExpired as exc:
            stop_process_tree(worker)
            stdout, stderr = worker.communicate()
            (out_dir / 'codex_stdout.log').write_text(stdout[-200000:], encoding='utf-8')
            (out_dir / 'codex_stderr.log').write_text(stderr[-200000:], encoding='utf-8')
            raise CodexBlocked(f'Codex turn exceeded {timeout_s}s; thread saved if initialized') from exc
        returncode = worker.returncode
    (out_dir / 'codex_stdout.log').write_text(stdout[-200000:], encoding='utf-8')
    (out_dir / 'codex_stderr.log').write_text(stderr[-200000:], encoding='utf-8')
    if returncode != 0:
        detail = (stderr or stdout)[-2000:]
        if any(keyword in detail.lower() for keyword in (
                'authentication', 'not logged in', 'unauthorized', 'quota', 'rate limit',
                'usage limit', 'insufficient', 'approval', 'permission denied')):
            raise CodexBlocked(f'Authentication, limits or permission blocker: {detail}')
        raise EngineError(f'Codex worker exited {returncode}: {detail}')
    if not result_file.is_file():
        raise EngineError('Codex worker exited without its result file')
    result = json.loads(result_file.read_text(encoding='utf-8'))
    if result.get('status') != ('ready' if prepare_only else 'completed'):
        detail = f'Codex turn status: {result.get("status")}, {result.get("error")}'
        if any(word in detail.lower() for word in ('quota', 'rate limit', 'usage limit', 'authentication', 'unauthorized', 'permission', 'approval')):
            raise CodexBlocked(detail)
        raise EngineError(detail)
    return result
