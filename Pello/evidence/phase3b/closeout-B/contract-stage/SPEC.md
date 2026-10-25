Synthetic n8n MCP QA only. Do not access HMP workflows, credentials or customer services.
Contract: {"workflow_name": "PELLO-3B-MCP-INTEGRATION-QA-bb491b32d40943d5ad8a", "webhook_path": "pello-3b-bb491b32d40943d5ad8a", "request_id_prefix": "pello-3b-", "operation": "double", "value_min": -1000000, "value_max": 1000000, "success_http_status": 200, "invalid_http_status": 400}
Valid: {request_id,status:"ok",result:value*2}; invalid: {request_id:string or null,status:"invalid",error:"invalid_input"}.
Webhook -> Edit Fields -> Respond to Webhook only. No Code, HTTP Request, schedule, credentials or other workflows.
