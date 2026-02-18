# Claude Code MCP Configuration Complete

**Date**: January 25, 2026  
**Status**: ✅ Configured

## Configuration Summary

Claude Code has been configured to connect to Agent Zero's MCP server.

### Configuration File

- **Location**: `/root/.claude/.mcp.json`
- **Status**: ✅ Created and validated

### Configuration Details

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

### MCP Server Details

- **Name**: `agent-zero`
- **Type**: `sse` (Server-Sent Events)
- **URL**: `http://localhost:8888/mcp/t-xbeIyWyhBATmcuJk/sse`
- **Token**: `xbeIyWyhBATmcuJk`

## Verification

### Check Configuration File

```bash
docker exec agent-zero cat /root/.claude/.mcp.json
```

### List MCP Servers

```bash
docker exec agent-zero claude-pro mcp list
```

Expected output should include `agent-zero` in the list of configured MCP servers.

### Test Connection

```bash
# Test by asking Claude Code to use Agent Zero
docker exec agent-zero claude-pro 'Use Agent Zero to list files in /a0 directory'
```

Or interactively:
```bash
docker exec -it agent-zero claude-pro
# Then ask: "Use Agent Zero to scan localhost"
```

## Available Agent Zero Tools

Once connected, Claude Code can use these Agent Zero tools:

### Communication Tools
- `send_message` - Send tasks to Agent Zero
- `finish_chat` - End chat sessions

### Security Assessment Tools
- `network_scan` - Run nmap/masscan scans
- `web_scan` - Run nikto/nuclei web scans
- `code_review` - Run semgrep/bandit SAST
- `get_assessment_state` - Get assessment state
- `update_finding` - Add/update findings
- `add_target` - Add targets to scope

## Usage Examples

### Example 1: Network Scanning

Ask Claude Code:
```
Use Agent Zero to scan 192.168.1.0/24 for open ports
```

Claude Code will invoke Agent Zero's `network_scan` tool.

### Example 2: Web Application Testing

Ask Claude Code:
```
Use Agent Zero to scan https://example.com for vulnerabilities
```

Claude Code will invoke Agent Zero's `web_scan` tool.

### Example 3: Code Review

Ask Claude Code:
```
Use Agent Zero to review the code in /app/src for security issues
```

Claude Code will invoke Agent Zero's `code_review` tool.

### Example 4: Task Delegation

Ask Claude Code:
```
Ask Agent Zero to install nmap and scan localhost
```

Claude Code will use `send_message` to delegate the task to Agent Zero.

## Troubleshooting

### MCP Server Not Listed

If `agent-zero` doesn't appear in `claude-pro mcp list`:

1. **Verify configuration file exists**:
   ```bash
   docker exec agent-zero ls -la /root/.claude/.mcp.json
   ```

2. **Check JSON syntax**:
   ```bash
   docker exec agent-zero cat /root/.claude/.mcp.json | python3 -m json.tool
   ```

3. **Restart Claude Code** (if running as a service):
   - The configuration is loaded when Claude Code starts
   - For one-off commands, it should load automatically

### Connection Errors

If Claude Code can't connect to Agent Zero:

1. **Verify Agent Zero is running**:
   ```bash
   docker ps | grep agent-zero
   ```

2. **Test MCP endpoint**:
   ```bash
   curl http://localhost:8888/mcp/t-xbeIyWyhBATmcuJk/sse
   ```

3. **Check token is correct**:
   ```bash
   docker exec agent-zero cat /a0/tmp/settings.json | grep mcp_server_token
   ```

### Tools Not Available

If Claude Code can't see Agent Zero tools:

1. **Verify MCP connection**:
   ```bash
   docker exec agent-zero claude-pro mcp list
   ```

2. **Check Agent Zero MCP server**:
   - Web UI → Settings → MCP Server
   - Verify server is enabled

3. **Test with send_message**:
   ```bash
   docker exec agent-zero claude-pro 'Use Agent Zero send_message tool to say hello'
   ```

## Configuration Persistence

The configuration file at `/root/.claude/.mcp.json` is:
- ✅ **Persistent**: Stored in container's filesystem
- ⚠️  **Not volume-mounted**: Will be lost if container is rebuilt
- 💡 **Recommendation**: Consider mounting `/root/.claude` as a volume if you want persistence

To make it persistent, add to `docker-compose.yml`:
```yaml
volumes:
  - ./claude-mcp-config:/root/.claude
```

## Related Documentation

- **[MCP Token Configuration](./MCP_TOKEN_CONFIGURED.md)** - Token setup
- **[How Claude Uses Agent Zero](./docs/HOW_CLAUDE_USES_AGENT_ZERO.md)** - Integration guide
- **[Test Claude Integration](./docs/TEST_CLAUDE_INTEGRATION.md)** - Testing procedures

## Quick Reference

**Configuration File**: `/root/.claude/.mcp.json`

**Verify Configuration**:
```bash
docker exec agent-zero claude-pro mcp list
```

**Test Connection**:
```bash
docker exec agent-zero claude-pro 'Use Agent Zero to list files'
```

**Update Configuration**:
```bash
./configure_claude_mcp.sh
```
