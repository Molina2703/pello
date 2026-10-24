"""Run a single official Codex Python SDK turn in a timeout-bounded subprocess."""
import argparse
import json
import os
import re
from pathlib import Path


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


def main() -> int:
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
    args = p.parse_args()
    from openai_codex import Codex, CodexConfig, Sandbox, ApprovalMode
    # Reuse the user's login; never silently fall back to paid API authentication.
    overrides = restricted_overrides() if args.role else ('forced_login_method="chatgpt"',)
    sandbox = Sandbox.read_only if args.role == 'supervisor' else Sandbox.workspace_write
    with Codex(CodexConfig(config_overrides=overrides)) as client:
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
        if args.thread_file.exists():
            thread = client.thread_resume(
                args.thread_file.read_text(encoding='utf-8').strip(),
                **options)
        else:
            thread = client.thread_start(**options)
            args.thread_file.parent.mkdir(parents=True, exist_ok=True)
            args.thread_file.write_text(thread.id, encoding='utf-8')
        if args.prepare_only:
            args.result.write_text(json.dumps({'status': 'ready', 'thread_id': thread.id,
                                              'role': args.role, 'sandbox': sandbox.value,
                                              'model': args.model, 'effort': args.effort}), encoding='utf-8')
            return 0
        turn_options = {}
        if args.effort:
            from openai_codex.generated.v2_all import ReasoningEffort
            turn_options['effort'] = ReasoningEffort(args.effort)
        if args.schema:
            turn_options['output_schema'] = json.loads(args.schema.read_text(encoding='utf-8'))
        turn = thread.run(args.prompt.read_text(encoding='utf-8'), **turn_options)
        status = getattr(turn.status, 'value', str(turn.status))
        usage = turn.usage.model_dump(mode='json') if turn.usage is not None else None
        data = {'status': status, 'thread_id': thread.id, 'turn_id': turn.id,
                'usage': usage, 'final_response': (turn.final_response or '')[-64000:],
                'error': str(turn.error) if turn.error else None}
        args.result.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
