"""Replaceable execution engines. Mock is a deterministic orchestration test, NOT AI."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time


class EngineError(Exception):
    pass


class CodexBlocked(EngineError):
    pass


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
              instructions='') -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    prompt_file = out_dir / 'codex_prompt.txt'
    result_file = out_dir / 'codex_result.json'
    prompt_file.write_text(prompt, encoding='utf-8')
    command = [sys.executable, '-m', 'athis_autopilot.codex_worker',
               '--workspace', str(workspace), '--prompt', str(prompt_file),
               '--thread-file', str(thread_file), '--result', str(result_file)]
    for flag, value in (('--role', role), ('--model', model), ('--effort', effort)):
        if value is not None:
            command.extend([flag, value])
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
    env = os.environ.copy()
    if role:
        permitted = {'PATH', 'PATHEXT', 'SYSTEMROOT', 'WINDIR', 'COMSPEC', 'TEMP', 'TMP',
                     'USERPROFILE', 'HOME', 'LOCALAPPDATA', 'APPDATA', 'PROGRAMFILES',
                     'PROGRAMFILES(X86)', 'CODEX_HOME', 'CODEX_CA_CERTIFICATE', 'SSL_CERT_FILE'}
        env = {key: value for key, value in env.items() if key.upper() in permitted}
    # Default to ChatGPT subscription session rather than accidental API-key billing.
    env.pop('OPENAI_API_KEY', None)
    env.pop('CODEX_API_KEY', None)
    # Runner must be importable even though the subprocess executes in an agent workspace.
    project_root = str(Path(__file__).resolve().parent.parent)
    env['PYTHONPATH'] = project_root + os.pathsep + env.get('PYTHONPATH', '')
    from .installation import stop_process_tree
    env['PYTHONUTF8'] = '1'
    worker = subprocess.Popen(command, cwd=workspace, env=env, stdout=subprocess.PIPE,
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
    (out_dir / 'codex_stdout.log').write_text(stdout[-200000:], encoding='utf-8')
    (out_dir / 'codex_stderr.log').write_text(stderr[-200000:], encoding='utf-8')
    if worker.returncode != 0:
        detail = (stderr or stdout)[-2000:]
        if any(keyword in detail.lower() for keyword in (
                'authentication', 'not logged in', 'unauthorized', 'quota', 'rate limit',
                'usage limit', 'insufficient', 'approval', 'permission denied')):
            raise CodexBlocked(f'Authentication, limits or permission blocker: {detail}')
        raise EngineError(f'Codex worker exited {worker.returncode}: {detail}')
    if not result_file.is_file():
        raise EngineError('Codex worker exited without its result file')
    result = json.loads(result_file.read_text(encoding='utf-8'))
    if result.get('status') != ('ready' if prepare_only else 'completed'):
        detail = f'Codex turn status: {result.get("status")}, {result.get("error")}'
        if any(word in detail.lower() for word in ('quota', 'rate limit', 'usage limit', 'authentication', 'unauthorized', 'permission', 'approval')):
            raise CodexBlocked(detail)
        raise EngineError(detail)
    return result
