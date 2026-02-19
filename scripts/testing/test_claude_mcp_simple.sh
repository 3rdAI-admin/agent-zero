#!/bin/bash
# Simple MCP Connection Test for Claude Code ↔ Agent Zero

set -e

echo "=========================================="
echo "Claude Code ↔ Agent Zero MCP Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get MCP token from container settings
echo -e "${BLUE}[Step 1] Getting MCP token...${NC}"
TOKEN=$(docker exec agent-zero bash -c "cat /a0/tmp/settings.json 2>/dev/null | grep -o '\"mcp_server_token\": \"[^\"]*\"' | cut -d'\"' -f4" || echo "")

if [ -z "$TOKEN" ] || [ "$TOKEN" = "" ]; then
    echo -e "${YELLOW}⚠️  MCP token not found in settings${NC}"
    echo ""
    echo "The token is generated from your username/password."
    echo "To get it:"
    echo "  1. Log into Agent Zero Web UI: http://localhost:8888"
    echo "  2. Go to: Settings > MCP Server"
    echo "  3. Copy the token from the MCP Server URL"
    echo ""
    echo "Or check: Settings > External Services > API Token"
    echo ""
    read -p "Enter MCP token (or press Enter to skip MCP test): " MANUAL_TOKEN
    if [ -n "$MANUAL_TOKEN" ]; then
        TOKEN="$MANUAL_TOKEN"
    else
        echo -e "${YELLOW}Skipping MCP connection test...${NC}"
        TOKEN=""
    fi
else
    echo -e "${GREEN}✅ Found MCP token: ${TOKEN:0:8}...${NC}"
fi
echo ""

if [ -n "$TOKEN" ]; then
    # Test MCP endpoint (Agent Zero serves MCP over HTTPS only)
    echo -e "${BLUE}[Step 2] Testing MCP endpoint...${NC}"
    MCP_URL="https://localhost:8888/mcp/t-${TOKEN}/sse"
    echo "   URL: $MCP_URL"
    
    # Test from host: use HTTPS and expect SSE stream (curl may not get 200 for long-lived SSE)
    SSE_HIT=$(curl -s -k -N -H "Accept: text/event-stream" --connect-timeout 3 "$MCP_URL" 2>/dev/null & PID=$!; sleep 2; kill $PID 2>/dev/null; wait $PID 2>/dev/null; true)
    RESPONSE="000"
    echo "$SSE_HIT" | grep -q "event: endpoint" && RESPONSE="200"
    
    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}✅ MCP endpoint is accessible (SSE event received)${NC}"
    elif [ "$RESPONSE" = "000" ]; then
        echo -e "${YELLOW}⚠️  Could not connect from host (use HTTPS, not HTTP)${NC}"
        echo "   Testing from inside container..."
        CONTAINER_HIT=$(docker exec agent-zero bash -c "curl -s -k -N --max-time 2 -H 'Accept: text/event-stream' 'https://localhost:80/mcp/t-${TOKEN}/sse' 2>/dev/null" || true)
        if echo "$CONTAINER_HIT" | grep -q "event: endpoint"; then
            echo -e "${GREEN}✅ MCP endpoint accessible from container${NC}"
        else
            echo -e "${RED}❌ MCP endpoint not accessible${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  Unexpected response: $RESPONSE${NC}"
    fi
    echo ""
    
    # Show configuration
    echo -e "${BLUE}[Step 3] Claude Code MCP Configuration${NC}"
    echo ""
    echo "Add this to Claude Code's mcp.json:"
    echo ""
    echo -e "${GREEN}{"
    echo "    \"mcpServers\": {"
    echo "        \"agent-zero\": {"
    echo "            \"type\": \"sse\","
    echo "            \"url\": \"$MCP_URL\""
    echo "        }"
    echo "    }"
    echo -e "}${NC}"
    echo ""
fi

# Test Agent Zero → Claude Code
echo -e "${BLUE}[Step 4] Testing Agent Zero → Claude Code...${NC}"
echo "   (This tests terminal invocation)"
TEST_CMD="claude-pro-yolo 'Hello, this is a test message from Agent Zero. Please respond with a brief confirmation.'"
RESULT=$(docker exec agent-zero bash -c "$TEST_CMD 2>&1" | head -10)

if echo "$RESULT" | grep -qi "hello\|hi\|received\|confirmation\|test"; then
    echo -e "${GREEN}✅ Claude Code responded${NC}"
elif echo "$RESULT" | grep -qi "Invalid API key\|Please run /login"; then
    echo -e "${YELLOW}⚠️  Claude Code needs authentication${NC}"
    echo "   Run: docker exec -it agent-zero claude-pro"
    echo "   Follow OAuth flow (use VNC if needed)"
else
    echo -e "${YELLOW}⚠️  Unexpected response${NC}"
    echo "   Response: $RESULT"
fi
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo ""
if [ -n "$TOKEN" ]; then
    echo -e "${GREEN}✅ MCP Token: Obtained${NC}"
    echo -e "${GREEN}✅ MCP Endpoint: Tested${NC}"
else
    echo -e "${YELLOW}⚠️  MCP Token: Not obtained${NC}"
fi
echo -e "${GREEN}✅ Agent Zero → Claude Code: Tested${NC}"
if [ -n "$TOKEN" ]; then
    echo -e "${BLUE}📋 Next: Configure Claude Code with MCP server${NC}"
else
    echo -e "${BLUE}📋 Next: Get MCP token from Web UI${NC}"
fi
echo ""
echo "For detailed instructions, see:"
echo "  - docs/TEST_CLAUDE_INTEGRATION.md"
echo "  - docs/HOW_CLAUDE_USES_AGENT_ZERO.md"
echo ""
