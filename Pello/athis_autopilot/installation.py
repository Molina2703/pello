"""Installation diagnostics. No credentials or model turns are returned."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
import platform


def subscription_env():
    env = os.environ.copy()
    for key in ('OPENAI_API_KEY', 'CODEX_API_KEY'):
        env.pop(key, None)
    env['PYTHONUTF8'] = '1'
    return env


def stop_process_tree(proc):
    if os.name == 'nt':
        subprocess.run(['taskkill', '/PID', str(proc.pid), '/T', '/F'],
                       capture_output=True, check=False)
    else:
        import signal
        os.killpg(proc.pid, signal.SIGKILL)
    proc.wait()


def check_auth(timeout=45):
    proc = subprocess.Popen(
        [sys.executable, '-m', 'athis_autopilot.installation', '--auth-child'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
        env=subscription_env(), start_new_session=(os.name != 'nt'))
    try:
        stdout, _ = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_process_tree(proc)
        return {'authenticated': False, 'status': 'BLOCKED', 'reason': 'SDK account check timed out'}
    if proc.returncode:
        return {'authenticated': False, 'status': 'BLOCKED', 'reason': 'SDK account unavailable; run pello login'}
    try:
        return json.loads(stdout)
    except ValueError:
        return {'authenticated': False, 'status': 'BLOCKED', 'reason': 'Invalid SDK account response'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--auth-child', action='store_true')
    parser.add_argument('--init', action='store_true')
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    if args.auth_child:
        from openai_codex import Codex, CodexConfig
        with Codex(CodexConfig(config_overrides=('forced_login_method="chatgpt"',))) as client:
            account = client.account().account
            auth_type = getattr(account.root, 'type', None) if account else None
            print(json.dumps({'authenticated': auth_type == 'chatgpt', 'auth_type': auth_type,
                              'status': 'REAL LOCAL VERIFIED' if auth_type == 'chatgpt' else 'BLOCKED'}))
        return 0
    if args.init:
        from .supervisor import Supervisor
        project = Path(__file__).resolve().parent.parent
        for name in ('config', 'reports', 'evidence'):
            (project / name).mkdir(exist_ok=True)
        config_path = project / 'config' / 'pello.json'
        if not config_path.exists():
            config_path.write_text((project / 'config' / 'pello.example.json').read_text(encoding='utf-8'), encoding='utf-8')
        config = json.loads(config_path.read_text(encoding='utf-8-sig'))
        runtime = Supervisor(project / config['runtime_root'])
        (runtime.root / 'jobs').mkdir(exist_ok=True)
        print('Initialized SQLite and runtime:', runtime.root)
    if args.verify:
        project = Path(__file__).resolve().parent.parent
        stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        evidence = project / 'evidence' / ('setup-check-' + stamp)
        evidence.mkdir(parents=True)
        env = subscription_env()
        commands = {
            'pip-check': [sys.executable, '-m', 'pip', 'check'],
            'unit-tests': [sys.executable, '-m', 'unittest', 'discover', '-s', str(project / 'tests'), '-v'],
            'module-entrypoint': [sys.executable, '-m', 'athis_autopilot', '--help'],
            'console-entrypoint': [str(Path(sys.executable).parent / ('pello.exe' if os.name == 'nt' else 'pello')), '--help'],
            'doctor': [sys.executable, '-m', 'athis_autopilot', 'doctor'],
            'mock-demo': [sys.executable, '-m', 'athis_autopilot', '--root', str(project / 'runtime' / 'setup-validation' / stamp), 'demo'],
        }
        outcomes = {}
        for name, command in commands.items():
            try:
                proc = subprocess.run(command, cwd=project, env=env, capture_output=True,
                                      text=True, encoding='utf-8', timeout=90)
                (evidence / (name + '.log')).write_text(proc.stdout + proc.stderr, encoding='utf-8')
                outcomes[name] = {'exit_code': proc.returncode, 'passed': proc.returncode == 0}
            except (OSError, subprocess.TimeoutExpired) as exc:
                outcomes[name] = {'passed': False, 'reason': str(exc)}
            print(name + ': ' + ('PASS' if outcomes[name]['passed'] else 'FAIL'))
        summary = {'at_utc': stamp, 'python': platform.python_version(), 'os': platform.platform(),
                   'executable': sys.executable, 'checks': outcomes,
                   'passed': all(item['passed'] for item in outcomes.values())}
        (evidence / 'result.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
        print('Verification evidence:', evidence)
        return 0 if summary['passed'] else 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
