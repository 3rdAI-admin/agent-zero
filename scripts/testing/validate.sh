#!/bin/bash
# Agent Zero Comprehensive Validation
# Runs validation phases sequentially

set +e  # Don't exit on errors, collect all results

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PASSED=0
FAILED=0
SKIPPED=0
CONTAINER_OK=0
LIVENESS_OK=0
READINESS_OK=0
RELIABILITY_OK=0
SUPERVISOR_OK=0
VNC_OK=0
CLAUDE_OK=0
WRAPPER_OK=0
VOLUMES_OK=0
MCP_OK=0
SECURITY_TOOLS_OK=0
RESOURCE_LIMITS_OK=0

LAST_CONTAINER_SCHEME="http"

container_endpoint_code() {
    local path="$1"
    local code="000"
    local scheme
    for scheme in http https; do
        if [ "$scheme" = "https" ]; then
            code=$(docker exec agent-zero curl -sk -o /dev/null -w '%{http_code}' --max-time 5 "${scheme}://localhost:80${path}" 2>/dev/null || echo "000")
        else
            code=$(docker exec agent-zero curl -s -o /dev/null -w '%{http_code}' --max-time 5 "${scheme}://localhost:80${path}" 2>/dev/null || echo "000")
        fi
        if [ "$code" != "000" ]; then
            LAST_CONTAINER_SCHEME="$scheme"
            echo "$code"
            return 0
        fi
    done
    echo "000"
}

container_endpoint_body() {
    local path="$1"
    if [ "${LAST_CONTAINER_SCHEME:-http}" = "https" ]; then
        docker exec agent-zero curl -sk --max-time 5 "https://localhost:80${path}" 2>/dev/null || true
    else
        docker exec agent-zero curl -s --max-time 5 "http://localhost:80${path}" 2>/dev/null || true
    fi
}

echo "=========================================="
echo "Agent Zero Validation"
echo "=========================================="
echo ""

# Phase 1: Container Health
echo -e "${BLUE}[Phase 1] Container Health${NC}"
if docker ps --filter name=agent-zero --format "{{.Names}}" 2>/dev/null | grep -q "^agent-zero$"; then
    echo -e "${GREEN}✅ Container is running${NC}"
    CONTAINER_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ Container is not running${NC}"
    echo "   Run: docker compose up -d"
    ((FAILED++))
    echo ""
    echo "STOPPING - Container must be running"
    exit 1
fi
echo ""

# Phase 2: Web UI
echo -e "${BLUE}[Phase 2] Liveness${NC}"
if [ "$(container_endpoint_code "/health")" = "200" ]; then
    echo -e "${GREEN}✅ Liveness endpoint accessible (/health)${NC}"
    LIVENESS_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ Liveness endpoint not accessible${NC}"
    ((FAILED++))
fi
echo ""

# Phase 3: Readiness
echo -e "${BLUE}[Phase 3] Readiness${NC}"
READY_CODE=$(container_endpoint_code "/ready")
READY_BODY=$(container_endpoint_body "/ready")
if [ "$READY_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Readiness endpoint reports ready (/ready)${NC}"
    DEGRADED=$(READY_BODY_ENV="$READY_BODY" python3 - <<'PY'
import json
import os
try:
    payload = json.loads(os.environ.get("READY_BODY_ENV", ""))
except Exception:
    print("")
    raise SystemExit(0)
phases = payload.get("phases", {}) if isinstance(payload, dict) else {}
degraded = [
    name
    for name, phase in phases.items()
    if isinstance(phase, dict)
    and not phase.get("required")
    and phase.get("status") == "failed"
]
print(", ".join(degraded))
PY
)
    if [ -n "$DEGRADED" ]; then
        echo "   Degraded phases: $DEGRADED"
    fi
    READINESS_OK=1
    ((PASSED++))
else
    BLOCKING=$(READY_BODY_ENV="$READY_BODY" python3 - <<'PY'
import json
import os
import sys
try:
    payload = json.loads(os.environ.get("READY_BODY_ENV", ""))
except Exception:
    print("")
    raise SystemExit(0)
phases = payload.get("phases", {}) if isinstance(payload, dict) else {}
blocking = [
    name
    for name, phase in phases.items()
    if isinstance(phase, dict)
    and phase.get("required")
    and phase.get("status") != "ready"
]
print(", ".join(blocking))
PY
)
    echo -e "${RED}❌ Readiness endpoint not ready${NC}"
    if [ -n "$BLOCKING" ]; then
        echo "   Blocking phases: $BLOCKING"
    fi
    ((FAILED++))
fi
echo ""

# Phase 3b: Reliability
echo -e "${BLUE}[Phase 3b] Reliability${NC}"
if ./scripts/testing/validate_reliability.sh; then
    echo -e "${GREEN}✅ Reliability validation passed${NC}"
    RELIABILITY_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ Reliability validation failed${NC}"
    ((FAILED++))
fi
echo ""

# Phase 4: Supervisor Services
echo -e "${BLUE}[Phase 4] Supervisor Services${NC}"
SERVICES=("run_ui" "xvfb" "fluxbox" "x11vnc")
RUNNING=0
for service in "${SERVICES[@]}"; do
    STATUS=$(docker exec agent-zero supervisorctl status "$service" 2>/dev/null | head -1 || echo "")
    if echo "$STATUS" | grep -q "RUNNING"; then
        echo -e "  ${GREEN}✅ $service: RUNNING${NC}"
        ((RUNNING++))
    else
        echo -e "  ${RED}❌ $service: ${STATUS:-NOT FOUND}${NC}"
    fi
done
if [ $RUNNING -eq ${#SERVICES[@]} ]; then
    SUPERVISOR_OK=1
    ((PASSED++))
else
    ((FAILED++))
fi
echo ""

# Phase 5: VNC Server
echo -e "${BLUE}[Phase 5] VNC Server${NC}"
if docker exec agent-zero supervisorctl status x11vnc 2>/dev/null | grep -q "RUNNING"; then
    echo -e "${GREEN}✅ VNC server running (vnc://localhost:5901)${NC}"
    VNC_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ VNC server not running${NC}"
    ((FAILED++))
fi
echo ""

# Phase 6: Claude Code
echo -e "${BLUE}[Phase 6] Claude Code${NC}"
if docker exec agent-zero which claude-pro >/dev/null 2>&1; then
    VERSION=$(docker exec agent-zero claude-pro --version 2>&1 | head -1 || echo "installed")
    echo -e "${GREEN}✅ Claude Code: $VERSION${NC}"
    CLAUDE_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ Claude Code not found${NC}"
    ((FAILED++))
fi

if docker exec agent-zero which claude-pro-yolo >/dev/null 2>&1; then
    echo -e "${GREEN}✅ claude-pro-yolo wrapper available${NC}"
    WRAPPER_OK=1
    ((PASSED++))
else
    echo -e "${RED}❌ claude-pro-yolo not found${NC}"
    ((FAILED++))
fi
echo ""

# Phase 7: Volume Mounts
echo -e "${BLUE}[Phase 7] Volume Mounts${NC}"
VOLUMES=("memory" "knowledge" "logs" "tmp" "claude-config")
MOUNTED=0
for vol in "${VOLUMES[@]}"; do
    if [ -d "./$vol" ]; then
        echo -e "  ${GREEN}✅ $vol${NC}"
        ((MOUNTED++))
    else
        echo -e "  ${YELLOW}⚠️  $vol (will be created)${NC}"
    fi
done
if [ $MOUNTED -ge 3 ]; then
    VOLUMES_OK=1
    ((PASSED++))
else
    ((SKIPPED++))
fi
echo ""

# Phase 8: MCP Configuration
echo -e "${BLUE}[Phase 8] MCP Server${NC}"
TOKEN="$(docker exec agent-zero bash -lc "cd /a0 && PYTHONPATH=/a0 /opt/venv-a0/bin/python -c 'from python.helpers import dotenv, runtime, settings; runtime.initialize(); dotenv.load_dotenv(); settings.reload_settings(); print(settings.get_settings()[\"mcp_server_token\"])'" 2>/dev/null || true)"
if [ -n "$TOKEN" ] && [ "$TOKEN" != "" ]; then
    echo -e "${GREEN}✅ MCP token configured${NC}"
    MCP_OK=1
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  MCP token not configured${NC}"
    ((SKIPPED++))
fi
echo ""

# Phase 9: Security Tools
echo -e "${BLUE}[Phase 9] Security Tools${NC}"
TOOLS=("nmap" "nikto")
FOUND=0
for tool in "${TOOLS[@]}"; do
    if docker exec agent-zero which "$tool" >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ $tool${NC}"
        ((FOUND++))
    else
        echo -e "  ${YELLOW}⚠️  $tool (optional)${NC}"
    fi
done
if [ $FOUND -gt 0 ]; then
    SECURITY_TOOLS_OK=1
    ((PASSED++))
else
    ((SKIPPED++))
fi
echo ""

# Phase 10: Resource Limits
echo -e "${BLUE}[Phase 10] Resource Limits${NC}"
MEMORY=$(docker inspect agent-zero --format='{{.HostConfig.Memory}}' 2>/dev/null || echo "0")
if [ "$MEMORY" != "0" ] && [ -n "$MEMORY" ]; then
    MEM_GB=$((MEMORY / 1024 / 1024 / 1024))
    echo -e "${GREEN}✅ Memory limit: ${MEM_GB}GB${NC}"
    RESOURCE_LIMITS_OK=1
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Memory limit not set${NC}"
    ((SKIPPED++))
fi
echo ""

# Summary Table
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""
printf "| %-20s | %-10s |\n" "Phase" "Status"
echo "|----------------------|-----------|"
printf "| %-20s | %-10s |\n" "1. Container" "$([ $CONTAINER_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "2. Liveness" "$([ $LIVENESS_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "3. Readiness" "$([ $READINESS_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "3b. Reliability" "$([ $RELIABILITY_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "4. Supervisor" "$([ $SUPERVISOR_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "5. VNC" "$([ $VNC_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "6. Claude Code" "$([ $CLAUDE_OK -eq 1 ] && [ $WRAPPER_OK -eq 1 ] && echo "✅ PASS" || echo "❌ FAIL")"
printf "| %-20s | %-10s |\n" "7. Volumes" "$([ $VOLUMES_OK -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
printf "| %-20s | %-10s |\n" "8. MCP" "$([ $MCP_OK -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
printf "| %-20s | %-10s |\n" "9. Security Tools" "$([ $SECURITY_TOOLS_OK -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
printf "| %-20s | %-10s |\n" "10. Resources" "$([ $RESOURCE_LIMITS_OK -eq 1 ] && echo "✅ PASS" || echo "⚠️  SKIP")"
echo ""
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Skipped: $SKIPPED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Overall: PASSED${NC}"
    exit 0
else
    echo -e "${RED}❌ Overall: FAILED - $FAILED critical issues${NC}"
    exit 1
fi
