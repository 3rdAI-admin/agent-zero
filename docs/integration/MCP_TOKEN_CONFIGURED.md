# MCP Token Configuration Complete

**Date**: January 25, 2026  
**Status**: ✅ Configured

## Configuration Summary

The MCP token has been successfully configured in Agent Zero's settings.

### Token Details

- **Token**: `xbeIyWyhBATmcuJk`
- **Location**: `/a0/tmp/settings.json`
- **Generated From**: Runtime ID + Username + Password (SHA256 hash)

### MCP Connection URLs

**SSE Endpoint** (Server-Sent Events):
```
http://localhost:8888/mcp/t-xbeIyWyhBATmcuJk/sse
```

**HTTP Endpoint** (Streamable HTTP):
```
http://localhost:8888/mcp/t-xbeIyWyhBATmcuJk/http/
```

## Claude Code Configuration

Add this to Claude Code's `mcp.json` configuration file:

```json
{
    "mcpServers": {
        "agent-zero": {
            "type": "sse",
            "url": "http://localhost:8888/mcp/t-xbeIyWyhBATmcuJk/sse"
        }
    }
}
```

**For remote access** (if Agent Zero is on a different machine):

```json
{
    "mcpServers": {
        "agent-zero": {
            "type": "sse",
            "url": "http://YOUR_AGENT_ZERO_IP:8888/mcp/t-xbeIyWyhBATmcuJk/sse"
        }
    }
}
```

## Verification

### Method 1: Via Web UI
1. Open Agent Zero Web UI: http://localhost:8888
2. Navigate to: **Settings > MCP Server**
3. Verify the MCP Server URL matches the token above

### Method 2: Via Settings File
```bash
docker exec agent-zero cat /a0/tmp/settings.json | grep mcp_server_token
```

### Method 3: Test Endpoint
```bash
# Test SSE endpoint (may return 200, 401, or 500 depending on headers)
curl http://localhost:8888/mcp/t-xbeIyWyhBATmcuJk/sse
```

**Note**: The endpoint may return various status codes when accessed directly with curl, as it expects specific MCP protocol headers. This is normal - the important thing is that the endpoint exists and the token is configured.

## Token Regeneration

The token is automatically generated from:
- Runtime ID (persistent across restarts)
- Username (`AUTH_LOGIN`)
- Password (`AUTH_PASSWORD`)

**If you change your credentials**, the token will automatically update when:
1. Settings are reloaded in the Web UI
2. Agent Zero restarts
3. Settings are saved via the API

To manually regenerate:
```bash
./configure_mcp_token.sh
```

## MCP Server Reconfiguration

The MCP server automatically reconfigures when:
- Settings are saved via Web UI
- Settings are updated via API
- Agent Zero restarts

If you need to force reconfiguration, restart Agent Zero:
```bash
docker restart agent-zero
```

## Next Steps

1. ✅ **MCP Token**: Configured
2. ⏭️ **Configure Claude Code**: Add MCP server to Claude Code's config
3. ⏭️ **Test Connection**: Verify Claude Code can connect to Agent Zero
4. ⏭️ **Test Tools**: Try using Agent Zero tools from Claude Code

## Available MCP Tools

Once Claude Code is connected, it can use these Agent Zero tools:

### Communication
- `send_message` - Send tasks to Agent Zero
- `finish_chat` - End chat sessions

### Security Assessment
- `network_scan` - Run nmap/masscan scans
- `web_scan` - Run nikto/nuclei web scans
- `code_review` - Run semgrep/bandit SAST
- `get_assessment_state` - Get assessment state
- `update_finding` - Add/update findings
- `add_target` - Add targets to scope

## Troubleshooting

### Token Not Working

1. **Verify token in settings**:
   ```bash
   docker exec agent-zero cat /a0/tmp/settings.json | grep mcp_server_token
   ```

2. **Regenerate token**:
   ```bash
   ./configure_mcp_token.sh
   ```

3. **Restart Agent Zero**:
   ```bash
   docker restart agent-zero
   ```

### MCP Endpoint Not Accessible

1. **Check Agent Zero is running**:
   ```bash
   docker ps | grep agent-zero
   ```

2. **Check Web UI is accessible**:
   ```bash
   curl http://localhost:8888
   ```

3. **Verify port mapping**:
   ```bash
   docker port agent-zero
   ```

### Token Changed After Credential Update

This is expected! The token is generated from credentials. If you change your username/password:
1. The token will automatically update
2. Update Claude Code's MCP configuration with the new token
3. Get the new token from: Settings > MCP Server

## Related Documentation

- **[How Claude Uses Agent Zero](./docs/HOW_CLAUDE_USES_AGENT_ZERO.md)** - Integration guide
- **[Test Claude Integration](./docs/TEST_CLAUDE_INTEGRATION.md)** - Testing procedures
- **[MCP vs A2A Comparison](./docs/MCP_VS_A2A_COMPARISON.md)** - Protocol comparison

## Quick Reference

**Get Token**:
```bash
docker exec agent-zero cat /a0/tmp/settings.json | grep mcp_server_token
```

**Regenerate Token**:
```bash
./configure_mcp_token.sh
```

**MCP URL Format**:
```
http://localhost:8888/mcp/t-{TOKEN}/sse
```
