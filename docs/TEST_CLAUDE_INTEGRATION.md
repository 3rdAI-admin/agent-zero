# Testing Claude Code Integration with Agent Zero

This guide walks you through testing the bidirectional integration between Claude Code and Agent Zero.

## Prerequisites

- Agent Zero running in Docker container
- Claude Code installed in the container
- Access to Agent Zero Web UI

## Quick Test

Run the automated test script:

```bash
./test_claude_integration.sh
```

This will test:
1. ✅ Claude Code installation
2. ✅ Agent Zero Web UI accessibility
3. ✅ Agent Zero → Claude Code (terminal execution)
4. ✅ MCP endpoint availability
5. ✅ MCP token configuration
6. ✅ YOLO mode wrapper

## Manual Testing

### Test 1: Agent Zero → Claude Code

**Purpose**: Verify Agent Zero can invoke Claude Code

```bash
# Test basic invocation
docker exec agent-zero claude-pro-yolo 'Say hello and confirm you can receive messages'

# Test with a task
docker exec agent-zero claude-pro-yolo 'Write a Python function to calculate fibonacci numbers'
```

**Expected Result**: Claude Code responds with code or analysis

**Note**: If you see "Invalid API key", Claude Code needs authentication. See authentication guide.

### Test 2: Get MCP Token

**Purpose**: Obtain the token needed for Claude Code to connect to Agent Zero

**Method 1: Via Web UI (Recommended)**
1. Open Agent Zero Web UI: http://localhost:8888
2. Log in with your credentials
3. Navigate to: **Settings > MCP Server**
4. Copy the MCP Server URL (contains the token)
   - Format: `http://localhost:8888/mcp/t-{TOKEN}/sse`

**Method 2: Via Settings File**
```bash
docker exec agent-zero cat /a0/tmp/settings.json | grep mcp_server_token
```

**Method 3: Generate from Credentials**
The token is generated from your username and password. You can find it in:
- **Settings > External Services > API Token**

### Test 3: MCP Connection Test

**Purpose**: Verify Claude Code can connect to Agent Zero's MCP server

**Option A: Using Test Script**
```bash
# Get your token first (from Web UI)
python3 test_mcp_connection.py YOUR_TOKEN
```

**Option B: Manual Test**
```bash
# Test MCP endpoint (replace TOKEN with your actual token)
curl http://localhost:8888/mcp/t-TOKEN/sse
```

**Expected Result**: 
- Status 200: Connection successful
- Status 401: Authentication issue (check token)
- Status 404: Endpoint not found (check URL)

### Test 4: Claude Code → Agent Zero (MCP)

**Purpose**: Verify Claude Code can invoke Agent Zero tools via MCP

**Prerequisites**:
- MCP token obtained
- Claude Code configured with Agent Zero MCP server

**Configuration**:
Add to Claude Code's MCP configuration (typically `mcp.json`):

```json
{
    "mcpServers": {
        "agent-zero": {
            "type": "sse",
            "url": "http://localhost:8888/mcp/t-YOUR_TOKEN/sse"
        }
    }
}
```

**Test Commands in Claude Code**:

1. **Test send_message tool**:
   ```
   Ask Agent Zero to list the files in /a0 directory
   ```

2. **Test network_scan tool**:
   ```
   Use Agent Zero to scan localhost for open ports
   ```

3. **Test web_scan tool**:
   ```
   Use Agent Zero to scan https://example.com for vulnerabilities
   ```

**Expected Result**: Claude Code invokes Agent Zero tools and receives responses

## Troubleshooting

### Issue: Claude Code "Invalid API key"

**Solution**: Claude Code needs OAuth authentication
1. Run: `docker exec -it agent-zero claude-pro`
2. Follow OAuth flow (use VNC if needed for CAPTCHA)
3. See `CLAUDE_CODE_AUTH.md` for details

### Issue: MCP Connection Failed

**Check**:
1. Agent Zero is running: `docker ps | grep agent-zero`
2. Web UI is accessible: `curl http://localhost:8888`
3. Token is correct (from Settings > MCP Server)
4. URL format is correct: `http://localhost:8888/mcp/t-{TOKEN}/sse`

### Issue: Tools Not Available

**Check**:
1. MCP connection is established (check Claude Code logs)
2. Agent Zero MCP server is enabled (Settings > MCP Server)
3. Token has not changed (regenerate if credentials changed)

### Issue: Port Not Accessible

**Check**:
- Internal port: 80 (inside container)
- External port: 8888 (from host)
- Port mapping: `docker-compose.yml` shows `8888:80`

## Integration Status Checklist

- [ ] Claude Code installed (`claude-pro --version`)
- [ ] Agent Zero Web UI accessible
- [ ] Agent Zero → Claude Code working (terminal test)
- [ ] MCP token obtained
- [ ] MCP endpoint accessible
- [ ] Claude Code configured with MCP server
- [ ] Claude Code → Agent Zero working (MCP test)
- [ ] Both directions tested successfully

## Next Steps

Once integration is tested:

1. **Use Granular Tools**: Direct tool access for specific operations
2. **Use send_message**: Conversational interface for complex workflows
3. **Set Up Security Assessments**: Use shared assessment state
4. **Automate Workflows**: Combine Claude Code analysis with Agent Zero execution

## See Also

- **[How Claude Uses Agent Zero](./HOW_CLAUDE_USES_AGENT_ZERO.md)** - Detailed integration guide
- **[MCP vs A2A Comparison](./MCP_VS_A2A_COMPARISON.md)** - Protocol comparison
- **[Claude Code Integration](../knowledge/default/main/claude_code_integration.md)** - Knowledge base entry
