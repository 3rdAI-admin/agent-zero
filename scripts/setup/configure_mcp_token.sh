#!/bin/bash
# Show the effective MCP token for Agent Zero.

set -e

echo "=========================================="
echo "Configuring MCP Token for Agent Zero"
echo "=========================================="
echo ""

TOKEN="$(docker exec agent-zero bash -lc "cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c 'from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.get_settings()[\"mcp_server_token\"])'" 2>/dev/null || true)"

if [ -z "$TOKEN" ]; then
    echo "❌ Could not resolve MCP token from runtime."
    echo "   Check that the container is running and AUTH_* values are configured."
    exit 1
fi

echo "✅ MCP token resolved from runtime"
echo "   Token: $TOKEN"
echo ""
echo "📋 MCP Connection URLs:"
echo "   SSE:  http://localhost:8888/mcp/t-${TOKEN}/sse"
echo "   HTTP: http://localhost:8888/mcp/t-${TOKEN}/http/"
echo ""
echo "📝 Claude Code Configuration (add to mcp.json):"
echo "{"
echo '    "mcpServers": {'
echo '        "agent-zero": {'
echo '            "type": "sse",'
echo "            \"url\": \"http://localhost:8888/mcp/t-${TOKEN}/sse\""
echo '        }'
echo '    }'
echo "}"

echo ""
echo "=========================================="
echo "Configuration Complete"
echo "=========================================="
echo ""
echo "⚠️  Note: The MCP token is runtime-derived."
echo "   This script no longer writes settings files because the token is not"
echo "   persisted in usr/settings.json or tmp/settings.json."
echo ""
echo "To verify:"
echo "  1. Check Web UI: http://localhost:8888 → Settings → MCP Server"
echo "  2. Test endpoint: curl http://localhost:8888/mcp/t-TOKEN/sse"
echo ""
