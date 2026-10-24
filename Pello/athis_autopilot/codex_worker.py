"""Run a single official Codex Python SDK turn in a timeout-bounded subprocess."""
import argparse
import json
import os
import re
import sqlite3
from contextlib import closing, nullcontext
from datetime import datetime, timezone
from pathlib import Path
import sys
import traceback


def restricted_overrides():
    """Disable inherited external tools without changing the user's Codex config."""
    import tomllib
    config_home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    path = config_home / 'config.toml'
    config = tomllib.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    overrides = ['forced_login_method="chatgpt"', 'web_search="disabled"',
                 'features.apps=false', 'features.plugins=false', 'features.multi_agent=false',
                 'sandbox_workspace_write.network_access=false',
                 'sandbox_workspace_write.writable_roots=[]',
                 'sandbox_workspace_write.exclude_tmpdir_env_var=true',
                 'sandbox_workspace_write.exclude_slash_tmp=true',
                 'shell_environment_policy.inherit="none"']
    for name in config.get('mcp_servers', {}):
        # The CLI's -c key path parser splits literal dots; quoting a normal
        # identifier creates a different server entry instead of disabling it.
        if not re.fullmatch(r'[A-Za-z0-9_-]+', name):
            raise ValueError('Cannot safely disable an inherited MCP name with special characters')
        overrides.append('mcp_servers.' + name + '.enabled=false')
    return tuple(overrides)


def persist_session(args, thread_id):
    if args.session_db is None:
        return
    if not args.role or not args.project_id:
        raise ValueError('A durable session requires its project and role')
    timestamp = datetime.now(timezone.utc).isoformat(timespec='seconds')
    with closing(sqlite3.connect(args.session_db, timeout=15)) as cx, cx:
        existing = cx.execute('SELECT thread_id FROM pello_sessions WHERE project_id=? AND role=?',
                              (args.project_id, args.role)).fetchone()
        if existing is None:
            cx.execute('INSERT INTO pello_sessions VALUES(?,?,?,?,?,?,?)',
                       (args.project_id, args.role, thread_id, timestamp, None, args.task_id, 'IN_FLIGHT'))
        elif existing[0] != thread_id:
            raise ValueError('Refusing to replace a role thread without reconciliation')
        else:
            cx.execute("UPDATE pello_sessions SET status='IN_FLIGHT',task_id=? WHERE project_id=? AND role=?",
                       (args.task_id, args.project_id, args.role))


def main(argv=None, *, client=None, thread_cache=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--prompt', type=Path, required=True)
    p.add_argument('--thread-file', type=Path, required=True)
    p.add_argument('--result', type=Path, required=True)
    p.add_argument('--role', choices=['supervisor', 'executor'])
    p.add_argument('--model')
    p.add_argument('--effort', choices=['low', 'medium'])
    p.add_argument('--schema', type=Path)
    p.add_argument('--instructions', type=Path)
    p.add_argument('--prepare-only', action='store_true')
    p.add_argument('--session-db', type=Path)
    p.add_argument('--project-id')
    p.add_argument('--task-id')
    args = p.parse_args(argv)
    from openai_codex import Codex, CodexConfig, Sandbox, ApprovalMode
    # Reuse the user's login; never silently fall back to paid API authentication.
    overrides = restricted_overrides() if args.role else ('forced_login_method="chatgpt"',)
    sandbox = Sandbox.read_only if args.role == 'supervisor' else Sandbox.workspace_write
    scope = nullcontext(client) if client is not None else Codex(CodexConfig(config_overrides=overrides))
    with scope as client:
        account = client.account().account
        if account is None or getattr(account.root, 'type', None) != 'chatgpt':
            raise RuntimeError('ChatGPT authentication required; run pello login')
        if args.model:
            catalog = client.models().data
            selected = next((item for item in catalog if item.model == args.model), None)
            if selected is None or (args.effort and args.effort not in
                    [item.reasoning_effort.value for item in selected.supported_reasoning_efforts]):
                raise RuntimeError('Requested model/effort not available; no automatic model fallback')
        options = {'cwd': str(args.workspace), 'sandbox': sandbox,
                   'approval_mode': ApprovalMode.deny_all}
        if args.model:
            options['model'] = args.model
        if args.instructions:
            options['developer_instructions'] = args.instructions.read_text(encoding='utf-8')
        cache_key = str(args.thread_file.resolve())
        if thread_cache is not None and cache_key in thread_cache:
            thread = thread_cache[cache_key]
            if args.thread_file.read_text(encoding='utf-8').strip() != thread.id:
                raise ValueError('Cached role handle does not match its persisted thread')
        elif args.thread_file.exists():
            thread = client.thread_resume(
                args.thread_file.read_text(encoding='utf-8').strip(),
                **options)
        else:
            thread = client.thread_start(**options)
            args.thread_file.parent.mkdir(parents=True, exist_ok=True)
            args.thread_file.write_text(thread.id, encoding='utf-8')
        if thread_cache is not None:
            thread_cache[cache_key] = thread
        if args.prepare_only:
            args.result.write_text(json.dumps({'status': 'ready', 'thread_id': thread.id,
                                              'role': args.role, 'sandbox': sandbox.value,
                                              'model': args.model, 'effort': args.effort}), encoding='utf-8')
            return 0
        # Persist the real ID before inference, while keeping a fresh thread in
        # this app-server process until its first turn materializes its rollout.
        persist_session(args, thread.id)
        turn_options = {}
        if args.effort:
            from openai_codex.generated.v2_all import ReasoningEffort
            turn_options['effort'] = ReasoningEffort(args.effort)
        if args.schema:
            turn_options['output_schema'] = json.loads(args.schema.read_text(encoding='utf-8'))
        (args.result.parent / 'model-turn-submitted.json').write_text(json.dumps({
            'thread_id': thread.id, 'role': args.role, 'at_utc': datetime.now(timezone.utc).isoformat(),
            'note': 'Submission boundary, not proof of model completion'}), encoding='utf-8')
        turn = thread.run(args.prompt.read_text(encoding='utf-8'), **turn_options)
        status = getattr(turn.status, 'value', str(turn.status))
        usage = turn.usage.model_dump(mode='json') if turn.usage is not None else None
        data = {'status': status, 'thread_id': thread.id, 'turn_id': turn.id,
                'usage': usage, 'final_response': (turn.final_response or '')[-64000:],
                'error': str(turn.error) if turn.error else None}
        args.result.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return 0


def serve():
    from openai_codex import Codex, CodexConfig
    with Codex(CodexConfig(config_overrides=restricted_overrides())) as client:
        threads = {}
        for line in sys.stdin:
            try:
                exit_code = main(json.loads(line), client=client, thread_cache=threads)
                reply = {'exit_code': exit_code}
            except Exception as exc:
                traceback.print_exc(file=sys.stderr)
                reply = {'exit_code': 1, 'error': f'{type(exc).__name__}: {exc}'}
            print(json.dumps(reply), flush=True)
    return 0


if __name__ == '__main__':
    raise SystemExit(serve() if sys.argv[1:] == ['--serve'] else main())
