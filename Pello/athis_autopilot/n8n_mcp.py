"""Official n8n MCP through the existing Codex SDK runtime, never direct REST."""
import json
import os
from pathlib import Path
import tomllib

SERVER = 'n8n'
ORIGIN = 'https://n8n-production-3374.up.railway.app'
ENDPOINT = ORIGIN + '/mcp-server/http'
PROTECTED_IDS = {'dFoCUpXVrP9gc9rY', 'I4qwL8MuXvTotZKU'}
READ_TOOLS = {'search_workflows', 'get_workflow_details', 'get_node_types',
              'search_nodes', 'get_workflow_history', 'get_workflow_version',
              'get_workflow_sdk_reference', 'get_workflow_best_practices',
              'get_workflow_execution', 'search_workflow_executions', 'validate_workflow'}
RESOURCE_READS = {'get_workflow_details', 'get_workflow_history', 'get_workflow_version',
                  'get_workflow_execution', 'search_workflow_executions'}


def connection_summary():
    home = Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex')))
    config = tomllib.loads((home / 'config.toml').read_text(encoding='utf-8'))
    server = config.get('mcp_servers', {}).get(SERVER, {})
    if server.get('url') != ENDPOINT or server.get('enabled', True) is not True:
        raise ValueError('Expected enabled official n8n connection is unavailable')
    # Only non-secret configuration leaves this function.
    return {'server': SERVER, 'endpoint': ENDPOINT, 'configured': True}


def executor_config(role, tools=None, *, controlled_mutation=False):
    if role != 'executor':
        raise ValueError('n8n MCP is available only to the controlled executor')
    connection_summary()
    config = {'mcp_servers.n8n.enabled': True, 'mcp_servers.n8n.startup_timeout_sec': 120}
    if tools is not None:
        from .n8n_operations import MUTATIONS
        if not set(tools) <= READ_TOOLS | (MUTATIONS if controlled_mutation else set()):
            raise ValueError('Preflight allows read-only tools only')
        config['mcp_servers.n8n.enabled_tools'] = sorted(tools)
    return config


def worker_request(client, *, role, workspace, request):
    """No model inference in this transport context; Core submits exact RPC args.

    The enclosing worker's global config disables every MCP server. This fresh
    executor context enables only n8n. Planner/Reviewer handles never inherit it.
    """
    from openai_codex import Sandbox, ApprovalMode
    from openai_codex.generated.v2_all import ListMcpServerStatusResponse, McpServerToolCallResponse
    action = request['action']
    tool = request.get('tool')
    proof = request.get('operation')
    from .n8n_operations import MUTATIONS, claim_operation, finish_operation
    if action not in ('inventory', 'call') or (action == 'call' and tool not in READ_TOOLS | (MUTATIONS if proof else set())):
        raise ValueError('Unapproved MCP preflight action')
    if tool in RESOURCE_READS and not proof:
        raise ValueError('Resource reads require project ownership authorization')
    arguments = request.get('arguments', {})
    if tool == 'search_workflows' and not str(arguments.get('query', '')).startswith('PELLO-3B-'):
        raise ValueError('Preflight search must target the dedicated QA namespace')
    if 'workflowId' in arguments and arguments['workflowId'] in PROTECTED_IDS:
        raise ValueError('Protected workflow is outside the pilot')
    thread = client.thread_start(cwd=str(workspace), sandbox=Sandbox.read_only,
        approval_mode=ApprovalMode.deny_all, ephemeral=True,
        config=executor_config(role, None if action == 'inventory' else {tool}, controlled_mutation=bool(proof)),
        developer_instructions='MCP transport context. No model turns. Only Core submits authorized operations.')
    rpc = client._client  # SDK 0.163 exposes native MCP RPC on CodexClient.
    if action == 'inventory':
        raw = rpc.request('mcpServerStatus/list', {'threadId': thread.id, 'serverName': SERVER},
                          response_model=ListMcpServerStatusResponse)
        result = raw.model_dump(mode='json', by_alias=True)
    else:
        if proof: claim_operation(proof, tool, arguments, thread.id)
        raw = rpc.request('mcpServer/tool/call', {'threadId': thread.id, 'server': SERVER,
                          'tool': tool, 'arguments': arguments}, response_model=McpServerToolCallResponse)
        result = raw.model_dump(mode='json', by_alias=True)
        if proof: finish_operation(proof, result)
    return {'status': 'completed', 'thread_id': thread.id, 'server': SERVER,
            'action': action, 'tool': tool, 'result': result, 'model_inference': False}
