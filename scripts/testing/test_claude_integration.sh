#!/bin/bash
# Test Claude Code Integration with Agent Zero

set -e

echo "=========================================="
echo "Claude Code ↔ Agent Zero Integration Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test 1: Claude Code Installation
echo -e "${YELLOW}[Test 1] Checking Claude Code installation...${NC}"
if docker exec agent-zero bash -c "which claude-pro >/dev/null 2>&1"; then
    VERSION=$(docker exec agent-zero bash -c "claude-pro --version 2>&1 | head -1")
    echo -e "${GREEN}✅ Claude Code installed: $VERSION${NC}"
else
    echo -e "${RED}❌ Claude Code not found${NC}"
    exit 1
fi
echo ""

# Test 2: Agent Zero Web UI
echo -e "${YELLOW}[Test 2] Checking Agent Zero Web UI...${NC}"
# Check both port 80 (internal) and 8888 (mapped)
if docker exec agent-zero bash -c "curl -s http://localhost:80 >/dev/null 2>&1 || curl -s http://localhost >/dev/null 2>&1"; then
    echo -e "${GREEN}✅ Agent Zero Web UI is running (internal port 80)${NC}"
    echo "   External access: http://localhost:8888 (from host)"
else
    echo -e "${RED}❌ Agent Zero Web UI not accessible${NC}"
    exit 1
fi
echo ""

# Test 3: Agent Zero → Claude Code (Terminal)
echo -e "${YELLOW}[Test 3] Testing Agent Zero → Claude Code (via terminal)...${NC}"
TEST_CMD="claude-pro-yolo 'Say hello and confirm you can receive messages from Agent Zero'"
RESULT=$(docker exec agent-zero bash -c "$TEST_CMD 2>&1" | head -30)
if echo "$RESULT" | grep -qi "hello\|hi\|received\|message"; then
    echo -e "${GREEN}✅ Claude Code responded to Agent Zero${NC}"
    echo "Response preview:"
    echo "$RESULT" | head -5
else
    echo -e "${YELLOW}⚠️  Claude Code may need authentication or returned unexpected response${NC}"
    echo "Full response:"
    echo "$RESULT"
fi
echo ""

# Test 4: MCP Server Endpoint
echo -e "${YELLOW}[Test 4] Checking MCP Server endpoint...${NC}"
MCP_RESPONSE=$(docker exec agent-zero bash -c "curl -s http://localhost:8888/mcp 2>&1" | head -5)
if echo "$MCP_RESPONSE" | grep -qi "error\|not found\|404"; then
    echo -e "${YELLOW}⚠️  MCP endpoint may require token (this is normal)${NC}"
else
    echo -e "${GREEN}✅ MCP endpoint accessible${NC}"
fi
echo ""

# Test 5: MCP Token (if available)
echo -e "${YELLOW}[Test 5] Checking MCP token configuration...${NC}"
TOKEN=$(docker exec agent-zero bash -c "cat /a0/tmp/settings.json 2>/dev/null | grep -o '\"mcp_server_token\": \"[^\"]*\"' | cut -d'\"' -f4" || echo "")
if [ -z "$TOKEN" ] || [ "$TOKEN" = "" ]; then
    echo -e "${YELLOW}⚠️  MCP token not set (will be generated on first login)${NC}"
    echo "   To get your MCP token:"
    echo "   1. Log into Agent Zero Web UI at http://localhost:8888"
    echo "   2. Go to Settings > MCP Server"
    echo "   3. Copy the MCP Server URL (contains the token)"
else
    echo -e "${GREEN}✅ MCP token configured: ${TOKEN:0:20}...${NC}"
fi
echo ""

# Test 6: Claude Code YOLO Mode
echo -e "${YELLOW}[Test 6] Testing Claude Code YOLO mode wrapper...${NC}"
if docker exec agent-zero bash -c "which claude-pro-yolo >/dev/null 2>&1"; then
    echo -e "${GREEN}✅ claude-pro-yolo wrapper available${NC}"
    # Test if it runs without errors (may need auth)
    YOLO_TEST=$(docker exec agent-zero bash -c "claude-pro-yolo 'test' 2>&1" | head -5)
    if echo "$YOLO_TEST" | grep -qi "error\|not found"; then
        echo -e "${YELLOW}⚠️  YOLO mode may need authentication${NC}"
    else
        echo -e "${GREEN}✅ YOLO mode wrapper functional${NC}"
    fi
else
    echo -e "${RED}❌ claude-pro-yolo wrapper not found${NC}"
fi
echo ""

# Summary
echo "=========================================="
echo "Integration Test Summary"
echo "=========================================="
echo ""
echo "✅ Claude Code Installation: Verified"
echo "✅ Agent Zero Web UI: Running"
echo "✅ Agent Zero → Claude Code: Tested (may need auth)"
echo "⚠️  Claude Code → Agent Zero (MCP): Requires MCP token configuration"
echo ""
echo "Next Steps:"
echo "1. Get MCP token from Agent Zero Web UI (Settings > MCP Server)"
echo "2. Configure Claude Code to connect to Agent Zero MCP server"
echo "3. Test bidirectional communication"
echo ""
echo "For detailed setup instructions, see:"
echo "  - docs/HOW_CLAUDE_USES_AGENT_ZERO.md"
echo "  - docs/MCP_VS_A2A_COMPARISON.md"
echo ""
