import argparse
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import sys
from .supervisor import Supervisor


def main():
    project = Path(__file__).resolve().parent.parent
    cli = argparse.ArgumentParser(prog='python -m athis_autopilot.cli', description='ATHIS DEV AUTOPILOT V1')
    cli.add_argument('--root', type=Path, help='Runtime, state, evidence location')
    sub = cli.add_subparsers(dest='command', required=True)
    start = sub.add_parser('start', help='New autonomous job from a product specification')
    start.add_argument('--spec', type=Path, required=True)
    start.add_argument('--suite', type=Path, required=True, help='Owner-authored independent acceptance suite')
    start.add_argument('--mode', choices=['mock', 'codex'], default='mock')
    demo = sub.add_parser('demo', help='Offline red -> green demonstration using deterministic mock')
    resume = sub.add_parser('resume', help='Resume an existing job from SQLite')
    resume.add_argument('job_id')
    status = sub.add_parser('status', help='Inspect persistent job state')
    status.add_argument('job_id')
    doctor = sub.add_parser('doctor', help='Check prerequisites; does not run model turns')
    doctor.add_argument('--check-auth', action='store_true', help='Read SDK account status without showing credentials')
    login = sub.add_parser('login', help='Authenticate official Codex SDK using ChatGPT')
    login.add_argument('--device', action='store_true', help='Use device-code flow')
    args = cli.parse_args()
    if args.root is None:
        config_path = project / 'config' / 'pello.json'
        config = json.loads(config_path.read_text(encoding='utf-8-sig')) if config_path.exists() else {}
        args.root = project / config.get('runtime_root', 'runtime')
    if args.command == 'login':
        try:
            from openai_codex import Codex
        except ImportError:
            print('Install SDK first: python -m pip install -r requirements-codex.txt')
            return 2
        with Codex() as codex:
            handle = codex.login_chatgpt_device_code() if args.device else codex.login_chatgpt()
            if args.device:
                print('Open:', handle.verification_url, 'Code:', handle.user_code, flush=True)
            else:
                print('Open:', handle.auth_url, flush=True)
            print('Finish login in your browser. This terminal waits for the SDK confirmation.', flush=True)
            success = bool(handle.wait().success)
            print('Authenticated:', success)
        return 0 if success else 2
    if args.command == 'doctor':
        checks = {
            'python': sys.version.split()[0], 'os': platform.platform(),
            'python_executable': sys.executable,
            'virtual_environment': sys.prefix != sys.base_prefix,
            'git_installed': shutil.which('git') is not None,
            'codex_python_sdk_installed': importlib.util.find_spec('openai_codex') is not None,
            'runtime_root': str(args.root.resolve()),
            'chatgpt_codex_login_verified': None,
            'notes': 'SDK availability is NOT proof of an authenticated, usable Codex account.'
        }
        auth_code = 0
        if args.check_auth and checks['codex_python_sdk_installed']:
            from .installation import check_auth
            auth = check_auth()
            checks['authentication'] = auth
            checks['chatgpt_codex_login_verified'] = auth.get('authenticated', False)
            auth_code = 0 if auth.get('authenticated') else 2
        print(json.dumps(checks, indent=2, ensure_ascii=False))
        return auth_code or (0 if checks['git_installed'] and checks['codex_python_sdk_installed'] else 2)
    supervisor = Supervisor(args.root)
    if args.command == 'status':
        print(json.dumps(supervisor.job(args.job_id), indent=2, ensure_ascii=False))
        return 0
    if args.command == 'resume':
        job_id = args.job_id
    elif args.command == 'demo':
        job_id = supervisor.create(project / 'examples/clinica/spec.json',
                                   project / 'examples/clinica/acceptance', 'mock')
    elif args.command == 'start':
        job_id = supervisor.create(args.spec, args.suite, args.mode)
    print('JOB_ID:', job_id, flush=True)
    job = supervisor.run(job_id)
    print('STATUS:', job['state'])
    print('TURNS:', job['turns'], '| FIXES:', job['fixes'], '| LAST_TESTS:', job['last_tests'])
    print('REPORT:', (supervisor.root / 'jobs' / job_id / 'report.md'))
    return 0 if job['state'] == 'LISTO_PARA_REVISION' else 2


if __name__ == '__main__':
    raise SystemExit(main())
