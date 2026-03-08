#!/usr/bin/env bash
# Test Cursor/Claude → Agent Zero MCP connectivity.
# Agent Zero serves MCP over HTTPS only (HTTP returns empty reply).

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Config: same as typical Cursor config (HTTPS, token in URL)
HOST="${AGENT_ZERO_HOST:-192.168.50.7}"
PORT="${AGENT_ZERO_PORT:-8888}"
BASE="https://${HOST}:${PORT}"

echo "=========================================="
echo "Agent Zero MCP connectivity test"
echo "=========================================="
echo ""

# Resolve token from container runtime
TOKEN=""
if docker ps --format '{{.Names}}' | grep -qx agent-zero; then
  TOKEN="$(docker exec agent-zero bash -lc "cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c 'from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.get_settings()[\"mcp_server_token\"])'" 2>/dev/null || true)"
fi

if [ -z "$TOKEN" ]; then
  echo -e "${YELLOW}Could not read MCP token from container. Set TOKEN or run configure_mcp_token.sh.${NC}"
  echo "Using token from env or default for URL test only..."
  TOKEN="${MCP_TOKEN:-11mu_QnUJiEWloEq}"
fi

echo -e "${BLUE}1. Web UI (HTTPS)${NC}"
UI_CODE=$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 -k "$BASE/" 2>/dev/null || echo "000")
if [ "$UI_CODE" = "302" ] || [ "$UI_CODE" = "200" ]; then
  echo -e "   ${GREEN}OK${NC} $BASE/ → HTTP $UI_CODE"
else
  echo -e "   ${RED}FAIL${NC} $BASE/ → HTTP $UI_CODE (expected 200/302)"
fi
echo ""

echo -e "${BLUE}2. MCP SSE endpoint (first event)${NC}"
SSE_URL="$BASE/mcp/t-$TOKEN/sse"
# SSE keeps connection open; we capture first line and exit after a short time
SSE_OUT=$(curl -sS -k -N --connect-timeout 5 -H "Accept: text/event-stream" "$SSE_URL" 2>/dev/null & PID=$!; sleep 2; kill $PID 2>/dev/null; wait $PID 2>/dev/null) || true
if echo "$SSE_OUT" | grep -q "event: endpoint"; then
  echo -e "   ${GREEN}OK${NC} SSE sent initial event (endpoint)"
  echo "$SSE_OUT" | head -3 | sed 's/^/   /'
else
  echo -e "   ${RED}FAIL${NC} No SSE event received (timeout or wrong token)"
  echo "   URL: $SSE_URL"
fi
echo ""

echo -e "${BLUE}3. MCP streamable-http endpoint${NC}"
HTTP_URL="$BASE/mcp/t-$TOKEN/http"
HTTP_CODE=$(curl -sS -o /dev/null -w "%{http_code}" --connect-timeout 5 -k "$HTTP_URL" 2>/dev/null || echo "000")
if [ "$HTTP_CODE" = "307" ] || [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "405" ]; then
  echo -e "   ${GREEN}OK${NC} $HTTP_URL → HTTP $HTTP_CODE (307/405 normal for GET)"
else
  echo -e "   ${YELLOW}INFO${NC} $HTTP_URL → HTTP $HTTP_CODE"
fi
echo ""

echo "=========================================="
echo "Cursor/Claude must use HTTPS (not HTTP)."
echo "Example: https://$HOST:$PORT/mcp/t-$TOKEN/sse"
echo "=========================================="
