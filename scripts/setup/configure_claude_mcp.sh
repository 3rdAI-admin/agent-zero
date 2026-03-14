#!/bin/bash
# Configure Claude Code MCP Client to connect to Agent Zero

set -e

echo "=========================================="
echo "Configuring Claude Code MCP Client"
echo "=========================================="
echo ""

# Get MCP token from Agent Zero runtime
TOKEN="$(docker exec agent-zero bash -lc "cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c 'from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.get_settings()[\"mcp_server_token\"])'" 2>/dev/null || true)"

if [ -z "$TOKEN" ]; then
echo "❌ Error: MCP token not available from Agent Zero runtime"
    echo ""
    echo "Please run: ./configure_mcp_token.sh first"
    exit 1
fi

echo "✅ Found MCP token: ${TOKEN:0:8}..."
echo ""

# Create Claude Code config directory
echo "[Step 1] Creating Claude Code config directory..."
docker exec agent-zero bash -c "mkdir -p /root/.claude" || true
echo "✅ Config directory ready"
echo ""

# Create/Update .mcp.json file
echo "[Step 2] Creating/updating .mcp.json configuration..."
docker exec agent-zero bash -lc "TOKEN=\$(cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c 'from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.get_settings()[\"mcp_server_token\"])'); echo \"{\" > /root/.claude/.mcp.json && echo '  \"mcpServers\": {' >> /root/.claude/.mcp.json && echo '    \"agent-zero\": {' >> /root/.claude/.mcp.json && echo '      \"type\": \"sse\",' >> /root/.claude/.mcp.json && echo \"      \\\"url\\\": \\\"http://localhost:8888/mcp/t-\${TOKEN}/sse\\\"\" >> /root/.claude/.mcp.json && echo '    }' >> /root/.claude/.mcp.json && echo '  }' >> /root/.claude/.mcp.json && echo '}' >> /root/.claude/.mcp.json"

# Verify configuration
echo "[Step 3] Verifying configuration..."
CONFIG_VALID=$(docker exec agent-zero bash -c "cat /root/.claude/.mcp.json | python3 -m json.tool >/dev/null 2>&1 && echo 'valid' || echo 'invalid'")

if [ "$CONFIG_VALID" = "valid" ]; then
    echo "✅ Configuration file is valid JSON"
    echo ""
    echo "Configuration:"
    docker exec agent-zero bash -c "cat /root/.claude/.mcp.json | python3 -m json.tool"
else
    echo "❌ Configuration file is invalid JSON"
    exit 1
fi

echo ""
echo "=========================================="
echo "Configuration Complete"
echo "=========================================="
echo ""
echo "✅ Claude Code MCP configuration created at:"
echo "   /root/.claude/.mcp.json"
echo ""
echo "📋 MCP Server Details:"
echo "   Name: agent-zero"
echo "   Type: sse"
echo "   URL: http://localhost:8888/mcp/t-${TOKEN}/sse"
echo ""
echo "🔍 To verify configuration:"
echo "   docker exec agent-zero claude-pro mcp list"
echo ""
echo "📝 To test connection:"
echo "   docker exec agent-zero claude-pro 'Use Agent Zero to list files in /a0'"
echo ""
echo "⚠️  Note: Claude Code may need to be restarted or reloaded"
echo "   for the MCP configuration to take effect."
echo ""
