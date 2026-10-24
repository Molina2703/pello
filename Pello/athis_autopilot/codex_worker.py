"""Run a single official Codex Python SDK turn in a timeout-bounded subprocess."""
import argparse
import json
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--workspace', type=Path, required=True)
    p.add_argument('--prompt', type=Path, required=True)
    p.add_argument('--thread-file', type=Path, required=True)
    p.add_argument('--result', type=Path, required=True)
    args = p.parse_args()
    from openai_codex import Codex, CodexConfig, Sandbox, ApprovalMode
    # Reuse the user's login; never silently fall back to paid API authentication.
    with Codex(CodexConfig(config_overrides=('forced_login_method="chatgpt"',))) as client:
        account = client.account().account
        if account is None or getattr(account.root, 'type', None) != 'chatgpt':
            raise RuntimeError('ChatGPT authentication required; run pello login')
        if args.thread_file.exists():
            thread = client.thread_resume(
                args.thread_file.read_text(encoding='utf-8').strip(),
                cwd=str(args.workspace), sandbox=Sandbox.workspace_write,
                approval_mode=ApprovalMode.deny_all)
        else:
            thread = client.thread_start(
                cwd=str(args.workspace), sandbox=Sandbox.workspace_write,
                approval_mode=ApprovalMode.deny_all)
            args.thread_file.write_text(thread.id, encoding='utf-8')
        turn = thread.run(args.prompt.read_text(encoding='utf-8'))
        status = getattr(turn.status, 'value', str(turn.status))
        usage = turn.usage.model_dump(mode='json') if turn.usage is not None else None
        data = {'status': status, 'thread_id': thread.id, 'turn_id': turn.id,
                'usage': usage, 'final_response': (turn.final_response or '')[-12000:],
                'error': str(turn.error) if turn.error else None}
        args.result.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
