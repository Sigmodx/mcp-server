# sigmodx-mcp

MCP server for [Sigmodx](https://sigmodx.com) — audit infrastructure
for AI agents making consequential decisions.

Exposes Sigmodx as MCP tools any compatible agent framework can call.
Works with Claude, Cursor, LangChain, AutoGen, and any MCP client.

## Installation

```bash
pip install sigmodx-mcp
```

## Usage

```bash
SIGMODX_API_KEY=your-key \
SIGMODX_AGENT_ID=your-agent-uuid \
sigmodx-mcp
```

## Claude Desktop / Cursor configuration

Add to your MCP config:

```json
{
  "mcpServers": {
    "sigmodx": {
      "command": "sigmodx-mcp",
      "env": {
        "SIGMODX_API_KEY": "your-api-key",
        "SIGMODX_AGENT_ID": "your-agent-uuid"
      }
    }
  }
}
```

## Available tools

| Tool | Description |
|------|-------------|
| `sigmodx_log_invoice_decision` | Log invoice approval/rejection |
| `sigmodx_log_gl_decision` | Log GL entry review decision |
| `sigmodx_log_anomaly_decision` | Log anomaly flag/clear/escalate |
| `sigmodx_verify_attestation` | Verify a verification string |
| `sigmodx_get_reliability` | Get agent ALLOW/LIMIT/BLOCK state |
| `sigmodx_hash_inputs` | Hash input payload (no auth needed) |

## Links

- [Sigmodx](https://sigmodx.com)
- [API reference](https://sigmodx.com/docs/agent-api)
- [GitHub](https://github.com/Sigmodx/mcp-server)
