"""Catalogue-validated routing. Read-only probe makes no inference calls."""
import json
import subprocess
import sys
from .engines import worker_environment, CodexBlocked
from .installation import stop_process_tree
from .supervisor import now


def probe_capabilities():
    proc = subprocess.Popen([sys.executable, '-m', 'athis_autopilot.model_policy', '--probe'],
        env=worker_environment(True), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, encoding='utf-8', start_new_session=(sys.platform != 'win32'))
    try:
        stdout, stderr = proc.communicate(timeout=60)
    except subprocess.TimeoutExpired as exc:
        stop_process_tree(proc)
        raise CodexBlocked('Model/account probe timed out; no inference submitted') from exc
    if proc.returncode:
        raise CodexBlocked('Model/account probe unavailable: ' + stderr[-1500:])
    return json.loads(stdout)


def select_model(policy, capabilities, *, phase, risk='routine', attempt=1):
    if not capabilities.get('authenticated'):
        raise CodexBlocked('ChatGPT authentication required')
    remaining = capabilities.get('remaining_percent')
    if remaining is not None and remaining <= 0:
        raise CodexBlocked('Quota exhausted; preserve state before continuing')
    advanced = risk == 'high' or attempt > 1
    model = policy.advanced_model if advanced else policy.routine_model
    effort = policy.advanced_effort if advanced else policy.routine_effort
    # Review/planning are separate responsibilities; routine tiny fixtures need no expensive default.
    if effort not in capabilities.get('models', {}).get(model, []):
        raise CodexBlocked(f'Unavailable configured model/effort {model}/{effort}; no silent substitution')
    return {'model': model, 'effort': effort, 'reason': ('risk/failure escalation' if advanced else 'routine bounded increment'),
            'phase': phase, 'remaining_percent_at_probe': remaining, 'capabilities_at': capabilities.get('at')}


def main():
    from openai_codex import CodexConfig
    from openai_codex.client import CodexClient
    from openai_codex.generated.v2_all import GetAccountRateLimitsResponse
    from .codex_worker import restricted_overrides
    client = CodexClient(config=CodexConfig(config_overrides=restricted_overrides()))
    try:
        client.start(); client.initialize()
        account = client.account_read().account
        models = {m.model: [e.reasoning_effort.value for e in m.supported_reasoning_efforts]
                  for m in client.model_list().data}
        remaining = None
        windows = []
        try:
            limits = client.request('account/rateLimits/read', {}, response_model=GetAccountRateLimitsResponse)
            # Only usage windows; never persist account IDs, credits or credential material.
            for window in (limits.rate_limits.primary, limits.rate_limits.secondary):
                if window is not None:
                    windows.append({'used_percent': window.used_percent, 'resets_at': window.resets_at})
            if windows:
                remaining = min(max(0, 100 - w['used_percent']) for w in windows)
        except Exception:
            pass  # Unknown capacity is not zero or unlimited; execution errors still block.
        print(json.dumps({'authenticated': account is not None and account.root.type == 'chatgpt',
                          'models': models, 'remaining_percent': remaining, 'usage_windows': windows, 'at': now()}))
    finally:
        client.close()


if __name__ == '__main__':
    main()
